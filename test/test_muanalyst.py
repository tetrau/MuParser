import unittest
from muparser import MuParser, MuAnalyst


class TestMuAnalyst(unittest.TestCase):
    class Parser1(MuParser):
        FIXED_DATA = {'a': '//a/text()'}

    class Parser2(MuParser):
        FIXED_DATA = {'b': '//b/text()'}

    def setUp(self):
        self.source_1 = ['<a>{}</a>'.format(i) for i in range(5)]
        self.source_2 = ['<b>{}</b>'.format(i) for i in range(5)]
        self.extra_1 = [{'id': i} for i in range(5)]

    def test_mu_analyst(self):
        analyst = MuAnalyst(sources=(self.source_1, self.source_2),
                            parsers=(self.Parser1(), self.Parser2()),
                            extras=(MuAnalyst.repeat_none(), self.extra_1),
                            processes=2)
        r = [i for i in analyst.analyze()]
        except_result = [{'a': '0', 'b': '0', 'id': 0},
                         {'a': '1', 'b': '1', 'id': 1},
                         {'a': '2', 'b': '2', 'id': 2},
                         {'a': '3', 'b': '3', 'id': 3},
                         {'a': '4', 'b': '4', 'id': 4}]
        self.assertEqual(r, except_result)
