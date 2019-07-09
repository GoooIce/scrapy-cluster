# -*- coding: utf-8 -*-
import scrapy

from scrapy import Item, Field
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders.sitemap import SitemapSpider

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import logging


class RawResponseItem(Item):
    appid = Field()
    crawlid = Field()
    url = Field()
    response_url = Field()
    status_code = Field()
    status_msg = Field()
    response_headers = Field()
    request_headers = Field()
    body = Field()
    links = Field()
    attrs = Field()
    success = Field()
    exception = Field()
    encoding = Field()

class RsswithggzySpider(SitemapSpider):
    name = 'rsswithggzy'
    allowed_domains = ['ggzy.gov.cn']
    sitemap_urls = ['http://www.ggzy.gov.cn/information/rss/01/0101rss.xml']
    _logger = logging

    def parse(self, response):
        self._logger.DEBUG("crawled url {}".format(response.request.url))
        cur_depth = 0
        if 'curdepth' in response.meta:
            cur_depth = response.meta['curdepth']

        # capture raw response
        item = RawResponseItem()
        # populated from response.meta
        item['appid'] = response.meta['appid']
        item['crawlid'] = response.meta['crawlid']
        item['attrs'] = response.meta['attrs']

        # populated from raw HTTP response
        item["url"] = response.request.url
        item["response_url"] = response.url
        item["status_code"] = response.status
        item["status_msg"] = "OK"
        item["response_headers"] = self.reconstruct_headers(response)
        item["request_headers"] = response.request.headers
        item["body"] = response.body
        item["encoding"] = response.encoding
        item["links"] = []

        # determine whether to continue spidering
        if cur_depth >= response.meta['maxdepth']:
            self._logger.DEBUG("Not spidering links in '{}' because" \
                " cur_depth={} >= maxdepth={}".format(
                                                      response.url,
                                                      cur_depth,
                                                      response.meta['maxdepth']))
        else:
            # we are spidering -- yield Request for each discovered link
            link_extractor = LinkExtractor(
                            allow_domains=response.meta['allowed_domains'],
                            allow=response.meta['allow_regex'],
                            deny=response.meta['deny_regex'],
                            deny_extensions=response.meta['deny_extensions'])

        for link in link_extractor.extract_links(response):
                # link that was discovered
                the_url = link.url
                the_url = the_url.replace('\n', '')
                item["links"].append({"url": the_url, "text": link.text, })
                req = Request(the_url, callback=self.parse)

                req.meta['priority'] = response.meta['priority'] - 10
                req.meta['curdepth'] = response.meta['curdepth'] + 1

                if 'useragent' in response.meta and \
                        response.meta['useragent'] is not None:
                    req.headers['User-Agent'] = response.meta['useragent']

                self._logger.DEBUG("Trying to follow link '{}'".format(req.url))
                yield req

        # raw response has been processed, yield to item pipeline
        yield item


process = CrawlerProcess(get_project_settings())

# 'followall' is the name of one of the spiders of the project.
process.crawl('rsswithggzy')
process.start() # the script will block here until the crawling is finished