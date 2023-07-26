import unittest
from job import JobTracker
import main
class JobTests(unittest.TestCase):

    def setUp(self):
        self.job = JobTracker()
        self.job.set_up_from_file(r"C:\Users\iangs\PycharmProjects\BoneLabServer\test-res\TEST1_EVAL_AUTOSEG_TRNSFR.COM")

    def test_com(self):
        actual = self.job.get_com_name()
        expected = "TEST1_EVAL_AUTOSEG_TRNSFR.COM"
        self.assertEqual(expected, actual)

    def test_img(self):
        actual = self.job.get_image_name()
        expected = "TEST1.AIM"
        self.assertEqual(expected, actual)





