# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Property(scrapy.Item):
    # define the fields for your item here like:
    link = scrapy.Field()
    id = scrapy.Field()
    address = scrapy.Field()
    beds = scrapy.Field()
    baths = scrapy.Field()
    sqft = scrapy.Field()
    rent = scrapy.Field()
    image = scrapy.Field()
    geohash= scrapy.Field()
    latitude= scrapy.Field()
    longitude=scrapy.Field()