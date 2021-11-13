import datetime as dt
import time

import requests

from bs4 import BeautifulSoup


def get_soup(url_):
    """

    :param url_: String, url for website
    :return: BeautifulSoup object if successful request else None
    """
    res = requests.get(url_, headers={'User-Agent': 'Mozilla/5.0'})
    if res.status_code == 200:
        return BeautifulSoup(res.content, 'lxml')


srcs = {
    'ap': {
        'url': 'https://apnews.com',
        'base_url': 'https://apnews.com',  # href links to articles are relative
        'parsers': {
            'links': lambda s: [a.attrs['href']
                                for a in s.find('div', {'data-key': 'main-story'}).find_all('a')
                                if a.attrs['href'][:9] == '/article/'],
            'header': lambda s: s.find('a', {'data-key': 'card-headline'}).text.strip(),
            'title': lambda s: s.find('h1').text.strip(),
            'article': [
                lambda ar: ar.find('div', {'data-key': 'article'}).find_all('p'),
                lambda ar: ar
            ],
            'content': lambda s: ' '.join([p.text.strip() for p in s.find_all('p')])
        }
    },
    'fox': {
        'url': 'https://www.foxnews.com',
        'base_url': '',
        'parsers': {
            'links': lambda s: [a.attrs['href']
                                for a in s.find('div', {'class': 'main main-primary js-river'})\
                                .find_all('a')
                                if 'https://www.foxnews.com' in a.attrs['href'] and\
                                a.attrs['href'].count('/') >= 4],
            'header': lambda s: s.find('h2', {'class': 'title title-color-default'}).text.strip(),
            'title': lambda s: s.find('h1', {'class': 'headline'}).text.strip(),
            'content': lambda s: ' '.join([p.text.strip()
                                           for p in s.find('div', {'class': 'article-body'}).find_all('p')
                                           if not p.find('strong')])
        }
    }
}

if __name__ == "__main__":
    articles = []
    for src in srcs:
        soup = get_soup(srcs[src]['url'])
        urls = set(srcs[src]['parsers']['links'](soup))

        for url in urls:
            full_url = srcs[src]['base_url'] + url
            article_soup = get_soup(full_url)

            article = {
                'source': src,
                'url': full_url,
                'date_scraped': dt.datetime.now(),
                'title': article_soup.find('h1').text.strip(),
                'content': srcs[src]['parsers']['content'](article_soup),
            }
            time.sleep(1)
