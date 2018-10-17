import unittest
from muparser import _ClassDict


class TestClassDict(unittest.TestCase):
    def setUp(self):
        self.class_dict = _ClassDict({str: str.upper})

    def test_class_dict(self):
        f = self.class_dict['s']
        self.assertEqual(str.upper, f)
