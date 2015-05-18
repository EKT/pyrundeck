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

# from unittest.mock import patch
import nose.tools as nt
from lxml import etree


from rundeck_client_api import config


class TestRundeckClientAPIFunctional:
    def setup(self):
        with open(config.rundeck_token_file) as fl:
            token = fl.readline().strip()
            self.client = RundeckApiClient(token, config.root_url)

    def pretty_print_xml(self, data):
        return etree.tostring(data, pretty_print=True).decode('utf-8')

    def functional_api_test(self, mock_get):
        # Find what endpoints are available
        endpoints = self.client.endpoints
        nt.assert_is_not_none(endpoints)

        # --Import a new job

        # Verify that the import job endpoint is implemented
        nt.assert_is_not_none(endpoints.get('import_job'))

        # Try to import a good job
        with open('test_data/good_job_definition.xml') as fl:
            good_job = fl.read()
        status_code, data = self.client.perform_request('import_job', data={'xmlBatch': good_job})

        # Verify that the call returned 200 [OK] and that it successfully created a job
        nt.assert_equal(status_code, 200, 'API call did not return status OK:\n{}'.format(data.find(".//message").text))
        nt.assert_dict_contains_subset({'count': '1'}, data.find(".//succeeded"),
                                       'Failed to create job. Error message:\n{}'.format(data.find('.//error').text))

        # Try to import a bad job
        with open('test_data/bad_job_definition.xml') as fl:
            bad_job = fl.read()
        status_code, data = self.client.perform_request('import_job', data={'xmlBatch': bad_job})

        # Verify that the call returned 200 [OK] and that it failed to create a job
        nt.assert_equal(status_code, 200, 'API call did not return status OK:\n{}'.format(data.find(".//message").text))
        nt.assert_dict_contains_subset({'count': '0'}, data.find(".//succeeded"),
                                       'Did not fail to create job. API returned:\n{}'.format(self.pretty_print_xml(
                                           data)))

        # --Find out what jobs are available

        # Verify that the list jobs endpoint is implemented
        nt.assert_is_not_none(endpoints.get('list_jobs'))
        status_code, data = self.client.perform_request('list_jobs', project='')

        # Verify that the call returned status 200
        nt.assert_equal(status_code, 200, 'API call did not return status OK:\n{}'.format(data.find(".//message").text))

        # Verify that the newly created job exists in the list
        nt.assert_in('test_job_2', [j.name for j in data.iterfind('.//name')],
                     'Created job not found. API response:\n{}'.format(self.pretty_print_xml(data)))

        # Run the new job

        # Verify the results of the run

        # Delete the new job

        # Get the available jobs

        # Verify that the new job has been deleted


