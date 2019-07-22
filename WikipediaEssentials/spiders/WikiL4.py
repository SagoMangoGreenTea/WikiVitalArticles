import scrapy
import os
import re

# Directory for the pages
DIR = "data"
if not os.path.exists(DIR):
    os.mkdir(DIR)

# Helper function ==> filter non-relevant wiki urls
def good_url(link):
    # Split link
    link_split = link.split("/")
    # Exceptions
    if not link.startswith("/wiki"):
        return(False)
    elif link.startswith("/wiki/Wikipedia"):
        return(False)
    elif link.startswith("/wiki/User"):
        return(False)
    elif link.startswith("/wiki/Template"):
        return(False)
    elif link.startswith("/wiki/Special"):
        return(False)
    elif link.startswith("/wiki/Help"):
        return(False)
    elif link.startswith("/wiki/Portal"):
        return(False)
    elif link.startswith("/wiki/Category"):
        return(False)
    elif link.startswith("/wiki/Main_Page"):
        return(False)
    else:
        return(True)

class WikiEssentials_L4(scrapy.Spider):

    name = "WL4"

    def start_requests(self):

        """Start scraping here"""

        url = "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4"

        # Yield
        yield scrapy.Request(url = url, callback = self.top_level_categories)

    def top_level_categories(self, response):

        """Scrape top-level categories from the page"""

        # Search for wikitable
        for supercat in response.css("#mw-content-text > div > table a::attr(href)").getall():
            # Join with baseurl
            supercat_url = response.urljoin(supercat)
            # Go down the tree
            self.log("Parsing page %s" % supercat)
            # Yield
            yield scrapy.Request(supercat_url, callback=self.scrape_category_page)

    def scrape_category_page(self, response):

        """Scrape a category page and metadata"""

        content = response.css("#mw-content-text")
        headers = content.css("h2")

        # Construct the super category
        parent_cat = response.url.replace("https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/", "")

        # If does not exist, make
        if not os.path.exists(os.path.join(DIR, parent_cat)):
            os.mkdir(os.path.join(DIR, parent_cat))

        # Retrieve category names
        subcats = [header.css("h2 span::text").get() for header in headers]

        # For each header, do
        for i, header in enumerate(headers):
            # If contents, then skip
            if header.css("h2 span").get() is None: continue
            # Else get subcategory for current and next header
            header_current = subcats[i]
            header_next = subcats[i+1] if i < (len(subcats)-1) else None

            # Find <div> tags between the two sub categories
            if header_next is not None:
                div_siblings = content.xpath("//*[preceding-sibling::h2[span[text() = '{}']] and following-sibling::h2[span[text() = '{}']]]".format(header_current, header_next))
            else:
                # Find <div> tags between the last sub category and the navigation box
                div_siblings = content.xpath("//*[preceding-sibling::h2[span[text() = '{}']] and following-sibling::div[@class='navbox']]".format(header_current))

            # Remake name
            subcategory = re.sub(r'\(.*\)', '', header_current).strip().replace(" ", "_")

            # Make sub category dir if not exists
            subcat_dir = os.path.join(DIR, parent_cat, subcategory)
            if not os.path.exists(subcat_dir):
                os.mkdir(subcat_dir)

            # Find urls
            subsection_urls = div_siblings.css("a::attr(href)").getall()
            # If empty, continue
            if len(subsection_urls) == 0: continue
            # For each page, retrieve and save
            for ref in subsection_urls:
                if good_url(ref):
                    # To scrape_page
                    save_file = ref.strip("/wiki/") + ".html"
                    page_url = "https://en.wikipedia.org" + ref
                    yield scrapy.Request(page_url, callback=self.scrape_page, meta={'file_name':os.path.join(subcat_dir,save_file)})

    def scrape_page(self, response):

        """Save the html file to disk"""

        # Retrieve file name
        filename = response.meta["file_name"]

        # Make file path and write html
        with open(filename, 'wb') as f:
            f.write(response.body)
