'''
STEVEN UNIVERSE: Scrape Steven Universe Wiki and analyze transcripts

Author: Charmaine Runes

This file contains helper functions to calculate the term frequency–inverse
document frequency, which reflects how important a word is to a document in a
collection (i.e., corpus)
'''

import math
import pandas as pd
import numpy as np
import csv
import re

def create_list_tokens(document):
    '''
    Takes a document and returns a list of tokens, stripped of trailing numeric
        characters and punctuation.

    Inputs:
        - document (str): A string representation of a document

    Returns a list of tokens
    '''
    raw_tokens = document.split()
    cleaned_list = []

    for token in raw_tokens:
        stripped_token = re.sub(r'[^\w\s]', '', token)
        cleaned_token = re.sub(r'[0-9]', '', stripped_token).lower()

        if cleaned_token != '':
            cleaned_list.append(cleaned_token)

    return cleaned_list


def count_distinct_tokens(list_of_tokens, token_counts):
    '''
    Takes a list of tokens and updates a dictionary with each distinct string
        and the number of times it appears in the list.

    Inputs:
        - list_of_tokens (list): List of tokens
        - token_counts (dict): Dictionary mapping token to counts

    Returns None, updates dictionary in place
    '''
    for token in list_of_tokens:
        if token not in token_counts:
            token_counts[token] = 1
        else:
            token_counts[token] += 1

    return None


def sort_by_count(token_counts, reverse=True):
    '''
    Takes a dictionary of tokens and counts, and returns a list of tuples,
        sorted in descending order by default

    Inputs:
        - token_counts (dict): Dictionary mapping token to counts
        - reverse (bool): Whether to sort in descending order, or not

    Returns a list of tuples, sorted by value, in descending order
    '''
    return sorted(token_counts.items(), key=lambda x: x[1], reverse=reverse)


def calculate_tf(term, token_counts):
    '''
    Calculates the term frequency in a specific document. See Wikipedia entry
        for details on formula.

    Inputs:
        - term (str): Term of interest
        - token_counts (dict): Dictionary mapping terms to their frequencies

    Returns the augmented term frequency, or if the term is not in the document,
        zero.
    '''
    if term not in token_counts:
        return 0

    f_td = token_counts[term]
    max_ftd = sort_by_count(token_counts)[0][1]

    return 0.5 + (0.5 * (f_td / max_ftd))


def count_documents_with_term(term, corpus):
    '''
    Counts the number of documents that contain the term

    Inputs:
        - term (str): The term of interest
        - corpus (dict): The collection of documents where the
            key is some identifier, and the value is a list of
            tokens
    '''
    num_documents=0

    for document, tokens in corpus.items():
        if term in tokens:
             num_documents += 1

    return num_documents


def calculate_idf(term, corpus):
    '''
    Calculates the vanilla inverse document frequency of a term

    Inputs:
        - term (str): The term of interest
        - corpus (dict): The collection of documents where the
            key is some identifier, and the value is a list of
            tokens
    '''
    docs_with_term = count_documents_with_term(term, corpus)

    return math.log(len(corpus) / docs_with_term)


def calculate_tfidf(term, document_tokens, corpus):
    '''
    Calculate the tf-idf of a term in a document, given a corpus

    Inputs:
    - term (str): The term of interest
    - document_tokens (list): List of tokens in a document
    - corpus (dict): The collection of documents where the
            key is some identifier, and the value is a list of
            tokens
    '''
    token_frequency_map = {}
    count_distinct_tokens(document_tokens, token_frequency_map)

    tf = calculate_tf(term, token_frequency_map)
    idf = calculate_idf(term, corpus)
    tfidf = tf * idf

    return tfidf


def build_dictionary(document, corpus):
    '''
    Build a dictionary that maps tokens in a specific doc to their tf-idf values

    Inputs:
        - document (list): a list of tokens
        - corpus (dict): maps an identifier to a list of tokens

    Returns: dictionary i.e., {token: tf-idf}
    '''
    token_to_tfidf = {}

    for token in document:
        if token not in token_to_tfidf:
            token_to_tfidf[token] = calculate_tfidf(token, document, corpus)

    return token_to_tfidf


def find_most_salient(corpus, k):
    '''
    Takes a collection of documents and an integer k and returns a dictionary of
        the k most salient terms, that is, the terms with the highest tf–idf,
        for each document.

    Inputs:
        - corpus (dict): maps an identifier to a list of tokens
        - k (int): number of terms per document to pull

    Returns a dictionary where the key is the identifier, and the value, a list
        of the k most salient terms
    '''

    k_most_salient = {}

    for doc_id, tokens in corpus.items():
        most_salient_by_doc = []

        if tokens:
            token_to_tfidf = build_dictionary(tokens, corpus)
            sorted_list = sort_by_count(token_to_tfidf)

            for token, count in sorted_list[:k]:
                most_salient_by_doc.append(token)

        k_most_salient[doc_id] = most_salient_by_doc

    return k_most_salient


