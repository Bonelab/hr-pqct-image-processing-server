"""
send.py
Author: Ian Smith
Description: Class to handle sending data back to the OpenVMS system
"""
import shutil
import subprocess
import os
import fnmatch

import constants, ip_utils
from job import JobData



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
        self.job_type = None
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
            self.job_type = jd.data.get(constants.JOB)

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
        self.job_type = None

    def send(self, base_dir):
        """
        Method for using sftp to send the data back to OpenVMS
        :param base_dir: Base directory/reference to job data
        :return: True on success, False on fail
        """
        self._prepare(base_dir)
        self.logs.log_debug("Sending {} to {} at {}".format(self.image_name, self.hostname, self.destination))
        try:
            self._get_send_for_job()
            self.logs.log_debug(
                "{} successfully transferred to {} at {}".format(self.image_name, self.hostname, self.destination))
            self._reset()
            return True
        except Exception as e:
            self.logs.log_error("Transfer to {} of {} failed: Error {}".format(self.image_name, self.hostname, e))
            shutil.move(base_dir, constants.FAILED)
            self._reset()
            return False

    def _get_send_for_job(self):
        """
        Selects method for sending, allows for sending in different formats
        :return:
        """
        if self.job_type == "radius_tibia_final":
            pass  # self._send_radius_tibia_final()

    def _send_radius_tibia_final(self):
        """
        Send method for radius_tibia_final job type
        :return:
        """
        # Checking that the images are actually there
        file_patterns = ["*_CORT_MASK.AIM", "*_TRAB_MASK.AIM"]
        matching_files = []

        for root, dirs, files in os.walk(self.image_dir):
            for file_pattern in file_patterns:
                matching_files.extend(fnmatch.filter(files, file_pattern))

        if not matching_files:
            raise FileNotFoundError("Image masks not found in masks dir")

        # Sending images here
        destination = ip_utils.convert_path(self.destination).replace("DK0", "DISK2")
        sftp_cmd = ['sftp', '{}@{}:{}'.format(self.username, self.hostname, destination)]
        masks = ip_utils.get_abs_paths(self.image_dir)
        put_cmd1 = ['put ' + masks[0], "quit"]
        put_cmd2 = ['put ' + masks[1], "quit"]
        # Use subprocess.Popen to execute the command
        p1 = subprocess.Popen(sftp_cmd, stdin=subprocess.PIPE)
        p1.communicate(input='\n'.join(put_cmd1).encode())
        p2 = subprocess.Popen(sftp_cmd, stdin=subprocess.PIPE)
        p2.communicate(input='\n'.join(put_cmd2).encode())

        if p1.returncode != 0:
            raise subprocess.CalledProcessError(p1.returncode, sftp_cmd)
        elif p2.returncode != 0:
            raise subprocess.CalledProcessError(p2.returncode, sftp_cmd)






