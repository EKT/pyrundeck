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

"""This module contains the mappings methods to the API endpoints.

Each endpoint of the API should have a corresponding method in the
class ``EndpointMixins``. The class ``RundeckApiClient`` subclasses
this class in order to inherit the defined methods.
"""

from pyrundeck.exceptions import RundeckException
from pyrundeck.xml2native import parse

__author__ = "Panagiotis Koutsourakis <kutsurak@ekt.gr>"


class EndpointMixins(object):
    """This class contains all the API endpoints in order not to clutter
    the :class:`pyrundeck.api.RundeckApiClient`.  Note that
    :code:`RundeckApiClient` is a subclass of *this* class, so it
    inherits all the methods defined here.

    The idea is to define a method for every endpoint in the Rundeck
    API, taking the appropriate parameters. For more details consult
    the Rundeck API `documentation
    <http://rundeck.org/docs/api/index.html>`_.

    .. warning:: This class should not be instantiated and used
                 directly. Trying to do so will definitely result in
                 runtime errors.
    """
    def import_job(self, native=False, **params):
        """Implements `import job`_

        .. _import job: http://rundeck.org/docs/api/index.html#importing-jobs
        """
        status, xml = self.post('{}/api/1/jobs/import'
                                       .format(self.root_url), params)
        if native:
            return status, parse(xml)
        else:
            return status, xml

    def list_jobs(self, native=False, **params):
        """Implements `list jobs`_

        .. _list jobs: http://rundeck.org/docs/api/index.html#listing-jobs
        """
        status, xml = self.get('{}/api/1/jobs'.format(self.root_url),
                                      params)
        if native:
            return status, parse(xml)
        else:
            return status, xml

    def run_job(self, native=False, **params):
        """Implements `run job`_

        .. _run job: http://rundeck.org/docs/api/index.html#running-a-job
        """
        try:
            job_id = params.pop('id')

            status, xml = self.get('{}/api/1/job/{}/run'
                                          .format(self.root_url, job_id),
                                          params)
            if native:
                return status, parse(xml)
            else:
                return status, xml
        except KeyError:
            raise RundeckException("job id is required for job execution")

    def execution_info(self, native=False, **params):
        """Implements `execution info`_

        .. _execution info: http://rundeck.org/docs/api/index.html#execution-info
        """
        try:
            execution_id = params.pop('id')

            status, xml =  self.get('{}/api/1/execution/{}'
                                    .format(self.root_url, execution_id),
                                    params)
            if native:
                return status, parse(xml)
            else:
                return status, xml

        except KeyError:
            raise RundeckException("execution id is required for "
                                   "execution info")

    def delete_job(self, **params):
        """Implements `delete job`_

        .. _delete job: http://rundeck.org/docs/api/index.html#deleting-a-job-definition
        """
        try:
            job_id = params.pop('id')

            status, xml = self.delete('{}/api/1/job/{}'.format(self.root_url,
                                                               job_id), params)
            return status, xml
        except KeyError:
            raise RundeckException("job id is required for job deletion")
