
import requests
import socket
import settings
import json
import time
import logging
import math
import textwrap

from lxml import html


FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
log = logging.getLogger(__name__)


class WorkerException(Exception):
    pass


class BasicUserParseWorker(object):

    """
    Given a username url, this worker finds all posts for that user and formats them
    """

    original_target = None

    to_crawl = []
    crawled = []
    max_links = 10
    cur_links = 0
    link_delay = 0.25

    results = []

    def __init__(self, target):
        if target:
            self.to_crawl.append(target)
            self.original_target = target

        self.max_links = settings.WORKERS.get('max_links', 10)
        self.link_delay = settings.WORKERS.get('link_delay', 0.25)

    def run(self, training_label=None, local=False):

        log.debug('Running worker...')

        u_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        al = 'en-US,en;q=0.8'
        ae = 'gzip, deflate, sdch'
        cc = 'max-age=0'
        conn = 'keep-alive'

        headers = {
            'User-Agent': u_agent,
            'Accept': accept,
            'Accept-Language': al,
            'Accept-Encoding': ae,
            'Cache-Control': cc,
            'Connection': conn,
        }

        # for url in self.to_crawl:
        while self.to_crawl:
            url = self.to_crawl.pop(0)
            try:
                resp = requests.get(url, headers=headers)

                if resp.status_code != 200:
                    log.error('Non-200 HTTP Response Code: %s' % url)
                    raise IOError()

            except IOError:
                log.error('Could not get response from url (%s)' % url)
                raise WorkerException('Could not get response from %s' % url)

            self.cur_links += 1

            text = resp.text
            parse_results, next_page = self.parse_text(text, training_label=training_label)

            if parse_results:
                self.results += parse_results

            if next_page:
                self.add_links([next_page])

            self.crawled.append(url)
            time.sleep(self.link_delay)

        if local:
            return self.results, self.original_target
        else:
            log.debug('Woker job complete. Sending to Mother...')
            self.send_to_mother(self.results, self.original_target)

    def send_to_mother(self, data, original_target):
        log.debug('sending data to mother. Original target: %s' % original_target)

        address = settings.MOTHERSHIP.get('host', 'localhost')
        port = settings.MOTHERSHIP.get('port', 8080)

        addr = (address, port)

        sock = socket.socket()
        sock.connect(addr)

        data = {
            'data': data,
            'root': original_target
        }
        data_s = json.dumps(data)

        frames = textwrap.wrap(data_s, settings.BUFFER_SIZE)
        for frame in frames:
            sock.send(frame.encode('utf-8'))

        sock.close()

    def parse_text(self, text, training_label=None):
        """
        Parse the raw text from the link GET request
        NOTE: post_text can have multiple elements.
        NOTE: If the item is a user post there may not be a title or post_text

        :param text: Raw text from website (HTML, etc)
        :return: a list of posts in the form [(title, subreddit, post_text), ...]
        """
        page_tree = html.fromstring(text)
        table = page_tree.xpath('.//div[@class="PostList"]')[0]
        entries = table.xpath('.//div[contains(@class, "Post__content m-profile")]')

        results = []

        for entry in entries:
            title = ''.join(entry.xpath('.//a[contains(@class, "Post__titleLink")]/text()'))
            post_link = ''.join(entry.xpath('.//a[contains(@class, "Post__sourceLink")]/text()'))
            post_author = ''.join(entry.xpath('.//a[contains(@class, "Post__authorLink")]/text()'))
            subreddit = ''.join(entry.xpath('.//div[contains(@class, "Post__tagline")]/a[contains(@class, "Post__subredditLink")]/text()'))
            post_text = ''.join(entry.xpath('.//div[contains(@class, "Post__prominentComment")]/div/div/div[contains(@class, "md")]/p/text()'))

            results.append((title, subreddit, post_text, post_link, post_author, training_label))

        return results, 0

    def add_links(self, links):
        """
        Add the list of links to the 'to_crawl' list if they haven't been crawled already and if we haven't hit max
        links.
        :param links: list of strings (urls)
        :return:
        """
        links = list(set(links))
        [self.to_crawl.append(item) for item in links if item not in self.crawled and self.cur_links < self.max_links]
