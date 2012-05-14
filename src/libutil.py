# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import platform
import shlex
import subprocess
import urllib2
import sys

from exceptions import *

class LibUtil(object):
  def __init__(self, cache_dir, verbose=False):
    if not platform.platform().startswith("Darwin"):
      raise Exception("Only supported on OSX.")

    self.cache_dir = cache_dir

    # Sanity check: are we on a platform we understand?
    if platform.mac_ver()[0].startswith('10.6'):
      self.ver = 21
    elif platform.mac_ver()[0].startswith('10.7'):
      self.ver = 25
    else:
      raise Exception("Unrecognized OSX version: %s" % platform.mac_ver())

    # Sanity check: does cc exist?
    if not os.path.exists("/usr/bin/cc"):
      raise CompilerNeededException()

    # look the result in build dir
    if not os.path.exists(os.path.join(cache_dir, "libutil-%s" % self.ver, "libutil1.0.dylib")):
      self._download_and_compile(verbose)
      self.did_compile = True
    else:
      self.did_compile = False
    assert os.path.exists(os.path.join(cache_dir, "libutil-%s" % self.ver, "libutil1.0.dylib"))

  def _download_and_compile(self, verbose=False):
    if verbose:
      sys.stderr.write("Downloading libUtil...\n")

    # Download
    req = urllib2.urlopen('http://opensource.apple.com/tarballs/libutil/libutil-%s.tar.gz' % self.ver)
    tarfilename = os.path.join(self.cache_dir, 'libutil-%s.tar.gz' % self.ver)
    f = open(tarfilename, 'w')
    f.write(req.read())
    f.close()
    req.close()

    # Untar
    if verbose:
      sys.stderr.write("Extracting libUtil...\n")

    oldcwd = os.getcwd()
    try:
      os.chdir(os.path.dirname(tarfilename))
      ret = self._system('tar xfz %s' % tarfilename)
      assert ret == 0
    finally:
      os.chdir(oldcwd)
    os.unlink(tarfilename)

    # Compile
    if verbose:
      sys.stderr.write("Compiling libUtil...\n")
    folder_name = os.path.join(self.cache_dir, "libutil-%s" % self.ver)
    assert os.path.exists(os.path.join(folder_name, "Makefile"))
    oldcwd = os.getcwd()
    try:
      os.chdir(folder_name)
      self._system("make")
    finally:
      os.chdir(oldcwd)

  def _system(self, cmd):
    args = shlex.split(cmd)
    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()
    return p.returncode

  @property
  def include_path(self):
    return os.path.join(self.cache_dir, "libutil-%s" % self.ver)

  @property
  def link_path(self):
    return os.path.join(self.cache_dir, "libutil-%s" % self.ver)
