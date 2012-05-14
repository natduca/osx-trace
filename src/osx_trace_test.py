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
import unittest
import osx_trace
import optparse
import os
import subprocess
import sys
import StringIO

from exceptions import *

class MockTrace(object):
  def __init__(self):
    self.reset()

  def reset(self):
    self._call_return_value = 0
    self._calls = []

  def call(self, args, sudo=False):
    self._calls.append((args, sudo))
    return self._call_return_value

  @property
  def calls(self):
    return self._calls

  def set_call_return_value(self, value):
    self._call_return_value = value

  @property
  def codes_file(self):
    return "trace.codes"

def osx_trace_main(*args):
  old_sys_argv = sys.argv
  old_sys_stdout = sys.stdout
  old_sys_stderr = sys.stderr
  try:
    sys.argv = [old_sys_argv[0]]
    sys.argv.extend(args)
    parser = optparse.OptionParser(usage=osx_trace.main_usage())
    sys.stdout = StringIO.StringIO()
    sys.stderr = sys.stdout
    return osx_trace.main(parser)
  finally:
    sys.argv = old_sys_argv
    sys.stdout = old_sys_stdout
    sys.stderr = old_sys_stderr

class OSXTraceTest(unittest.TestCase):
  def setUp(self):
    self._real_create_trace_cmd = osx_trace.create_trace_cmd

  def tearDown(self):
    osx_trace.create_trace_cmd = self._real_create_trace_cmd

  # Sanity check of the full script etc.
  def test_toplevel_script_smoketest(self):
    script = os.path.join(os.path.dirname(__file__), "../osx-trace")
    assert os.path.exists(script)

    p = subprocess.Popen([script, "help"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (stdout, stderr) = p.communicate()
    self.assertTrue(stdout.startswith("Usage: osx-trace <command> [options]"))

  def test_trace_but_cant_compile(self):
    osx_trace.create_trace_cmd = lambda x: CompilerNeededException()
    ret = osx_trace_main("record")
    assert ret != 0

  def test_record_empty(self):
    osx_trace.create_trace_cmd = lambda x: MockTrace()
    ret = osx_trace_main("record")
    assert ret != 0

  def test_record(self):
    trace = MockTrace()
    osx_trace.create_trace_cmd = lambda options: trace

    ret = osx_trace_main("record", "test.trace")
    assert ret == 0
    calls = trace.calls
    self.assertEquals(3, len(calls))

    self.assertTrue(calls[0][1]) # sudo
    self.assertEquals(["-r"], calls[0][0])

    self.assertTrue(calls[1][1]) # sudo
    self.assertEquals("-L", calls[1][0][0])
    self.assertEquals(2, len(calls[1][0]))

    self.assertFalse(calls[2][1]) # not sudo
    self.assertEquals(6, len(calls[2][0]))
    self.assertEquals("-t", calls[2][0][0])
    self.assertEquals("-R", calls[2][0][1])
    self.assertEquals("-o", calls[2][0][3])
    self.assertEquals("test.trace", calls[2][0][4])
    self.assertEquals("trace.codes", calls[2][0][5])

