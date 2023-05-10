from scrapy import Field, Item


class MarkingItem(Item):
    marking = Field()
    site = Field()
    link = Field()
    series_id = Field()
    name = Field()
