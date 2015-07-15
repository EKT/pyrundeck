Usage
=====

The ``RundeckApiClient``
------------------------
First you need to get an API token from the rundeck installation (see the rundeck documentation_ for instructions).
At the moment PyRundeck only supports token based authentication.

Import the ``RundeckApiClient`` class::

    >>> from pyrundeck import RundeckApiClient

and create an instance::

    >>> rundeck_api_token = 'TtC6519V5tHbfz9mJfQiih6kG4CmPoCA'
    >>> rundeck_api_base_url = 'http://rundeck.example.com'  # The final / should not be given
    >>> rundeck = RundeckApiClient(rundeck_api_token, rundeck_api_base_url)

This object is all you need to interact with the Rundeck installation.

Each endpoint of the rundeck API_ corresponds to a method in the ``RundeckClientApi``. For instance if you need to
see the list of jobs for a specific project you need to call ``rundeck.list_jobs``::

    >>> status, jobs = rundeck.list_jobs(project='API_client_development')

Every method returns a pair: the status code of the request and an instance of ``lxml.etree`` that represents the XML
response of the server::

    >>> status
    200
    >>> ``jobs``
    <Element result at 0x7f54e01c0dd0>
    >>> print etree.tostring(jobs, pretty_print=True)
    <result success="true" apiversion="13">
      <jobs count="4">
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
        <job id="8d5ebfc8-d69a-4808-819e-9c57b7f288d2">
          <name>test_job_2</name>
          <group/>
          <project>API_client_development</project>
          <description/>
        </job>
        <job id="35c01c7a-6957-49fa-970a-d549e6b5f83a">
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
