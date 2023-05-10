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
            for column in response.xpath('(//table/tr)[1]/td')
        ]
        if len(column_names) == 1:
            return

        is_2_table = column_names in (['OrgNr', 'Figur'], ['OrgNr', 'Figur', ''])
        is_4_table = column_names == ['MPG-Nr', 'Figur', 'Serie', 'ab']
        assert is_2_table or is_4_table, (column_names, response.url)

        series_name: str = None

        for line in response.xpath("//table/tr"):

            if is_4_table:
                column3 = line.xpath('string(./td[3])').get().strip()
                if column3 and column3 != '"':
                    series_name = column3
                elif not column3:
                    series_name = None
            elif is_2_table:
                if line.xpath('./td[1]/a/img/@src').get() == "../genPict/Detail.gif":
                    series_name = line.xpath('string(./td[2])').get().strip()
                elif not line.xpath('string(./td[1])').get().strip():
                    series_name = None

            if series_name is None:
                continue

            marking = line.xpath('string(./td[1])').get().strip()
            if not marking or marking in ('OrgNr', 'MPG-Nr', '???', 'ohne'):
                continue
            if '?' in marking:
                continue

            toy_name = line.xpath('string(./td[2])').get().strip()

            yield MarkingItem(
                marking=marking,
                site='euro-kat.de',
                link=response.url,
                series_id=' '.join(series_name.split()) or None,
                name=' '.join(toy_name.split()) or None,
            )
