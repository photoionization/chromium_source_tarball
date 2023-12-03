#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_URL = 'https://chromium.googlesource.com/chromium/src.git'

def current_os():
  if sys.platform.startswith('linux'):
    return 'linux'
  elif sys.platform.startswith('win'):
    return 'win'
  elif sys.platform == 'darwin':
    return 'mac'
  else:
    raise ValueError(f'Unsupported platform: {sys.platform}')

def add_depot_tools_to_path():
  depot_tools_path = os.path.join(ROOT_DIR, 'vendor', 'depot_tools')
  os.environ['DEPOT_TOOLS_UPDATE'] = '0'
  os.environ['PATH'] = depot_tools_path + os.pathsep + os.environ['PATH']

def main():
  parser = argparse.ArgumentParser(description='Checkout Chromium source code')
  parser.add_argument('--target-os', default=current_os(),
                      help='Target operating system (win, mac, or linux)')
  parser.add_argument('--revision',
                      help='The revision to checkout')
  args = parser.parse_args()

  if os.path.exists('src'):
    print('The src dir already exists.')
    return 1

  # The source tarball is usually built on Linux machines.
  target_os = [ args.target_os ]
  if args.target_os == 'win':
    target_os += [ 'linux' ]

  add_depot_tools_to_path()

  # Write .gclient file.
  if args.revision:
    src = f'{SRC_URL}@{args.revision}'
  else:
    src = SRC_URL
  subprocess.check_call([ 'gclient', 'config', '--name', 'src', src ])
  with open(os.path.join('.gclient'), 'a') as f:
    joined = '", "'.join(target_os)
    f.write(f'target_os = [ "{joined}" ]\n')

  # Checkout code.
  subprocess.check_call([ 'gclient', 'sync', '--nohooks', '--no-history' ])

  # Execute some necessary hook steps.
  subprocess.check_call([ sys.executable,
                          os.path.join(ROOT_DIR, 'run_hooks.py') ])

if __name__ == '__main__':
  main()
