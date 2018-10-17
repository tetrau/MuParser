from muparser import MuParser
import unittest
import os


class MuParseTest(unittest.TestCase):
    def setUp(self):
        PATH = os.path.abspath(os.path.split(__file__)[0])
        with open(os.path.join(PATH, 'sample.html')) as f:
            self.html_string = f.read()

    def test_fixed_data(self):
        class TestParser(MuParser):
            FIXED_DATA = {'title': '//h1[@id="title"]/text()'}

        r = TestParser().parse(self.html_string)
        self.assertDictEqual(r, {'title': 'Title'})

    def test_dynamic_data(self):
        class TestParser(MuParser):
            DYNAMIC_DATA = {'//tr/td[1]/text()': '//tr/td[2]/text()'}

        r = TestParser().parse(self.html_string)
        self.assertDictEqual(r, {'Cell A': 'Cell B',
                                 'Cell 1': 'Cell 2'})

    def test_fixed_data_formatter(self):
        class TestParser(MuParser):
            FIXED_DATA = {'title': '//h1[@id="title"]/text()'}
            FIXED_FILED_VALUE_FORMATTER = {str: str.upper}

        r = TestParser().parse(self.html_string)
        self.assertDictEqual(r, {'title': 'TITLE'})

    def test_dynamic_data_formatter(self):
        class TestParser(MuParser):
            DYNAMIC_FILED_NAME_FORMATTER = {str: str.lower}
            DYNAMIC_FILED_VALUE_FORMATTER = {str: lambda x: x.replace(' ', '')}
            DYNAMIC_DATA = {'//tr/td[1]/text()': '//tr/td[2]/text()'}

        r = TestParser().parse(self.html_string)
        self.assertDictEqual(r, {'cell a': 'CellB', 'cell 1': 'Cell2'})

    def test_post_processing(self):
        class TestParser(MuParser):
            DYNAMIC_FILED_NAME_FORMATTER = {str: str.lower}
            DYNAMIC_FILED_VALUE_FORMATTER = {str: lambda x: x.replace(' ', '')}
            DYNAMIC_DATA = {'//tr/td[1]/text()': '//tr/td[2]/text()'}

            def post_processing(self, d):
                return {k.replace(' ', '_'): v for k, v in d.items()}

        r = TestParser().parse(self.html_string)
        self.assertDictEqual(r, {'cell_a': 'CellB', 'cell_1': 'Cell2'})

    def test_all(self):
        class TestParser(MuParser):
            FIXED_FILED_VALUE_FORMATTER = {str: str.upper}
            DYNAMIC_FILED_NAME_FORMATTER = {str: str.lower}
            DYNAMIC_FILED_VALUE_FORMATTER = {str: lambda x: x.replace(' ', '')}
            FIXED_DATA = {'title': '//h1[@id="title"]/text()'}
            DYNAMIC_DATA = {'//tr/td[1]/text()': '//tr/td[2]/text()'}

            def post_processing(self, d):
                return {k.replace(' ', '_'): v for k, v in d.items()}

        excepted = {'cell_a': 'CellB',
                    'cell_1': 'Cell2',
                    'title': 'TITLE'}
        r = TestParser().parse(self.html_string)
        self.assertDictEqual(r, excepted)
