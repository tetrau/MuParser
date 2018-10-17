import lxml.html
import lxml.etree


class MuParserException(Exception):
    pass


class BadXpath(MuParserException):
    pass


class ClassDict:
    def __init__(self, d):
        self.data = d

    @staticmethod
    def identity(x):
        return x

    def __getitem__(self, item):
        for key, value in self.data.items():
            if isinstance(item, key):
                return value
        return self.identity


class GoodHtml:
    xpath_cache = {}

    def __init__(self, html, encoding='utf-8', cache_xpath=True):
        if isinstance(html, bytes):
            html = html.decode(encoding)
        self.html = lxml.html.fromstring(html)
        self.cache_xpath = cache_xpath

    def get_xpath(self, xpath):
        if self.cache_xpath:
            if xpath in self.xpath_cache:
                return self.xpath_cache[xpath]
            else:
                xpath_obj = lxml.etree.XPath(xpath)
                self.xpath_cache[xpath] = xpath_obj
                return xpath_obj
        else:
            return lxml.etree.XPath(xpath)

    def xpath(self, xpath: str):
        xpath = self.get_xpath(xpath)
        result = xpath(self.html)
        if not isinstance(result, list):
            result = [result]
        for idx, r in enumerate(result):
            if isinstance(r, str):
                result[idx] = str(r)
        return result


class MuParser:
    FIXED_DATA = {}
    DYNAMIC_DATA = {}
    FIXED_FILED_VALUE_FORMATTER = ClassDict({})
    DYNAMIC_FILED_NAME_FORMATTER = ClassDict({})
    DYNAMIC_FILED_VALUE_FORMATTER = ClassDict({})

    def to_string(self, e):
        if isinstance(e, lxml.html.HtmlElement):
            return lxml.html.tostring(e, encoding=self.encoding)
        else:
            return e

    def __init__(self, encoding='utf-8', raise_=True, default_formatter=True):
        self.default_formatter = default_formatter
        self.raise_ = raise_
        self.encoding = encoding
        self.html = None

    def _raise_exception(self, exception):
        if self.raise_:
            raise exception

    def _parse_fixed_data(self):
        if not isinstance(self.FIXED_FILED_VALUE_FORMATTER, ClassDict):
            self.FIXED_FILED_VALUE_FORMATTER = ClassDict(self.FIXED_FILED_VALUE_FORMATTER)
        result = {}
        for key, xpath in self.FIXED_DATA.items():
            value = self.html.xpath(xpath)
            if not (len(value) <= 1 or len(set(value)) == 1):
                exp = BadXpath('{} returns multiple distinct results')
                self._raise_exception(exp)
            value = value[0]
            value = self.FIXED_FILED_VALUE_FORMATTER[value](value)
            result[key] = value
        return result

    def _parse_dynamic(self):
        if not isinstance(self.DYNAMIC_FILED_NAME_FORMATTER, ClassDict):
            self.DYNAMIC_FILED_NAME_FORMATTER = ClassDict(self.DYNAMIC_FILED_NAME_FORMATTER)
        if not isinstance(self.DYNAMIC_FILED_VALUE_FORMATTER, ClassDict):
            self.DYNAMIC_FILED_VALUE_FORMATTER = ClassDict(self.DYNAMIC_FILED_VALUE_FORMATTER)
        result = {}
        for key_xpath, value_xpath in self.DYNAMIC_DATA.items():
            keys = self.html.xpath(key_xpath)
            values = self.html.xpath(value_xpath)
            if len(keys) != len(values):
                self._raise_exception(BadXpath('{} and {} selected elements do not match'))
            keys = map(lambda x: self.DYNAMIC_FILED_NAME_FORMATTER[x](x), keys)
            values = map(lambda x: self.DYNAMIC_FILED_VALUE_FORMATTER[x](x), values)
            result.update(dict(zip(keys, values)))
        return result

    def parse(self, html):
        self.html = GoodHtml(html, encoding=self.encoding)
        result = {}
        result.update(self._parse_dynamic())
        result.update(self._parse_fixed_data())
        result = self.post_processing(result)
        if self.default_formatter:
            rtn = {}
            for key, value in result.items():
                key = self.to_string(key)
                value = self.to_string(value)
                rtn[key] = value
            return rtn
        else:
            return result

    def post_processing(self, d):
        return d