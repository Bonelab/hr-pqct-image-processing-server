"""
job.py Version 2.0
Author: Ian Smith
Description: This file contains a JobData and a JobManager class. The JobData class is a context managed class meant
to be able to read data from formatted folders and import the data into the program here. JobManager is a class that
sort of serves as a filemanager, with the ability to format files into the folder structure recognized by job data.
It also handles things like movement of files within the program
Created 2023-06-12
"""
import yaml

import constants, ip_utils

import os
import shutil
from datetime import datetime
from datetime import timedelta


class JobData:
    """
    A class to act as a common interface to access job images and metadata
    This class allows the job data to behave like a file
    """
    def __init__(self, base_dir):
        """
        Constructor method
        Imports data into the class
        :param base_dir: base directory of job data -- outermost folder of data
        """
        self.base = base_dir
        self.base_name = os.path.basename(base_dir)

        self.com_file_path = None
        self.com_file_name = None
        self.data = {}

        self.image_file_path = None
        self.image_file_name = None

        self.proc_dir_name = 'masks'
        self.proc_dir_path = os.path.join(base_dir, self.proc_dir_name)

        self.initialize()

    def __enter__(self):
        """
        Method to implement opening up job data via a context manager
        :return: self
        """
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Method to implement opening up job data via a context manager
        Whatever is changed in the data attribute will be written to the com file
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self._write_yaml()

    def initialize(self):
        """
        Initializes job data, finds com file and then associated image file
        :return:
        """
        self.com_file_name = self._find_com()
        self.com_file_path = os.path.join(self.base, self.com_file_name)
        self.data = self._parse_yaml()
        image_path = self._find_image()
        self.image_file_path = image_path
        self.image_file_name = self.data.get(constants.TARGET_IMAGE)

    def _find_image(self):
        """
        Function to find associated image file from the associated com file
        :return: returns path to associated image file
        """
        if self.data is None:
            raise FileNotFoundError
        image_name = self.data.get(constants.TARGET_IMAGE).lower()
        image_path = os.path.join(self.base, image_name)
        if os.path.exists(image_path):
            return image_path

    def _find_com(self):
        """
        Finds com file within base directory
        :return: Returns the full path to the com file
        """
        if os.path.isdir(self.base):
            contents = os.listdir(self.base)
        else:
            contents = []
        for file in contents:
            if file.lower().endswith(".yaml"):
                return file
        raise FileNotFoundError

    def _parse_yaml(self):
        print(self.com_file_path)
        with open(self.com_file_path, 'r') as file:
            command_file = yaml.safe_load(file)
        return command_file

    def _write_yaml(self):
        with open(self.com_file_path, 'w') as file:
            yaml.safe_dump(self.data, file, default_flow_style=False)



