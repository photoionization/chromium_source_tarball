#!/usr/bin/env python3

import feedparser
import re
import sys

from datetime import datetime, timedelta

def find_versions(content):
  return re.findall(r'\d+\.\d+\.\d+\.\d+', content)

def get_versions_in_last_25_hours(feed_url):
  feed = feedparser.parse(feed_url)
  twenty_four_hours_ago = datetime.now() - timedelta(hours=25)

  version_numbers = []
  for entry in reversed(feed.entries):
    published = datetime(*entry.published_parsed[:6])
    if published > twenty_four_hours_ago:
      version_numbers.extend(find_versions(entry.content[0].value))

  return sorted(set(version_numbers), reverse=True)

def main():
  feed_url = 'http://googlechromereleases.blogspot.com/atom.xml'
  versions = get_versions_in_last_25_hours(feed_url)
  print(' '.join(versions[:3]))

if __name__ == "__main__":
  main()
