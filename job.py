# job.py Version 2.0
# Author: Ian Smith
# Description: This file contains a JobData and a JobManager class. The JobData class is a context managed class meant
# to be able to read data from formatted folders and import the data into the program here. JobManager is a class that
# sort of serves as a filemanager, with the ability to format files into the folder structure recognized by job data.
# It also handles things like movement of files within the program
# Created 2023-06-12


import ip_utils

import os
import shutil
import datetime

FILENAME = "EVAL_FNAME"
TARGET_IMAGE = "TARGET_FILE"
EXT = "FEXT"

DEST = 'destination'
BATCHES = 'batches'
DEL = 'del'
FAILED = 'failed'
LOGS = 'logs'
MODELS = 'models'
DONE = 'processed'
REC = 'rec'
TMP = 'tmp'
JOB_DIRS = [BATCHES, DEST, DONE, FAILED]
DIRS = [BATCHES, DEL, DEST, FAILED, LOGS, MODELS, DONE, REC, TMP]


# JobData Class, can be context managed for easier resource management
# Used as an access point for job data
# Only internal functions are to initialize the data
# On __init__ takes input of the base dir of a job, imports the data from there
class JobData:
    def __init__(self, base_dir):
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
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


    # Initialize the data within the class from base dir
    def initialize(self):
        self.com_file_name = self._find_com()
        self.com_file_path = os.path.join(self.base, self.com_file_name)
        self.data = ip_utils.parse_com(self.com_file_path)
        image_path = self._find_image()
        self.image_file_path = image_path
        self.image_file_name = self.data.get("TARGET_FILE")

    # Find the target image file just from the data from the com file
    def _find_image(self):
        image_name = self.data.get("TARGET_FILE")
        image_path = os.path.join(self.base, image_name)
        if os.path.exists(image_path):
            return image_path

    # Finds the com file from the base dir
    def _find_com(self):
        contents = os.listdir(self.base)
        for file in contents:
            if file.lower().endswith(".com"):
                return file



class JobManager:
    def __init__(self, logger):
        self.logs = logger
        self._ensure_directories_exist()

    # Function to move job data once formatted into the standard format
    def move(self, job_base, destination):
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
            rename = self._name_dir(job_base)
            path = os.path.dirname(job_base)
            new_path = os.path.join(path, rename)
            os.rename(job_base, rename)
            self.logs.log_debug("{} renamed to {}".format(os.path.basename(job_base), rename))
            new_base = shutil.move(new_path, destination)
        return os.path.abspath(new_base)

    def create_job_data(self, com_file):
        com, img = self._create_association(com_file)
        base = self._format_job_data(com, img)
        return base

    def _format_job_data(self, com_file, image_file):
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
        metadata = ip_utils.parse_com(com_file)
        job_names = self._get_all_jobs()
        cur_job_name = metadata.get("IPL_FNAME")
        count = 0

        for name in job_names:
            if cur_job_name in name:
                count += 1

        if count > 0:
            cur_job_name = cur_job_name + "({})".format(count)
        # TODO change job name within com file? or just add

        return cur_job_name

    # TODO fix possible bug here may also be in move. Currently unsure.
    @staticmethod
    def _get_all_jobs():
        job_names = []
        for folder in JOB_DIRS:
            job_names = job_names + ip_utils.get_abs_paths(folder)
        for path in job_names:
            with JobData(path) as jd:
                job_names = list(map(lambda x: x.replace(path, jd.base_name), job_names))
        return job_names

    # Takes in an absolute path of the com file
    def _create_association(self, com_file_path):
        dir_path = os.path.dirname(com_file_path)
        data = ip_utils.parse_com(com_file_path)
        pths = ip_utils.get_abs_paths(dir_path)
        target = data.get(TARGET_IMAGE)
        if target is None:
            raise ValueError
        image_file_path = None
        for file in pths:
            file_base = os.path.basename(file)
            if file_base.lower() == target.lower():
                image_file_path = file
                nm = data.get(FILENAME)
                self.logs.log_debug("{} Received".format(nm))
                return com_file_path, image_file_path
        if image_file_path is None:
            nm = os.path.basename(com_file_path)
            self.logs.log_error('Could not find associated image file for {}'.format(nm))
            os.remove(com_file_path)
            raise FileNotFoundError("Image file not found for {}".format(nm))


    def _ensure_directories_exist(self, dirs=None):
        if dirs is None:
            dirs = DIRS
        for folder in dirs:
            self._create_directory_if_not_exist(folder)

    def _create_directory_if_not_exist(self, folder):
        full_path = os.path.join(os.getcwd(), folder)
        if not os.path.exists(full_path):
            os.mkdir(full_path)
            self.logs.log_debug("Creating {}".format(folder))