class JobManager:
    """
    A class to handle necessary file operations within the system
    """
    def __init__(self, logger):
        """
        Constructor method
        :param logger: Injected Logger
        """
        self.logs = logger
        self._ensure_directories_exist()

    # Function to move job data once formatted into the standard format
    def move(self, job_base, destination):
        """
        Method to move job data directories
        :param job_base: Name of directory you want to move
        :param destination: Destination location of where you want to move the dir
        :return: Returns the path of the moved directory
        """
        with JobData(job_base) as jd:
            date = datetime.today()
            date_str = date.strftime("%Y-%m-%d")
            jd.data[constants.DATE] = date_str

        try:
            new_base = shutil.move(job_base, destination)
        except FileExistsError:
            rename = self._name_dir(job_base)
            path = os.path.dirname(job_base)
            new_path = os.path.join(path, rename)
            os.rename(job_base, rename)
            self.logs.log_debug("{} renamed to {}".format(os.path.basename(job_base), rename))
            new_base = shutil.move(new_path, destination)
        except shutil.Error:
            with JobData(job_base) as jd:
                com_file = jd.com_file_path
            rename = self._name_dir(com_file) + "\\"
            path = os.path.dirname(job_base)
            new_path = os.path.join(path, rename)
            os.rename(job_base, new_path)
            self.logs.log_debug("{} renamed to {}".format(os.path.basename(job_base), rename))
            new_base = shutil.move(new_path, destination)
        return os.path.abspath(new_base)

    def create_job_data(self, com_file):
        """
        Initialization method for formatting files into JobData format
        :param com_file: COM file of data that you want to format
        :return: returns the path of the formatted JobData
        """
        com, img = self._create_association(com_file)
        base = self._format_job_data(com, img)
        return base

    def _format_job_data(self, com_file, image_file):
        """
        Method to move JobData files into the JobData dir also creates masks subdir
        :param com_file: Com file to be moved
        :param image_file: Image file to be moved
        :return:
        """
        self.logs.log_debug("Formatting {}".format(os.path.basename(image_file)))
        com_file = os.path.abspath(com_file)
        dir_name = os.path.dirname(com_file)
        image_file = os.path.abspath(image_file)
        base = os.path.join(dir_name, self._name_dir(com_file))
        os.mkdir(base)

        shutil.move(com_file, base)
        shutil.move(image_file, base)
        mask_dir = os.path.join(base, "masks")
        os.mkdir(mask_dir)
        return base

    def _name_dir(self, com_file):
        """
        Method to name a jobs base directory, will append a version number to it if there are multiple of the same name
        :param com_file: com file
        :return: Returns the job name
        """
        # metadata = self._parse_com(com_file)
        metadata = self._parse_yaml(com_file)
        job_names = self._get_all_jobs()
        cur_job_name = metadata.get(constants.F_NAME)  # TODO: Change this to the proper param
        count = 0

        for name in job_names:
            if cur_job_name in name:
                count += 1

        if count > 0:
            cur_job_name = cur_job_name + "-{}".format(count)
        # TODO change job name within com file? or just add

        return cur_job_name

    # TODO fix possible bug here may also be in move. Currently unsure.
    @staticmethod
    def _get_all_jobs():
        """
        Gets all jobs from all locations (Failed, Processed, batches, rec...)
        :return: returns the list of job names
        """
        job_names = []
        for folder in constants.JOB_DIRS:
            job_names = job_names + ip_utils.get_abs_paths(folder)
        for path in job_names:
            if os.path.isdir(path):
                with JobData(path) as jd:
                    job_names = list(map(lambda x: x.replace(path, jd.base_name), job_names))
            else:
                job_names.remove(path)
                
        return job_names

    def _parse_yaml(self, file_path):
        with open(file_path, 'r') as file:
            command_file = yaml.safe_load(file)
        return command_file

    # Takes in an absolute path of the com file
    def _create_association(self, com_file_path):
        """
        Creates an association between a com file and an image file
        :param com_file_path: com file name that you want to get the association for
        :return: returns the com and image file paths
        """
        if os.path.isdir(com_file_path):
            raise FileNotFoundError
        
        dir_path = os.path.dirname(com_file_path)
        data = self._parse_yaml(com_file_path)
        pths = os.listdir(dir_path)
        target = data.get(constants.TARGET_IMAGE)
        if target is None or target.endswith(".ISQ"):
            raise ValueError
        image_file_path = None
        for file in pths:
            if file.lower() == target.lower():
                image_file_path = file
                image_file_path = os.path.join(dir_path, image_file_path)
                self.logs.log_debug("{} Received".format(data.get(constants.TARGET_IMAGE)))
                return com_file_path, image_file_path
        if image_file_path is None:
            nm = os.path.basename(com_file_path)
            self.logs.log_error('Could not find associated image file for {}'.format(nm))
            raise FileNotFoundError("Image file not found for {}".format(nm))

    def _ensure_directories_exist(self, dirs=None):
        """
        Checks the list of directories to make sure that they exist
        :param dirs: custom list of directories to check
        :return: None
        """
        if dirs is None:
            dirs = constants.DIRS
        for folder in dirs:
            self._create_directory_if_not_exist(folder)

    def _create_directory_if_not_exist(self, folder):
        """
        Creates a directory if it is found to not exist
        :param folder: name of dir that does not exist
        :return: None
        """
        full_path = os.path.join(os.getcwd(), folder)
        if not os.path.exists(full_path):
            os.mkdir(full_path)
            self.logs.log_debug("Creating {}".format(folder))

    def cleanup(self, directory):
        files = ip_utils.get_abs_paths(directory)
        for file in files:
            to_del = False
            with JobData(file) as jd:
                if jd.data.get(constants.DATE) is None:
                    date = datetime.today()
                    date_str = date.strftime("%Y-%m-%d")
                    jd.data[constants.DATE] = date_str
                    jd.data[constants.DATE] = date_str
                elif self._check_date(jd.data.get(constants.DATE)):
                    to_del = True
            if to_del:
                shutil.rmtree(file)

    @staticmethod
    def _check_date(date_str):
        dt = datetime.fromisoformat(date_str)
        cur = datetime.today()
        time_diff = cur - dt
        if time_diff > timedelta(days=constants.TIME_TO_DELETE):
            return True
        else:
            return False
