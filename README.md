# WikipediaEssentials

This is a scrapy project containing code used to download and post-process [Wikipedia vital pages](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles). Currently supports downloading [Level 4](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4) only but code could easily be adapted to include other levels.

The postprocessing script is adapted from the [sensimark](https://github.com/amirouche/sensimark) project by [amirouche](https://github.com/amirouche/sensimark/commits?author=amirouche).

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

If you also want the expanded sections for the history and business & economics sections from level 5, then execute:

```python
scrapy crawl WL5
```

as well. These sections will be downloaded in 'data_L5' folder. You should manually copy the files to the 'data' folder under the correct category before executing the post-processing script.

## Post-processing articles

The `postprocess.py` script segments and tags the articles for later use (e.g. for use in word embeddings).

Execute the following in a terminal:

```python
python postprocess.py
```

Execute the following to view additional options

```python
python postprocess.py -h
```
