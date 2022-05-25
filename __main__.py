# Copyright 2022-2026, Blurware, LLC.  All rights reserved.

import pulumi
from pulumi_azure_native import containerregistry
from pulumi_azure_native import operationalinsights
from pulumi_azure_native import resources


from pulumi_azure_native import app
import pulumi_docker as docker
import os 
import pulumi_azure as azure

resource_group = resources.ResourceGroup("rg")

workspace = operationalinsights.Workspace("loganalytics",
    resource_group_name=resource_group.name,
    sku=operationalinsights.WorkspaceSkuArgs(name="PerGB2018"),
    retention_in_days=30)

workspace_shared_keys = pulumi.Output.all(resource_group.name, workspace.name) \
    .apply(lambda args: operationalinsights.get_shared_keys(
        resource_group_name=args[0],
        workspace_name=args[1]
    ))

# Standup Managed KubeEnvironment
managed_environment = app.ManagedEnvironment("managedEnvironment",
    app_logs_configuration=app.AppLogsConfigurationArgs(
        log_analytics_configuration=app.LogAnalyticsConfigurationArgs(
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

"""
# Backup Stand up AKS Cluster and managege ArcConfirguration for more control over the cluster. 
kube_env = azure.containerservice.KubernetesCluster("kubeevn",
    location=resource_group.location,
    resource_group_name=resource_group.name,
    dns_prefix="exampleaks1",
    default_node_pool=azure.containerservice.KubernetesClusterDefaultNodePoolArgs(
        name="default",
        node_count=1,
        vm_size="Standard_D2_v2",
    ),
    identity=azure.containerservice.KubernetesClusterIdentityArgs(
        type="SystemAssigned",
    ),
    tags={
        "Environment": "Dev",
    })
"""


container_app = azure_native.app.ContainerApp("containerApp",
    configuration=azure_native.app.ConfigurationArgs(
        dapr=azure_native.app.DaprArgs(
            app_port=3000,
            app_protocol="http",
            enabled=True,
        ),
        ingress=azure_native.app.IngressArgs(

            custom_domains=[
                azure_native.app.CustomDomainArgs(
                    binding_type="SniEnabled",
                    certificate_id="/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/rg/providers/Microsoft.App/managedEnvironments/demokube/certificates/my-certificate-for-my-name-dot-com",
                    name="www.my-name.com",
                ),
                azure_native.app.CustomDomainArgs(
                    binding_type="SniEnabled",
                    certificate_id="/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/rg/providers/Microsoft.App/managedEnvironments/demokube/certificates/my-certificate-for-my-other-name-dot-com",
                    name="www.my-other-name.com",
                ),
            ],
            external=True,
            target_port=3000,
            traffic=[azure_native.app.TrafficWeightArgs(
                label="production",
                revision_name="testcontainerApp0-ab1234",
                weight=100,
            )],
        ),
    ),
    location="East US",
    managed_environment_id=managed_environment.id,
    name="testcontainerApp0",
    resource_group_name="rg",
    template=azure_native.app.TemplateArgs(
        containers=[azure_native.app.ContainerArgs(
            image="repo/testcontainerApp0:v1",
            name="testcontainerApp0",
            probes=[azure_native.app.ContainerAppProbeArgs(
                http_get=azure_native.app.ContainerAppProbeHttpGetArgs(
                    http_headers=[azure_native.app.ContainerAppProbeHttpHeadersArgs(
                        name="Custom-Header",
                        value="Awesome",
                    )],
                    path="/health",
                    port=8080,
                ),
                initial_delay_seconds=3,
                period_seconds=3,
                type="liveness",
            )],
        )],
        scale=azure_native.app.ScaleArgs(
            max_replicas=5,
            min_replicas=1,
            rules=[azure_native.app.ScaleRuleArgs(
                custom=azure_native.app.CustomScaleRuleArgs(
                    metadata={
                        "concurrentRequests": "50",
                    },
                    type="http",
                ),
                name="httpscalingrule",
            )],
        ),
    ))
pulumi.export("url", container_app.configuration.apply(lambda c: c.ingress).apply(lambda i: i.fqdn))

# https://www.pulumi.com/blog/azure-container-apps/
# https://www.pulumi.com/registry/packages/azure-native/api-docs/app/containerapp/