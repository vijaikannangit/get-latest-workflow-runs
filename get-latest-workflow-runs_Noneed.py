import requests
import argparse
import os
import csv

parser = argparse.ArgumentParser(prog='Get Latest Workflow Runs',
                                 description='Gets the latest workflow runs for the repositories in the organization for the given workflow id')
parser.add_argument(
    '-o',
    '--org',
    required=False,
    help='Provide Org name')

parser.add_argument(
    '-u',
    '--user',
    required=False,
    help='Provide user name')

parser.add_argument(
    '-w',
    '--workflow',
    required=True,
    help='Provide workflow file name (ex: code-ql.yml)')

parser.add_argument(
    '-f',
    '--outfile',
    required=True,
    help='Provide output file name (ex: code-ql-runs.yml)')

parser.add_argument('--verbose', action='store_true')

args = parser.parse_args()
workflow_id = args.workflow
org = args.org
user = args.user
outfile = args.outfile
verbose = args.verbose
token = os.environ["GH_TOKEN"]
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}
owner = org if org else user
owner_path = f"orgs/{org}" if org else f"users/{user}"
output_file_name = outfile if outfile else "output.csv"

def print_debug(msg):
    if verbose:
        print(f"verbose: {msg}")

def get_items_with_pagination(url):
    output = []
    page = 1
    while True:
        print_debug(f"Getting list of items in page: {page}")
        url = f"{url}?" if '?' not in url else f"{url}&"
        url = f"{url}per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        # print(f"{url}, status : {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            output.extend(data)
            page += 1
        else:
            break
    return output

def get_repositories():
    """Get the list of repositories for the organization

    Args:
        enterprise_org (str) : Source GitHub Enterprise Organization
        access_token (str) : Source GitHub Token(PAT)
        
    Returns:
        dict: (json data) : repos for the organization
    """
    print_debug(f"Getting list of repos")
    return get_items_with_pagination(f"https://api.github.com/{owner_path}/repos")

def get_latest_workflow_run(repo):
    output = {}
    output['repo'] = repo
    response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs?page=1&per_page=1', headers=headers)
    if response.status_code == 200:
        workflow_runs = response.json()['workflow_runs']
        if workflow_runs and len(workflow_runs) > 0:
            latest_run = workflow_runs[0]
            run_id = latest_run['id']
            output.update(get_run_info(repo, run_id))
        else:
            output.update(get_error_run_info("No runs found for the workflow"))
    else:
        output.update(get_error_run_info("Workflow not found"))
    print_debug(output)
    return output

def get_run_info(repo, run_id):
    output = {}
    response_run = requests.get(f'https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}', headers=headers)
    if response_run.status_code == 200:
        run_info = response_run.json()
        conclusion = run_info["conclusion"]
        output['result'] = conclusion
        output['message'] = run_info["message"] if conclusion == 'failure' else ""
    else:
        output = get_error_run_info(f"Error in getting workflow run details: {response_run.status_code}")
    return output

def get_error_run_info(message):
    output = {}
    output['result'] = ""
    output['message'] = message
    return output

def write_csv(data, filename):
    print_debug("Writing to CSV")
    with open(filename, 'w', newline='') as csv_file:
        fieldnames = ['repo', 'result', 'message']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print_debug("Writing to CSV completed")

repos = get_repositories()
repo_run_list = []
for repo in repos:
    repo_name = repo['name']
    print_debug(f"Processing repo: {owner}/{repo_name}")
    repo_run_list.append(get_latest_workflow_run(repo_name))
write_csv(repo_run_list, output_file_name)