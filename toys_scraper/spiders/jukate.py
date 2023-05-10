import string
from dataclasses import dataclass

from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from toys_scraper.items import MarkingItem

ALLOWED_MARKINGS_SYMBOLS = string.ascii_uppercase + 'n' + ' ' + string.punctuation + string.digits


class JukateSpider(CrawlSpider):
    name = "jukate-spider"
    allowed_domains = ["jukate.ru"]
    start_urls = ["http://jukate.ru/"]

    rules = [
        Rule(LinkExtractor(allow=['.*hp.*', '.*spielzeug.*']), callback='parse', follow=True),
        Rule(LinkExtractor(), follow=True),
    ]

#    pages_wo_tables = []

    def parse(self, response: Response, **kwargs):
        tables = response.xpath('//table')
#        if not tables:
#            self.pages_wo_tables.append(response.url)
        for table in tables:
            title = table.xpath("./preceding-sibling::h2[1]/text()").get()

            @dataclass
            class LineContent:
                name: str
                comment: str

            lines = [
                LineContent(
                    name=line.xpath('string(./td[2])').get().strip(),
                    comment=line.xpath('string(./td[5])').get().strip(),
                )
                for line in table.xpath('./tr[position() > 1]')
            ]
            if not lines:
                continue

            def looks_like_marking(s: str) -> bool:
                if any(c not in ALLOWED_MARKINGS_SYMBOLS for c in s):
                    return False
                if all(c not in string.digits for c in s):
                    return False
                return True

            n_names_look_like_markings = len(list(filter(lambda line: looks_like_marking(line.name), lines)))
            n_comments_look_like_markings = len(list(filter(lambda line: looks_like_marking(line.comment), lines)))

            if n_names_look_like_markings < max(1, len(lines) - 2) and n_comments_look_like_markings < max(1, len(lines) - 2):
                continue

            use_name_as_marking = n_names_look_like_markings >= n_comments_look_like_markings

            for line in lines:
                marking = line.comment
                name = line.name
                if use_name_as_marking:
                    marking = line.name
                    name = None
                if not looks_like_marking(marking):
                    continue

                yield MarkingItem(
                    marking=marking,
                    site='jukate.ru' + ('/eng' if 'eng' in response.url else ''),
                    link=response.url,
                    series_id=title,
                    name=name,
                )

#    @classmethod
#    def from_crawler(cls, crawler, *args, **kwargs):
#        spider = super(JukateSpider, cls).from_crawler(crawler, *args, **kwargs)
#        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
#        return spider

#    def spider_closed(self, spider):
#        if spider is not self:
#            return
#        print(self.pages_wo_tables)
