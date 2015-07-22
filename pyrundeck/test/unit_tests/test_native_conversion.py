# Copyright (c) 2007-2015, National Documentation Centre (EKT, www.ekt.gr)
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

from os import path

from lxml import etree
import nose.tools as nt
from nose.tools import raises

from pyrundeck.test import config
import pyrundeck.xml2native as xmlp


__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


class TestXMLToNativePython:
    def test_parser_creates_single_job(self):
        single_job = path.join(config.rundeck_test_data_dir,
                               'single_job_from_response.xml')
        with open(single_job) as job_fl:
            single_job_etree = etree.fromstring(job_fl.read())
        correct = {
            'id': "ea17d859-32ff-45c8-8a0d-a16ac1ea3566",
            'name': 'long job',
            'group': None,
            'project': 'API_client_development',
            'description': 'async testing'
        }
        nt.assert_equal(correct, xmlp.parse_single_job(single_job_etree))

    @raises(xmlp.RundeckParseError)
    def test_parse_single_job_raises_if_not_job_tag(self):
        xml_tree = etree.fromstring("<foo/>")
        xmlp.parse_single_job(xml_tree)

    def test_parse_single_job_raises_if_missing_mandatory(self):
        missing_id = ('<job><name>long job</name><group/><project>'
                      'API_client_development</project><description>'
                      'async testing</description></job>')
        nt.assert_raises(xmlp.RundeckParseError, xmlp.parse_single_job,
                         etree.fromstring(missing_id))
        missing_name = ('<job id="foo"><group/><project>API_client_development'
                        '</project><description>async testing</description>'
                        '</job>')
        nt.assert_raises(xmlp.RundeckParseError, xmlp.parse_single_job,
                         etree.fromstring(missing_name))
        missing_project = ('<job id="foo"><name>foo</name><group/>'
                           '<description>asynctesting</description></job>')
        nt.assert_raises(xmlp.RundeckParseError, xmlp.parse_single_job,
                         etree.fromstring(missing_project))

    def test_parser_creates_multiple_jobs(self):
        multiple_jobs = path.join(config.rundeck_test_data_dir,
                                  'multiple_jobs.xml')
        with open(multiple_jobs) as jobs_fl:
            multiple_jobs = etree.fromstring(jobs_fl.read())
        correct = {
            'count': 3,
            'jobs':
            [
                {
                    'id': "3b8a86d5-4fc3-4cc1-95a2-8b51421c2069",
                    'name': 'job_with_args',
                    'group': None,
                    'project': 'API_client_development',
                    'description': None
                },
                {
                    'id': "ea17d859-32ff-45c8-8a0d-a16ac1ea3566",
                    'name': 'long job',
                    'group': None,
                    'project': 'API_client_development',
                    'description': 'async testing'
                },
                {
                    'id': "78f491e7-714f-44c6-bddb-8b3b3a961ace",
                    'name': 'test_job_1',
                    'group': None,
                    'project': 'API_client_development',
                    'description': None
                },
            ]
        }

        nt.assert_equal(correct, xmlp.parse_multiple_jobs(multiple_jobs))
