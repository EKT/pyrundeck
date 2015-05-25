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

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"

import nose.tools as nt
from unittest.mock import patch

import rundeck_client_api as rca
from rundeck_client_api import config, api


class TestCoreRundeckAPIClient:
    def setup(self):
        with open(config.rundeck_token_file) as fl:
            self.token = fl.readline().strip()
            self.client = api.RundeckApiClient(self.token, config.root_url)
            self.api_version = config.api_version

    @patch('rundeck_client_api.api.RundeckApiClient._perform_request')
    def test_get_method_correctly_calls_perform(self, mock_perform):
        url = 'https://rundeck.example.com/api/13/foo'
        params = {
            'a': 'b',
            'c': 'd'
        }
        self.client.get(url, params=params)
        mock_perform.assert_called_once_with(url, params=params, method='GET')

    @patch('rundeck_client_api.api.RundeckApiClient._perform_request')
    def test_post_method_correctly_calls_perform(self, mock_perform):
        url = 'https://rundeck.example.com/api/13/foo'
        params = {
            'a': 'b',
            'c': 'd'
        }
        self.client.post(url, params=params)
        mock_perform.assert_called_once_with(url, params=params, method='POST')

    @patch('rundeck_client_api.api.RundeckApiClient._perform_request')
    def test_delete_method_correctly_calls_perform(self, mock_perform):
        url = 'https://rundeck.example.com/api/13/foo'
        params = {
            'a': 'b',
            'c': 'd'
        }
        self.client.delete(url, params=params)
        mock_perform.assert_called_once_with(url, params=params, method='DELETE')

    @patch('rundeck_client_api.api.RundeckApiClient._perform_request')
    def test_all_methods_return_correctly_result_of_perform_request(self, mock_perform):
        ret = 'mock_perform_value'
        mock_perform.return_value = ret
        res1 = self.client.get('foo')
        nt.assert_equal(res1, ret)

        res2 = self.client.post('foo')
        nt.assert_equal(res2, ret)

        res3 = self.client.post('foo')
        nt.assert_equal(res3, ret)

    @patch('requests.get')
    def test_perform_request_sets_correct_headers(self, mock_get):
        url = 'https://rundeck.example.com/api/13/foo'

        self.client._perform_request(url)
        args = mock_get.call_args
        nt.assert_equal(2, len(args))
        nt.assert_equal(url, args[0])
        nt.assert_in('headers', args[1])
        headers = args[1]['headers']
        nt.assert_dict_contains_subset({'X-Rundeck-Auth-Token': self.token,
                                        'User-Agent': 'PyRundeck v ' + rca.__version__}, headers)
