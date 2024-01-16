import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst

class ProductItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    image_url = scrapy.Field()
    product_url = scrapy.Field()
    seller= scrapy.Field()