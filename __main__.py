# Copyright 2022, Blurware, LLC.  All rights reserved.
import os
import pulumi
import pulumi_azure_native as azure_native
import pulumi_azure as azure

resource_group = azure_native.resources.ResourceGroup("rg")

workspace = azure_native.operationalinsights.Workspace("loganalytics",
    resource_group_name=resource_group.name,
    sku=azure_native.operationalinsights.WorkspaceSkuArgs(name="PerGB2018"),
    retention_in_days=30)

workspace_shared_keys = pulumi.Output.all(resource_group.name, workspace.name) \
    .apply(lambda args: azure_native.operationalinsights.get_shared_keys(
        resource_group_name=args[0],
        workspace_name=args[1]
    ))

# Standup Managed KubeEnvironment
managed_environment = azure_native.app.ManagedEnvironment("managedEnvironment",
    app_logs_configuration=azure_native.app.AppLogsConfigurationArgs(
        log_analytics_configuration=azure_native.app.LogAnalyticsConfigurationArgs(
            customer_id=workspace.customer_id, 
            shared_key=workspace_shared_keys.apply(lambda r: r.primary_shared_key)
        ),
        destination="log-analytics"
    ),
    dapr_ai_connection_string="InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://northcentralus-0.in.applicationinsights.azure.com/",
    location="East US",
    name="testcontainerenv",
    resource_group_name=resource_group.name,
    zone_redundant=False)


container_app = azure_native.app.ContainerApp("supacoda",
    resource_group_name=resource_group.name,
    managed_environment_id=managed_environment.id, 
    configuration=azure_native.app.ConfigurationArgs(
        ingress=azure_native.app.IngressArgs(
            external=True,
            target_port=8020),
        registries=[azure_native.app.RegistryCredentialsArgs(
            server="docker.io", 
            username="harleydev", 
            password_secret_ref="dockerToken"
         )], 
         secrets= [azure_native.app.SecretArgs(
            name="dockerToken", 
            value=os.getenv('DOCKERHUB_TOKEN')
         )]
    ), 
    template=azure_native.app.TemplateArgs(
            containers=[azure_native.app.ContainerArgs(
                name="supacoda",
                image="harleydev/supacoda:latest"
            )]
        )
    
)
pulumi.export("url", container_app.configuration.apply(lambda c: c.ingress).apply(lambda i: i.fqdn))

# https://www.pulumi.com/blog/azure-container-apps/
# https://www.pulumi.com/registry/packages/azure-native/api-docs/app/containerapp/