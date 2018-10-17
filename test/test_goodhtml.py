from muparser import _GoodHtml
import unittest
import os


class GoodHtmlTest(unittest.TestCase):
    def setUp(self):
        PATH = os.path.abspath(os.path.split(__file__)[0])
        with open(os.path.join(PATH, 'sample.html')) as f:
            self.html_string = f.read()

    def test_xpath(self):
        good_html = _GoodHtml(self.html_string)
        r = good_html.xpath('//div[@class="block"]/p[1]/text()')
        self.assertEqual(['p1'], r)
