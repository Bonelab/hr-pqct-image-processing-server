"""
send.py
Author: Ian Smith
Description: Class to handle sending data back to the OpenVMS system
"""
import shutil
import subprocess
import os
import fnmatch
import traceback

import constants
import ip_utils
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
            self.job_type = jd.data.get(constants.JOB_TYPE)
            self.job_type = self.job_type.lower()

        self.username = self.dat.get("CLIENT_USERNAME")
        self.hostname = self.dat.get("CLIENT_HOSTNAME")
        self.destination = self.dat.get("CLIENT_DIR")

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
        success = False
        self._prepare(base_dir)
        self.logs.log_debug("Sending {} to {} at {}".format(self.image_name, self.hostname, self.destination))
        try:
            self._get_send_for_job()
            self.logs.log_debug(
                "{} successfully transferred to {} at {}".format(self.image_name, self.hostname, self.destination))
            success = True
        except NotImplementedError as e:
            self.logs.log_error(f"NotImplementedError: {e}")
            success = False
        except Exception as e:
            self.logs.log_error("Transfer to {} of {} failed: Error {}".format(self.image_name, self.hostname, e))
            self.logs.log_error(traceback.format_exc())
            success = False
        finally:
            self._reset()

        return success

    def _get_send_for_job(self):
        """
        Selects method for sending, allows for sending in different formats
        :return:
        """
        self.job_type = self.job_type.lower()
        if self.job_type == "radius_tibia_final":
            self._send_radius_tibia_final()
        else:
            raise NotImplementedError(f"Job Type: {self.job_type} not implemented in this system.")

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

        masks = ip_utils.get_abs_paths(self.image_dir)
        destination = ip_utils.convert_path(self.destination).replace("DK0", "DISK2")
        
        batch_path = self.write_batch_file_radius_tibia(destination, self.image_dir, masks[0], masks[1])
        
        
        vms_path_to_trab_mask = self.dat.get('FILE_TRAB_MASK_AIM').replace("DK0", "DISK2")
        vms_path_to_cort_mask = self.dat.get('FILE_CORT_MASK_AIM').replace("DK0", "DISK2")
        vms_aim_path = self.dat.get('FILE_AIM').replace("DK0", "DISK2")
        
        sftp_cmd = ['sftp', f'-b{batch_path}', 'xtremect2@emily.ucalgary.ca'] # Possibly add -i argument to point to key file 
        
        fix_trab_mask = ['ssh', '-p22', '-c3des-cbc', '-oKexAlgorithms=+diffie-hellman-group1-sha1', '-oHostKeyAlgorithms=+ssh-dss', f'{self.username}@{self.hostname}', f'set file/attr=(lrl:512, rfm:fix) {vms_path_to_trab_mask}']
        fix_cort_mask = ['ssh', '-p22', '-c3des-cbc', '-oKexAlgorithms=+diffie-hellman-group1-sha1', '-oHostKeyAlgorithms=+ssh-dss', f'{self.username}@{self.hostname}', f'set file/attr=(lrl:512, rfm:fix) {vms_path_to_cort_mask}']
        
        masks_to_gobj = ['ssh', '-p22', '-c3des-cbc', '-oKexAlgorithms=+diffie-hellman-group1-sha1', '-oHostKeyAlgorithms=+ssh-dss', f'{self.username}@{self.hostname}', f'@COM:HIJACK_MASKS_TO_GOBJ.COM {vms_aim_path}']
        
        p1 = subprocess.Popen(sftp_cmd, stdin=subprocess.PIPE) # Sending masks as AIMs
        
        if p1.returncode != 0:
            p1.kill
            raise subprocess.CalledProcessError(p1.returncode, sftp_cmd)
        
        p2 = subprocess.Popen(fix_trab_mask, stdin=subprocess.PIPE) # Fixing trab mask attributes
        
        if p2.returncode != 0:
            p2.kill
            raise subprocess.CalledProcessError(p2.returncode, fix_trab_mask)
        
        p3 = subprocess.Popen(fix_cort_mask, stdin=subprocess.PIPE) # Fixing cort mask attributes
        
        if p3.returncode != 0:
            p3.kill
            raise subprocess.CalledProcessError(p3.returncode, fix_trab_mask)

        p4 =  subprocess.Popen(masks_to_gobj, stdin=subprocess.PIPE) # Turning masks to GOBJ
        
        if p4.returncode != 0:
            p4.kill
            raise subprocess.CalledProcessError(p4.returncode, masks_to_gobj)



    def write_batch_file_radius_tibia(self, destination_path, path_to_masks_dir, mask1_name, mask2_name):
        """
        Takes in a list of sftp commands to generate a batch send file
        """
        batch_file_path = os.path.join(path_to_masks_dir, "batch.txt") 
        with open(batch_file_path, 'w') as f:
            f.write("lcd " + destination_path + "\n")
            f.write("cd " + path_to_masks_dir  + "\n")
            f.write("put " + mask1_name + "\n")
            f.write("put " + mask2_name + "\n")
            f.write("exit")
        return batch_file_path



