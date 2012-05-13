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
import sys

def handle_options(options, args):
  """Called by bootstrapper to process global commandline options."""
  import logging
  if options.verbose >= 2:
    logging.basicConfig(level=logging.DEBUG)
  elif options.verbose:
    logging.basicConfig(level=logging.INFO)
  else:
    logging.basicConfig(level=logging.WARNING)

def main(main_name):
  """The main entry point to the bootstrapper. Call this with the module name to
  use as your main app."""
  mod = __import__(main_name, {}, {}, True)
  import optparse
  parser = optparse.OptionParser(usage=mod.main_usage())
  parser.add_option('--curses', action="store_true", dest="curses", help="Use curses UI")
  parser.add_option('--objc', action="store_true", dest="objc", help="Enable objc support")
  parser.add_option(
      '-v', '--verbose', action='count', default=0,
      help='Increase verbosity level (repeat as needed)')
  original_parse_args = parser.parse_args
  def parse_args_shim():
    options, args = original_parse_args()
    handle_options(options, args)
    return options, args
  parser.parse_args = parse_args_shim

  sys.exit(mod.main(parser))
