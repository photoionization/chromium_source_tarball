#!/usr/bin/env python3

import feedparser
import re
import sys

from datetime import datetime, timedelta

def find_version(content):
  versions = re.findall(r'(?<![.?\d])\d+\.\d+\.\d+\.\d+(?![.?\d])', content)
  if len(versions) > 0:
    return versions[0]
  else:
    return None

def get_versions_in_last_25_hours(feed_url):
  feed = feedparser.parse(feed_url)
  one_day_ago = datetime.now() - timedelta(hours=25)

  version_numbers = []
  for entry in feed.entries:
    published = datetime(*entry.published_parsed[:6])
    if published <= one_day_ago:
      break
    if not 'Desktop' in entry.title:
      continue
    version = find_version(entry.content[0].value)
    if version:
      version_numbers.append(version)

  return version_numbers

def main():
  feed_url = 'http://googlechromereleases.blogspot.com/atom.xml'
  versions = get_versions_in_last_25_hours(feed_url)
  print(' '.join(versions[:3]))

if __name__ == "__main__":
  main()
