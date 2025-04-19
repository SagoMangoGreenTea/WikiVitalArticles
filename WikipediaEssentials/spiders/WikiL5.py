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
        categories = os.listdir('Links')
        for category in categories:
            category_dir = os.path.join(DIR, category.split('.')[0])
            if not os.path.exists(category_dir):
                os.mkdir(category_dir)
            self.category_dir = category_dir
            with open(os.path.join('Links', category)) as file:
                urls = file.readlines()

            # Yield
            for url in urls:
                yield scrapy.Request(url = url, callback = self.scrape_category_page_header1, meta={'out_dir': category_dir})

        # urls = ["https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Geography/Cities"]
        # for url in urls:
        #     yield scrapy.Request(url = url, callback = self.scrape_category_page_header1, meta={'out_dir': os.path.join(DIR, 'Geography')})
            
    
    
    def get(self, selector):
        entities = set()

        links = selector.css('ol li a::attr(href)').getall()

        for href in links:
            if href.startswith('/wiki/') and ':' not in href:
                entity = urllib.parse.unquote(href.split('/wiki/')[-1])
                entities.add(entity)

        return list(entities)
    

    def scrape_category_page_header1(self, response):

        """Scrape a category page and metadata for a page where categories are divided by h1 tags"""

        # Construct the super category
        parent_cat = response.url.split("/")[-1]
        out_dir = response.meta['out_dir']

        # If does not exist, make
        if not os.path.exists(os.path.join(out_dir, parent_cat)):
            os.mkdir(os.path.join(out_dir, parent_cat))

        content_children = response.xpath('//div[@class="mw-content-ltr mw-parser-output"]/*')
        
        i = 0
        start_collecting = False
        while i < len(content_children):
            child = content_children[i]
            if child.css("h1 ::text").get() is not None:
                if start_collecting:
                    with open(out_file, 'w', encoding='utf-8') as file:
                        print(len(entities))
                        for e in entities:
                            file.write(e + '\n')
                    entities = []
                    subcategory = child.css("h1 ::text").get().strip()
                    subcategory = re.sub(r'\(.*\)', '', subcategory).strip().replace(" ", "_")
                    out_file = os.path.join(out_dir, parent_cat, subcategory) + '.txt'
                    print('start: ' + subcategory)
                else:
                    # Remake name
                    subcategory = child.css("h1 ::text").get().strip()
                    subcategory = re.sub(r'\(.*\)', '', subcategory).strip().replace(" ", "_")
                    out_file = os.path.join(out_dir, parent_cat, subcategory) + '.txt'
                    start_collecting = True
                    entities = []
                    print('start: ' + subcategory)
            
            if start_collecting:
                e = self.get(child)
                entities.extend(e)

            i += 1
        with open(out_file, 'w', encoding='utf-8') as file:
            print(len(entities))
            for e in entities:
                file.write(e + '\n')
        

    def scrape_category_page_generic(self, response):
        entities = set()
        out_dir = response.meta['out_dir']
        out_file = os.path.join(out_dir, response.url.split('/')[-1] + '.txt')
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