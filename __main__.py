# Copyright 2022-2026, Blurware, LLC.  All rights reserved.

import pulumi
from pulumi_azure_native import containerregistry
from pulumi_azure_native import operationalinsights
from pulumi_azure_native import resources
from pulumi_azure_native import web
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


container_app = web.ContainerApp("containerApp",
    configuration=web.ConfigurationArgs(
        ingress=web.IngressArgs(
            external=True,
            target_port=3000,
        ),
    ),
    kind="containerApp",
    kube_environment_id=kube_env.id,
    location="East US",
    name="supacoda",
    resource_group_name=resource_group.name,
    template=web.TemplateArgs(
        containers=[web.ContainerArgs(
            image=f"{os.getenv('DOCKERHUB_USERNAME')}/supacoda:latest",
            name="supacoda",
        )],
        scale=web.ScaleArgs(
            max_replicas=5,
            min_replicas=1,
            rules=[web.ScaleRuleArgs(
                custom=web.CustomScaleRuleArgs(
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
