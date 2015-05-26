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
from lxml import etree
import requests

from rundeck_client_api.endpoints import EndpointMixins
from rundeck_client_api import __version__
from rundeck_client_api.helpers import _transparent_params

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


class RundeckApiClient(EndpointMixins):
    def __init__(self, token, root_url, client_args=None):
        self.root_url = root_url
        self.token = token

        default_headers = {'User-Agent': 'PyRundeck v ' + __version__}

        self.client_args = client_args or {}
        if 'headers' not in self.client_args:
            self.client_args['headers'] = default_headers
        elif 'User-Agent' not in self.client_args['headers']:
            self.client_args['headers'].update(default_headers)

        auth_token_header = {'X-Rundeck-Auth-Token': self.token}
        self.client_args['headers'].update(auth_token_header)

    def _perform_request(self, url, method='GET', params=None):
        params = params or {}

        params, files = _transparent_params(params)
        requests_args = {}
        for k, v in self.client_args.items():
            requests_args[k] = v

        if method == 'POST':
            requests_args.update({
                'data': params,
                'files': files,
            })
        else:
            requests_args['params'] = params

        response = requests.request(method, url, **requests_args)

        if response.text != '':
            return response.status_code, etree.fromstring(response.text)
        else:
            return response.status_code, None

    def get(self, url, params=None):
        return self._perform_request(url, method='GET', params=params)

    def post(self, url, params=None):
        return self._perform_request(url, method='POST', params=params)

    def delete(self, url, params=None):
        return self._perform_request(url, method='DELETE', params=params)
