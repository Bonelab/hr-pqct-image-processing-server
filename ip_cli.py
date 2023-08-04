import pickle
import socket

from job import JobData
import ip_utils


ip_addr = "127.0.0.1"
port = 4000
ADDR = (ip_addr, port)

class CLI:
    def __init__(self, queue, processor, send, file_manager):
        self.queue = queue
        self.processor = processor
        self.send = send
        self.file_manager = file_manager

        self.server = None
        self._bind_socket()

        self.conn = None
        self.client_addr = None

    def cli(self):
        self.conn, self.client_addr = self.server.accept()
        data = self.conn.recv(1024)
        cmd = pickle.loads(data)
        self._cli_handle(cmd)
        self.conn = None
        self.client_addr = None


    def _bind_socket(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        self.server.listen()

    def _send_to_cli(self, dat, cmd):
        to_send = [cmd, dat]
        to_send = pickle.dumps(to_send)
        self.conn.sendall(to_send)


    def _cli_handle(self, cmd):
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
        else:
            pass

    def _get_jobs(self):
        jbs = self.queue.get_jobs()
        if self.processor.current is not None:
            jbs. insert(0, self.processor.current)
        return jbs


    def _handle_jobs(self):
        jbs = self._get_jobs()
        self._send_to_cli(jbs, "jobs")

    def _handle_completed(self):
        a = ip_utils.get_abs_paths("processed")
        b = []
        for job in a:
            b.append(JobData(job))
        self._send_to_cli(b, "completed")

    def _handle_info(self, jobname):
        jbs = self._get_jobs()
        for job in jbs:
            if jobname.lower() in job.image_file_name.lower():
                self._send_to_cli(job, "info")
                return

    def _handle_move(self, cmd):
        try:
            self.queue.move_queue(cmd[1], cmd[2])
            jbs = self._get_jobs()
            self._send_to_cli(jbs, "move")
        except ValueError:
            self._send_to_cli("Exception", "move")

    def _handle_restart(self, jobname):
        paths = ip_utils.get_abs_paths("processed")
        for path in paths:
            if jobname.lower() in JobData(path).image_file_name.lower():
                self.queue.enqueue(path)
                jbs = self._get_jobs()
                self._send_to_cli(jbs, "restart")
                return
    def _handle_remove(self, jobname):
        self.queue.remove_from_queue(jobname)
        jbs = self._get_jobs()
        self._send_to_cli(jbs,  "delete")

