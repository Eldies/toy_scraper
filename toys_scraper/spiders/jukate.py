import scrapy


class JukateSpider(scrapy.Spider):
    name = "jukate-spider"
    allowed_domains = ["jukate.ru"]
    start_urls = ["http://jukate.ru/"]

    def parse(self, response):
        self.log(f'Visited "{response.url}"')
