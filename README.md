# Deploy Frontend Landing Page using Azure Container Services

# Create a Service Principle 
`
az ad sp create-for-rbac --name supacoda --role contributor \
                --scopes /subscriptions/{subscriptions}/resourceGroups/{resourceGroup} \
                --sdk-auth
 `               
