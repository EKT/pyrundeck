# Copyright (c) 2015, National Documentation Centre (EKT, www.ekt.gr)
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

#     Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.

#     Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.

#     Neither the name of the National Documentation Centre nor the
#     names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written
#     permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from nose.tools import raises
from lxml import etree

from pyrundeck import RundeckApiClient, RundeckException

# import dance of mock.patch for versions earlier than python 3.3
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


class TestEndpoints:
    def setup(self):
        self.token = 'token'
        self.root_url = 'http://rundeck.example.com'
        self.client = RundeckApiClient(self.token, self.root_url)

        self.response = (200,
                         etree.fromstring('<test_xml attribute="foo">'
                                          '<element other_attribute="lala">'
                                          'Text</element><element>Other '
                                          'Text</element>\n</test_xml>\n'))

    @raises(RundeckException)
    def test_run_job_raises_exception_if_no_id(self):
        self.client.run_job()

    @raises(RundeckException)
    def test_execution_info_raises_exception_if_no_execution_id(self):
        self.client.execution_info()

    @raises(RundeckException)
    def test_delete_job_raises_exception_if_no_job_id(self):
        self.client.delete_job()
