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
import tempfile
import trace
import libutil
import re
import sys
import os
import subprocess

# Once you've done this:
#  trace -t -R raw_trace -o text_trace trace.codes
def create_trace_cmd(options):
  """Creates the trace cmd used for operations within this module."""
  root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
  cache_dir = os.path.join(root, ".cache")
  if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)

  if not os.path.exists("/usr/bin/cc"):
    sys.stderror.write("No compiler found. Install XCode and try again.\n")
    sys.exit(255)

  u = libutil.LibUtil(cache_dir, verbose=True)
  return trace.Trace(u, cache_dir, verbose=True)

def CMDrecord(parser):
  """Records a kernel trace"""
  options, args = parser.parse_args()
  if len(args) != 1:
    sys.stderr.write("Required: name of trace file to record into.\n")
    return 255
  trace_cmd = create_trace_cmd(options)
  trace_cmd.call(["-r"], sudo=True) # We dont care about the return value here.
  try:
    rawfile = tempfile.NamedTemporaryFile()
    rawfile_name = rawfile.name
    sys.stderr.write("Press Ctrl-c to stop tracing...")
    sys.stderr.flush()
    try:
      ret = trace_cmd.call(["-L", rawfile_name], sudo=True)
      assert ret == 0
    except KeyboardInterrupt:
      pass
    sys.stderr.write("\n")
    if os.path.exists(args[0]):
      trace_cmd.rawcall(["/usr/bin/sudo", "rm", "%s" % args[0]])
    if os.path.exists(args[0]):
      sys.stderr.write("%s already exists. Cannot overwrite.\n" % args[0])
      return 255

    sys.stderr.write("Converting to text...")
    sys.stderr.flush()
    ret = trace_cmd.call(["-t", "-R", rawfile_name, "-o", args[0], trace_cmd.codes_file], sudo=True)

    # chmod the file to be the umask of the current user
    # and owned by the current user/group
    umask = os.umask(7); os.umask(umask)
    ret = trace_cmd.rawcall(["/usr/bin/sudo", "chmod", oct(0777 & ~umask), args[0]])
    assert ret == 0
    trace_cmd.rawcall(["/usr/bin/sudo", "chown", str(os.getuid()), args[0]])
    trace_cmd.rawcall(["/usr/bin/sudo", "chgrp", str(os.getgid()), args[0]])

    assert ret == 0
    sys.stderr.write("\n")

  finally:
    rawfile.close()

  if os.path.exists(rawfile_name):
    os.unlink(rawfile_name)
  return 0

def Command(name):
  return getattr(sys.modules[__name__], 'CMD' + name, None)

def CMDhelp(parser):
  """Print list of commands or help for a specific command"""
  _, args = parser.parse_args()
  if len(args) == 1:
    sys.argv = [args[0], '--help']
    GenUsage(parser, 'help')
    return CMDhelp(parser)
  # Do it late so all commands are listed.
  parser.print_help()
  return 0


def GenUsage(parser, command):
  """Modify an OptParse object with the function's documentation."""
  obj = Command(command)
  more = getattr(obj, 'usage_more', '')
  if command == 'help':
    command = '<command>'
  else:
    # OptParser.description prefer nicely non-formatted strings.
    parser.description = re.sub('[\r\n ]{2,}', ' ', obj.__doc__)
  parser.set_usage('usage: %%prog %s [options] %s' % (command, more))

def getdoc(x):
  if getattr(x, '__doc__'):
    return x.__doc__
  return '<Missing docstring>'

def main_usage():
  return "Usage: osx-trace [global options] <command> [command arguments]"

def main(parser):
  """Doesn't parse the arguments here, just find the right subcommand to
  execute."""
  # Create the option parse and add --verbose support.
  old_parser_args = parser.parse_args
  def parse():
    options, args = old_parser_args()
    return options, args
  parser.parse_args = parse

  non_switch_args = [i for i in sys.argv[1:] if not i.startswith('-')]
  if non_switch_args:
    command = Command(non_switch_args[0])
    if command:
      if non_switch_args[0] == 'help':
        CMDhelp.usage_more = ('\n\nCommands are:\n' + '\n'.join([
              '  %-10s %s' % (fn[3:], getdoc(Command(fn[3:])).split('\n')[0].strip())
              for fn in dir(sys.modules[__name__]) if fn.startswith('CMD')]))

      # "fix" the usage and the description now that we know the subcommand.
      GenUsage(parser, non_switch_args[0])
      new_args = list(sys.argv[1:])
      new_args.remove(non_switch_args[0])
      new_args.insert(0, sys.argv[0])
      sys.argv = new_args
      return command(parser)
    else:
      # Not a known command. Default to help.
      print "Unrecognized command: %s\n" % non_switch_args[0]
  else: # default command
    CMDhelp.usage_more = ('\n\nCommands are:\n' + '\n'.join([
          '  %-10s %s' % (fn[3:], getdoc(Command(fn[3:])).split('\n')[0].strip())
          for fn in dir(sys.modules[__name__]) if fn.startswith('CMD')]))
    GenUsage(parser, 'help')
    return CMDhelp(parser)

