from typing import Any
import scrapy
from scrapy.http import Response

class SevenEleven(scrapy.Spider):
    name = '7-eleven'
    start_urls=['https://www.tiendaenlinea.7-eleven.com.mx/']
    
    def parse(self, response):
        menu_items = response.css('.vtex-mega-menu-2-x-menuItem')

        for item in menu_items:
            item_text = item.css('::text').get()
            item_link = item.css('a::attr(href)').get()

            print(f'Texto: {item_text}')
            print(f'Enlace: {item_link}')





