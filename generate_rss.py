"""Fetch only Naver Ads notice page 1; publish an append-only RSS feed."""
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = 'https://ads.naver.com/notice'
ROOT = Path(__file__).resolve().parent
STATE = ROOT / 'data' / 'notices.json'
SITE = ROOT / 'site'


class NoticeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = {}
        self.current = None
        self.in_title = False
        self.in_date = False
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            match = re.fullmatch(r'/notice/(\d+)(?:\?.*)?', attrs.get('href', ''))
            if match:
                self.current = {'id': match[1], 'title': '', 'source_date': ''}
        if self.current is not None:
            if tag == 'p' and 'post_title' in attrs.get('class', '').split():
                self.in_title = True
            if self.in_title and tag == 'span':
                self.skip += 1
            if tag == 'span' and 'date' in attrs.get('class', '').split():
                self.in_date = True

    def handle_data(self, data):
        if self.current is not None and self.in_title and not self.skip:
            self.current['title'] += data
        if self.current is not None and self.in_date:
            self.current['source_date'] += data

    def handle_endtag(self, tag):
        if tag == 'span':
            self.in_date = False
        if tag == 'span' and self.skip:
            self.skip -= 1
        if tag == 'p':
            self.in_title = False
        if tag == 'a' and self.current is not None:
            item = self.current
            item['title'] = ' '.join(item['title'].split())
            if item['title']:
                item['source_date'] = item['source_date'].strip()
                datetime.strptime(item['source_date'], '%Y-%m-%d')
                item['url'] = f"{SOURCE}/{item['id']}"
                self.items[item['id']] = item
            self.current = None
            self.in_title = False
            self.in_date = False
            self.skip = 0


def parse_notices(html):
    parser = NoticeParser()
    parser.feed(html)
    if not parser.items:
        raise ValueError('No notices found. Refusing to replace the existing feed.')
    return parser.items


def fetch():
    for attempt in range(3):
        try:
            request = Request(SOURCE, headers={'User-Agent': 'NaverAdsNoticeRSS/1.0', 'Accept': 'text/html'})
            with urlopen(request, timeout=45) as response:
                return response.read().decode('utf-8')
        except Exception:
            if attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))


def write_feed(items):
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    for name, value in [('title', '네이버 광고 공지사항'), ('link', SOURCE),
                        ('description', '첫 페이지에서 발견한 공지의 제목, URL, 원문 작성일'), ('language', 'ko')]:
        ET.SubElement(channel, name).text = value
    for item in reversed(list(items.values())):
        node = ET.SubElement(channel, 'item')
        ET.SubElement(node, 'title').text = item['title']
        ET.SubElement(node, 'link').text = item['url']
        ET.SubElement(node, 'guid', isPermaLink='true').text = item['url']
        source_date = item.get('source_date')
        if source_date:
            # The source provides a date only. Midnight KST is a conversion
            # convention, not the actual time the notice was published.
            published = datetime.strptime(source_date, '%Y-%m-%d').replace(
                tzinfo=timezone(timedelta(hours=9)))
            ET.SubElement(node, 'pubDate').text = format_datetime(published)
            ET.SubElement(node, 'description').text = f'작성일: {source_date}'
        else:
            # Do not misrepresent discovery time as an original publication date.
            ET.SubElement(node, 'description').text = '작성일: 확인되지 않음'
    ET.indent(rss)
    SITE.mkdir(exist_ok=True)
    ET.ElementTree(rss).write(SITE / 'rss.xml', encoding='utf-8', xml_declaration=True)
    (SITE / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>네이버 광고 공지 RSS</title><h1>네이버 광고 공지 RSS</h1><p><a href="rss.xml">RSS 피드</a></p>', encoding='utf-8')
    (SITE / '.nojekyll').touch()


def main():
    current = parse_notices(fetch())
    items = json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {}
    now = format_datetime(datetime.now(timezone.utc), usegmt=True)
    added = 0
    # Oldest first so the RSS displays the newest discovery first.
    for notice_id, item in reversed(list(current.items())):
        if notice_id not in items:
            items[notice_id] = {**item, 'discovered_at': now}
            added += 1
        else:
            # Backfill original dates without changing GUIDs or notice titles.
            items[notice_id]['source_date'] = item['source_date']
    write_feed(items)
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'First page: {len(current)} notices; new: {added}; retained: {len(items)}')


if __name__ == '__main__':
    main()
