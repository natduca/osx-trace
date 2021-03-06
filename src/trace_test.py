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
import trace
import os
import subprocess
import tempfile
import unittest
import shlex
import libutil

class TraceTest(unittest.TestCase):
  def setUp(self):
    # create a directory hierarchy to do tests in
    self.test_data_dir = os.path.realpath(os.path.join(tempfile.gettempdir(), 'trace_test'))
    if os.path.exists(self.test_data_dir):
      self.rm_rf(self.test_data_dir)
    self.system('mkdir %s' % self.test_data_dir)

  def test_start_cold(self):
    util = libutil.LibUtil(self.test_data_dir)
    trace1 = trace.Trace(util, self.test_data_dir)
    self.assertTrue(trace1.did_compile)
    self.assertEquals(os.path.join(self.test_data_dir, "trace", "trace"), trace1._executable)
    self.assertEquals(os.path.join(self.test_data_dir, "trace.codes"), trace1.codes_file)

  def test_start_warm(self):
    util = libutil.LibUtil(self.test_data_dir)
    trace1 = trace.Trace(util, self.test_data_dir)
    self.assertTrue(trace1.did_compile)
    trace2 = trace.Trace(util, self.test_data_dir)
    self.assertFalse(trace2.did_compile)

  def test_call_mocked(self):
    real_system = os.system
    system_args = []
    def mock_system(*args):
      del system_args[:]
      system_args.extend(args)
      return 7
    os.system = mock_system
    try:
      util = libutil.LibUtil(self.test_data_dir)
      trace1 = trace.Trace(util, self.test_data_dir)
      ret = trace1.call(["test"], sudo=False)
      self.assertEquals(7, ret)
      self.assertEquals("%s test" % trace1._executable, system_args[-1])

      ret = trace1.call(["test"], sudo=True)
      self.assertEquals("%s test" % trace1._executable, system_args[-1])
      self.assertEquals(7, ret)
    finally:
      os.system = real_system


  def system(self, cmd):
    args = shlex.split(cmd)
    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()
    return p.returncode

  def rm_rf(self, dirname):
    self.system('rm -rf -- %s' % dirname)

  def tearDown(self):
    if self.test_data_dir:
      if os.path.exists(self.test_data_dir):
        self.rm_rf(self.test_data_dir)
      self.test_data_dir = None

