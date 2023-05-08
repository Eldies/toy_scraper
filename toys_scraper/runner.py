from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from toys_scraper.spiders.eurokat import EuroKatSpider
from toys_scraper.spiders.jukate import JukateSpider

settings = get_project_settings()
process = CrawlerProcess(settings)

process.crawl(JukateSpider)
process.crawl(EuroKatSpider)

process.start()
