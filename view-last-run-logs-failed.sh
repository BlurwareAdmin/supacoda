export GH_RUN_ID=$(gh run list --workflow deploy.yml --json databaseId | jq ".[0].databaseId") 
gh run view $GH_RUN_ID --log-failed