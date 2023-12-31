"""
ip_cli.py
Author: Ian Smith
Description: Handles communication with the external cli python program
"""
import os.path

from job import JobData
import constants, ip_utils

import pickle
import socket


class CLI:
    def __init__(self, queue, processor, send, file_manager, main_loop):
        """
        Constructor Method
        :param queue: Instance of main ManagedQueue
        :param processor: Instance of main Processor
        :param send: Instance of main Send
        :param file_manager: Instance of main JobManager
        """
        self.queue = queue
        self.processor = processor
        self.send = send
        self.file_manager = file_manager
        self.main = main_loop

        self.server = None
        self._bind_socket()

        self.conn = None
        self.client_addr = None

    def cli(self):
        """
        Method to initialize CLI
        :return:
        """
        self.conn, self.client_addr = self.server.accept()
        data = self.conn.recv(1024)
        cmd = pickle.loads(data)
        self._cli_handle(cmd)
        self.conn = None
        self.client_addr = None

    def _bind_socket(self):
        """
        Method to bind the socket and start listening on it
        :return: None
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(constants.ADDR)
        self.server.listen()

    def _send_to_cli(self, dat, cmd):
        """
        Method to send data out to external CLI program
        :param dat: data that is being sent
        :param cmd: command associated with data
        :return: None
        """
        to_send = [cmd, dat]
        to_send = pickle.dumps(to_send)
        self.conn.sendall(to_send)

    def _cli_handle(self, cmd):
        """
        Handles commands sent to CLI module
        :param cmd: Command to handle
        :return: None
        """
        command = cmd[0]
        if command == "jobs":
            self._handle_jobs()
        elif command == "completed":
            self._handle_completed()
        elif command == "info":
            self._handle_info(cmd[1])
        elif command == "move":
            self._handle_move(cmd)
        elif command == "restart":
            self._handle_restart(cmd[1])
        elif command == "delete":
            self._handle_remove(cmd[1])
        elif command == "failed":
            self._handle_failed()
        elif command == "pause":
            self._handle_pause()
        elif command == "unpause":
            self._handle_unpause()


    def _get_jobs(self):
        """
        Gets current jobs on queue
        :return: None
        """
        jobs = self.queue.get_state()
        if self.processor.current is not None:
            jobs.insert(0, self.processor.current)
        return jobs

    @staticmethod
    def _jobs_from_dir(directory):
        """
        Get jobs from a specific directory
        :param directory:  you want to get the jobs from
        :return: List of jobs as JobData
        """
        job_pths = ip_utils.get_abs_paths(directory)
        jobs = []
        for path in job_pths:
            jobs.append(JobData(path))
        return jobs

    def _handle_jobs(self):
        """
        Handles the collection of the list of jobs from queue and sends them to CLI
        :return: None
        """
        jbs = self._get_jobs()
        self._send_to_cli(jbs, "jobs")

    def _handle_completed(self):
        """
        Gets completed jobs and sends them to CLI
        :return: None
        """
        comp = self._jobs_from_dir(constants.DONE)
        self._send_to_cli(comp, "completed")

    def _handle_failed(self):
        """
        Gets failed jobs and sends them to CLI
        :return: None
        """
        fail = self._jobs_from_dir( constants.FAILED)
        self._send_to_cli(fail, "failed")

    def _handle_info(self, jobname):
        """
        Gets the info from a specific job and sends it to the CLI
        :param jobname:
        :return: None
        """
        jbs = self._get_jobs()
        for job in jbs:
            if jobname.lower() == job.base_name.lower():
                self._send_to_cli(job, "info")
                return

    def _handle_move(self, cmd):
        """
        Handles movement of a job within the queue
        :param cmd: data about what to move
        :return: None
        """
        try:
            self.queue.move_queue(cmd[1], cmd[2])
            jbs = self._get_jobs()
            self._send_to_cli(jbs, "move")
        except ValueError:
            self._send_to_cli("Exception", "move")

    def _handle_restart(self, jobname):
        """
        Handles restarting/requeueing a job
        :param jobname: The job to be restarted/requeued
        :return: None
        """
        paths = ip_utils.get_abs_paths("processed")
        for path in paths:
            if jobname.lower() == JobData(path).base_name.lower():
                self.queue.enqueue(path)
                jbs = self._get_jobs()
                self._send_to_cli(jbs, "restart")
                return

    def _handle_remove(self, jobname):
        """
        Handles removing a job from the queue
        :param jobname: Job to be removed
        :return: None
        """
        self.queue.remove_from_queue(jobname)
        jbs = self._get_jobs()
        self._send_to_cli(jbs, "delete")
        
    def _handle_pause(self):
        if self.main.paused == False:
            self.main.set_processing_state(True)
            self._send_to_cli("paused","pause")
        else:
            self._send_to_cli("already_paused","pause")
        
    
    def _handle_unpause(self):
        if self.main.paused == True:
            self.main.set_processing_state(False)
            self._send_to_cli("unpaused","unpause")
        else:
            self._send_to_cli("already_unpaused","unpause")
        

    def _skip_current(self):
        """
        Unimplemented command to kill the currently processing job
        :return:
        """
        self.processor.shutdown()