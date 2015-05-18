with open('../rundeck/rundeck_client_api/local_rundeck_token') as fl:
    token = fl.readline().strip()

# Export jobs from project
root_url = 'http://192.168.50.2:4400'
requests.get(root_url + 'api/12/jobs/export?project=API_client_development',
             headers={'X-Rundeck-Auth-Token': token})

# Import jobs
with open('./job_definition') as fl:
    xml_jobs = fl.read()
requests.post(root_url + 'api/12/jobs/import', headers={'X-Rundeck-Auth-Token': token},
              data={'xmlBatch': xml_jobs})

# List all jobs
requests.get(root_url + 'api/12/jobs?project=API_client_development',
             headers={'X-Rundeck-Auth-Token': token})
