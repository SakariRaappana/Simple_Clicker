"""This is a working prototype of a simple but fully autonomus website "smoke
testing" tool. The purpose of this tool is later on to be integrated with a set
of other testing services.

This script still needs more testing on different enviroments and more
precise error handling.

This script is written by Sakari Raappana
"""
import sys
import requests
from requests_html import HTML, HTMLSession
from requests.exceptions import ConnectionError, MissingSchema, InvalidSchema, ReadTimeout
import numpy as np
from colorama import Fore, Style, Back

class SimpleClicker():

    def __init__(self, base_url, depth=1, limit=400, timeout=5):
        self.base_url = base_url
        self.depth = depth
        self.limit = limit
        self.timeout = timeout
        self.session = HTMLSession()

    def get_links(self, url):
        links, ext_links = [], []
        try:
            r = self.session.get(url, timeout=self.timeout)
            for link in r.html.absolute_links:
                if self.base_url in link:
                    links.append(link)
                else:
                    ext_links.append(link)
        except ConnectionError:
            print('Error occured while connecting to the given url.')
            sys.exit(1)

        except (MissingSchema, InvalidSchema):
            print('Error invalid URL')
            sys.exit(1)
        return links, ext_links
      

    def validate_links(self, links):
        green = {}
        yellow = {}
        red = []
        ping_list = []

        for link in links:
            try:
                response = requests.get(link, timeout=self.timeout)
                status_code = response.status_code
                ping = round(response.elapsed.total_seconds(), 4)
                
                if status_code == 200:
                    green.update( {link: [status_code, ping]} )
                    ping_list.append(ping)
                else:
                    yellow.update( {link: [status_code, ping]} )
                    ping_list.append(ping)
            except (ConnectionError, MissingSchema, InvalidSchema, ReadTimeout):
                red.append(link)
        
        links_total = len(green) + len(yellow) + len(red)
        try:
            ratio = (len(green) / links_total) * 100
        except:
            print('Some error occured and links were not found. Make sure that the URL is in correct form.')
            sys.exit(1)
        
        return green, yellow, red, links_total, ratio, ping_list



#------------- Main part of the script ----------------------------
''' Define the base url that you want to scan.
On the initialization of the "Simple Clicker" you can define depth value
and total limit number.

First the algorithm will collect all the links from the given base url.
If depth is more than 0 then also sub directories up to given depth
will be scanned for links.

Then all the links are validated by their http response and the response
time is calculated. '''

base_url = 'https://www.google.fi/'
clicker = SimpleClicker(base_url, depth=0, limit=200)

all_links = set()
all_ext_links = set()

root_links, ext_links = clicker.get_links(base_url)
all_links = all_links.union(root_links)
all_ext_links = all_ext_links.union(ext_links)

page_links = root_links
for _ in range(clicker.depth):
    links = set()
    ext_links = set()
    for link in page_links:
        if len(all_links) > clicker.limit:
            break
        temp, ext_temp = clicker.get_links(link)
        links = links.union(temp)
        all_links = all_links.union(temp)
        ext_links = ext_links.union(ext_temp)
        all_ext_links = all_ext_links.union(ext_links)
        
    page_links = links

green, yellow, red, links_total, ratio, ping_list = clicker.validate_links(all_links)
ext_green, ext_yellow, ext_red, ext_links_total, ext_ratio, ext_ping_list = clicker.validate_links(ext_links)
#--------------------------------------------------------------------



#------------- Printing the results to terminal ---------------------
def build_report():

    print(f'''
    ===============================================================

    Links under the given base URL:

    Total amount of links: {links_total}
    Succes rate: {round(ratio)}%
    HTTP response times:
        Min: {min(ping_list)}
        Max: {max(ping_list)}
        Mean: {round(np.mean(ping_list), 5)}
        Std: {round(np.std(ping_list), 5)}

    Number of {Fore.GREEN}"HTTP 200"{Style.RESET_ALL} responses: {len(green)}
    ''')
    for key, value in green.items():
        print(f'\t{key}\n\tStatus Code: {value[0]}  Ping: {value[1]} \n')
    print('\n')

    print(f'Number of {Fore.BLUE}{Style.DIM}other HTTP{Style.RESET_ALL} responses: {len(yellow)} \n')
    for key, value in yellow.items():
        print(f'\t{key}\n\tStatus Code: {value[0]}  Ping: {value[1]} \n')
    print('\n')

    print(f'Number of {Fore.RED}incorrect or timeouted links: {Style.RESET_ALL} {len(red)} \n')
    for link in red:
        print(f'\t{link}')
    print('\n')


    print('External links on given base URL:\n')

    print(f'Number of {Fore.GREEN}"HTTP 200"{Style.RESET_ALL} responses: {len(ext_green)} \n')
    for key, value in ext_green.items():
        print(f'\t{key}\n\tStatus Code: {value[0]}  Ping: {value[1]} \n')
    print('\n')

    print(f'Number of {Fore.BLUE}other HTTP{Style.RESET_ALL} responses: {len(ext_yellow)} \n')
    for key, value in ext_yellow.items():
        print(f'\t{key}\n\tStatus Code: {value[0]}  Ping: {value[1]} \n')
    print('\n')

    print(f'Number of {Fore.RED}incorrect or timeouted links: {Style.RESET_ALL} {len(ext_red)} \n')
    for link in ext_red:
        print(f'\t{link}')
    print('\n')

    print('===============================================================')


build_report()
#--------------------------------------------------------------------