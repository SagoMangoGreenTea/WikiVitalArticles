#!/usr/bin/env python3
## Post-process wikipedia articles

from path import Path
import os
import syntok.segmenter as segmenter
from lxml import html
from lxml.html.clean import clean_html
import argparse

SNIP_LENGTH = 100
UPPER_BOUND = 220
LOWER_BOUND = 160
MIN_SENTENCE_TOKENS = 10

# options
OUT_FILE = "WikiEssentials_L4.txt"

# Utility functions

# Function from: https://github.com/amirouche/sensimark
def extract_paragraphs(element):

    """Extract paragraphs from wikipedia articles"""

    if element.tag == 'hr':
        return []
    if element.tag == 'p':
        text = clean_html(element).text_content()
        text = ' '.join(text.split())
        return [text]
    if element.tag[0] == 'h':
        text = clean_html(element).text_content()
        text = ' '.join(text.split())
        return [text]
    out = list()
    for child in get_children(element):
        out.extend(extract_paragraphs(child))
    return out

# Function from: https://github.com/amirouche/sensimark
def html2paragraph(string):

    """Turn html into paragraphs of text"""

    out = list()
    xml = html.fromstring(string)
    # extract title
    title = xml.xpath('/html/head/title/text()')[0]
    title = ' '.join(title.split())  # sanitize
    out.append(title)
    # extract the rest
    body = xml.xpath('/html/body')[0]
    out.extend(extract_paragraphs(body))
    return out

# Function from: https://github.com/amirouche/sensimark
def get_children(xml):

    """List children ignoring comments"""

    return [e for e in xml.iterchildren() if not isinstance(e, html.HtmlComment)]

def process_file(input_file):

    """Read an input (html) file from disk and process to paragraph-size chunks"""
    #input_file = "data/./Arts/Literature/The_Golden_Ass.html"
    # Create labels from file path
    labels = '+'.join(input_file.split("/")[2:4])

    # Open input file
    #with open(input_file, "r") as f:
    #    file_as_string = f.read()

    with input_file.open() as f:
        file_as_string = f.read()

    # Process html
    paragraphs_from_html = '\n\n'.join(html2paragraph(file_as_string))
    paragraphs = segmenter.process(paragraphs_from_html)

    # Cut into snippets of approximate size
    final_paragraphs = []
    snippet_hold = []
    snippet_length_hold = 0
    for paragraph in paragraphs:
        if snippet_length_hold < LOWER_BOUND:
            snippet = snippet_hold
            snippet_length = snippet_length_hold
        else:
            snippet = []
            snippet_hold = []
            snippet_length = 0
        for sentence in paragraph:
            sentence_new = []
            for token in sentence:
                sentence_new.append(token.spacing + token.value)
            # Add sentence to snippet
            sentence_length = len(sentence_new)
            if sentence_length < MIN_SENTENCE_TOKENS: continue
            snippet_length_updated = snippet_length + sentence_length
            if snippet_length_updated < LOWER_BOUND:
                snippet.append("".join(sentence_new))
                snippet_length = snippet_length_updated
                continue
            if snippet_length_updated > UPPER_BOUND:
                final_paragraphs.append("".join(snippet))
                snippet = []
                snippet.append("".join(sentence_new))
                snippet_length = len(snippet)
            else:
                snippet.append("".join(sentence_new))
                snippet_length = snippet_length_updated
        # Add to hold
        snippet_hold = snippet
        snippet_length_hold = snippet_length
    # (last snippet)
    if len(snippet_hold) > 0:
        final_paragraphs.append("".join(snippet))

    # Print
    if len(final_paragraphs) > 0:
        print("\t[==>] Snippets: [{}]\n\t[==>] Sample: {}\n\t[==>] Length: {}\n".format(len(final_paragraphs), final_paragraphs[0],
                                                                                  len(final_paragraphs[0].split(" "))))

    return(final_paragraphs, labels)

    # Iterate
    """
    final_paragraphs = []
    for paragraph in paragraphs:
        paragraph_clean = []
        for sentence in paragraph:
            sentence_clean = []
            for token in sentence:
                sentence_clean.append(token.value)
            # Minimum length of sentence
            if len(sentence_clean) > 5: paragraph_clean.append(" ".join(sentence_clean))

        if len(paragraph_clean) > 1: final_paragraphs.append(" ".join(paragraph_clean))

    # Return
    return(final_paragraphs, labels)
    """

# Call

if __name__ == "__main__":

    # Parse arguments
    argparser = argparse.ArgumentParser()

    # Maximum number of paragraphs
    argparser.add_argument('-m', "--max_paragraphs",
                           help="Maximum number of paragraphs to process for an article",
                           required=False, type = int)

    # Retrieve arguments passed by user
    args = argparser.parse_args()
    mp = args.max_paragraphs

    # Check if data exists
    assert os.path.exists("data"), "Data not found. Run the scraper first (see README)"

    # Get articles
    io = Path("data")

    # Write to disk
    #stop = 0
    with Path(OUT_FILE).open('w') as outFile:

        all_articles = io.glob("./*/*/*")
        n = len(all_articles)
        docnr = 1
        # For each article on disk, do ...
        for k, WikiArticle in enumerate(all_articles):
            # Cat
            print(" Handling article: {} -- {}% complete".format(WikiArticle, round((k / n) * 100, 2)))
            # Process article
            paragraphs, label = process_file(WikiArticle)
            # Write
            for i, paragraph in enumerate(paragraphs):
                outFile.write("{}\t{}\t{}\n".format("DOC" + str(docnr), label, paragraph))
                if mp is not None:
                    if i == mp:
                        break
            # Add to document number
            docnr += 1
            #stop += 1
            #if stop == 100:
                #break
