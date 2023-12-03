#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

from checkout import ROOT_DIR, add_depot_tools_to_path, current_os

def download_from_google_storage(bucket, sha):
  subprocess.check_call([
      sys.executable,
      'src/third_party/depot_tools/download_from_google_storage.py',
      '--no_resume', '--extract', '--no_auth',
      '--bucket', bucket,
      '-s', sha ])

def main():
  parser = argparse.ArgumentParser(description='Checkout Chromium source code')
  parser.add_argument('--target-os', default=current_os(),
                      help='Target operating system (win, mac, or linux)')
  args = parser.parse_args()

  add_depot_tools_to_path()

  subprocess.check_call([
      sys.executable,
      os.path.join(ROOT_DIR, 'src/build/util/lastchange.py'),
      '-o',
      os.path.join(ROOT_DIR, 'src/build/util/LASTCHANGE') ])

  download_from_google_storage(
      'chromium-nodejs/16.13.0',
      'src/third_party/node/linux/node-linux-x64.tar.gz.sha1')
  if args.target_os == 'mac':
    download_from_google_storage(
        'chromium-nodejs/16.13.0',
        'src/third_party/node/mac/node-darwin-x64.tar.gz.sha1')
    download_from_google_storage(
        'chromium-nodejs/16.13.0',
        'src/third_party/node/mac/node-darwin-arm64.tar.gz.sha1')
  elif args.target_os == 'win':
    download_from_google_storage(
        'chromium-nodejs/16.13.0',
        'src/third_party/node/win/node.exe.sha1')

if __name__ == '__main__':
  main()
