git commit -am "Update"
git push
sleep 10
unset GH_RUN_ID
export GH_RUN_ID=$(gh run list --workflow deploy.yml --json databaseId | jq ".[0].databaseId") 
gh run watch $GH_RUN_ID