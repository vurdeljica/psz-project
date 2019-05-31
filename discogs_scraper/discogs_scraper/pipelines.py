# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .db_manager import DatabaseManager
from .items import DiscogsAlbum
from .items import DiscogsArtist

class DiscorgScraperPipeline(object):

    def __init__(self):
        self.db_manager = DatabaseManager()

    def process_item(self, item, spider):
        if isinstance(item, DiscogsAlbum):
            self.db_manager.store_album_db(item)
        elif isinstance(item, DiscogsArtist):
            self.db_manager.update_artist_info(item)
        return item

