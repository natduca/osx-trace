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

# This file manages the downloading and compiling of the core
# osx trace utility.
import os
import platform
import shlex
import subprocess
import urllib2
from exceptions import *

class Trace(object):
  def __init__(self, libutil, build_dir, verbose=False):
    if not platform.platform().startswith("Darwin"):
      raise Exception("Only supported on OSX.")

    self.build_dir = build_dir

    # Sanity check: does cc exist?
    if not os.path.exists("/usr/bin/cc"):
      raise CompilerNeededException()

    base = "/"

    # look the result in build dir
    if not os.path.exists(os.path.join(build_dir, "trace", "trace")):
      self._download_and_compile(libutil, verbose)
      self.did_compile = True
    else:
      self.did_compile = False
    assert os.path.exists(os.path.join(build_dir, "trace", "trace"))
    assert os.path.exists(os.path.join(build_dir, "trace.codes"))

  def _download_and_compile(self, libutil, verbose=False):

    if verbose:
      print "Downloading trace utility..."

    # Download trace file
    trace_c_url = "http://opensource.apple.com/source/system_cmds/system_cmds-541/trace.tproj/trace.c?txt"
    trace_path = os.path.join(self.build_dir, "trace")
    if not os.path.exists(trace_path):
      os.mkdir(trace_path)

    trace_c_file = os.path.join(self.build_dir, "trace", "trace.c")
    trace_o_file = os.path.join(self.build_dir, "trace", "trace.o")
    trace_executable_file = os.path.join(self.build_dir, "trace", "trace")

    req = urllib2.urlopen(trace_c_url)
    f = open(trace_c_file, 'w')
    f.write(req.read())
    f.close()
    req.close()


    # Download un-stripped kdebug.h
    if platform.mac_ver()[0].startswith('10.6'):
      kdebug_h_url = "http://www.opensource.apple.com/source/xnu/xnu-1504.15.3/bsd/sys/kdebug.h?txt"
    elif platform.mac_ver()[0].startswith('10.7'):
      kdebug_h_url = "http://www.opensource.apple.com/source/xnu/xnu-1699.24.23/bsd/sys/kdebug.h?txt"
    else:
      raise Exception("Unrecognized OSX version: %s" % platform.mac_ver())
    kdebug_h_path = os.path.join(self.build_dir, "kdebug", "sys")
    kdebug_h_include_path = os.path.join(self.build_dir, "kdebug")
    if not os.path.exists(kdebug_h_path):
      os.makedirs(kdebug_h_path)
    kdebug_h_file = os.path.join(kdebug_h_path, "kdebug.h")

    req = urllib2.urlopen(kdebug_h_url)
    f = open(kdebug_h_file, 'w')
    f.write(req.read())
    f.close()
    req.close()

    # Download trace.codes
    codes_url = "http://www.opensource.apple.com/source/xnu/xnu-1699.24.23/bsd/kern/trace.codes?txt"
    codes_file = os.path.join(self.build_dir, "trace.codes")
    req = urllib2.urlopen(codes_url)
    f = open(codes_file, 'w')
    f.write(req.read())
    f.close()
    req.close()

    # Compile trace
    if verbose:
      print "Compiling trace utility..."

    # cc
    args = ["/usr/bin/cc",
            "-arch", "x86_64",
            "-arch", "i386",
            "-Os",
            "-I%s" % kdebug_h_include_path,
            "-I%s" % libutil.include_path,
            "-DPRIVATE",
            "-D__APPLE_API_PRIVATE",
            "-c",
            "-o", trace_o_file,
            trace_c_file
            ]
    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    p.communicate()
    assert p.returncode == 0

    # link
    args = ["/usr/bin/cc",
            "-arch", "x86_64",
            "-arch", "i386",
            "-Os",
            "-L%s" % libutil.link_path,
            "-lutil",
            "-o", trace_executable_file,
            trace_o_file
            ]
    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    p.communicate()
    assert p.returncode == 0

  def system(self, cmd):
    args = shlex.split(cmd)
    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()
    return p.returncode

  def executable(self):
    return os.path.join(build_dir, "trace", "trace")

  def codes(self):
    return os.path.join(build_dir, "trace.codes")

