import lxml.html
import lxml.etree
import multiprocessing
import itertools


class MuParserException(Exception):
    pass


class BadXpath(MuParserException):
    pass


class _ClassDict:
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


class _GoodHtml:
    xpath_cache = {}

    def __init__(self, html, encoding='utf-8', cache_xpath=True):
        if isinstance(html, bytes):
            self.html = lxml.html.fromstring(html.decode(encoding))
        elif isinstance(html, lxml.html.HtmlElement):
            self.html = html
        else:
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
    FIXED_FILED_VALUE_FORMATTER = _ClassDict({})
    DYNAMIC_FILED_NAME_FORMATTER = _ClassDict({})
    DYNAMIC_FILED_VALUE_FORMATTER = _ClassDict({})

    def to_string(self, e):
        if isinstance(e, lxml.html.HtmlElement):
            return lxml.html.tostring(e, encoding=self.encoding)
        else:
            return e

    def __init__(self, encoding='utf-8', raise_=True, default_formatter=True):
        self.default_formatter = default_formatter
        self.raise_ = raise_
        self.encoding = encoding

    def _raise_exception(self, exception):
        if self.raise_:
            raise exception

    def _parse_fixed_data(self, html):
        if not isinstance(self.FIXED_FILED_VALUE_FORMATTER, _ClassDict):
            self.FIXED_FILED_VALUE_FORMATTER = _ClassDict(self.FIXED_FILED_VALUE_FORMATTER)
        result = {}
        for key, xpath in self.FIXED_DATA.items():
            value = html.xpath(xpath)
            if not (len(value) <= 1 or len(set(value)) == 1):
                exp = BadXpath('{} returns multiple distinct results')
                self._raise_exception(exp)
            value = value[0]
            value = self.FIXED_FILED_VALUE_FORMATTER[value](value)
            result[key] = value
        return result

    def _parse_dynamic(self, html):
        if not isinstance(self.DYNAMIC_FILED_NAME_FORMATTER, _ClassDict):
            self.DYNAMIC_FILED_NAME_FORMATTER = _ClassDict(self.DYNAMIC_FILED_NAME_FORMATTER)
        if not isinstance(self.DYNAMIC_FILED_VALUE_FORMATTER, _ClassDict):
            self.DYNAMIC_FILED_VALUE_FORMATTER = _ClassDict(self.DYNAMIC_FILED_VALUE_FORMATTER)
        result = {}
        for key_xpath, value_xpath in self.DYNAMIC_DATA.items():
            keys = html.xpath(key_xpath)
            values = html.xpath(value_xpath)
            if len(keys) != len(values):
                self._raise_exception(BadXpath('{} and {} selected elements do not match'))
            keys = map(lambda x: self.DYNAMIC_FILED_NAME_FORMATTER[x](x), keys)
            values = map(lambda x: self.DYNAMIC_FILED_VALUE_FORMATTER[x](x), values)
            result.update(dict(zip(keys, values)))
        return result

    def parse(self, html, extra=None):
        html = _GoodHtml(html, encoding=self.encoding)
        result = {}
        result.update(self._parse_dynamic(html))
        result.update(self._parse_fixed_data(html))
        if extra:
            result.update(extra)
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


class MuAnalyst:
    @staticmethod
    def repeat_none():
        return itertools.repeat(None)

    def __init__(self, sources, parsers, extras=None, processes=None):
        self.sources = list(sources)
        if not extras:
            self.extras = [self.repeat_none() for _ in self.sources]
        else:
            self.extras = [(self.repeat_none() if e is None else e) for e in extras]
        self.parsers = list(parsers)
        self.processes = processes

    @staticmethod
    def _f(args):
        parsers, sources, extras = args
        result = {}
        for idx, (s, e) in enumerate(zip(sources, extras)):
            result.update(parsers[idx].parse(s, e))
        return result

    def analyze(self):
        with multiprocessing.Pool(processes=self.processes) as pool:
            it = pool.imap(self._f, zip(itertools.repeat(self.parsers),
                                        zip(*self.sources),
                                        zip(*self.extras)))
            for i in it:
                yield i
