"""
send.py
Author: Ian Smith
Description: Class to handle sending data back to the openVMS system
"""
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
        self.logs = logger

    def _prepare(self, base_dir):
        with JobData(base_dir) as jd:
            self.dat = jd.data
            self.image_dir = jd.proc_dir_path
            self.image_name = jd.image_file_name

        self.username = self.dat.get("CLIENT_USERNAME")
        self.hostname = self.dat.get("CLIENT_HOSTNAME")
        self.destination = self.dat.get("CLIENT_DESTINATION")

    def send(self, base_dir):
        self._prepare(base_dir)
        self.logs.log_debug("Sending {}".format(self.image_name))
        try:
            sftp_cmd = ['sftp', '-q',
                        '{}@{}:{}'.format(self.username, self.hostname,
                                          ip_utils.convert_path(self.destination))]
            put_cmd = ['put -r {}'.format(os.path.abspath(self.image_dir))]

            # Use subprocess.Popen to execute the command
            process = subprocess.Popen(sftp_cmd, stdin=subprocess.PIPE)
            process.communicate(input='\n'.join(put_cmd).encode())
            process.wait()
         
            self.logs.log_debug("{} successfully transferred to {}".format(self.image_name, self.hostname))
            return True
        except Exception:
            self.logs.log_error("Transfer to {} of {} failed".format(self.image_name, self.hostname))
            return False

