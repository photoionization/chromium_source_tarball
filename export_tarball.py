#!/usr/bin/env python3
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
This tool creates a tarball with all the sources, but without .git directories.

It can also remove files which are not strictly required for build, so that
the resulting tarball can be reasonably small (last time it was ~110 MB).

Example usage:

export_tarball.py /foo/bar

The above will create file /foo/bar.tar.xz.
"""

import lzma
import optparse
import os
import subprocess
import sys
import tarfile


NONESSENTIAL_DIRS = {
    'android_webview',
    'buildtools/reclient',
    'chrome/android',
    'chrome/browser/ui/android',
    'chromecast',
    'infra',
    'ios',
    'ios_internal',
    'native_client',
    'native_client_sdk',
    'third_party/android_platform',
    'third_party/apache-linux',
    'third_party/apache-mac',
    'third_party/apache-mac-arm64',
    'third_party/apache-windows-arm64',
    'third_party/angle/third_party/VK-GL-CTS/src/android',
    'third_party/angle/third_party/VK-GL-CTS/src/external',
    'third_party/catapult/third_party/vinn/third_party',
    'third_party/closure_compiler',
    'third_party/blink/manual_tests',
    'third_party/blink/perf_tests',
    'third_party/blink/tools',
    'third_party/blink/web_tests',
    'third_party/dawn/third_party/khronos/OpenGL-Registry/specs',
    'third_party/dawn/third_party/dxc/tools',
    'third_party/dawn/tools',
    'third_party/hunspell_dictionaries',
    'third_party/hunspell/tests',
    'third_party/jdk/current',
    'third_party/jdk/extras',
    'third_party/liblouis/src/tests/braille-specs',
    'third_party/swift-toolchain/',
    'third_party/swiftshader/third_party/llvm-10.0',
    'third_party/swiftshader/third_party/llvm-16.0',
    'third_party/xdg-utils/tests',
    'v8/test',
}

ESSENTIAL_FILES = (
    'chrome/test/data/webui/i18n_process_css_test.html',
    'chrome/test/data/webui/mojo/foobar.mojom',

    # TODO(rockot): Remove this once web_ui_test.mojom is no longer in the
    # chrome/test directory (https://crbug.com/926270).
    'chrome/test/data/webui/web_ui_test.mojom',

    # Allows the orchestrator_all target to work with gn gen
    'v8/test/torque/test-torque.tq',
)

ESSENTIAL_GIT_DIRS = (
    # The .git subdirs in the Rust checkout need to exist to build rustc.
    'third_party/rust-src/',)

TEST_DIRS = {
    'chrome/test/data',
    'components/test/data',
    'courgette/testdata',
    'extensions/test/data',
    'media/test/data',
    'native_client/src/trusted/service_runtime/testdata',
    'third_party/breakpad/breakpad/src/processor/testdata',
    'third_party/catapult/tracing/test_data',
    'third_party/dawn/test',
    'third_party/dawn/third_party/dxc/test',
    'third_party/swiftshader/tests',
    'tools/perf/testdata',
}


# Workaround lack of the exclude parameter in add method in python-2.4.
# TODO(phajdan.jr): remove the workaround when it's not needed on the bot.
class MyTarFile(tarfile.TarFile):
  def set_remove_nonessential_files(self, remove):
    # pylint: disable=attribute-defined-outside-init
    self.__remove_nonessential_files = remove

  def set_verbose(self, verbose):
    # pylint: disable=attribute-defined-outside-init
    self.__verbose = verbose

  def set_progress(self, progress):
    # pylint: disable=attribute-defined-outside-init
    self.__progress = progress
    self.__count = 0

  def set_src_dir(self, src_dir):
    # pylint: disable=attribute-defined-outside-init
    self.__src_dir = src_dir

  def __report_skipped(self, name):
    if self.__verbose:
      print('D\t%s' % name)

  def __report_added(self, name):
    self.__count += 1
    if (self.__count + 1) % 1000 == 0:
      print('.', end='', flush=True)
    if self.__verbose:
      print('A\t%s' % name)

  # pylint: disable=redefined-builtin
  def add(self, name, arcname=None, recursive=True, *, filter=None):
    rel_name = os.path.relpath(name, self.__src_dir)
    _, file_name = os.path.split(name)

    if file_name in ('.svn', 'out'):
      self.__report_skipped(name)
      return

    if file_name == '.git':
      if not any(
          rel_name.startswith(essential) for essential in ESSENTIAL_GIT_DIRS):
        self.__report_skipped(name)
        return

    if self.__remove_nonessential_files:
      # WebKit change logs take quite a lot of space. This saves ~10 MB
      # in a bzip2-compressed tarball.
      if 'ChangeLog' in name:
        self.__report_skipped(name)
        return

      # Preserve GYP/GN files, and other potentially critical files, so that
      # build/gyp_chromium / gn gen can work.
      #
      # Preserve `*.pydeps` files too. `gn gen` reads them to generate build
      # targets, even if those targets themselves are not built
      # (crbug.com/1362021).
      keep_file = ('.gyp' in file_name or '.gn' in file_name or
                   '.isolate' in file_name or '.grd' in file_name or
                   file_name.endswith('.pydeps') or rel_name in ESSENTIAL_FILES)

      # Remove contents of non-essential directories.
      if not keep_file:
        for nonessential_dir in (NONESSENTIAL_DIRS | TEST_DIRS):
          if rel_name.startswith(nonessential_dir) and os.path.isfile(name):
            self.__report_skipped(name)
            return

    self.__report_added(name)
    tarfile.TarFile.add(self, name, arcname=arcname, recursive=recursive)


def main(argv):
  parser = optparse.OptionParser()
  parser.add_option('--basename')
  parser.add_option('--nonessential-files', action='store_true', default=False)
  parser.add_option('--test-data', action='store_true', default=False)
  parser.add_option('--verbose', action='store_true', default=False)
  parser.add_option('--progress', action='store_true', default=True)
  parser.add_option('--src-dir', default='src')

  options, args = parser.parse_args(argv)

  if len(args) != 1:
    print('You must provide only one argument: output file name')
    print('(without .tar.xz extension).')
    return 1

  if not os.path.exists(options.src_dir):
    print('Cannot find the src directory ' + options.src_dir)
    return 1

  output_fullname = args[0] + '.tar.xz'
  output_basename = options.basename or os.path.basename(args[0])

  archive = MyTarFile.open(output_fullname, 'w:xz',
                           preset=(9 | lzma.PRESET_EXTREME))
  archive.set_remove_nonessential_files(not options.nonessential_files)
  archive.set_verbose(options.verbose)
  archive.set_progress(options.progress)
  archive.set_src_dir(options.src_dir)
  try:
    if options.test_data:
      for directory in TEST_DIRS:
        test_dir = os.path.join(options.src_dir, directory)
        if not os.path.isdir(test_dir):
          # A directory may not exist depending on the milestone we're building
          # a tarball for.
          print('"%s" not present; skipping.' % test_dir)
          continue
        archive.add(test_dir,
                    arcname=os.path.join(output_basename, directory))
    else:
      archive.add(options.src_dir, arcname=output_basename)
  finally:
    archive.close()

  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
