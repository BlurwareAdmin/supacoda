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


container_app = app.ContainerApp("containerApp",
    configuration=app.ConfigurationArgs(
        dapr=app.DaprArgs(
            app_port=8020,
            app_protocol="http",
            enabled=True,
        ),
        ingress=app.IngressArgs(
            external=True,
            target_port=8020,
            traffic=[app.TrafficWeightArgs(
                label="production",
                revision_name="testcontainerApp0-ab1234",
                weight=100,
            )],
        ),
    ),
    location="East US",
    managed_environment_id=managed_environment.id,
    name="supacoda",
    resource_group_name=resource_group.name,
    template=app.TemplateArgs(
        containers=[app.ContainerArgs(
            image="harleydev/supacoda:latest",
            name="supacoda",
            probes=[app.ContainerAppProbeArgs(
                http_get=app.ContainerAppProbeHttpGetArgs(
                    http_headers=[app.ContainerAppProbeHttpHeadersArgs(
                        name="Custom-Header",
                        value="Awesome",
                    )],
                    path="/health",
                    port=8020,
                ),
                initial_delay_seconds=3,
                period_seconds=3,
                type="liveness",
            )],
        )],
        scale=app.ScaleArgs(
            max_replicas=5,
            min_replicas=1,
            rules=[app.ScaleRuleArgs(
                custom=app.CustomScaleRuleArgs(
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