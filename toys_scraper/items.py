from scrapy import Field, Item


class MarkingItem(Item):
    marking = Field()
    site = Field()
    link = Field()
