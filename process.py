import ip_utils
from job import JobData

import subprocess


class Processor:
    def __init__(self, logger, file_manager):
        self.logs = logger
        self.file_manager = file_manager
        self.radius_tibia_final = "/home/bonelab/repos/Bonelab/HR-pQCT-Segmentation/"
        self.current = None
        self._perform_startup()

    def _perform_startup(self):
        self.logs.log_debug("Clearing out destination dir")
        files = ip_utils.get_abs_paths("/home/bonelab/bls/destination")
        for i in files:
            self.file_manager.move(i, "batches")

    def process_image(self, job_base):
        job_data = JobData(job_base)
        job_type = job_data.data.get("JOB")
        self.current = job_data
        self._get_processor(job_type, job_data)
        self.current = None

    def _get_processor(self, job_type, job_data):
        if job_type == "radius_tibia_final":
            self._radius_tibia_final(job_data)

    def _radius_tibia_final(self, job_data):
        self.logs.log_debug("Processing {}".format(job_data.image_file_name))
        cmd = ["python", "/home/bonelab/repos/Bonelab/HR-pQCT-Segmentation/segment.py", job_data.base, "radius_tibia_final", "--image-pattern", job_data.image_file_name.lower()]
        print(cmd)
        proc = subprocess.Popen(cmd)
        proc.wait()