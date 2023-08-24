"""
process.py
Author: Ian Smith
Description: This module should contain all operations related to calling/executing image processing algorithms.
"""
import shutil

import constants
import ip_utils
from job import JobData

import subprocess


class Processor:
    """
    A class to handle the processing of images, uses a factory method to decide what type of job a job is based off of
    the job's metadata
    """
    def __init__(self, logger, file_manager):
        """
        Constructor method
        :param logger: Injected Logger from the ip_logger class
        :param file_manager: A JobManager class instance
        """
        self.logs = logger
        self.file_manager = file_manager
        self.current = None
        self.process = None
        self._perform_startup()

    def _perform_startup(self):
        """
        On startup, clears the destination directory of jobs
        :return: None
        """
        self.logs.log_debug("Clearing out destination dir")
        files = ip_utils.get_abs_paths("/home/bonelab/bls/destination")
        for i in files:
            self.file_manager.move(i, "batches")

    def process_image(self, job_base):
        """
        Method to initialize the processing of an image
        :param job_base: Path to the job
        :return: None
        """
        job_data = JobData(job_base)
        self.current = job_data
        try:
            self._skip()
            #self._get_processor(job_data)
            self.current = None
            return True
        except Exception as e:
            self.logs.log_error("An error has occurred with {}: {}".format(job_data.base_name, e))
            return False
        finally:
            self.process = None
            self.current = None

    def _get_processor(self, job_data):
        """
        Factory method to choose the processing method for selected job
        :param job_data: JobData
        :return: None
        """
        job_type = job_data.data.get("JOB")
        if job_type == "radius_tibia_final":
            self._radius_tibia_final(job_data)

    def _radius_tibia_final(self, job_data):
        """
        Method to execute the radius-tibia image segmentation, raises error on failed processing job
        :param job_data: JobData instance
        :return: None
        """
        self.logs.log_debug("Processing {}".format(job_data.image_file_name))
        # the first item in the list is the path to the python interpreter with the conda env and the 2nd is the path to run the model
        cmd = [constants.RAD_TIB_PATH_TO_ENV, constants.RAD_TIB_PATH_TO_START, job_data.base,
               constants.RAD_TIB_TRAINED_MODELS, "--image-pattern", job_data.image_file_name.lower()]

        self.process = subprocess.run(cmd)

        if self.process.returncode == 0:
            self.logs.log_debug("radius-tibia-final job {} finished successfully".format(job_data.base_name))
        else:
            raise subprocess.CalledProcessError

    def shutdown(self):
        """
        Method to shut down the processing module
        :return:
        """
        if self.process is not None:
            self.process.kill()

    def _skip(self):
        pass