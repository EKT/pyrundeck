Usage
=====

The ``RundeckApiClient``
------------------------
First you need to get an API token from the rundeck installation (see the
rundeck documentation_ for instructions). At the moment PyRundeck only supports
token based authentication.

Import the ``RundeckApiClient`` class::

    >>> from pyrundeck import RundeckApiClient

and create an instance::

    >>> rundeck_api_token = 'TtC6519V5tHbfz9mJfQiih6kG4CmPoCA'
    >>> rundeck_api_base_url = 'http://rundeck.example.com'
    >>> rundeck = RundeckApiClient(rundeck_api_token, rundeck_api_base_url)

This object is all you need to interact with the Rundeck installation.

Each endpoint of the rundeck API_ corresponds to a method in the
``RundeckClientApi``. For instance if you need to see the list of jobs for a
specific project you need to call ``rundeck.list_jobs``::

    >>> status, jobs = rundeck.list_jobs(project='API_client_development')

Every method returns a pair: the status code of the request and a dictionary
that represents the response of the server::

    >>> status
    200
    >>> jobs
    {'apiversion': '13',
     'jobs': {'count': 3,
      'list': [{'description': None,
        'group': None,
        'id': '3b8a86d5-4fc3-4cc1-95a2-8b51421c2069',
        'name': 'job_with_args',
        'project': 'API_client_development'},
       {'description': None,
        'group': None,
        'id': '78f491e7-714f-44c6-bddb-8b3b3a961ace',
        'name': 'test_job_1',
        'project': 'API_client_development'},
       {'description': None,
        'group': None,
        'id': 'b07b05b0-0a37-4f88-8a51-4bee77ceefb4',
        'name': 'test_job_2',
        'project': 'API_client_development'}]},
     'success': 'true'}


Alternatively by calling the endpoint using the named parameter ``native`` with
the value ``False``, you get an instance of ``lxml.etree`` that corresponds
exactly to the server XML response::

    >>> status, jobs = rundeck.list_jobs(project='API_client_development', native=False)
    >>> status
    200
    >>> jobs
    <Element result at 0x7f488718f488>
    >>> print(etree.tostring(jobs).decode())
    <result success="true" apiversion="13">
      <jobs count="3">
        <job id="3b8a86d5-4fc3-4cc1-95a2-8b51421c2069">
          <name>job_with_args</name>
          <group/>
          <project>API_client_development</project>
          <description/>
        </job>
        <job id="78f491e7-714f-44c6-bddb-8b3b3a961ace">
          <name>test_job_1</name>
          <group/>
          <project>API_client_development</project>
          <description/>
        </job>
        <job id="b07b05b0-0a37-4f88-8a51-4bee77ceefb4">
          <name>test_job_2</name>
          <group/>
          <project>API_client_development</project>
          <description/>
        </job>
      </jobs>
    </result>


For more details on how to handle ``etree`` objects see the lxml_ documentation.

.. _documentation: http://rundeck.org/docs/api/index.html#token-authentication
.. _API: http://rundeck.org/docs/api/
.. _lxml: http://lxml.de/
