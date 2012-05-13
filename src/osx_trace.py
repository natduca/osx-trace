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

# The things you need to for a trace on 10.6.8 are:
# download the util lib and build it
#  http://opensource.apple.com/source/libutil/libutil-21/
#  http://opensource.apple.com/tarballs/libutil/libutil-21.tar.gz
# download the bsd version of kdebug.h
#   http://www.opensource.apple.com/source/xnu/xnu-1504.15.3/bsd/sys/kdebug.h?txt
# download the (10.7.3!) trace app
#  http://opensource.apple.com/source/system_cmds/system_cmds-541/trace.tproj/
# build trace.app but:
#   point it at kdebug.h -DPRIVATE -D__APPLE_API_PRIVATE
#   /Developer/usr/bin/cc -arch x86_64 -arch i386 -g -Os -I/System/Library/Frameworks/System.framework/PrivateHeaders -I/System/Library/Frameworks/System.framework/PrivateHeaders/bsd -I./libutil-21 -I/tmp/UNTITLED_PROJECT/Build/UNTITLED_PROJECT -c -o /tmp/UNTITLED_PROJECT/Build/UNTITLED_PROJECT/trace.o trace.c/Developer/usr/bin/cc -arch x86_64 -arch i386 -arch ppc -g -Os -pipe -I/System/Library/Frameworks/System.framework/PrivateHeaders -I/System/Library/Frameworks/System.framework/PrivateHeaders/bsd -I./libutil-21 -I/tmp/UNTITLED_PROJECT/Build/UNTITLED_PROJECT -c -o trace.o trace.c
#   /Developer/usr/bin/cc -arch x86_64 -arch i386 -dead_strip -lutil 
# download the (10.7.3!) trace codes
#    http://www.opensource.apple.com/source/xnu/xnu-1699.24.23/bsd/kern/trace.codes


# URLs for 10.7.3:
# http://www.opensource.apple.com/tarballs/libutil/libutil-25.tar.gz
# http://www.opensource.apple.com/source/xnu/xnu-1699.24.23/bsd/sys/kdebug.h

# Once you've done this:
#  sudo trace -r  # reset
#  sudo trace -L raw_trace
#  trace -t -R raw_trace -o text_trace trace.codes

def main_usage():
  return "Kernel tracing utility for OSX"

def main(parser):
  print "Not implemented"
  return 255
