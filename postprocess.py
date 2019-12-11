#!/usr/bin/env python3
## Post-process wikipedia articles

from path import Path
import os
import syntok.segmenter as segmenter
from lxml import html
from lxml.html.clean import clean_html
import argparse
import re

MIN_SENTENCE_TOKENS = 5
MIN_PARAGRAPH_TOKENS = 10

# options
OUT_FILE = "WikiEssentials_L4.txt"

# Utility functions

# Remove everything between parentheses
def clear_parentheses(string):

    """Remove everything between parentheses"""

    return(re.sub(r'\(.*\)', '', string))

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

def process_file(input_file, clean_string = False, verbose = False):

    """Read an input (html) file from disk and process to paragraph-size chunks"""

    # Create labels from file path
    labels = '+'.join(input_file.split("/")[2:4])

    # Open input file
    with input_file.open() as f:
        file_as_string = f.read()

    # Process html
    paragraphs_from_html = '\n\n'.join(html2paragraph(file_as_string))
    paragraphs = segmenter.process(paragraphs_from_html)

    paragraphs_new = []
    for k, paragraph in enumerate(paragraphs):
        paragraph_new = []
        for sentence in paragraph:
            sentence_new = []
            for token in sentence:
                sentence_new.append(token.spacing + token.value)
            # Join
            sentence_new_joined = "".join(sentence_new)
            # Clean
            if clean_string:
                # Remove citations
                sentence_new_joined = re.sub(r'\[[0-9]{1,3}\]', '', sentence_new_joined)
                # Remove anything between round brackets
                sentence_new_joined = re.sub(r'\(.*\)', '', sentence_new_joined)
                # Remove anything between square brackets
                sentence_new_joined = re.sub(r'\[.*\]', '', sentence_new_joined)
            if not sentence_new_joined.endswith("Wikipedia") and len(sentence_new_joined.split(" ")) > MIN_SENTENCE_TOKENS: paragraph_new.append(sentence_new_joined)
        # Paragraph must be > 5
        if len(" ".join(paragraph_new).split(" ")) > MIN_PARAGRAPH_TOKENS: paragraphs_new.append("".join(paragraph_new))

    # Print
    if verbose:
        if len(paragraphs_new) > 0:
            print("\t[==>] Snippets: [{}]\n\t[==>] Sample: {}\n\t[==>] Length: {}\n".format(len(paragraphs_new), paragraphs_new[0],
                                                                                      len(paragraphs_new[0].split(" "))))

    # Return
    return(paragraphs_new, labels)

# Call

if __name__ == "__main__":

    # Parse arguments
    argparser = argparse.ArgumentParser()

    # Maximum number of paragraphs
    argparser.add_argument('-m', "--max_paragraphs",
                           help="Maximum number of paragraphs to process for an article",
                           required=False, type = int)
    argparser.add_argument('-v', "--verbose",
                           help="Boolean (defaults to False). Print paragraph lengths, s paragraph sample and number of paragraphs per wikipedia article to the terminal",
                           required=False, default = False, type = bool)
    argparser.add_argument('-c', "--clean_string",
                           help="Boolean (defaults to False). Does some basic preprocessing (e.g. remove special characters and remove anything between parentheses)",
                           required=False, default = False, type = bool)

    # Retrieve arguments passed by user
    args = argparser.parse_args()
    mp = args.max_paragraphs
    verbose = args.verbose
    clean_string = args.clean_string

    # Check if data exists
    assert os.path.exists("data"), "Data not found. Run the scraper first (see README)"

    # Get articles
    io = Path("data")

    # Write to disk
    #stop = 0
    with Path(OUT_FILE).open('w') as outFile:

        # Headers
        outFile.write("document_id\toutcome_label\tparagraph_id\tparagraph_text\n")

        all_articles = io.glob("./*/*/*")
        n = len(all_articles)
        docnr = 1
        # For each article on disk, do ...
        for k, WikiArticle in enumerate(all_articles):
            # Cat
            print(" Handling article: {} -- {}% complete".format(WikiArticle, round((k / n) * 100, 2)))
            # Process article
            paragraphs, label = process_file(WikiArticle, clean_string=clean_string, verbose = verbose)
            # Write
            for i, paragraph in enumerate(paragraphs):
                outFile.write("{}\t{}\t{}\t{}\n".format("DOC" + str(docnr), label, i, paragraph))
                if mp is not None:
                    if i == mp:
                        break
            # Add to document number
            docnr += 1
            #stop += 1
            #if stop == 100:
                #break
