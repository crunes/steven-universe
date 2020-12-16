'''
STEVEN UNIVERSE: Scrape Steven Universe Wiki episode guide and transcripts

Author: Charmaine Runes

This file crawls through the Steven Universe Wiki, scrapes episode transcripts,
and stores them in JSON files.
'''

import queue
import json
import sys
import csv
import bs4
import util
import datetime

INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'for', 'from', 'how', 'i', 'in', 'include',
                    'is', 'not', 'of', 'on', 'or', 's', 'so', 'such', 'that',
                    'the', 'their', 'this', 'through', 'to', 'we', 'were',
                    'which', 'will', 'with', 'yet'])

EPISODES_URL = "https://steven-universe.fandom.com/wiki/Episode_Guide"
TRANSCRIPTS_URL = "https://steven-universe.fandom.com/wiki/Category:Transcripts"

class Season():
    '''
    Class for a Season. See Constructor for attributes.
    '''

    def __init__(self, name, num_episodes, start_date, end_date, episodes):
        '''
        Creates an instance of a Season.

        Attributes:
            - name (str): Name of season e.g., "Season 1", "Future"
            - num_episodes (int): Number of episodes in the season
            - start_date (str): Season start date e.g., "December 7, 2019"
            - end_date (str): Season end date e.g., "March 27, 2020"
            - episodes (list): List of Episodes
        '''
        self.name = name
        self.num_episodes = num_episodes
        self.start_date = start_date
        self.end_date = end_date
        self.episodes = []


class Episode():
    '''
    Class for an Episode. See Constructor for attributes.
    '''

    def __init__(self, title):
        '''
        Creates an instance of an Episode.

        Attributes:
            - title (str): Name of the episode e.g., "Alone Together"
            - num_series (int): The episode number in the series
            - num_season (int): The episode number in the season
            - airdate (str): Date the episode first aired
            - description (str): Brief episode summary
            - transcript (list): List of dictionaries
        '''
        self.title = title

        self.num_series = None
        self.num_season = None
        self.airdate = None
        self.description = None
        self.transcript = []

    # Create methods for Episodes
    def count_speaker_lines(self, character):
        '''
        Returns the number of lines a specific character has in an episode

        Inputs:
        - character (str): Name of character (e.g., Steven)

        Returns the number of lines they speak in the episode
        '''

        return None


def open_json_file(filename):
    '''
    Opens a JSON file

    Inputs:
        filename: a JSON file

    Outputs:
        a Python-readable file
    '''
    with open(filename) as f:
        py_file = f.read()

    return json.loads(py_file)


def download_convert_webpage(url):
    '''
    Downloads a webpage using a URL and converts it to a BeautifulSoup object

    Inputs:
        url (str): a webpage address

    Outputs:
        a BeautifulSoup object to parse through, if the URL request goes
            through; if not, returns None
    '''

    request = util.get_request(url)

    if request is not None:
        text = util.read_request(request)

        assert text is not None
        soup = bs4.BeautifulSoup(text, "html5lib")

        return soup


def create_episode_obj(soup):
    '''
    Creates an instance of an Episode and pulls the transcript line by line
    '''
    # Remove '/Transcript' from the title
    title = soup.find('h1', id="firstHeading").text[:-11]
    current_ep = Episode(title)

    table = soup.find('table', class_ = 'wikitable bgrevo')
    rows = table.find_all('tr')

    for row in rows[1:]:
        # Skip the first row; it will always be Speaker and Dialogue
        content = {}
        speaker = row.find('th')
        data = row.find('td').text[:-2] # To remove the '\n'

        if speaker:
            content['speaker'] = speaker.text[:-1] # To remove the '\n'
            content['quote'] = data

        elif '[' in data:
            content['location'] = data[1:] # To remove parentheses

        elif '(' in data:
            content['description'] = data[1:] # To remove parentheses

        current_ep.transcript.append(content)

    return current_ep





# Crawl through pages


# Get requests
