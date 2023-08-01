import ip_utils
import subprocess
import os

from job import JobData


FAILED = "failed"

class Send:
    def __init__(self, logger):
        self.images = None
        self.destination = None
        self.hostname = None
        self.username = None
        self.dat = None
        self.job_data = None
        self.logs = logger


    def _prepare(self, base_dir):
        self.job_data = JobData(base_dir)
        self.dat = self.job_data.data

        self.username = self.dat.get("CLIENT_USERNAME")
        self.hostname = self.dat.get("CLIENT_HOSTNAME")
        self.destination = self.dat.get("CLIENT_DESTINATION")
        self.images = self.job_data.proc_dir_path


    def send(self, base_dir):
        self._prepare(base_dir)
        self.logs.log_debug("Sending {}".format(self.job_data.image_file_name))
        try:
            sftp_cmd = ['sftp', '-q',
                        '{}@{}:{}'.format(self.username, self.hostname,
                                          ip_utils.convert_path(self.destination))]
            put_cmd = ['put -r {}'.format(os.path.abspath(self.images))]

            # Use subprocess.Popen to execute the command
            process = subprocess.Popen(sftp_cmd, stdin=subprocess.PIPE)
            process.communicate(input='\n'.join(put_cmd).encode())
            process.wait()

            self.logs.log_debug("{} successfully transferred to {}".format(self.job_data.image_file_name, self.hostname))
            self.move_finished()
        except Exception:
            self.logs.log_error("Transfer to {} of {} failed".format(self.job_data.image_file_name, self.hostname))
            self.move(FAILED)