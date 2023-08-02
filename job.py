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
from datetime import datetime

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
        self.initialize(self.base)
        self.base_name = os.path.basename(base_dir)

        self.com_file_path = None
        self.com_file_name = None
        self.data = {}

        self.image_file_path = None
        self.image_file_name = None

        self.proc_dir_name = None
        self.proc_dir_path = None

    def initialize(self, base_dir):
        self.base = base_dir
        contents = ip_utils.get_abs_paths(self.base)
        for file in contents:
            if file.lower.endswith(".com"):
                self.com_file_path = file
                self.com_file_name = os.path.basename(self.com_file_path)
                self.data = ip_utils.parse_com(self.com_file_path)
                break
        for file in contents:
            if file.lower.endswith(self.data.get("FEXT").lower):
                self.image_file_path = file
                self.image_file_name = os.path.basename(self.image_file_path)


    #
    # def update(self, base_dir):
    #     self.base = base_dir
    #     self.com_file_path = os.path.join(self.base, self.com_file_name)
    #     self.image_file_path = os.path.join(self.base, self.image_file_name)
    #     if self.proc_dir_name is not None:
    #         self.proc_dir_path = os.path.join(self.base, self.proc_dir_name)



    # This function is meant to be used when a file is done being processed so a date is added to the com file so a job
    # can be restarted within some time after it being completed after that time though the datetime in the file is used
    # to track when to delete the file


    # ON CALL: Returns just the file name of the .COM file




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
        self.logs.log_debug("Formatting {}".format(image_file))
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
    def move(self, job_base,destination):
        try:
            shutil.move(job_base, destination)
        except shutil.Error as e:
            new_name = job_base + datetime.timestamp
            os.rename(job_base, new_name)
            self.move(new_name, destination)