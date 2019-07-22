# WikipediaEssentials

This is a scrapy project containing code used to download and post-process [Wikipedia vital pages](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles). Currently supports downloading [Level 4](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4) only but code could easily be adapted to include other levels.

## Installing prerequisites

Execute

```python
pip3 install -r requirements.txt
```

## Running the scraper

NOTE: this scraper will download some += 10.000 pages totalling +- 3GB. This is not a friendly thing to do to Wikipedia (they'd rather that you use the dumps or API). Please don't run this script too often.

Execute the following in a terminal:

```python
scrapy crawl WL4
```

## Post-processing articles

The `postprocess.py` script segments and tags the articles for later use (e.g. for use in word embeddings). 
