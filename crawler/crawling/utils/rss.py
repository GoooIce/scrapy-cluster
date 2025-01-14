"""
Module for processing Rss.

Note: The main purpose of this module is to provide support for the
RssSpider, its API is subject to change without notice.
"""

import lxml.etree
from six.moves.urllib.parse import urljoin


class Rss(object):
    """Class to parse Rss (type=urlset) and Rss Index
    (type=rssindex) files"""

    def __init__(self, xmltext):
        xmlp = lxml.etree.XMLParser(recover=True, remove_comments=True, resolve_entities=False)
        self._root = lxml.etree.fromstring(xmltext, parser=xmlp)
        rt = self._root.tag
        self.type = self._root.tag.split('}', 1)[1] if '}' in rt else rt

    def __iter__(self):
        for elem in self._root.getchildren():
            d = {}
            for el in elem.getchildren():
                tag = el.tag
                name = tag.split('}', 1)[1] if '}' in tag else tag

                if name == 'link':
                    if 'href' in el.attrib:
                        d.setdefault('alternate', []).append(el.get('href'))
                else:
                    d[name] = el.text.strip() if el.text else ''

            if 'loc' in d:
                yield d