import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
TEST_PATH = os.path.abspath(os.path.dirname(__file__))

loader = unittest.TestLoader()
suite = loader.discover(TEST_PATH, pattern='test_*.py')

runner = unittest.TextTestRunner()
runner.run(suite)
