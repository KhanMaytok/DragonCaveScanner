import random
import time
from bs4 import BeautifulSoup

import requests
from dc_scanner.constants import Dragons


class DcScanner(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'})
        self.base_url = 'https://dragcave.net/'

    def get_egg_info(self):
        url = 'http://dragcave.wikia.com/wiki/Which_egg_is_which%3F'
        res = self.session.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        common_egg_table = soup.findAll('table', {'class': 'dc_table'})[0]
        eggs_tr = common_egg_table.findAll('tr')
        for tr in eggs_tr:
            cells = tr.findAll('td')
            if cells[0].find('a') is not None:
                dragon_name = cells[2].get_text()
                dragon_obj = {
                    '{}'.format(dragon_name): {'egg_text': cells[1].get_text(), 'egg_link': cells[2].find('a')['href']}}

    def login(self):
        payload = {
            'username': self.username,
            'password': self.password,
            'submit': None
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'origin': self.base_url
        }

        time.sleep(random.uniform(1, 3))
        self.session.post('https://dragcave.net/login', data=payload, headers=headers)

    def get_url(self, suffix):
        return "{}{}".format(self.base_url, suffix)

    def pick_random_abandoned(self):
        headers = {
            'referer': 'https://dragcave.net/abandoned'
        }

        url = 'https://dragcave.net/abandoned'
        res = self.session.get(url)
        time.sleep(random.uniform(1, 3))
        soup = BeautifulSoup(res.content, 'html.parser')
        eggs_container = soup.find('div', {'class': 'ap'})
        eggs = eggs_container.findAll('a')
        random_egg = random.choice(eggs)
        egg_url = random_egg['href']
        res = self.session.get(self.get_url(egg_url), headers=headers)

    def get_specific_dragon(self, dragon_name):
        headers = {
            'referer': self.base_url
        }
        cave_codes = {
            'coast': '1',
            'desert': '2',
            'forest': '3',
            'jungle': '4',
            'alpine': '5'
        }

        dragon = Dragons[dragon_name]
        habitat_number = cave_codes.get(dragon.get('habitat'))
        url = self.get_url('locations/{}'.format(habitat_number))
        res = self.session.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        eggs_div = soup.find('div', {'class': 'eggs'})
        eggs_span = eggs_div.findAll('span')
        for idx, egg_span in enumerate(eggs_span):
            span_text = egg_span.get_text()
            if dragon.get('egg_text') == span_text:
                egg_url = 'https://dragcave.net{}'.format(egg_span.parent.find('a')['href'])
                print(egg_url)
                time.sleep(0.5)
                self.session.get(egg_url, headers={'referer': url})
                return True
        return False
