#!/usr/bin/env python3

import os
import subprocess
import sys
import urllib.request

from checkout import add_depot_tools_to_path

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

def main():
  add_depot_tools_to_path()

  subprocess.check_call([ sys.executable,
                          'src/build/util/lastchange.py',
                          '-o',
                          'src/build/util/LASTCHANGE' ])
  subprocess.check_call([ sys.executable,
                          'src/build/util/lastchange.py',
                          '-m', 'GPU_LISTS_VERSION',
                          '--revision-id-only',
                          '--header', 'src/gpu/config/gpu_lists_version.h' ])
  subprocess.check_call([ sys.executable,
                          'src/build/util/lastchange.py',
                          '-m', 'SKIA_COMMIT_HASH',
                          '-s', 'src/third_party/skia',
                          '--header', 'src/skia/ext/skia_commit_hash.h' ])
  subprocess.check_call([ sys.executable,
                          'src/build/util/lastchange.py',
                          '-s', 'src/third_party/dawn',
                          '--revision', 'src/gpu/webgpu/DAWN_VERSION' ])
  download_from_google_storage(
      'chromium-nodejs',
      sha_file='src/third_party/node/node_modules.tar.gz.sha1')
  download_from_google_storage(
      'chromium-fonts',
      sha_file='src/third_party/test_fonts/test_fonts.tar.gz.sha1')

if __name__ == '__main__':
  main()
