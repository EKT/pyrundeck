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

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import nose.tools as nt
from nose.tools import raises
from lxml import etree
from pyrundeck import RundeckApiClient, RundeckException


def element_equality(e1, e2):
    if e1.tag != e2.tag:
        return False
    if e1.text != e2.text:
        return False
    if e1.tail != e2.tail:
        return False
    if e1.attrib != e2.attrib:
        return False
    if len(e1) != len(e2):
        return False

    return all(element_equality(c1, c2) for c1, c2 in zip(e1, e2))


class TestEndpoints(object):
    def __init__(self):
        self.root_url = 'http://www.example.com'
        self.xml_str = ('<result success="true" apiversion="13">'
                        '<jobs count="3">'
                        '<job id="3b8a86d5-4fc3-4cc1-95a2-8b51421c2069">'
                        '<name>job_with_args</name>'
                        '<group/>'
                        '<project>API_client_development</project>'
                        '<description/>'
                        '</job>'
                        '<job id="78f491e7-714f-44c6-bddb-8b3b3a961ace">'
                        '<name>test_job_1</name>'
                        '<group/>'
                        '<project>API_client_development</project>'
                        '<description/>'
                        '</job>'
                        '<job id="b07b05b0-0a37-4f88-8a51-4bee77ceefb4">'
                        '<name>test_job_2</name>'
                        '<group/>'
                        '<project>API_client_development</project>'
                        '<description/>'
                        '</job>'
                        '</jobs>'
                        '</result>')
        self.xml_tree = etree.fromstring(self.xml_str)
        self.native_result = {
            'apiversion': '13',
            'jobs': {
                'count': 3,
                'list': [
                    {
                        'description': '',
                        'group': '',
                        'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
                        'name': 'job_with_args',
                        'project': 'API_client_development'
                    },
                    {
                        'description': '',
                        'group': '',
                        'id': '78f491e7-714f-44c6-bddb-8b3b3a961ace',
                        'name': 'test_job_1',
                        'project': 'API_client_development'
                    },
                    {
                        'description': '',
                        'group': '',
                        'id': 'b07b05b0-0a37-4f88-8a51-4bee77ceefb4',
                        'name': 'test_job_2',
                        'project': 'API_client_development'
                    }
                ]
            },
            'success': 'true'
        }
        self.return_status = 200

    def setup(self):
        self.client = RundeckApiClient('mock_token', self.root_url)

    # Tests for RundeckApiClient.import_job
    @patch('pyrundeck.RundeckApiClient.post')
    def test_import_job_xml(self, mock_post):
        mock_post.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/1/jobs/import'.format(self.root_url)

        status, res = self.client.import_job(native=False,
                                             xmlBatch='mock xmlBatch')

        mock_post.assert_called_once_with(actual_url,
                                          {'xmlBatch': 'mock xmlBatch'})
        nt.assert_equal(status, self.return_status)
        nt.assert_true(element_equality(res, self.xml_tree))

    @patch('pyrundeck.RundeckApiClient.post')
    def test_import_job_native(self, mock_post):
        mock_post.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/1/jobs/import'.format(self.root_url)

        status, res = self.client.import_job(xmlBatch='mock xmlBatch')

        mock_post.assert_called_once_with(actual_url,
                                          {'xmlBatch': 'mock xmlBatch'})
        nt.assert_equal(status, self.return_status)
        nt.assert_equal(res, self.native_result)

    # Tests for RundeckApiClient.export_jobs
    @patch('pyrundeck.RundeckApiClient.get')
    def test_export_jobs_xml(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/1/jobs/export'.format(self.root_url)

        status, res = self.client.export_jobs(native=False)

        mock_get.assert_called_once_with(actual_url, {})
        nt.assert_equal(status, self.return_status)
        nt.assert_true(element_equality(res, self.xml_tree))

    @patch('pyrundeck.RundeckApiClient.get')
    def test_export_jobs_native(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/1/jobs/export'.format(self.root_url)

        status, res = self.client.export_jobs()

        mock_get.assert_called_once_with(actual_url, {})
        nt.assert_equal(status, self.return_status)
        nt.assert_equal(res, self.native_result)

    # Tests for RundeckApiClient.list_jobs
    @patch('pyrundeck.RundeckApiClient.get')
    def test_list_jobs_xml(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/1/jobs'.format(self.root_url)

        status, res = self.client.list_jobs(native=False,
                                            project='mock project arg')

        mock_get.assert_called_once_with(actual_url,
                                         {'project': 'mock project arg'})
        nt.assert_equal(status, self.return_status)
        nt.assert_true(element_equality(res, self.xml_tree))

    @patch('pyrundeck.RundeckApiClient.get')
    def test_list_jobs_native(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/1/jobs'.format(self.root_url)

        status, res = self.client.list_jobs(project='mock project arg')

        mock_get.assert_called_once_with(actual_url,
                                         {'project': 'mock project arg'})
        nt.assert_equal(status, self.return_status)
        nt.assert_equal(res, self.native_result)

    # Tests for RundeckApiClient.run_job
    @patch('pyrundeck.RundeckApiClient.get')
    def test_run_job_xml(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        job_id = 'mock id'
        actual_url = '{}/api/1/job/{}/run'.format(self.root_url, job_id)

        status, res = self.client.run_job(native=False, id=job_id)

        mock_get.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_true(element_equality(res, self.xml_tree))

    @patch('pyrundeck.RundeckApiClient.get')
    def test_run_job_native(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        job_id = 'mock id'
        actual_url = '{}/api/1/job/{}/run'.format(self.root_url, job_id)

        status, res = self.client.run_job(id=job_id)
        mock_get.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_equal(res, self.native_result)

    @raises(RundeckException)
    def test_run_job_raises_if_no_id(self):
        self.client.run_job()

    # Tests for RundeckApiClient.execution_info
    @patch('pyrundeck.RundeckApiClient.get')
    def test_execution_info_xml(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        execution_id = 'mock id'
        actual_url = '{}/api/1/execution/{}'.format(self.root_url,
                                                    execution_id)

        status, res = self.client.execution_info(native=False, id=execution_id)

        mock_get.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_true(element_equality(res, self.xml_tree))

    @patch('pyrundeck.RundeckApiClient.get')
    def test_execution_info_native(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        execution_id = 'mock id'
        actual_url = '{}/api/1/execution/{}'.format(self.root_url,
                                                    execution_id)

        status, res = self.client.execution_info(id=execution_id)

        mock_get.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_equal(res, self.native_result)

    @raises(RundeckException)
    def test_execution_info_raises_if_no_id(self):
        self.client.execution_info()

    # Tests for RundeckApiClient.delete_job
    @patch('pyrundeck.RundeckApiClient.delete')
    def test_delete(self, mock_delete):
        mock_delete.return_value = (self.return_status, '')
        job_id = 'mock id'
        actual_url = '{}/api/1/job/{}'.format(self.root_url,
                                              job_id)

        status, res = self.client.delete_job(id=job_id)

        mock_delete.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_equal('', res)

    @raises(RundeckException)
    def test_delete_raises_if_no_id(self):
        self.client.delete_job()

    # Tests for RundeckApiClient.job_executions_info
    @patch('pyrundeck.RundeckApiClient.get')
    def test_job_executions_info_xml(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        job_id = 'mock id'
        actual_url = '{}/api/1/job/{}/executions'.format(self.root_url,
                                                         job_id)

        status, res = self.client.job_executions_info(native=False, id=job_id)

        mock_get.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_true(element_equality(res, self.xml_tree))

    @patch('pyrundeck.RundeckApiClient.get')
    def test_job_executions_info_native(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        job_id = 'mock id'
        actual_url = '{}/api/1/job/{}/executions'.format(self.root_url,
                                                         job_id)

        status, res = self.client.job_executions_info(id=job_id)

        mock_get.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_equal(res, self.native_result)

    @raises(RundeckException)
    def test_job_executions_info_raises_if_no_id(self):
        self.client.job_executions_info()

    # Tests for RundeckApiClient.running_executions
    @patch('pyrundeck.RundeckApiClient.post')
    def test_running_executions_xml(self, mock_post):
        mock_post.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/1/executions/running'.format(self.root_url)

        status, res = self.client.running_executions(native=False)

        mock_post.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_true(element_equality(res, self.xml_tree))

    @patch('pyrundeck.RundeckApiClient.post')
    def test_running_executions_native(self, mock_post):
        mock_post.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/1/executions/running'.format(self.root_url)

        status, res = self.client.running_executions()

        mock_post.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_equal(res, self.native_result)

    # Tests for RundeckApiClient.system_info
    @patch('pyrundeck.RundeckApiClient.get')
    def test_system_info_xml(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/1/system/info'.format(self.root_url)

        status, res = self.client.system_info(native=False)

        mock_get.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_true(element_equality(res, self.xml_tree))

    @patch('pyrundeck.RundeckApiClient.get')
    def test_system_info_native(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/1/system/info'.format(self.root_url)

        status, res = self.client.system_info()

        mock_get.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_equal(res, self.native_result)

    # Tests for RundeckApiClient.job_definition
    @patch('pyrundeck.RundeckApiClient.get')
    def test_job_definition_xml(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        job_id = 'mock id'
        actual_url = '{}/api/1/job/{}'.format(self.root_url, job_id)

        status, res = self.client.job_definition(native=False,
                                                 id=job_id)

        mock_get.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_true(element_equality(res, self.xml_tree))

    @patch('pyrundeck.RundeckApiClient.get')
    def test_job_definition_native(self, mock_get):
        mock_get.return_value = (self.return_status, self.xml_tree)
        job_id = 'mock id'
        actual_url = '{}/api/1/job/{}'.format(self.root_url, job_id)

        status, res = self.client.job_definition(id=job_id)

        mock_get.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_equal(res, self.native_result)

    @raises(RundeckException)
    def test_job_definition_raises_if_no_id(self):
        self.client.job_definition()

    # Tests for RundeckApiClient.bulk_job_delete
    @patch('pyrundeck.RundeckApiClient.delete')
    def test_bulk_job_delete_xml(self, mock_delete):
        mock_delete.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/5/jobs/delete'.format(self.root_url)

        status, res = self.client.bulk_job_delete(native=False)

        mock_delete.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_true(element_equality(res, self.xml_tree))

    @patch('pyrundeck.RundeckApiClient.delete')
    def test_bulk_job_delete_native(self, mock_delete):
        mock_delete.return_value = (self.return_status, self.xml_tree)
        actual_url = '{}/api/5/jobs/delete'.format(self.root_url)

        status, res = self.client.bulk_job_delete()

        mock_delete.assert_called_once_with(actual_url, {})

        nt.assert_equal(status, self.return_status)
        nt.assert_equal(res, self.native_result)
