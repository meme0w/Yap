import time
from pip._vendor import requests
from bs4 import BeautifulSoup
from queue import Queue
import threading

def time_news():
    ret = requests.get("https://time.com/section/world/")
    retdata = ret.text
    soup = BeautifulSoup(retdata, features="html.parser")

    if not soup:
        exit(0)

    news_list = []

    container = soup.find('div', class_='section-related__touts-wrapper')
    if container is not None:
        for news in container.find_all('div', class_='taxonomy-tout'):
            h2_element = news.find('h2', class_='headline')
            h2_text = h2_element.text.strip() if h2_element is not None else ''

            h3_element = news.find('h3', class_='summary')
            h3_text = h3_element.text.strip() if h3_element is not None else ''

            byline_element = news.find('span', class_='byline')
            byline_text = byline_element.text.strip() if byline_element is not None else ''

            news_list.append({
                'site_name': "time.com",
                'title': h2_text,
                'description': h3_text,
                'byline': byline_text
            })
    return news_list

def nytimes_news():
    ret = requests.get("https://www.nytimes.com/section/world")
    retdata = ret.text
    soup = BeautifulSoup(retdata, features="html.parser")

    if not soup:
        exit(0)
    news_list = []
    for article in soup.find_all('article', class_='css-1l4spti'):
        title = article.find('h3', class_='css-1kv6qi e15t083i0')
        title = title.text.strip() if title else ''

        description = article.find('p', class_='css-1pga48a e15t083i1')
        description = description.text.strip() if description else ''

        author = article.find_all('span', class_='css-1n7hynb')
        author = ', '.join([a.text.strip() for a in author]) if author else ''
        news_list.append({
            'site_name': "nytimes.com",
            'title': title,
            'description': description,
            'byline': author
        })
    return news_list


def secret_tink_news():
    ret = requests.get("https://secrets.tinkoff.ru/novosti/?internal_source=header-novosti")
    retdata = ret.text
    soup = BeautifulSoup(retdata, features="html.parser")

    if not soup:
        exit(0)
    news_list = []
    for article in soup.find_all('article', class_='Preview_tertiary Preview_day'):
        title = article.find('div', class_='Preview_title')
        description = article.find('p', class_='Preview_description')
        date = article.find('time', class_='DateTime_datetime')
        tags = article.find_all('span', class_='ClickableText_label')

        title = title.text.strip() if title else ''
        description = description.text.strip() if description else ''
        date = date.text.strip() if date else ''
        tags = [tag.text for tag in tags] if tags else []

        news_list.append({
            'site_name': "secrets.tinkoff.ru",
            'title': title,
            'description': description,
            'byline': date + ', ' + ', '.join(tags)
        })
    return news_list


class NewsCollector:
    def __init__(self, agency_name, url, parse_method, refresh_rate=60):
        self.agency_name = agency_name
        self.url = url
        self.parse_method = parse_method
        self.refresh_rate = refresh_rate
        self.news_queue = Queue()
        self.stop_signal = False
        self.displayed_news = set()

    def collect_news(self):
        return self.parse_method()

    def background_task(self):
        while not self.stop_signal:
            news = self.collect_news()
            for i in news:
                self.news_queue.put(i)
            time.sleep(self.refresh_rate)

    def start(self):
        background_thread = threading.Thread(target=self.background_task, daemon=True)
        background_thread.start()

def print_news(collectors):
    displayed_news = set()
    try:
        while True:
            for collector in collectors:
                while not collector.news_queue.empty():
                    a = collector.news_queue.get()
                    if a['title'] not in displayed_news:
                        displayed_news.add(a['title'])
                        print("\033[1m" + a['site_name'].center(50) + "\033[0m")
                        print("\033[1m" + "Заголовок: " + "\033[0m" + a['title'])
                        print("\033[1m" + "Описание: " + "\033[0m" + a.get('description', ''))
                        print("\033[1m" + "Метка публикации: " + "\033[0m" + a.get('byline', ''))
                        print("-" * 50)
                        print(flush=True)
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        for collector in collectors:
            collector.stop_signal = True

if __name__ == '__main__':
    agencies = [
        {
            'url': 'https://time.com/section/world/',
            'parse_method': time_news
        },
        {
            'url': 'https://www.nytimes.com/section/world',
            'parse_method': nytimes_news
        },
        {
            'url': 'https://secrets.tinkoff.ru/novosti/?internal_source=header-novosti',
            'parse_method': secret_tink_news
        }
    ]

    collectors = []
    for agency in agencies:
        collector = NewsCollector(agency_name=agency['url'], url=agency['url'], parse_method=agency['parse_method'])
        collectors.append(collector)
        collector.start()

    print_news(collectors)