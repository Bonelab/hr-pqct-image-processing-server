# cli.py
# Author: Ian Smith
# Description: Allows for communication with the main part of the image processing server while it is daemonized
# Created: 2023-06-16
'''
Commands that can be used:

-j, --jobs: Shows current jobs in the queue

-i <jobname>, --info <jobname>: Gest info about a job

-d, --delete: deletes a job from the queue

-c, --completed: shows jobs that have successfully completed 

-f, --failed: shows jobs that have failed recently 

-p, --pause: pauses the processing on the server. if there is a job currently running it will finish before pausing

-u, --unpause: unpauses the server if it is paused
'''



import socket
import pickle
import argparse
import sys

import constants

JOBNAME = "EVAL_FNAME"
FILE_TYPE = "FEXT"
JOB_TYPE = "JOB_TYPE"
CLIENT_ADDR = "CLIENT_HOSTNAME"
ACCOUNT_NAME = "CLIENT_USERNAME"

FORMAT = "utf-8"
ip_addr = "127.0.0.1"



# Form [<command>, <arg1>, <arg2>, ..., <argn>]
# In the future change to {"command":<command>, "args": [<arg0>, <arg1>, <arg2>, ..., <argn>]}
# SEND: Sends the command to the server
def send(msg, client):
    msg = pickle.dumps(msg)
    client.sendall(msg)


def create_parser():
    parser = argparse.ArgumentParser(description="Segmentation Server for HR-pQCT scans")
    parser.add_argument(
        "-j",
        "--jobs",
        action="store_true",
        default=False,
        help="Shows a list of jobs currently on queue and currently being processed"
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store",
        type=str,
        default=None,
        help="Delete a job from the queue that is not currently active"
    )
    parser.add_argument(
        "-r",
        "--restart",
        action="store",
        metavar="JOBNAME",
        help="Restart a job that has recently been finished")
    parser.add_argument(
        "-c",
        "--completed",
        action="store_true",
        default=False,
        help="Shows jobs completed within the last {} days".format(constants.TIME_TO_DELETE)
    )
    parser.add_argument(
        "-p",
        "--pause",
        action="store_true",
        default=False,
        help="Pauses the processing of jobs. Server will still recieve jobs."
    )
    parser.add_argument(
        "-u",
        "--unpause",
        action="store_true",
        default=False,
        help="Unpauses the processing of jobs if it is already paused"
    )
    parser.add_argument(
        "-i",
        "--info",
        metavar="JOBNAME",
        action="store",
        type=str,
        default=None,
        help="Get information about a specific job"
    )
    parser.add_argument(
        "-m",
        "--move",
        metavar=("JOBNAME", "NEW_POSITION"),
        nargs=2,
        action="store",
        default=None,
        help="Move an item within the queue"
    )
    parser.add_argument(
        "-f",
        "--failed",
        action="store_true",
        default=False,
        help="Shows failed jobs within the last {} days".format(constants.TIME_TO_DELETE)
    )
    return parser


def handle_args(client, args):
    success = False
    args_keys = vars(args)
    for key in args_keys:
        if not (args_keys.get(key) is None or args_keys.get(key) is False):
            cmd = [key]
            # print(cmd)
            # print(args_keys.get(key))
            op = isinstance(args_keys.get(key), list)
            if isinstance(args_keys.get(key), list):
                cmd = cmd + args_keys.get(key)
            else:
                cmd.append(args_keys.get(key))
            send(cmd, client)
            success = True
            
    if success == False:
        raise NoCommandError


def handle_response(data):
    command = data[0]
    if command == "jobs":
        print("Jobs in queue: (0 is being processed)")
        print_jobs(data[1])
    elif command == "move":
        if data[1] != "Exception":
            print("Job Moved:")
            print_jobs(data[1])
        else:
            print("Index for job out of range")
    elif command == "restart":
        print("Job Re-queued:")
        print_jobs(data[1])
    elif command == "delete":
        print("Job Deleted")
        print_jobs(data[1])
    elif command == "completed":
        print("Completed Jobs:")
        print_jobs(data[1])
    elif command == "info":
        print_info(data[1])
    elif command == "failed":
        print("Failed Jobs:")
        print_jobs(data[1])
    elif command == "pause":
        if data[1] == "paused":
            print("Processing paused")
        elif data[1] == "already_paused":
            print("Processing is already paused, use -u to unpause")            
    elif command == "unpause":
        if data[1] == "unpaused":
            print("Processsing unpaused")
        elif data[1] == "already_unpaused":
            print("Processing is already unpaused, use -p to pause")
    else:
        print("Please input a command")
    print()


def print_info(info):
    if info is not None:
        print("Job Information")
        print("Job Name:\t\t{}".format(info.base_name))
        print("COM Name:\t\t{}".format(info.com_file_name))
        print("Image file:\t\t{}".format(info.image_file_name))
        print("Job Type:\t\t{}".format(info.data.get(JOB_TYPE)))
        print("File Type:\t\t{}".format(info.data.get(FILE_TYPE)))
        print("Client Name:\t\t{}@{}".format(info.data.get(ACCOUNT_NAME), info.data.get(CLIENT_ADDR)))


def print_jobs(job_list):
    count = 0
    for job in job_list:
        if count % 4 == 0 and count != 0:
            sys.stdout.write("\n{}: {}\t\t\t".format(count, job.base_name))
        else:
            sys.stdout.write("{}: {}\t\t\t".format(count, job.base_name))
        count += 1


def cli():
    args = create_parser().parse_args()
    try:
        client_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connect.connect(constants.ADDR)
        handle_args(client_connect, args)

        response_data = b''
        while True:
            chunk = client_connect.recv(1024)

            if not chunk:
                break
            elif chunk is None:
                break
            response_data += chunk

        response = pickle.loads(response_data)
        handle_response(response)
    except NoCommandError as e:
        print("Please enter a command or use the -h flag to see available commands")
    except Exception as e:
        print("No Response From Server", e)


class NoCommandError(Exception):
    def __init__(self, message="No command provided by the user"):
        self.message=message
        super().__init__(self.message)

cli()
