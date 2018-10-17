import unittest
from muparser import ClassDict


class TestClassDict(unittest.TestCase):
    def setUp(self):
        self.class_dict = ClassDict({str: str.upper})

    def test_class_dict(self):
        f = self.class_dict['s']
        self.assertEqual(str.upper, f)
