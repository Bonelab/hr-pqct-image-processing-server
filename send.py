import ip_utils
import subprocess
import os

from job import JobData


FAILED = "failed"

class Send:
    def __init__(self, logger):
        self.image_dir = None
        self.image_name = None
        self.destination = None
        self.hostname = None
        self.username = None
        self.dat = None
        self.job_data = None
        self.logs = logger


    def _prepare(self, base_dir):
        self.job_data = JobData(base_dir)
        self.dat = self.job_data.data
        self.image_dir = self.job_data.proc_dir_path
        self.image_name = self.job_data.image_file_name

        # with JobData(base_dir) as jd:
        #     self.dat = jd.data
        #     self.image_dir = jd.proc_dir_path
        #     self.image_name = jd.image_file_name
        self.username = self.dat.get("CLIENT_USERNAME")
        self.hostname = self.dat.get("CLIENT_HOSTNAME")
        self.destination = self.dat.get("CLIENT_DESTINATION")


    def send(self, base_dir):
        self._prepare(base_dir)
        self.logs.log_debug("Sending {}".format(self.job_data.image_file_name))
        try:
            sftp_cmd = ['sftp', '-q',
                        '{}@{}:{}'.format(self.username, self.hostname,
                                          ip_utils.convert_path(os.path.abspath(self.image_dir)))]
            put_cmd = ['put -r {}'.format(self.destination)]

            # Use subprocess.Popen to execute the command
            process = subprocess.Popen(sftp_cmd, stdin=subprocess.PIPE)
            process.communicate(input='\n'.join(put_cmd).encode())
            process.wait()

            self.logs.log_debug("{} successfully transferred to {}".format(self.image_name, self.hostname))
            return True
        except Exception:
            self.logs.log_error("Transfer to {} of {} failed".format(self.image_name, self.hostname))
            return False