from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from toys_scraper.items import MarkingItem


class EuroKatSpider(CrawlSpider):
    name = "euro-kat-spider"
    allowed_domains = ["euro-kat.de"]
    start_urls = ["http://euro-kat.de/"]

    le_kwargs = dict(tags=("a", "area", "frame"), attrs=("href", "src"))

    rules = [
        Rule(LinkExtractor(allow='euro-kat.de/[^/]*$', **le_kwargs), follow=True),
        Rule(LinkExtractor(allow=['MenStart', 'MenSub', 'MenJahre', 'MenBlank'], **le_kwargs), follow=True),
        Rule(LinkExtractor(allow='JGListen', **le_kwargs), callback='parse_list', follow=True),
        #        Rule(LinkExtractor(tags=("a", "area", "frame"), attrs=("href", "src")), follow=True),
    ]

    def parse_list(self, response: Response, **kwargs):
        if len(response.xpath('//table')) == 0:
            return
        column_names = [
            column.xpath('string(.)').get().strip()
            for column in response.xpath('//table[1]/tr[1]/td')
        ]
        if len(column_names) == 1:
            return
        assert column_names[0] in ('OrgNr', 'MPG-Nr'), (column_names, response.url)
        for line in response.xpath('//table/tr'):
            marking = line.xpath('string(./td[1])').get().strip()
            if not marking or marking in ('OrgNr', 'MPG-Nr', '???', 'ohne'):
                continue
            if '?' in marking:
                continue
            yield MarkingItem(
                marking=marking,
                site='euro-kat.de',
                link=response.url,
            )
