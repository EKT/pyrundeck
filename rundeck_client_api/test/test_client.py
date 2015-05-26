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

import nose.tools as nt
from lxml import etree
import time

from rundeck_client_api import config, api

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"

class TestRundeckClientAPIFunctional:
    def __init__(self):
        with open(config.rundeck_token_file) as fl:
            self.token = fl.readline().strip()

    def setup(self):
        self.client = api.RundeckApiClient(self.token, config.root_url)

    def pretty_print_xml(self, data):
        return etree.tostring(data, pretty_print=True).decode('utf-8')

    def functional_api_test(self):
        # --Import a new job

        # Try to import a good job
        with open(config.rundeck_test_data_dir + '/good_job_definition.xml') as fl:
            good_def = fl.read()
        status_code, data = self.client.import_job(xmlBatch=good_def)

        # Verify that the call returned 200 [OK] and that it successfully created a job
        nt.assert_equal(status_code, 200, 'API call did not return status OK:')
        nt.assert_dict_contains_subset({'count': '1'}, data.find(".//succeeded").attrib, 'Failed to create job.')

        # Try to import a bad job
        with open(config.rundeck_test_data_dir + '/bad_job_definition.xml') as fl:
            bad_def = fl.read()
        status_code, data = self.client.import_job(xmlBatch=bad_def)

        # Verify that the call returned 200 [OK] and that it failed to create a job
        nt.assert_equal(status_code, 200, 'API call did not return status OK')
        nt.assert_dict_contains_subset({'count': '0'}, data.find(".//succeeded").attrib, 'Did not fail to create job.')

        # --Find out what jobs are available
        status_code, data = self.client.list_jobs(project=config.test_project)

        # Verify that the call returned status 200
        nt.assert_equal(status_code, 200, 'API call did not return status OK')

        # Verify that the newly created job exists in the list
        nt.assert_in('test_job_2', [j.text for j in data.iterfind('.//name')],
                     'Created job not found. API response:\n{}'.format(self.pretty_print_xml(data)))

        # --Run the new job
        job_id = None
        for job in data.iter("job"):
            if job.find('.//name').text == 'test_job_2':
                job_id = job.get('id')

        if job_id is None:
            nt.assert_true(False, "job id not found")

        status_code, data = self.client.run_job(id=job_id)

        # Verify that the call returned 200 [OK]
        nt.assert_equal(status_code, 200, 'API call did not return status OK')
        # Verify the results of the run
        nt.assert_dict_contains_subset({'success': 'true'}, data.attrib, 'Failed to run job.')
        execution_id = data.find(".//execution").get('id')

        # Verify that the execution succeeded
        time.sleep(5)  # wait for the execution to finish
        status_code, data = self.client.execution_info(id=execution_id)
        nt.assert_equal(status_code, 200, 'API call did not return status OK')
        nt.assert_dict_contains_subset({'status': 'succeeded'}, data.find('.//execution').attrib)

        # Try to run a nonexistent job
        status_code, data = self.client.run_job(id='123-abc')

        nt.assert_equal(status_code, 404,
                        'Non existent job run, did not return 404:\n{}'.format(data.find(".//message")))
        nt.assert_dict_contains_subset({'error': 'true'}, data.attrib,
                                       'Non existent job run, result is not "error". API returned:{}\n'.format(
                                           self.pretty_print_xml(data)))

        # --Delete the new job
        status_code, data = self.client.delete_job(id=job_id)

        nt.assert_equal(status_code, 204, 'Delete request failed.')

        # Verify that the new job has been deleted
        status_code, data = self.client.list_jobs(data={'project': config.test_project})
        nt.assert_not_in(job_id, [j.get('id') for j in data.iter('job')], 'Job deletion failed.')
