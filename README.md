# Latest workflow runs

This gets the result of latest workflow runs for the given workflow.

This takes below parameters
- **-o | --org**: Required. GitHub Organization name
- **-w | --workflow**: Required. Workflow file name. Provide the workflow file name (Ex: *code-ql.yml*)
- **-f | --outfile**: Optional. Output csv file name (Ex: *code-ql-runs.csv*), If not provided, it generates output file as *output.csv*
- **--verbose**: Optional. The flag to run the script in debug mode

This provides csv output with below fields:
- **repo**: Repository name
- **result**: Latest run result. success or failure. It will be empty incase workflow not found in the repo.
- **message**: The error message. It will be empty incase of success result.

This creates output
## How to run

Set the environment variable *GH_TOKEN* with your github token. This should have read access to workflows and its runs.
```
    export GH_TOKEN=$GITHUB_TOKEN
```
#### Example
```
    export GH_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Execute the script

```
    python get-latest-workflow-runs.py --org $ORG_NAME --workflow $WORKFLOW_FILE_NAME
```

#### Example
```
    python get-latest-workflow-runs.py --org my-org --workflow code-ql.yml
    
```
To run with debug mode
```
    python get-latest-workflow-runs.py --org my-org --workflow code-ql.yml --verbose
```
