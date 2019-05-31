# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DiscogsAlbum(scrapy.Item):
    album_name = scrapy.Field()
    artist_names = scrapy.Field() #reduntant information
    album_id = scrapy.Field()
    artist_ids = scrapy.Field()
    genre = scrapy.Field()
    label = scrapy.Field()
    style = scrapy.Field()
    format = scrapy.Field()
    country = scrapy.Field()
    year = scrapy.Field()
    num_of_releases = scrapy.Field()
    have = scrapy.Field()
    want = scrapy.Field()
    avg_rating = scrapy.Field()
    ratings = scrapy.Field()
    last_sold = scrapy.Field()
    lowest = scrapy.Field()
    median = scrapy.Field()
    highest = scrapy.Field()


class DiscogsArtist(scrapy.Item):
    artist_id = scrapy.Field()
    credits = scrapy.Field()
    vocals = scrapy.Field()
    site = scrapy.Field()
    arranged_by_cnt = scrapy.Field()
    lyrics_by_cnt = scrapy.Field()
    music_by_cnt = scrapy.Field()

    @staticmethod
    def listToArtist(lstOfTuples):
        tuple = lstOfTuples[0]

        item = DiscogsArtist()
        item['artist_id'] = tuple[0]
        item['credits'] = tuple[1]
        item['vocals'] = tuple[2]
        item['site'] = tuple[3]
        item['arranged_by_cnt'] = tuple[4]
        item['lyrics_by_cnt'] = tuple[5]
        item['music_by_cnt'] = tuple[6]
        return item


class DiscogsSongs(scrapy.Item):
    song_id = scrapy.Field()
    song_name = scrapy.Field()
    album_id = scrapy.Field()
    duration = scrapy.Field()
