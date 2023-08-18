"""
process.py
Author: Ian Smith
Description: This module should contain all operations related to calling/executing image processing algorithms.
"""

import ip_utils
from job import JobData

import subprocess

# TODO remove
TMP_OUT = "logs/output.txt"


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
        self.radius_tibia_final = "/home/bonelab/repos/Bonelab/HR-pQCT-Segmentation/"
        self.current = None
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
            self._get_processor(job_data)
            self.current = None
            return True
        except Exception as e:
            self.logs.log_error("An error has occurred with {}: {}".format(job_data.base_name, e))
            return False
        finally:
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
        :param job_data: JobData
        :return: None
        """
        self.logs.log_debug("Processing {}".format(job_data.image_file_name))
        cmd = ["python", "/home/bonelab/repos/Bonelab/HR-pQCT-Segmentation/segment.py", job_data.base,
               "radius_tibia_final", "--image-pattern", job_data.image_file_name.lower()]
        with open(TMP_OUT, "w") as f:
            proc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)

        if proc.returncode == 0:
            self.logs.log_debug("radius-tibia-final job {} finished successfully".format(job_data.base_name))
        else:
            raise ChildProcessError
