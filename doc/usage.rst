Usage
=====

The ``RundeckApiClient``
------------------------
First you need to get an API token from the rundeck installation (see the rundeck documentation_ for instructions).
At the moment PyRundeck only supports token based authentication.

Import the ``RundeckApiClient`` class::

    from pyrundeck.api import RundeckApiClient

and create an instance::

    rundeck_api_token = 'TtC6519V5tHbfz9mJfQiih6kG4CmPoCA'
    rundeck_api_base_url = 'http://rundeck.example.com'  # The final / should not be given
    rundeck = RundeckApiClient(rundeck_api_token, rundeck_api_base_url)

This object is all you need to interact with the Rundeck installation.

Each endpoint of the rundeck API_ corresponds to a method in the ``RundeckClientApi``. For instance if you need to
see the list of jobs for a specific project you need to call ``rundeck.list_jobs``::

    status, jobs = rundeck.list_jobs(project='my_rundeck_project')

Every method returns a pair: the status code of the request and an instance of ``lxml.etree`` that represents the XML
response of the server::

    ``jobs``


.. _documentation: http://rundeck.org/docs/api/index.html#token-authentication
.. _API: http://rundeck.org/docs/api/
