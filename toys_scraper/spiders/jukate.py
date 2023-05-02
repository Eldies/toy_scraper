import string
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from toys_scraper.items import MarkingItem


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
            comment_cells = table.xpath('./tr[position() > 1]/td[5]')
            name_cells = table.xpath('./tr[position() > 1]/td[2]')
            comment_texts = comment_cells.xpath('string(.)').getall()
            name_texts = name_cells.xpath('string(.)').getall()
            comment_texts = list(filter(lambda s: s and s != '-', map(lambda s: s.strip(), comment_texts)))
            name_texts = list(filter(lambda s: s and s != '-', map(lambda s: s.strip(), name_texts)))

            def looks_like_marking(s: str) -> bool:
                if any(c in string.ascii_lowercase and c != 'n' for c in s):
                    return False
                if all(c not in string.digits for c in s):
                    return False
                return True

            if len(comment_texts) > len(comment_cells) - 2 and all(looks_like_marking(t) for t in comment_texts):
                texts = comment_texts
            elif len(name_texts) > len(name_cells) - 2 and all(looks_like_marking(t) for t in name_texts):
                texts = name_texts
            else:
                texts = []

            for text in texts:
                yield MarkingItem(
                    marking=text,
                    site='jukate.ru' + ('/eng' if 'eng' in response.url else ''),
                    link=response.url,
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
