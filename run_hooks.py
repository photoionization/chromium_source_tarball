#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import urllib.request

from checkout import add_depot_tools_to_path, current_os

def download_from_google_storage(
    bucket, sha_file=None, sha1=None, extract=True, output=None):
  args = [ sys.executable,
           'src/third_party/depot_tools/download_from_google_storage.py',
           '--no_resume', '--no_auth',
           '--bucket', bucket ]
  if sha1:
    args += [ sha1 ]
  if sha_file:
    args += [ '-s', sha_file ]
  if extract:
    args += [ '--extract' ]
  if output:
    args += [ '-o', output ]
  subprocess.check_call(args)

def download_to(url, target):
  if not os.path.exists(target):
    urllib.request.urlretrieve(url, target)

def main():
  parser = argparse.ArgumentParser(description='Checkout Chromium source code')
  parser.add_argument('--target-os', default=current_os(),
                      help='Target operating system (win, mac, or linux)')
  args = parser.parse_args()

  add_depot_tools_to_path()

  subprocess.check_call([ sys.executable,
                          'src/build/util/lastchange.py',
                          '-o',
                          'src/build/util/LASTCHANGE' ])
  subprocess.check_call([ sys.executable,
                          'src/build/util/lastchange.py',
                          '-s', 'src/third_party/dawn',
                          '--revision', 'src/gpu/webgpu/DAWN_VERSION' ])

  download_from_google_storage(
      'chromium-nodejs',
      sha_file='src/third_party/node/node_modules.tar.gz.sha1')
  if args.target_os == 'mac':
    download_to('https://chrome-infra-packages.appspot.com/dl/gn/gn/mac-amd64/+/latest',
                'src/buildtools/mac/gn')
    download_from_google_storage(
        'chromium-nodejs/16.13.0',
        sha_file='src/third_party/node/mac/node-darwin-x64.tar.gz.sha1')
    download_from_google_storage(
        'chromium-nodejs/16.13.0',
        sha_file='src/third_party/node/mac/node-darwin-arm64.tar.gz.sha1')
    download_from_google_storage(
        'chromium-browser-clang',
        sha_file='src/tools/clang/dsymutil/bin/dsymutil.x64.sha1',
        extract=False,
        output='src/tools/clang/dsymutil/bin/dsymutil')
  else:
    download_to('https://chrome-infra-packages.appspot.com/dl/gn/gn/linux-amd64/+/latest',
                'src/buildtools/linux64/gn')
    download_from_google_storage(
        'chromium-nodejs/16.13.0',
        sha_file='src/third_party/node/linux/node-linux-x64.tar.gz.sha1')
  if args.target_os == 'win':
    download_to('https://chrome-infra-packages.appspot.com/dl/gn/gn/windows-amd64/+/latest',
                'src/buildtools/win/gn.exe')
    download_from_google_storage(
        'chromium-nodejs/16.13.0',
        sha_file='src/third_party/node/win/node.exe.sha1')

if __name__ == '__main__':
  main()
