# job.py Version 1.0
# Author: Ian Smith
# Description: Job object for Autosegment_Server, these objects are tracked by the state class. This class holds all the
# functionality for moving, tracking, processing and sftping files
# Created 2023-06-12
import logging
import os
import shutil
import time
import subprocess
from datetime import datetime

FILENAME = "EVAL_FNAME"
FAILED = "failed"
BATCHES = r"C:\Users\iangs\PycharmProjects\BoneLabServer\batches"
MASKS = r"C:\Users\iangs\PycharmProjects\BoneLabServer\processed"


class JobTracker:
    def __init__(self):
        self.com_file = None
        self.image_file = None
        self.name = None
        self.data = {}
        self.setup_logging()
        self.proc_image = None

    # Setting up logging with this method makes it so that there is one logger for each error and debug shared across
    # all filetracker objects
    def setup_logging(self):
        self.debug_logger = self._create_logger("debug", "logs/debug.log", logging.DEBUG)
        self.error_logger = self._create_logger("error", "logs/error.log", logging.ERROR)

    # Creating loggers for error and debug
    def _create_logger(self, name, filename, level):
        logger = logging.getLogger("{}-{}-{}".format(self.__class__.__name__, id(self), name))
        logger.setLevel(level)
        if not logger.handlers:
            handler = logging.FileHandler(filename)
            handler.setLevel(level)
            form = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(form)
            logger.addHandler(handler)
            logger.propagate = False
        return logger

    # Set the com file for the filetracker Object
    def set_com_file(self, file_path):
        if file_path.lower().endswith(".com"):
            self.com_file = file_path
            self.data = parse_com(self.com_file)
            self.name = self.data.get(FILENAME)
        else:
            nm = os.path.basename(file_path)
            self.error_logger.error('Invalid extension for COM file in {}'.format(nm))
            raise ValueError('Invalid file extension for COM file')

    # Appends the date to the end of the com file, important for cleaning up the garbage after a week
    def append_to_com(self):
        with open(self.com_file, 'a') as f:
            date = datetime.today()
            date_string = date.strftime("%Y-%m-%d")
            f.write('$ DATE_FINISHED :== {}'.format(date_string))

    # Remove date at the end of the com file
    def rm_from_com(self):
        with open(self.com_file, 'r') as f:
            lines = f.readlines()

        with open(self.com_file, 'w') as f:
            for line in lines:
                if 'DATE_FINISHED' not in line:
                    f.write(line)

    # Can set up the filetracker object from just the com file
    def set_up_from_file(self, file_path):
        dir_path = os.path.dirname(file_path)
        if file_path.lower().endswith(".com"):
            self.set_com_file(file_path)
            count = 0
            while count < 60:  # TODO CHANGE BACK TO 60 IN FINAL VER
                pths = get_abs_paths(dir_path)
                for file in pths:
                    if self.data.get(FILENAME).lower() in file.lower() and self.data.get("FEXT").lower() in file.lower():
                        self.set_image_file(file)
                        nm = self.data.get(FILENAME)
                        self.debug_logger.debug("{} Received".format(nm))
                        self.rm_from_com()
                        return True
                count += 1
                time.sleep(1)
            if self.image_file is None:
                nm = self.get_com_name()
                self.error_logger.error('Could not find associated image file for {}'.format(nm))
                raise FileNotFoundError("Image file not found")
        elif file_path.lower().endswith(".aim"):
            self.set_image_file(file_path)
            f_name = os.path.basename(file_path)
            file_next = os.path.splitext(f_name)[0]
            count = 0
            while count < 1:  # TODO CHANGE BACK TO 60 IN FINAL VER
                pths = get_abs_paths(dir_path)
                for file in pths:
                    if file_next.lower() in file.lower() and file.lower().endswith(".com"):
                        self.set_com_file(file)
                        nm = self.data.get(FILENAME)
                        self.debug_logger.debug("{} Received".format(nm))
                        self.rm_from_com()
                        return True
                count += 1
                time.sleep(1)
            if self.com_file is None:
                nm = self.get_image_name()
                self.error_logger.error('Could not find associated COM file for {}'.format(nm))
                raise FileNotFoundError("COM file not found")
        else:
            raise FileNotFoundError

    # Set the image file for the JobTracker object
    def set_image_file(self, file_path):
        if file_path.lower().endswith(".aim"):   # or file_path.lower().endswith(".isq") or file_path.lower(#).endswith(".gobj")
            self.image_file = file_path
        else:
            raise ValueError("Invalid file extension for image file")


    def process(self):
        proc = subprocess.Popen("cd {} && python3 segment.py --image-pattern {} --masks-subdirectory {}".format(BATCHES, self.get_image_name(), MASKS))
        proc.wait()

    # METHOD to move the set of files between directories
    def move(self, directory):
        try:
            self.com_file = shutil.move(self.com_file, directory)
            self.image_file = shutil.move(self.image_file, directory)
        except FileExistsError:
            self.error_logger.error("Duplicate file of {} found in {}".format(self.get_image_name(), directory))
            os.remove(self.com_file)
            os.remove(self.image_file)

    # This function is meant to be used when a file is done being processed so a date is added to the com file so a job
    # can be restarted within some time after it being completed after that time though the datetime in the file is used
    # to track when to delete the file
    def move_finished(self):
        self.com_file = shutil.move(self.com_file, 'destination')
        self.image_file = shutil.move(self.image_file, 'destination')
        self.append_to_com()

    def send(self):
        nm = self.get_image_name()
        hn = self.data.get("CLIENT_HOSTNAME")
        try:
            sftp_cmd = 'sftp -q -r {}@{}:{} <<< $\'put {}\''.format(self.data.get("CLIENT_USERNAME"), self.data.get("CLIENT_HOSTNAME"), convert_path(self.data.get("CLIENT_DESTINATION")), self.com_file)
            subprocess.run(sftp_cmd, shell=True, check=True, executable='/bin/bash')
            self.debug_logger.debug("{} successfully transferred to {}".format(nm, hn))
            self.move_finished()
        except subprocess.CalledProcessError as e:
            self.error_logger.error("Transfer to {} of {} failed".format(hn, nm))
            self.move(FAILED)

    def test_send(self):
        # Files get sent here and then timestamped
        self.move_finished()

    # ON CALL: Returns just the file name of the .COM file
    def get_com_name(self):
        return os.path.basename(self.com_file)

    # ON CALL: Returns just the file name of the image file
    def get_image_name(self):
        return os.path.basename(self.image_file)

    # On
    def log_action(self, action):
        nm = self.data.get(FILENAME)
        self.debug_logger.debug("{} {}".format(nm, action))


def remove(self):
    os.remove(self.image_file)
    os.remove(self.com_file)





# Converts a file path from the vms format to the linux format
def convert_path(path):
    if "[" in path or "]" in path:
        path = path.replace(":", "")
        path = path.replace(".", "/")
        path = path.replace("[", "/")
        path = path.replace("]", "/")
        path = "/" + path
    return path

def get_abs_paths(directory):
    files = os.listdir(directory)
    n_files = []
    for f in files:
        f = os.path.join(directory, f)
        f = os.path.abspath(f)
        f = os.path.normpath(f)
        n_files.append(f)
    return n_files

def parse_com(file_path):
    command_file = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip("$").strip()
            if "!" in line:
                sp = line.split("!")
                line = sp[0]
            if ":==" in line:
                split = line.split(":==")
                if split[1] != "":
                    command_file[split[0].strip()] = split[1].strip()
    print(command_file)
    return command_file