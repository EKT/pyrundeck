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
from pyrundeck.exceptions import RundeckException

__author__ = 'kutsurak'

class EndpointMixins:
    def import_job(self, **params):
        return self.post('{}/api/1/jobs/import'.format(self.root_url), params)

    def list_jobs(self, **params):
        return self.get('{}/api/1/jobs'.format(self.root_url), params)

    def run_job(self, **params):
        job_id = None
        try:
            job_id = params.pop('id')
        except KeyError:
            raise RundeckException(message="job id is required for job execution")

        return self.get('{}/api/1/job/{}/run'.format(self.root_url, job_id))

    def execution_info(self, **params):
        execution_id = None
        try:
            execution_id = params.pop('id')
        except KeyError:
            raise RundeckException(message="execution id is required for execution info")

        return self.get('{}/api/1/execution/{}'.format(self.root_url, execution_id))

    def delete_job(self, **params):
        job_id = None
        try:
            job_id = params.pop('id')
        except KeyError:
            raise RundeckException(message="job id is required for job deletion")

        return self.delete('{}/api/1/job/{}'.format(self.root_url, job_id))
