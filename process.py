import shutil
import subprocess
import os
from job import JobData


# TODO add current tracking to here
class Processor:
    def __init__(self, logger):
        self.logs = logger
        self.radius_tibia_final = "/home/bonelab/repos/Bonelab/HR-pQCT-Segmentation/"

    def _perform_startup(self):
        if len(os.listdir("destination")) != 0:
            files = os.listdir()
            self.process_image(files[0])
            files.pop(0)
            for i in files:
                shutil.move(i, "batches")





    def process_image(self, job_base):
        job_data = JobData(job_base)
        job_type = job_data.data.get("JOB")
        self._get_processor(job_type, job_data)

    def _get_processor(self, job_type, job_data):
        if job_type == "radius_tibia_final":
            self._radius_tibia_final(job_data)

    def _radius_tibia_final(self, job_data):
        self.logs.log_debug("Processing {}".format(job_data.image_file_name))
        cmd = ["python", "/home/bonelab/repos/Bonelab/HR-pQCT-Segmentation/segment.py", job_data.base, "radius_tibia_final", "--image-pattern", job_data.image_file_name.lower()]
        print(cmd)
        proc = subprocess.Popen(cmd)
        proc.wait()

