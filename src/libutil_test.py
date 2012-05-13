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
import libutil
import os
import subprocess
import tempfile
import unittest
import shlex

class LibUtilTest(unittest.TestCase):
  def setUp(self):
    # create a directory hierarchy to do tests in
    self.test_data_dir = os.path.realpath(os.path.join(tempfile.gettempdir(), 'libutil_test'))
    if os.path.exists(self.test_data_dir):
      self.rm_rf(self.test_data_dir)
    self.system('mkdir %s' % self.test_data_dir)

  def test_start_cold(self):
    util = libutil.LibUtil(self.test_data_dir)
    self.assertTrue(util.did_compile)

  def test_start_warm(self):
    util1 = libutil.LibUtil(self.test_data_dir)
    self.assertTrue(util1.did_compile)
    util2 = libutil.LibUtil(self.test_data_dir)
    self.assertFalse(util2.did_compile)

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

