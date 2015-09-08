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
    def setup(self):
        self.bogus_xml = etree.fromstring('<foo/>')
        self.parser = xmlp.RundeckParser()

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
        nt.assert_equal(expected, xmlp.parse(single_job_etree, 'composite',
                                             self.parser.job_parse_table))

    @raises(xmlp.ParseError)
    def test_job_raises_if_not_job_tag(self):
        xmlp.parse(self.bogus_xml, 'composite', self.parser.job_parse_table)

    def test_job_raises_if_missing_mandatory(self):
        missing_id = ('<job><name>long job</name><group/><project>'
                      'API_client_development</project><description>'
                      'async testing</description></job>')
        nt.assert_raises(xmlp.ParseError, xmlp.parse,
                         etree.fromstring(missing_id),
                         'composite',
                         self.parser.job_parse_table)
        missing_name = ('<job id="foo"><group/><project>API_client_development'
                        '</project><description>async testing</description>'
                        '</job>')
        nt.assert_raises(xmlp.ParseError, xmlp.parse,
                         etree.fromstring(missing_name),
                         'composite',
                         self.parser.job_parse_table)
        missing_project = ('<job id="foo"><name>foo</name><group/>'
                           '<description>asynctesting</description></job>')
        nt.assert_raises(xmlp.ParseError, xmlp.parse,
                         etree.fromstring(missing_project),
                         'composite',
                         self.parser.job_parse_table)

    def test_jobs_creates_multiple_jobs_correctly(self):
        multiple_jobs = path.join(config.rundeck_test_data_dir,
                                  'multiple_jobs.xml')
        with open(multiple_jobs) as jobs_fl:
            multiple_jobs = etree.fromstring(jobs_fl.read())
        expected = {
            'count': 3,
            'list': [
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

        nt.assert_equal(expected, xmlp.parse(multiple_jobs, 'list',
                                             self.parser.jobs_parse_table))

    @raises(xmlp.ParseError)
    def test_jobs_raises_if_not_jobs_tag(self):
        xmlp.parse(self.bogus_xml, 'list', self.parser.jobs_parse_table)

    @raises(xmlp.ParseError)
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
        xmlp.parse(xml_tree, 'list', self.parser.jobs_parse_table)

    @raises(xmlp.ParseError)
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
        xmlp.parse(xml_tree, 'list', self.parser.jobs_parse_table)

    def test_execution_creates_single_execution_correctly(self):
        nt.assert_equal.__self__.maxDiff = 1000
        test_data_file = path.join(config.rundeck_test_data_dir,
                                   'execution.xml')
        with open(test_data_file) as ex_fl:
            xml_str = ex_fl.read()
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
            'successfulNodes': {
                'list': [
                    {'name': 'localhost'}
                ]
            }
        }
        xml_tree = etree.fromstring(xml_str)
        nt.assert_equal(expected,
                        xmlp.parse(xml_tree, 'composite',
                                   self.parser.execution_parse_table))

    @raises(xmlp.ParseError)
    def test_execution_raises_if_given_wrong_tag(self):
        xmlp.parse(self.bogus_xml, 'composite',
                   self.parser.execution_parse_table)

    def test_date_creates_dates_correctly(self):
        start_str = ('<date-started unixtime="1437474661504">'
                     '2015-07-21T10:31:01Z'
                     '</date-started>')
        end_str = ('<date-ended unixtime="1437474662344">'
                   '2015-07-21T10:31:02Z'
                   '</date-ended>')

        start_tree = etree.fromstring(start_str)
        end_tree = etree.fromstring(end_str)

        start_expected = {
            'unixtime': '1437474661504',
            'time': '2015-07-21T10:31:01Z'
        }
        nt.assert_equal(start_expected,
                        xmlp.parse(start_tree, 'attribute text',
                                   self.parser.start_date_parse_table))

        end_expected = {
            'unixtime': '1437474662344',
            'time': '2015-07-21T10:31:02Z'
        }
        nt.assert_equal(end_expected,
                        xmlp.parse(end_tree, 'attribute text',
                                   self.parser.date_ended_parse_table))

    @raises(xmlp.ParseError)
    def test_date_raises_if_given_wrong_tag(self):
        xmlp.parse(self.bogus_xml, 'attribute text',
                   self.parser.start_date_parse_table)

    def test_node_creates_node_correctly(self):
        xml_str = '<node name="localhost"/>'
        xml_tree = etree.fromstring(xml_str)
        expected = {'name': 'localhost'}
        nt.assert_equal(expected, xmlp.parse(xml_tree, 'attribute',
                                             self.parser.node_parse_table))

    @raises(xmlp.ParseError)
    def test_node_raises_if_given_wrong_tag(self):
        xmlp.parse(self.bogus_xml, 'text', self.parser.node_parse_table)

    def test_nodes_create_node_list(self):
        xml_str = ('<successfulNodes><node name="localhost"/>'
                   '<node name="otherhost"/></successfulNodes>')
        xml_tree = etree.fromstring(xml_str)
        expected = {'list': [{'name': 'localhost'}, {'name': 'otherhost'}]}
        nt.assert_equal(expected,
                        xmlp.parse(xml_tree, 'list',
                                   self.parser.successful_nodes_parse_table))

    @raises(xmlp.ParseError)
    def test_nodes_raises_if_given_wrong_tag(self):
        xmlp.parse(self.bogus_xml, 'list',
                   self.parser.successful_nodes_parse_table)

    def test_option_creates_option_correctly(self):
        xml_str = '<option name="arg1" value="foo"/>'
        xml_tree = etree.fromstring(xml_str)
        expected = {'name': 'arg1', 'value': 'foo'}
        nt.assert_equal(expected,
                        xmlp.parse(xml_tree, 'attribute',
                                   self.parser.option_parse_table))

    @raises(xmlp.ParseError)
    def test_option_raises_if_given_wrong_tag(self):
        xmlp.parse(self.bogus_xml, 'attribute', self.parser.option_parse_table)

    def test_options_creates_option_list_correctly(self):
        xml_str = ('<options>'
                   '<option name="arg1" value="foo"/>'
                   '<option name="arg2" value="bar"/>'
                   '</options>')
        xml_tree = etree.fromstring(xml_str)
        expected = {
            'list': [
                {'name': 'arg1', 'value': 'foo'},
                {'name': 'arg2', 'value': 'bar'}
            ]
        }
        nt.assert_equal(expected, xmlp.parse(xml_tree, 'list',
                                             self.parser.options_parse_table))

    @raises(xmlp.ParseError)
    def test_options_raises_if_given_wrong_tag(self):
        xmlp.parse(self.bogus_xml, 'list', self.parser.options_parse_table)

    def test_executions_create_executions_array_correctly(self):
        nt.assert_equal.__self__.maxDiff = 1000
        test_data_file = path.join(config.rundeck_test_data_dir,
                                   'executions.xml')
        with open(test_data_file) as ex_fl:
            xml_str = ex_fl.read()
        xml_tree = etree.fromstring(xml_str)
        expected = {
            'count': 5,
            'list': [
                {
                    'argstring': '-arg1 foo',
                    'date-ended': {
                        'time': '2015-05-28T10:44:04Z',
                        'unixtime': '1432809844967'
                    },
                    'date-started': {
                        'time': '2015-05-28T10:44:04Z',
                        'unixtime': '1432809844290'
                    },
                    'description': 'echo $RD_OPTION_ARG1',
                    'href': 'http://192.168.50.2:4440/execution/follow/53',
                    'id': '53',
                    'job': {
                        'averageDuration': '1022',
                        'description': None,
                        'group': None,
                        'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                        'name': 'job_with_args',
                        'options': {
                            'list': [{'name': 'arg1', 'value': 'foo'}]
                        },
                        'project': 'API_client_development'
                    },
                    'project': 'API_client_development',
                    'status': 'succeeded',
                    'successfulNodes': {'list': [{'name': 'localhost'}]},
                    'user': 'admin'
                },
                {
                    'argstring': '-arg1 foo',
                    'date-ended': {
                        'time': '2015-05-28T10:43:32Z',
                        'unixtime': '1432809812305'
                    },
                    'date-started': {
                        'time': '2015-05-28T10:43:31Z',
                        'unixtime': '1432809811697'
                    },
                    'description': 'echo $RD_OPTION_ARG1',
                    'href': 'http://192.168.50.2:4440/execution/follow/52',
                    'id': '52',
                    'job': {
                        'averageDuration': '1022',
                        'description': None,
                        'group': None,
                        'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                        'name': 'job_with_args',
                        'options': {
                            'list': [{'name': 'arg1', 'value': 'foo'}]
                        },
                        'project': 'API_client_development'
                    },
                    'project': 'API_client_development',
                    'status': 'succeeded',
                    'successfulNodes': {'list': [{'name': 'localhost'}]},
                    'user': 'admin'
                },
                {
                    'argstring': '-arg1 faf',
                    'date-ended': {
                        'time': '2015-05-28T09:53:15Z',
                        'unixtime': '1432806795789'
                    },
                    'date-started': {
                        'time': '2015-05-28T09:53:15Z',
                        'unixtime': '1432806795182'
                    },
                    'description': 'echo $RD_OPTION_ARG1',
                    'href': 'http://192.168.50.2:4440/execution/follow/49',
                    'id': '49',
                    'job': {
                        'averageDuration': '1022',
                        'description': None,
                        'group': None,
                        'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                        'name': 'job_with_args',
                        'options': {
                            'list': [{'name': 'arg1', 'value': 'faf'}]
                        },
                        'project': 'API_client_development'
                    },
                    'project': 'API_client_development',
                    'status': 'succeeded',
                    'successfulNodes': {'list': [{'name': 'localhost'}]},
                    'user': 'admin'
                },
                {
                    'argstring': '-arg1 foo',
                    'date-ended': {
                        'time': '2015-05-28T09:51:49Z',
                        'unixtime': '1432806709852'
                    },
                    'date-started': {
                        'time': '2015-05-28T09:51:49Z',
                        'unixtime': '1432806709140'
                    },
                    'description': 'echo $1',
                    'href': 'http://192.168.50.2:4440/execution/follow/48',
                    'id': '48',
                    'job': {
                        'averageDuration': '1022',
                        'description': None,
                        'group': None,
                        'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                        'name': 'job_with_args',
                        'options': {
                            'list': [{'name': 'arg1', 'value': 'foo'}]
                        },
                        'project': 'API_client_development'
                    },
                    'project': 'API_client_development',
                    'status': 'succeeded',
                    'successfulNodes': {'list': [{'name': 'localhost'}]},
                    'user': 'admin'
                },
                {
                    'argstring': '-arg1 foo',
                    'date-ended': {
                        'time': '2015-05-28T09:48:01Z',
                        'unixtime': '1432806481363'
                    },
                    'date-started': {
                        'time': '2015-05-28T09:47:58Z',
                        'unixtime': '1432806478853'
                    },
                    'description': 'echo $arg1',
                    'href': 'http://192.168.50.2:4440/execution/follow/46',
                    'id': '46',
                    'job': {
                        'averageDuration': '1022',
                        'description': None,
                        'group': None,
                        'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                        'name': 'job_with_args',
                        'options': {
                            'list': [{'name': 'arg1', 'value': 'foo'}]
                        },
                        'project': 'API_client_development'
                    },
                    'project': 'API_client_development',
                    'status': 'succeeded',
                    'successfulNodes': {'list': [{'name': 'localhost'}]},
                    'user': 'admin'
                }
            ]
        }

        nt.assert_equal(expected,
                        xmlp.parse(xml_tree, 'list',
                                   self.parser.executions_parse_table))

    @raises(xmlp.ParseError)
    def test_executions_raises_if_given_wrong_tag(self):
        xmlp.parse(self.bogus_xml, 'list', self.parser.executions_parse_table)

    @raises(xmlp.ParseError)
    def test_executions_raises_if_count_ne_executions_len(self):
        with open(path.join(config.rundeck_test_data_dir,
                            'bad_executions.xml')) as fl:
            xml_tree = etree.fromstring(fl.read())
            xmlp.parse(xml_tree, 'list',
                       self.parser.executions_parse_table)

    def test_result_with_execution(self):
        expected = {
            'success': 'true',
            'apiversion': '13',
            'executions': {
                'count': 5,
                'list': [
                    {
                        'argstring': '-arg1 foo',
                        'date-ended': {
                            'time': '2015-05-28T10:44:04Z',
                            'unixtime': '1432809844967'
                        },
                        'date-started': {
                            'time': '2015-05-28T10:44:04Z',
                            'unixtime': '1432809844290'
                        },
                        'description': 'echo $RD_OPTION_ARG1',
                        'href': 'http://192.168.50.2:4440/execution/follow/53',
                        'id': '53',
                        'job': {
                            'averageDuration': '1022',
                            'description': None,
                            'group': None,
                            'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                            'name': 'job_with_args',
                            'options': {
                                'list': [{'name': 'arg1', 'value': 'foo'}]
                            },
                            'project': 'API_client_development'
                        },
                        'project': 'API_client_development',
                        'status': 'succeeded',
                        'successfulNodes': {'list': [{'name': 'localhost'}]},
                        'user': 'admin'
                    },
                    {
                        'argstring': '-arg1 foo',
                        'date-ended': {
                            'time': '2015-05-28T10:43:32Z',
                            'unixtime': '1432809812305'
                        },
                        'date-started': {
                            'time': '2015-05-28T10:43:31Z',
                            'unixtime': '1432809811697'
                        },
                        'description': 'echo $RD_OPTION_ARG1',
                        'href': 'http://192.168.50.2:4440/execution/follow/52',
                        'id': '52',
                        'job': {
                            'averageDuration': '1022',
                            'description': None,
                            'group': None,
                            'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                            'name': 'job_with_args',
                            'options': {
                                'list': [{'name': 'arg1', 'value': 'foo'}]
                            },
                            'project': 'API_client_development'
                        },
                        'project': 'API_client_development',
                        'status': 'succeeded',
                        'successfulNodes': {'list': [{'name': 'localhost'}]},
                        'user': 'admin'
                    },
                    {
                        'argstring': '-arg1 faf',
                        'date-ended': {
                            'time': '2015-05-28T09:53:15Z',
                            'unixtime': '1432806795789'
                        },
                        'date-started': {
                            'time': '2015-05-28T09:53:15Z',
                            'unixtime': '1432806795182'
                        },
                        'description': 'echo $RD_OPTION_ARG1',
                        'href': 'http://192.168.50.2:4440/execution/follow/49',
                        'id': '49',
                        'job': {
                            'averageDuration': '1022',
                            'description': None,
                            'group': None,
                            'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                            'name': 'job_with_args',
                            'options': {
                                'list': [{'name': 'arg1', 'value': 'faf'}]
                            },
                            'project': 'API_client_development'
                        },
                        'project': 'API_client_development',
                        'status': 'succeeded',
                        'successfulNodes': {'list': [{'name': 'localhost'}]},
                        'user': 'admin'
                    },
                    {
                        'argstring': '-arg1 foo',
                        'date-ended': {
                            'time': '2015-05-28T09:51:49Z',
                            'unixtime': '1432806709852'
                        },
                        'date-started': {
                            'time': '2015-05-28T09:51:49Z',
                            'unixtime': '1432806709140'
                        },
                        'description': 'echo $1',
                        'href': 'http://192.168.50.2:4440/execution/follow/48',
                        'id': '48',
                        'job': {
                            'averageDuration': '1022',
                            'description': None,
                            'group': None,
                            'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                            'name': 'job_with_args',
                            'options': {
                                'list': [{'name': 'arg1', 'value': 'foo'}]
                            },
                            'project': 'API_client_development'
                        },
                        'project': 'API_client_development',
                        'status': 'succeeded',
                        'successfulNodes': {'list': [{'name': 'localhost'}]},
                        'user': 'admin'
                    },
                    {
                        'argstring': '-arg1 foo',
                        'date-ended': {
                            'time': '2015-05-28T09:48:01Z',
                            'unixtime': '1432806481363'
                        },
                        'date-started': {
                            'time': '2015-05-28T09:47:58Z',
                            'unixtime': '1432806478853'
                        },
                        'description': 'echo $arg1',
                        'href': 'http://192.168.50.2:4440/execution/follow/46',
                        'id': '46',
                        'job': {
                            'averageDuration': '1022',
                            'description': None,
                            'group': None,
                            'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                            'name': 'job_with_args',
                            'options': {
                                'list': [{'name': 'arg1', 'value': 'foo'}]
                            },
                            'project': 'API_client_development'
                        },
                        'project': 'API_client_development',
                        'status': 'succeeded',
                        'successfulNodes': {'list': [{'name': 'localhost'}]},
                        'user': 'admin'
                    }
                ]
            }
        }
        with open(path.join(config.rundeck_test_data_dir,
                            'execution_result.xml')) as fl:
            xml_tree = etree.fromstring(fl.read())
            nt.assert_equal(expected, xmlp.parse(xml_tree))

    def test_result_with_jobs(self):
        expected = {
            'apiversion': '13',
            'jobs': {'count': 5,
                     'list': [
                         {'description': None,
                          'group': None,
                          'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                          'name': 'job_with_args',
                          'project': 'API_client_development'},
                         {'description': 'async testing',
                          'group': None,
                          'id': 'ea17d859-32ff-45c8-8a0d-a16ac1ea3566',
                          'name': 'long job',
                          'project': 'API_client_development'},
                         {'description': None,
                          'group': None,
                          'id': '78f491e7-714f-44c6-bddb-8b3b3a961ace',
                          'name': 'test_job_1',
                          'project': 'API_client_development'},
                         {'description': None,
                          'group': None,
                          'id': '8d5ebfc8-d69a-4808-819e-9c57b7f288d2',
                          'name': 'test_job_2',
                          'project': 'API_client_development'},
                         {'description': None,
                          'group': None,
                          'id': '734f8b9c-683d-49cd-a2f2-f317696b76f8',
                          'name': 'test_job_2',
                          'project': 'API_client_development'}
                     ]},
            'success': 'true'}
        with open(path.join(config.rundeck_test_data_dir,
                            'jobs_result.xml')) as fl:
            xml_tree = etree.fromstring(fl.read())
            nt.assert_equal(expected, xmlp.parse(xml_tree))

    def test_alternative_type(self):
        xml_str = ('<root foo="bar">'
                   '<tags>'
                   '<tag2 lala="test"/>'
                   '<tag2 lala="test2"/>'
                   '</tags>'
                   '</root>')

        xml_tree = etree.fromstring(xml_str)

        expected = {
            'foo': 'bar',
            'tags': {
                'list': [
                    {'lala': 'test'},
                    {'lala': 'test2'}
                ]
            }
        }

        actual_parse_table = {
            'type': 'composite',
            'all': [
                {
                    'tag': 'tags',
                    'type': 'list',
                    'skip count': True,
                    'element parse table':
                    {'tag': 'tag2', 'type': 'attribute'}
                }
            ]
        }

        alternative_parse_table = {
            'type': 'text'
        }

        parse_table = {
            'tag': 'root',
            'type': 'alternatives',
            'parse tables': [alternative_parse_table, actual_parse_table]
        }

        nt.assert_equal(expected, xmlp.parse(xml_tree, parse_table=parse_table,
                                             cb_type='alternatives'))
