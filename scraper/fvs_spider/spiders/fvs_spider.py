import scrapy
from scrapy.loader import ItemLoader
from fvs_spider.items import ProductItem
from scrapy.loader.processors import TakeFirst, MapCompose
from urllib.parse import urljoin
from w3lib.html import remove_tags

class FvSSpider(scrapy.Spider):
    name = 'fvs'
    allowed_domains = ['certideal.com', 'mobileshop.eu']
    start_urls = [
        'https://certideal.com/iphone-reconditionnes-82',
        'https://www.mobileshop.eu/fr/recherche/?keyword=iphone'
    ]

    def parse(self, response):
        if "certideal.com" in response.url:
            return self.parse_certideal(response)
        elif "mobileshop.eu" in response.url:
            return self.parse_mobileshop(response)
        elif "boulanger.com" in response.url:
            return self.parse_boulanger(response)
        
    
    def parse_mobileshop(self, response):
        # Boucle � travers tous les �l�ments 'product-wrap'
        for product in response.css('.product-wrap'):
            loader = ItemLoader(item=ProductItem(), selector=product, response=response)
            loader.default_output_processor = TakeFirst()  # Ajoutez cette ligne
 
            # Titre de l'article
            loader.add_css('title', '.product-name a::text')
 
            # Prix de l'article
            loader.add_css('price', '.price div::text')
 
            # Lien de l'image de l'article (en prenant l'attribut 'data-src' pour l'image paresseusement charg�e)
            loader.add_css('image_url', 'figure a img::attr(data-src)')
 
            # Lien vers l'article, r�solu en URL absolue
            loader.add_css('product_url', '.product-name a::attr(href)', MapCompose(response.urljoin))
            
            loader.add_value('seller', 'Mobileshop')
            # Renvoie l'item charg�
            yield loader.load_item()
 



    def parse_certideal(self, response):
    # Boucle � travers tous les �l�ments 'product-wrap'
        for product in response.css('.list-product-item.ajax_block_product'): 
            loader = ItemLoader(item=ProductItem(), selector=product, response=response)
            loader.default_output_processor = TakeFirst()  # Ajoutez cette ligne

            loader.add_css('title', 'h2.product-title::text')
            loader.add_css('price', 'span.product-price::text')
            loader.add_css('image_url', 'img.lazy-placeholder::attr(data-src)')
            loader.add_css('product_url', 'a[href]::attr(data-url)', MapCompose(response.urljoin))
            loader.add_value('seller', 'Certideal')
            # Renvoie l'item charg�
            yield loader.load_item()
