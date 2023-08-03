# job.py Version 1.0
# Author: Ian Smith
# Description: Job object for Autosegment_Server, these objects are tracked by the state class. This class holds all the
# functionality for moving, tracking, processing and sftping files
# Created 2023-06-12


import ip_utils
from ip_logging import Logger
import os
import shutil
import time
import subprocess
import datetime

FILENAME = "EVAL_FNAME"
TARGET_IMAGE = "TARGET_FILE"
EXT = "FEXT"

FAILED = "failed"
BATCHES = "batches"
MASKS = "processed"
DEST = "destination"


class JobData:
    def __init__(self, base_dir):
        self.base = base_dir

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

    def __exit__(self, exc_type, exc_value, traceback):
        pass


    def initialize(self):
        self.com_file_name = self._find_com()
        self.com_file_path = os.path.join(self.base, self.com_file_name)
        self.data = ip_utils.parse_com(self.com_file_path)
        image_path = self._find_image()
        self.image_file_path = image_path
        self.image_file_name = self.data.get("TARGET_FILE")

    def _find_image(self):
        image_name = self.data.get("TARGET_FILE")
        image_path = os.path.join(self.base, image_name)
        if os.path.exists(image_path):
            return image_path

    def _find_com(self):
        contents = os.listdir(self.base)
        for file in contents:
            if file.lower().endswith(".com"):
                return file


    # One instance of JobManager per thread?
    # What should JobManager do?
    # 1. Format the files into this format
    # | com file
    # | image file(s)
    # | system metadata
    # |_ Masks
    #   | cort_mask
    #   | trab_mask
    # 2. Create and retrieve checkpoints?
    # 3. Moving Files
    # 4. Removing Files


class JobManager:
    def __init__(self, logger):
        self.logs = logger

    def create_job_data(self, com_file):
        com, img = self._create_association(com_file)
        base = self._format_job_data(com, img)
        return base

    def _format_job_data(self, com_file, image_file):
        self.logs.log_debug("Formatting {}".format(os.path.basename(image_file)))
        com_file = os.path.abspath(com_file)
        dir_name = os.path.dirname(com_file)
        image_file = os.path.abspath(image_file)
        metadata = ip_utils.parse_com(com_file)
        base = os.path.join(dir_name, metadata.get("IPL_FNAME"))
        os.mkdir(base)
        shutil.move(com_file, base)
        shutil.move(image_file, base)
        mask_dir = os.path.join(base, "masks")
        os.mkdir(mask_dir)
        return base


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


    # Move fn, move the base directory of the data
    # Call update paths fn
    def move(self, job_base, destination):
        try:
            new_base = shutil.move(job_base, destination)
        except FileExistsError:
            now = datetime.datetime.now()
            date = now.strftime("_%Y%m%d%H%M%S")
            new_name = job_base + date
            os.rename(job_base, new_name)
            self.logs.log_debug("{} renamed to {}".format(job_base, new_name))
            new_base = shutil.move(new_name, destination)
        except shutil.Error:
            now = datetime.datetime.now()
            date = now.strftime("%Y_%m_%d_%H_%M_%S")
            new_name = job_base + date
            os.rename(job_base, new_name)
            self.logs.log_debug("{} renamed to {}".format(job_base, new_name))
            new_base = shutil.move(new_name, destination)
        return os.path.abspath(new_base)
