import subprocess

from job import JobData

# TODO add current tracking to here
class Processor:
    def __init__(self, logger):
        self.logs = logger
        self.radius_tibia_final = "/home/bonelab/repos/Bonelab/HR-pQCT-Segmentation/"

    def process_image(self, job_base):
        job_data = JobData(job_base)
        job_type = job_data.data.get("JOB")
        self._get_processor(job_type, job_data)

    def _get_processor(self, job_type, job_data):
        if job_type == "radius_tibia_final":
            self._radius_tibia_final(job_data)

    def _radius_tibia_final(self, job_data):
        cmd = ["python", "/home/bonelab/repos/Bonelab/HR-pQCT-Segmentation/segment.py", job_data.base, "radius_tibia_final", "-ip {}".format(job_data.image_file_name)]
        proc = subprocess.Popen(cmd)
        proc.wait()
