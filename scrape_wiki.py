'''
STEVEN UNIVERSE: Scrape Steven Universe Wiki and analyze transcripts

Author: Charmaine Runes

This file scrapes the Steven Universe Wiki for season data and episode
transcripts, storing them in CSV files to export into a SQLite database later.
'''

import sys
import os
import csv
import bs4
import re
import datetime

import util
import config

LIMITING_DOMAIN = "https://steven-universe.fandom.com"
DATA_FILEPATH = "/Users/charmainerunes/git/steven-universe/data/"

class Season():
    '''
    Class for a Season. See Constructor for attributes.
    '''

    def __init__(self, name):
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

        self.num_episodes = None
        self.start_date = None
        self.end_date = None
        self.episodes = []

    def __repr__(self):
        '''
        Returns a representation of the Season
        '''
        if len(self.name) == 1:
            repr_name = 'Season ' + self.name
        else:
            repr_name = 'Steven Universe: ' + self.name

        return repr(repr_name)


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
            - summary (str): Brief episode summary
            - transcript (list): List of dictionaries
        '''
        self.title = title

        self.season = None
        self.num_series = None
        self.num_season = None
        self.airdate = None
        self.summary = None
        self.transcript = []

    def __repr__(self):
        '''
        Returns a representation of the Episode
        '''
        repr_name = self.title
        if self.summary:
            repr_name += (':\n'+ self.summary)

        return repr(repr_name)

    # Create methods for Episodes
    def count_speaker_lines(self, character):
        '''
        Returns the number of lines a specific character has in an episode

        Inputs:
        - character (str): Name of character (e.g., Steven)

        Returns the number of lines they speak in the episode
        '''
        lines = 0

        for line in self.transcript:
            if 'speaker' in line and line['speaker'] == character:
                lines += 1

        return lines


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


def extract_transcript(url, episode):
    '''
    Updates an instance of an Episode with its transcript
    '''
    soup = download_convert_webpage(url)

    find_title = soup.find('h1', id="firstHeading")
    #print(find_title)

    if not find_title:
        print("Could not find title. This shouldn't happen.")

    else:
        title = find_title.text[:-11]
        print("Current episode title is:", episode.title)
        print("Title of this webpage is:", title)

        if len(title) > len(episode.title):
            assert title[:len(episode.title)] == episode.title
        elif len(episode.title) > len(title):
            assert title == episode.title[:len(title)]
        else:
            assert title == episode.title

    table = soup.find('table', class_ = 'wikitable bgrevo')
    rows = table.find_all('tr')
    #print("Number of rows:", len(rows))

    for row in rows[1:]:
        # Skip the first row; it will always be Speaker and Dialogue
        speaker = row.find('th')
        data = row.find('td')

        if not data:
            #print("Could not find data")
            continue

        data = data.text.strip() # To remove the '\n'

        content = {"episode": episode.title, # Connect transcript to episode
                   "speaker": None,
                   "actions": [],
                   "quote": None,
                   "location": None,
                   "description": None}

        if speaker:
            content['speaker'] = speaker.text.strip() # To remove the '\n'

            if '*' in data:
                content['actions'] = []
                num_actions = data.count('*') / 2
                pattern = r'(?<=\*).+?(?=\*)'
                matches = re.findall(pattern, data)

                for index, match in enumerate(matches):
                    if index % 2 == 0:
                        content['actions'].append(match)

                for action in content['actions']:
                    data = data.replace(action, '')
                clean_quote = " ".join(data.split()).replace('**', '').strip()

                content['quote'] = clean_quote

            else:
                content['quote'] = data

        elif '[' in data:
            #print(data)
            pattern = r'(?<=\[).+?(?=\])'
            results = re.search(pattern, data)
            if results:
                content['location'] = results.group(0)

        elif '(' in data:
            #print(data)
            pattern = r'(?<=\().+?(?=\))'
            results = re.search(pattern, data)
            if results:
                content['description'] = results.group(0)

        episode.transcript.append(content)
        #print("Appended content to the episode")

    return None


def convert_string_to_datetime(date_string, format='%B %d, %Y'):
    '''
    Returns the string input as a datetime object, given a specific format.

    Note: Move to util.py? This is a helper function
    '''
    formatted_date = datetime.datetime.strptime(date_string, format)

    # Fix this with regex??? LATER

    return formatted_date


def get_season_data(soup):
    '''
    Returns an instance of a Season object.
    '''
    list_of_seasons = []

    series_overview_table = soup.find_all('table', class_='wikitable')[0]
    rows = series_overview_table.find_all('tr')

    for row in rows[1:]:
        data = row.find_all('td')

        season_name = data[1].find('b').contents[0].strip('"')
        season = Season(season_name)
        print('Created an instance of a Season:', season.name)

        if season.name == 'Movie':
            season.num_episodes = 1
            #print(data[2].contents)

            airdate_str = data[2].contents[0].strip()
            season.start_date = convert_string_to_datetime(airdate_str)
            season.end_date = season.start_date

        else:
            season.num_episodes = int(data[2].contents[0].strip())

            start_date_str = data[3].contents[0].strip()
            season.start_date = convert_string_to_datetime(start_date_str)

            end_date_str = data[4].contents[0].strip()
            season.end_date = convert_string_to_datetime(end_date_str)

        list_of_seasons.append(season)

    return list_of_seasons


def get_episode_data(soup, all_seasons):
    '''
    '''
    num_table=2
    all_wikitables = soup.find_all('table', class_='wikitable')
    movie_table = soup.find_all('table', class_='bgrevo')[1]

    for num_season in range(len(all_seasons)):
        current_season = all_seasons[num_season]
        print("Working on season:", current_season.name)

        for num_episode in range(current_season.num_episodes):
            print("Working on episode:", num_episode+1)

            # Season 1 starts with table at index 2
            current_ep_table = all_wikitables[num_table]
            num_table += 1

            data = current_ep_table.find_all('td')

            if data:
                if current_season.name != "Movie":
                    ep_title = data[3].text.replace('"', '').strip()
                    current_ep = Episode(ep_title)

                    current_ep.num_series = data[0].text.strip()
                    current_ep.num_season = data[1].text.strip()
                    #current_ep.airdate = convert_string_to_datetime(data[4].text.strip())
                    current_ep.summary = data[6].text.strip()

                    ep_url = data[3].find('a').get('href')

                    # Add exception because Little Homeschool is a separate page
                    if ep_title == "Little Homeschool":
                        ep_url += '_(episode)'

                elif current_season.name == "Movie":
                    num_table -= 1 #Go back to previous wikitable
                    data = movie_table.find_all('td')

                    ep_title = data[1].text.strip()
                    #print(data[1])
                    current_ep = Episode(ep_title)

                    current_ep.summary = data[4].text.strip()
                    print(current_ep.summary)

                    ep_url = data[1].find('a').get('href')

                ep_url_to_visit = LIMITING_DOMAIN + ep_url + '/Transcript'
                print(ep_url_to_visit)

                extract_transcript(ep_url_to_visit, current_ep)
                print("Got transcript for " + current_ep.title)

                current_ep.season = current_season.name # Connect episode to season
                current_season.episodes.append(current_ep)

            else:
                continue

    return all_seasons

def ensure_dict(object):
    '''
    Make sure the object is of dictionary type
    '''

    if isinstance(object, dict):
        return object
    else:
        return object.__dict__

def write_rows(csvfile, list_of_dict, final_cols, header=False):
    '''
    Writes each dictionary into a CSV's row
    '''
    writer = csv.DictWriter(csvfile, fieldnames=final_cols)

    if header:
        writer.writeheader()

    for d in list_of_dict:
        to_parse = ensure_dict(d)
        filtered_d = dict(
            (k, v) for k, v in to_parse.items() if k in final_cols
        )
        writer.writerow(filtered_d)

    return None


def convert_to_csv(list_of_dict, file_name):
    '''
    Takes a list of pseudo-dictionaries and returns a CSV with a given filename
    '''
    skip_cols = ['episodes', 'transcript']
    def_a_dict = ensure_dict(list_of_dict[0])

    # Assumes that every pseudo-dictionary has the same keys
    final_cols = [col for col in def_a_dict.keys() if col not in skip_cols]

    if not os.path.isfile(file_name):
        with open(file_name, 'w') as csvfile:
            write_rows(csvfile, list_of_dict, final_cols, header=True)

    else:
        with open(file_name, 'a') as csvfile:
            write_rows(csvfile, list_of_dict, final_cols)

    return None


# Crawl through wiki pages
def main():
    '''
    Scrape wiki data, starting with the first episode of the first season,
    and creates Episode objects. Each Episode is then appended to the Season's
    list of episodes.
    '''
    starting_url = "https://steven-universe.fandom.com/wiki/Episode_Guide"
    season_csv = config.data_folder + 'seasons.csv'
    episode_csv = config.data_folder + 'episodes.csv'
    transcripts_csv = config.data_folder + 'transcripts.csv'

    soup = download_convert_webpage(starting_url)

    all_seasons = get_season_data(soup)
    print(all_seasons)

    seasons_with_episodes = get_episode_data(soup, all_seasons)
    print("Got episodes!")

    # Create seasons.csv
    print("Creating seasons.csv...")
    convert_to_csv(seasons_with_episodes, season_csv)

    for season in seasons_with_episodes:
        print("Adding episodes from", season.name, "to episodes.csv")
        # Build out episodes.csv
        convert_to_csv(season.episodes, episode_csv)

        # Build out transcripts.csv
        for episode in season.episodes:
            print("Adding transcript from", episode.title, "to transcripts.csv")
            convert_to_csv(episode.transcript, transcripts_csv)

    return None


if __name__ == "__main__":
    usage = "python3 scrape_wiki.py"
    main()
