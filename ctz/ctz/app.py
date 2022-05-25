"""
# Copyright 2022-2026, Blurware, LLC.  All rights reserved.

CTZ is a developer tool for container development with python. 
"""

import os
import subprocess

#Third-Party Imports 
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
import typer
import pulumi


def stamp_azure_client():
    """
    Creates a stamp client to perform actions against the azure api
    Reads env variables. Use ARM_XXXX. If ARM env found it will map them 
    to AZURE_XXX. 

    Rec: Use a secrets manager that can inject without the use of env, json, yaml, etc..  
    I prefer doppler or other secret management solutions like azure key vault but any should work. 
    Auth for Python SDK: https://docs.microsoft.com/en-us/python/api/overview/azure/resources?view=azure-python
    Doppler CLI: https://docs.doppler.com/docs/cli
    """
    os.environ['AZURE_TENANT_ID'] = os.environ.get('ARM_TENANT_ID', None) 
    os.environ['AZURE_CLIENT_ID'] = os.environ.get('ARM_CLIENT_ID', None)
    os.environ['AZURE_CLIENT_SECRET'] = os.environ.get('ARM_CLIENT_SECRET', None)
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID'] = os.environ.get("ARM_SUBSCRIPTION_ID", None)
    credentials = DefaultAzureCredential()
    client = ResourceManagementClient(credentials, subscription_id)
    return client

app = typer.Typer()

creds = DefaultAzureCredential()

@app.command(help="Start a new ctz project")
def init(
    container_name: str = "", 
    template: str = typer.Argument(
        "https://github.com/BlurwareAdmin/supacoda.git", 
        envvar="GIT_TEMPLATE")):
    """
    Generate a new stamp python container. 
        ctz init [container_name] 
    """
   
    subprocess.Popen(['git', 'clone', template])
    subprocess.Popen(['mv', 'supacoda/', container_name])

def login(): 
    if not check_login(): 
        subprocess.run( ['az', 'login', '--use-device-code'])

def check_login():
    user_meta = subprocess.run(
        [
        'az',
        'ad', 'signed-in-user', 'show', 
        '--output', 'json', 
        '--query', 'accountEnabled', 
        '--only-show-errors'], 
        capture_output=True, text=True
    ) 
    if user_meta.stdout is not None: 
       return True
    else: 
        return False




@app.command(help="Authenitcate with azure for developmet with ctz.")
def az_auth():
    """
    Authenticate via a device code with wthe az cli. 
    """
    try: 
        login()
    except Exception as e: 
        return e

@app.command(help="Enable Required Container APIs")
def enable_apis(name: str = "", all: bool = False ):
    resource_client = stamp_azure_client()
    if all:
        result_list = resource_client.providers.list()
        for provider in result_list:
            resource_client.providers.register(provider.namespace)
            break
    elif name:
         resource_client.providers.register(name)
         typer.echo(f"{name} enabled" )

@app.command(help="Install Extensions")
def isntall_extension(name: str = ""):
     subprocess.run([
         'az' , 'extension' ,'add' ,'--name', f'{name}' ,'--upgrade'
         ], stdout=subprocess.DEVNULL)

@app.command(help="Deploy a container to docker hub and az container apps.")
def deploy(
    container_repo_url: str = "" , 
    launch_location: str = "westus"):
    """
    Deploy your image to Azure Container Apps. This uses az cli underhood so your must be authenticated. 
    Use the command `ctz az_auth` for authenitcation with a device. 
    For more information, see microsoft docs. https://docs.microsoft.com/en-us/azure/developer/python/sdk/authentication-overview
    """
    
    typer.echo(f"Deploy Container App with {container_repo_url}")
    prep_containerapps()

@app.command(help="Pull a container & run locally.")
def run(container_repo_url: str):
    """
    Run your container locally for debugging. You must have docker enabled.
    """
    typer.echo(f"Hello {name}")

if __name__ == "__main__":
    app()

