import csv
import os
from urllib.parse import urlparse

import requests


def scrape_item(story):
    try:
        item_url = f'https://hacker-news.firebaseio.com/v0/item/{story}.json?print=pretty'
        item_response = requests.get(item_url, timeout=180)
        item = item_response.json()
    except:
        return

    if not item:
        return
    item.pop('kids', None)
    fields = list(item.keys())
    if 'url' not in fields:
        fields.append('url')
        item['url'] = ''
    if 'text' not in fields:
        fields.append('text')
        item['text'] = ''

    fields.append('domain')
    item['domain'] = ''
    if item['url']:
        parsed_uri = urlparse(item['url'])
        domain = parsed_uri.netloc
        if domain.count('.') > 1:
            if domain.startswith(sub_domains):
                domain = domain.split('.', 1)[1]
        item['domain'] = domain
    return item


if __name__ == '__main__':
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)

    urls = {
        'top': 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty',
        'new': 'https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty',
        'ask': 'https://hacker-news.firebaseio.com/v0/askstories.json?print=pretty',
        'show': 'https://hacker-news.firebaseio.com/v0/showstories.json?print=pretty',
        'jobs': 'https://hacker-news.firebaseio.com/v0/jobstories.json?print=pretty',
    }

    sub_domains = ('www.', 'mail.', 'blog.', 'ns.', 'smtp.', 'webmail.', 'docs.', 'jobs.', 'cs.', 'apply.', 'boards.')

    for key, value in urls.items():
        print(f'Scraping {key}')

        try:
            response = requests.get(value, timeout=180)
            stories = response.json()
        except:
            continue

        items = []
        for story in stories[:30]:
            item = scrape_item(story)
            if item:
                print(item)
                items.append(item)

        if not items:
            continue

        with open(os.path.join(data_dir, f'{key}.csv'), 'w') as file:
            writer = csv.DictWriter(file, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)
