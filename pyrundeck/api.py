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

"""This module contains the core of the API client.

The general idea is to abstract away all possible requests into three
methods (``RundeckApiClient.get``, ``RundeckApiClient.post`` and
``RundeckApiClient.delete``), that call the same method
``RundeckApiClient._perform_request`` that performs the actual
request.
"""

import logging
from lxml import etree
import requests

from pyrundeck.endpoints import EndpointMixins
from pyrundeck import __version__
from pyrundeck.helpers import _transparent_params

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


class RundeckApiClient(EndpointMixins):
    """The Rundeck API wrapper. This class is used to interact with the
    Rundeck server. In order to instantiate it you need to provide at
    least an access token and a root url for the Rundeck server.

    See :doc:`usage` for examples.

    :param token: The rundeck access token.
    :param root_url: The rundeck server URL.
    :param pem_file_path: (optional) A file path to a CA_BUNDLE for SSL
                          certificate validation. *Default value:* ``None``.
    :param client_args: (optional) Default values to be passed to
                        every request. This should be a dictionary,
                        notably containing a key
                        ``'headers'``. *Default value:* ``None``.
    :param log_level: (optional) The level at which logging happens.
                      *Default value:* ``logging.INFO``.
    """
    def __init__(self, token, root_url, pem_file_path=None,
                 client_args=None, log_level=logging.INFO):
        if root_url.endswith('/'):
            self.root_url = root_url[:-1]
        else:
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
        if self.root_url.startswith('https'):
            if pem_file_path is not None:
                self.client_args['verify'] = pem_file_path
            else:
                self.client_args['verify'] = True

        # TODO pass this as an arg? Timestamp it?
        logging.basicConfig(level=log_level, filename='pyrundeck.log')
        self.logger = logging.getLogger(__name__)

        self.pem_file_path = pem_file_path

    def _perform_request(self, url, method='GET', params=None):
        """Perform the request.

        This method uses the ``requests`` library to perform a request
        to the Rundeck API.
        """
        self.logger.debug('params = {}'.format(params))
        params = params or {}

        params, files = _transparent_params(params)
        self.logger.debug('params = {}'.format(params))
        requests_args = {}
        for key, val in self.client_args.items():
            requests_args[key] = val

        if method == 'POST':
            requests_args.update({
                'data': params,
                'files': files,
            })
        else:
            requests_args['params'] = params

        self.logger.debug('request args = {}'.format(requests_args))

        response = requests.request(method, url, **requests_args)

        self.logger.debug('status = {}'.format(response.status_code))
        self.logger.debug('text = {}'.format(response.text))

        if response.text != '':
            return response.status_code, etree.fromstring(response.text)
        else:
            return response.status_code, None

    def get(self, url, params=None):
        """Perform a GET request to the specified url passing the specified
        params.

        .. note:: This method should not be used directly. Use instead
                  the methods defined in
                  :py:class:`pyrundeck.endpoints.EndpointMixins`

        :param url: The URL of the request.
        :param params: (optional) A dictionary containing the parameters
                                  of the request.
        :return: A pair, where the first element is the status code of
                 the request and the second an ``lxml.etree`` object
                 created using the server response.

        """
        return self._perform_request(url, method='GET', params=params)

    def post(self, url, params=None):
        """Perform a POST request to the specified url passing the specified
        params.

        .. note:: This method should not be used directly. Use instead
                  the methods defined in
                  :py:class:`pyrundeck.endpoints.EndpointMixins`

        :param url: The URL of the request.
        :param params: (optional) A dictionary containing the parameters
                       of the request.
        :return: A pair, where the first element is the status code of
                 the request and the second an ``lxml.etree`` object
                 created using the server response.
        """
        return self._perform_request(url, method='POST', params=params)

    def delete(self, url, params=None):
        """Perform a DELETE request to the specified url passing the
        specified params.

        .. note:: This method should not be used directly. Use instead
                  the methods defined in
                  :py:class:`pyrundeck.endpoints.EndpointMixins`

        :param url: The URL of the request.
        :param params: (optional) A dictionary containing the parameters
                       of the request.
        :return: A pair, where the first element is the status code of the
                 request and the second is ``None``.
        """
        return self._perform_request(url, method='DELETE', params=params)
