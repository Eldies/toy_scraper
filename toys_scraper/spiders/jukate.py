from scrapy import signals
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider


class JukateSpider(CrawlSpider):
    name = "jukate-spider"
    allowed_domains = ["jukate.ru"]
    start_urls = ["http://jukate.ru/"]

    rules = [
        Rule(LinkExtractor(allow=['.*hp.*', '.*spielzeug.*']), callback='parse', follow=True),
        Rule(LinkExtractor(), follow=True),
    ]

    pages_wo_tables = []
    found_marks = []

    def parse(self, response: Response, **kwargs):
        tables = response.xpath('//table[contains(tr[1]/td[5], "Комментарий") or contains(tr[1]/td[5], "Comment")]')
        if not tables:
            self.pages_wo_tables.append(response.url)
        for table in tables:
            cells = table.xpath('./tr[position() > 1]/td[5]')
            for cell in cells:
                text = cell.xpath('string(.)').get().strip()
                if text != '-':
                    self.found_marks.append((text, response.url))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(JukateSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        if spider is not self:
            return
        print(self.pages_wo_tables)
        print(self.found_marks)
