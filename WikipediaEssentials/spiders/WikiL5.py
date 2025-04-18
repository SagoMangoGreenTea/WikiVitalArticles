# Collect more data about business people and business & economics from wikipedia vital articles Level 5

import scrapy
import os
import re
import urllib.parse

# Directory for the pages
DIR = "data_L5"
if not os.path.exists(DIR):
    os.mkdir(DIR)

class WikiEssentials_L5(scrapy.Spider):

    name = "WL5"

    def start_requests(self):

        """Start scraping here"""

        with open('L5_links.txt') as file:
            urls = file.readlines()

        # Yield
        for url in urls:
            yield scrapy.Request(url = url, callback = self.get_entity)
    
    def get_entity(self, response):
        entities = set()

        out_file = os.path.join(DIR, response.url.split('/')[-1] + '.txt')
        if os.path.exists(out_file):
            return

        links = response.css('ol li a::attr(href)').getall()

        for href in links:
            if href.startswith('/wiki/') and ':' not in href:
                entity = urllib.parse.unquote(href.split('/wiki/')[-1])
                entities.add(entity)

        with open(out_file, 'w', encoding='utf-8') as file:
            for e in entities:
                file.write(e + '\n')


