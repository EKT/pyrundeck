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

# import dance of mock.patch for versions earlier than python 3.3
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


from lxml import etree
import nose.tools as nt

from pyrundeck import api, __version__
from pyrundeck.test import config

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"

class TestCoreRundeckAPIClient:
    def setup(self):
        with open(config.rundeck_token_file) as fl:
            self.token = fl.readline().strip()
            self.client = api.RundeckApiClient(self.token, config.root_url)

            class Object(object):
                pass
            self.resp = Object()   # Dummy response object
            self.resp.status_code = 200
            self.resp.text = '<test_xml attribute="foo">\n    <element other_attribute="lala">Text</element>\n    <element>Other Text</element>\n</test_xml>\n'

    def test_initialization_sets_up_client_correctly(self):
        nt.assert_equal(self.token, self.client.token)
        nt.assert_dict_contains_subset({'X-Rundeck-Auth-Token': self.token,
                                        'User-Agent': 'PyRundeck v ' + __version__}, self.client.client_args['headers'])

        new_client = api.RundeckApiClient(self.token, config.root_url,
                                          client_args={'headers': {'User-Agent': 'dummy agent string'}})
        nt.assert_equal(self.token, new_client.token)
        nt.assert_dict_contains_subset({'X-Rundeck-Auth-Token': self.token,
                                        'User-Agent': 'dummy agent string'}, new_client.client_args['headers'])

    @patch('pyrundeck.api.RundeckApiClient._perform_request')
    def test_get_method_correctly_calls_perform(self, mock_perform):
        url = 'https://rundeck.example.com/api/13/foo'
        params = {
            'a': 'b',
            'c': 'd'
        }
        self.client.get(url, params=params)
        mock_perform.assert_called_once_with(url, params=params, method='GET')

    @patch('pyrundeck.api.RundeckApiClient._perform_request')
    def test_post_method_correctly_calls_perform(self, mock_perform):
        url = 'https://rundeck.example.com/api/13/foo'
        params = {
            'a': 'b',
            'c': 'd'
        }
        self.client.post(url, params=params)
        mock_perform.assert_called_once_with(url, params=params, method='POST')

    @patch('pyrundeck.api.RundeckApiClient._perform_request')
    def test_delete_method_correctly_calls_perform(self, mock_perform):
        url = 'https://rundeck.example.com/api/13/foo'
        params = {
            'a': 'b',
            'c': 'd'
        }
        self.client.delete(url, params=params)
        mock_perform.assert_called_once_with(url, params=params, method='DELETE')

    @patch('pyrundeck.api.RundeckApiClient._perform_request')
    def test_all_methods_return_correctly_result_of_perform_request(self, mock_perform):
        ret = 'mock_perform_value'
        mock_perform.return_value = ret
        res1 = self.client.get('foo')
        nt.assert_equal(res1, ret)

        res2 = self.client.post('foo')
        nt.assert_equal(res2, ret)

        res3 = self.client.post('foo')
        nt.assert_equal(res3, ret)

    @patch('requests.request')
    def test_perform_request_performs_correct_call_for_get_method(self, mock_request):
        url = 'https://rundeck.example.com/api/13/test_endpoint'
        mock_request.return_value = self.resp

        self.client._perform_request(url)
        args = mock_request.call_args
        nt.assert_equal(2, len(args))
        nt.assert_equal(('GET', url,), args[0])
        nt.assert_in('headers', args[1])
        headers = args[1]['headers']
        nt.assert_dict_contains_subset({'X-Rundeck-Auth-Token': self.token,
                                        'User-Agent': 'PyRundeck v ' + __version__}, headers)

    @patch('requests.request')
    def test_perform_requests_performs_correct_call_for_post_method(self, mock_request):
        url = 'https://rundeck.example.com/api/13/test_endpoint'
        mock_request.return_value = self.resp

        self.client._perform_request(url, method='POST', params={'xmlBatch': '123\n456'})

        args = mock_request.call_args
        nt.assert_equal(2, len(args))
        nt.assert_equal(('POST', url,), args[0])
        nt.assert_in('headers', args[1])
        nt.assert_in('data', args[1])
        headers = args[1]['headers']
        nt.assert_dict_contains_subset({'X-Rundeck-Auth-Token': self.token,
                                        'User-Agent': 'PyRundeck v ' + __version__}, headers)
        data = args[1]['data']
        nt.assert_dict_contains_subset({'xmlBatch': '123\n456'}, data)

    @patch('requests.request')
    def test_perform_requests_returns_correctly_for_get_method(self, mock_get):

        mock_get.return_value = self.resp

        url = 'https://rundeck.example.com/api/13/test_endpoint'
        status, data = self.client._perform_request(url)
        nt.assert_equal(200, status)
        nt.assert_equal(self.resp.text, etree.tostring(data, pretty_print=True).decode('utf-8'))

    @patch('requests.request')
    def test_perform_requests_calls_request_correctly_with_https_initialization(self, mock_request):
        mock_request.return_value = self.resp

        https_url = 'https://rundeck.example.com'

        client = RundeckApiClient(self.token, https_url)
        client._perform_request(https_url)

        args, kwargs = mock_request.call_args
        nt.assert_dict_contains_subset({'verify': True}, kwargs)

        path_to_pem = '/path/to/pem/file'
        other_client = RundeckApiClient(self.token, https_url, pem_file_path=path_to_pem)
        other_client._perform_request(https_url)
        args, kwargs = mock_request.call_args

        nt.assert_dict_contains_subset({'verify': path_to_pem}, kwargs)
