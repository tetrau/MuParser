import unittest
from muparser import MuParser, MuAnalyst


class TestMuAnalyst(unittest.TestCase):
    class Parser1(MuParser):
        FIXED_DATA = {'a': '//a/text()'}

    class Parser2(MuParser):
        FIXED_DATA = {'b': '//b/text()'}

    SIZE = 100

    def setUp(self):
        self.source_1 = ['<a>{}</a>'.format(i) for i in range(self.SIZE)]
        self.source_2 = ['<b>{}</b>'.format(i) for i in range(self.SIZE)]
        self.extra_1 = [{'id': i} for i in range(self.SIZE)]

    def test_mu_analyst(self):
        analyst = MuAnalyst(sources=(self.source_1, self.source_2),
                            parsers=(self.Parser1(), self.Parser2()),
                            extras=(MuAnalyst.repeat_none(), self.extra_1),
                            processes=2)
        r = [i for i in analyst.analyze()]
        except_result = [{'a': str(i), 'b': str(i), 'id': i} for i in range(self.SIZE)]
        self.assertEqual(r, except_result)
