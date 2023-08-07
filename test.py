from job import JobManager
from ip_logging import Logger

log = Logger
jm = JobManager(log)

jb = jm._get_all_jobs()
print(jb)