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
    def test_job_creates_single_job_correctly(self):
        single_job = path.join(config.rundeck_test_data_dir,
                               'single_job_from_response.xml')
        with open(single_job) as job_fl:
            single_job_etree = etree.fromstring(job_fl.read())
        expected = {
            'id': "ea17d859-32ff-45c8-8a0d-a16ac1ea3566",
            'name': 'long job',
            'group': None,
            'project': 'API_client_development',
            'description': 'async testing'
        }
        nt.assert_equal(expected, xmlp.job(single_job_etree))

    @raises(xmlp.RundeckParseError)
    def test_job_raises_if_not_job_tag(self):
        xml_tree = etree.fromstring("<foo/>")
        xmlp.job(xml_tree)

    def test_job_raises_if_missing_mandatory(self):
        missing_id = ('<job><name>long job</name><group/><project>'
                      'API_client_development</project><description>'
                      'async testing</description></job>')
        nt.assert_raises(xmlp.RundeckParseError, xmlp.job,
                         etree.fromstring(missing_id))
        missing_name = ('<job id="foo"><group/><project>API_client_development'
                        '</project><description>async testing</description>'
                        '</job>')
        nt.assert_raises(xmlp.RundeckParseError, xmlp.job,
                         etree.fromstring(missing_name))
        missing_project = ('<job id="foo"><name>foo</name><group/>'
                           '<description>asynctesting</description></job>')
        nt.assert_raises(xmlp.RundeckParseError, xmlp.job,
                         etree.fromstring(missing_project))

    def test_jobs_creates_multiple_jobs_correctly(self):
        multiple_jobs = path.join(config.rundeck_test_data_dir,
                                  'multiple_jobs.xml')
        with open(multiple_jobs) as jobs_fl:
            multiple_jobs = etree.fromstring(jobs_fl.read())
        expected = {
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

        nt.assert_equal(expected, xmlp.jobs(multiple_jobs))

    @raises(xmlp.RundeckParseError)
    def test_jobs_raises_if_not_jobs_tag(self):
        xml_tree = etree.fromstring('<foo/>')
        xmlp.jobs(xml_tree)

    @raises(xmlp.RundeckParseError)
    def test_jobs_raises_if_no_count(self):
        xml_str = ('<jobs>'
                   '<job id="3b8a86d5-4fc3-4cc1-95a2-8b51421c2069">'
                   '<name>job_with_args</name>'
                   '<group/>'
                   '<project>API_client_development</project>'
                   '<description/>'
                   '</job>'
                   '<job id="ea17d859-32ff-45c8-8a0d-a16ac1ea3566">'
                   '<name>long job</name>'
                   '<group/>'
                   '<project>API_client_development</project>'
                   '<description>async testing</description>'
                   '</job>'
                   '<job id="78f491e7-714f-44c6-bddb-8b3b3a961ace">'
                   '<name>test_job_1</name>'
                   '<group/>'
                   '<project>API_client_development</project>'
                   '<description/>'
                   '</job>'
                   '</jobs>')
        xml_tree = etree.fromstring(xml_str)
        xmlp.jobs(xml_tree)

    @raises(xmlp.RundeckParseError)
    def test_jobs_raises_if_count_neq_jobs_len(self):
        xml_str = ('<jobs count="5">'
                   '<job id="3b8a86d5-4fc3-4cc1-95a2-8b51421c2069">'
                   '<name>job_with_args</name>'
                   '<group/>'
                   '<project>API_client_development</project>'
                   '<description/>'
                   '</job>'
                   '<job id="ea17d859-32ff-45c8-8a0d-a16ac1ea3566">'
                   '<name>long job</name>'
                   '<group/>'
                   '<project>API_client_development</project>'
                   '<description>async testing</description>'
                   '</job>'
                   '<job id="78f491e7-714f-44c6-bddb-8b3b3a961ace">'
                   '<name>test_job_1</name>'
                   '<group/>'
                   '<project>API_client_development</project>'
                   '<description/>'
                   '</job>'
                   '</jobs>')
        xml_tree = etree.fromstring(xml_str)
        xmlp.jobs(xml_tree)

    def test_execution_creates_single_execution_correctly(self):
        nt.assert_equal.__self__.maxDiff = 1000
        xml_str = '<execution id="117" href="http://192.168.50.2:4440/execution/follow/117" status="succeeded" project="API_client_development"> <user>admin</user> <date-started unixtime="1437474661504">2015-07-21T10:31:01Z</date-started> <date-ended unixtime="1437474662344">2015-07-21T10:31:02Z</date-ended> <job id="78f491e7-714f-44c6-bddb-8b3b3a961ace" averageDuration="2716"> <name>test_job_1</name> <group/> <project>API_client_development</project> <description/> </job> <description>echo "Hello"</description> <argstring/> <successfulNodes> <node name="localhost"/> </successfulNodes> </execution>'
        expected = {
            'id': '117',
            'href': 'http://192.168.50.2:4440/execution/follow/117',
            'status': 'succeeded',
            'project': 'API_client_development',
            'user': 'admin',
            'date-started': {
                'unixtime': '1437474661504',
                'time': '2015-07-21T10:31:01Z'
            },
            'date-ended': {
                'unixtime': '1437474662344',
                'time': '2015-07-21T10:31:02Z'
            },
            'job': {
                'id': '78f491e7-714f-44c6-bddb-8b3b3a961ace',
                'averageDuration': '2716',
                'name': 'test_job_1',
                'group': None,
                'project': 'API_client_development',
                'description': None,
            },
            'description': 'echo "Hello"',
            'argstring': None,
            'successfulNodes': [
                {'name': 'localhost'}
            ]
        }
        xml_tree = etree.fromstring(xml_str)
        nt.assert_equal(expected, xmlp.execution(xml_tree))

    def test_parse_date_creates_dates_correctly(self):
        start_str = '<date-started unixtime="1437474661504">2015-07-21T10:31:01Z</date-started>'
        end_str = '<date-ended unixtime="1437474662344">2015-07-21T10:31:02Z</date-ended>'

        start_tree = etree.fromstring(start_str)
        end_tree = etree.fromstring(end_str)

        start_expected = {
            'unixtime': '1437474661504',
            'time': '2015-07-21T10:31:01Z'
        }
        nt.assert_equal(start_expected, xmlp.parse_date(start_tree))

        end_expected = {
            'unixtime': '1437474662344',
            'time': '2015-07-21T10:31:02Z'
        }
        nt.assert_equal(end_expected, xmlp.parse_date(end_tree))

    @raises(xmlp.RundeckParseError)
    def test_parse_date_raises_if_given_wrong_tag(self):
        xml_str = "<foo/>"
        xml_tree = etree.fromstring(xml_str)
        xmlp.parse_date(xml_tree)

    def test_node_creates_node_correctly(self):
        xml_str = '<node name="localhost"/>'
        xml_tree = etree.fromstring(xml_str)
        expected = {'name': 'localhost'}
        nt.assert_equal(expected, xmlp.node(xml_tree))

    @raises(xmlp.RundeckParseError)
    def test_node_raises_if_given_wrong_tag(self):
        xml_str = '<foo/>'
        xml_tree = etree.fromstring(xml_str)
        xmlp.node(xml_tree)

    def test_nodes_create_node_list(self):
        xml_str = ('<successfulNodes><node name="localhost"/>'
                   '<node name="otherhost"/></successfulNodes>')
        xml_tree = etree.fromstring(xml_str)
        expected = [{'name': 'localhost'}, {'name': 'otherhost'}]
        nt.assert_equal(expected, xmlp.nodes(xml_tree))

    @raises(xmlp.RundeckParseError)
    def test_nodes_raises_if_given_wrong_tag(self):
        xml_str = '<foo/>'
        xml_tree = etree.fromstring(xml_str)
        xmlp.nodes(xml_tree)
