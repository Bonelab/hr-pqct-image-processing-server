"""
send.py
Author: Ian Smith
Description: Class to handle sending data back to the OpenVMS system
"""
import paramiko
import subprocess
import os

import constants
from job import JobData
import ip_utils


class Send:
    def __init__(self, logger):
        """
        Constructor method
        :param logger: Injected Logger from ip_logging
        """
        self.image_dir = None
        self.image_name = None
        self.destination = None
        self.hostname = None
        self.username = None
        self.dat = None
        self.logs = logger

    def _prepare(self, base_dir):
        """
        Prepares data for sending, extracts username/hostname etc...
        :param base_dir:
        :return:
        """
        with JobData(base_dir) as jd:
            self.dat = jd.data
            self.image_dir = jd.proc_dir_path
            self.image_name = jd.image_file_name

        self.username = self.dat.get("CLIENT_USERNAME")
        self.hostname = self.dat.get("CLIENT_HOSTNAME")
        self.destination = self.dat.get("CLIENT_DESTINATION")

    def _reset(self):
        """
        Resets class parameters
        :return: None
        """
        self.image_dir = None
        self.image_name = None
        self.destination = None
        self.hostname = None
        self.username = None
        self.dat = None

    def send(self, base_dir):
        """
        Method for using sftp to send the data back to OpenVMS
        :param base_dir: Base directory/reference to job data
        :return: True on success, False on fail
        """
        self._prepare(base_dir)
        self.logs.log_debug("Sending {}".format(self.image_name))
        try:
            print(1)
            transport = paramiko.Transport((self.hostname, 22))
            print(2)
            transport.get_security_options().kex = "diffie-hellman-group1-sha1"
            print(3)
            transport.get_security_options().kex = "ssh-dss"
            print(4)
            private_key = paramiko.RSAKey(filename=constants.PRIVATE_KEY)
            print(5)
            transport.connect(self.username, pkey=private_key)
            print(6)
            sftp = transport.open_sftp_client()
            print(7)
            sftp.put(os.path.abspath(self.image_dir), ip_utils.convert_path(self.destination))
            print(8)
            sftp.close()
            print(9)
            transport.close()


            # sftp_cmd = ['sftp',
            #             '{}@{}:{}'.format(self.username, self.hostname,
            #                               ip_utils.convert_path(self.destination))]
            # put_cmd = ['put', '-r', os.path.abspath(self.image_dir)]
            #
            # # Use subprocess.Popen to execute the command
            # process = subprocess.Popen(sftp_cmd, stdin=subprocess.PIPE)
            # process.communicate(input='\n'.join(put_cmd).encode())
            # process.wait()

            self.logs.log_debug("{} successfully transferred to {} at {}".format(self.image_name, self.hostname, self.destination))
            self._reset()
            return True
        except Exception as e:
            self.logs.log_error("Transfer to {} of {} failed: Error {}".format(self.image_name, self.hostname, e))
            self._reset()
            return False
