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

def cipd(root, ensure):
  args = [ 'cipd', 'ensure', '-root', root, '-ensure-file', '-' ]
  process = subprocess.Popen(args,
                             text=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
  stdout, stderr = process.communicate(input=ensure)
  if process.returncode != 0:
    print(stdout)
    print(stderr)
    raise ValueError('cipd failed.')

def read_var_from_deps(var):
  with open('src/DEPS', 'r') as file:
    content = file.read()
    prefix = f"'{var}': '"
    start = content.find(prefix) + len(prefix)
    end = content.find("'", start)
    return content[start:end]

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

  gn_version = read_var_from_deps('gn_version')
  cipd('src/buildtools/mac', 'gn/gn/mac-amd64 ' + gn_version)
  cipd('src/buildtools/win', 'gn/gn/windows-amd64 ' + gn_version)
  cipd('src/buildtools/linux64', 'gn/gn/linux-amd64 ' + gn_version)

  download_from_google_storage(
      'chromium-nodejs',
      sha_file='src/third_party/node/node_modules.tar.gz.sha1')

  download_from_google_storage(
      'chromium-nodejs/16.13.0',
      sha_file='src/third_party/node/mac/node-darwin-x64.tar.gz.sha1')
  download_from_google_storage(
      'chromium-nodejs/16.13.0',
      sha_file='src/third_party/node/mac/node-darwin-arm64.tar.gz.sha1')
  download_from_google_storage(
      'chromium-nodejs/16.13.0',
      sha_file='src/third_party/node/linux/node-linux-x64.tar.gz.sha1')
  download_from_google_storage(
      'chromium-nodejs/16.13.0',
      extract=False,
      sha_file='src/third_party/node/win/node.exe.sha1')

  download_from_google_storage(
      'chromium-fonts',
      sha_file='src/third_party/test_fonts/test_fonts.tar.gz.sha1')

  download_from_google_storage(
      'chromium-browser-clang',
      sha_file='src/tools/clang/dsymutil/bin/dsymutil.x64.sha1',
      extract=False,
      output='src/tools/clang/dsymutil/bin/dsymutil')

if __name__ == '__main__':
  main()
