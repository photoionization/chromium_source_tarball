#!/usr/bin/env python3

import argparse
import feedparser

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('search_string',
                      help='String to search in article titles and summaries')
  args = parser.parse_args()

  rss_url = 'http://googlechromereleases.blogspot.com/atom.xml'
  feed = feedparser.parse(rss_url)

  matching_article = None
  for entry in reversed(feed.entries):
    if args.search_string in entry.title or \
       args.search_string in entry.summary:
      matching_article = entry
      break

  if matching_article:
    print(matching_article.content[0].value)
  else:
    print('No release notes.')

if __name__ == '__main__':
    main()