def clean_speaker(speaker_str):
    '''
    Takes a string representing one or more possible speakers and returns a set
        of cleaned speakers

        Examples:
        clean_speaker('Amethyst, Ruby & Sapphire') ->
            {'Amethyst', 'Ruby', 'Sapphire'}

        clean_speaker('Mr. Smiley and Jamie') ->
            {'Mr. Smiley', 'Jamie'}

    Input:
        - speaker_str (str): String representing one or more speakers

    Returns a set of clean speakers
    '''
    speaker_set = set([speaker.strip() for speaker in
                        re.split(', |& |and ', speaker) if speaker != ''])

    return speaker_set


def list_clean_speakers(transcripts):
    '''
    Takes a pandas DataFrame with speakers and returns a list of speaker sets

    Inputs:
        - transcripts (pandas DataFrame): a pandas DataFrame with speakers

    Returns a list of clean speaker sets e.g. [{'steven'}, {'garnet', 'pearl'}]
    '''
    cleaned_speakers = []

    for speaker in transcripts.speaker.unique():
    if isinstance(speaker, str):
        speaker_set = clean_speaker(speaker)

        if speaker_set not in cleaned_speakers:
            cleaned_speakers.append(speaker_set)

    return cleaned_speakers


def build_simple_corpus(df, index, doc_col, filter_by=None):
    '''
    Takes a pandas dataframe and returns a corpus i.e., a dictionary where the
        key is some identifier and the value is the document

    Inputs:
        - df (pandas DataFrame): dataset with columns for index and document
        - index (str): name of the column to use as key
        - doc_col (str): name of the column containing the document string
        - filter_by (tuple of strings): column, value to limit the data by

    Returns a dictionary of documents mapped to their identifier
    '''
    corpus = {}

    if filter_by:
        filter_col, filter_val = limit_by
        df = df.loc[df[filter_col] == filter_val, :]

    df = df.loc[df[doc_col].notna(), :] # Limit the data to the rows with values
    df['terms'] = df.apply(lambda row: create_list_tokens(row[doc_col]), axis=1)

    for i in range(len(df)):
        id = df.iloc[i][index]
        doc = df.iloc[i]['terms']

        if id not in corpus:
            corpus[id] = doc
        else:
            corpus[id].extend(doc)

    return corpus


def build_comprehensive_corpus(trans_df, ep_df):
    '''
    Takes the dataframes containing data on transcripts and episodes, and
        returns a comprehensive corpus that contains documents organized by
        episode, then season, then speaker.

        Example:
        {'Steven':
            {'Season 1':
                {'Gem Glow': ['noooo', 'this', 'cant', 'be', 'happening'],
                 'Laser Light Cannon': ['i', 'dont', 'know', 'hmm']
                },
             'Season 2':
                {...}
            },
        'Lars':
            {'Season 1':
                {'Gem Glow': [...],
                 'Laser Light Cannon': [...]
                },
            }
        }

    Inputs:
        - trans_df (df): a pandas DataFrame, each row a line in a transcript
        - ep_df (df): a pandas DataFrame, each row an episode in the series

    Returns a comprehensive corpus
    '''

    corpus = {', '.join(speaker): None for speaker in trans_df.speaker.unique()}

    merged_df = trans_df.merge(ep_df, left_on='episode', right_on='title')

    # Clean up speakers (in df?) and iterate through them


    for season in merged_df.season.unique():
        filtered = merged_df.loc[merged_df['season']==season, :]
        season_corpus = build_simple_corpus(filtered, episode, quote)
        corpus[speaker][season] = season_corpus









    return corpus


def main(k, transcripts=True):
    '''
    To do later!
    '''

    # If not transcripts
    # Build a corpus based on episode summaries

    # Else build a corpus based on transcripts

    return None


if __name__ == "__main__":
    usage = "python3 find_most_salient.py <k (int)> <transcripts, or episodes>"
    args_len = len(sys.argv)
    transcripts = True

    if args_len == 1:
        k = int(sys.argv[0])
    elif args_len == 2:
        try:
            k = int(sys.argv[0])
            if sys.argv[1] == 'episodes':
                transcripts = False
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)
        sys.exit(0)

    main(k, transcripts)
