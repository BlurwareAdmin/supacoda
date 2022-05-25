"""
# Copyright 2022-2026, Blurware, LLC.  All rights reserved.
CTZ is a developer tool for container development with python. 
"""

import os
import subprocess

#Third-Party Imports 
from azure.identity._credentials.azure_cli import AzureCliCredential
from azure.identity import DefaultAzureCredential
import typer
import pulumi
from pulumi import automation as auto

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
        typer.echo("You are already logged in!")
    else: 
        try: 
            typer.echo("You will need to sign in to continue. Default is device login. For Trusted Local Development Only.")
            subprocess.run( ['az', 'login', '--use-device-code'])
        except: 
            typer.echo('Login Failed.') 

@app.command(help="Authenitcate with azure for developmet with ctz.")
def az_auth():
    """
    Authenticate via a device code with wthe az cli. 
    """
    try: 
        login()
    except Exception as e: 
        return e

def prep_containerapps():
    login()
    
    # 
    out = subprocess.run(
        [
        'az' , 'extension', 'add' , 
        '--name', 'containerapp', 
        '--upgrade']
    )
    out = subprocess.run(
        [
        'az' ,'provider' ,'register' ,
        '--namespace' ,'Microsoft.OperationalInsights'
        ]
    )
    check_env = [
        'RESOURCE_GROUP', 'LOCATION', 'CONTAINERAPPS_ENVIRONMENT'
    ]
    checks = [
        os.getenv(x) is not None for x in check_env
    ]
    if False in checks:
        print(checks)
        typer.Abort()
    else: 
        # Create the resource g
        out = subprocess.Popen([
            'az', 'group',  'create' ,
            '--name' ,f"{os.getenv('RESOURCE_GROUP')}", 
            '--location' , f"{os.getenv('LOCATION')}"
        ])
        env = subprocess.Popen(
        ['az', 'containerapp', 'env', 'create' ,
            '--name' , f"{os.getenv('CONTAINERAPPS_ENVIRONMENT')}",
            '--resource-group', f"{os.getenv('RESOURCE_GROUP')}", 
            '--location', f"{os.getenv('LOCATION')}"
        ])
        print(out)

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
