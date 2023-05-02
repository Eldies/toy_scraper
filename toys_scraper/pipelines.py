import pymongo
from itemadapter import ItemAdapter


class MongoPipeline:

    collection_name = 'web_markings'
    new_collection_name = 'web_markings_new'
    old_collection_name = 'web_markings_old'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        list_of_collections = self.db.list_collection_names()
        if self.old_collection_name in list_of_collections:
            self.db.drop_collection(self.old_collection_name)
        if self.collection_name in list_of_collections:
            self.db[self.collection_name].rename(self.old_collection_name)
        self.db[self.new_collection_name].rename(self.collection_name)
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.new_collection_name].insert_one(ItemAdapter(item).asdict())
        return item
