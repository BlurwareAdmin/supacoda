"""
# Copyright 2022-2026, Blurware, LLC.  All rights reserved.
CTZ is a developer tool for container development with python. 
"""

import typer
import subprocess
from azure.identity import DefaultAzureCredential

app = typer.Typer()

@app.command(help="Start a new ctz project")
def init(container_name: str, repo: str):
    """
    Generate a new stamp python container. 
        ctz init [container_name] 
        cd [container_name]
        ctz build [container_name]
        ctz publish 
    """
    typer.echo(f"Hello {name}")

@app.command(help="Authenitcate with azure for developmet with ctz.")
def az_auth():
    """
    Authenticate via a device code with wthe az cli. 
    """
    if not service: 
        if service: 
            typer.echo("# Sign in with the AZ CLI. For development only.")
            subprocess.run( ['az', 'login', '--use-device-code'])
            credential = DefaultAzureCredential()
            if credential: 
                typer.echo("You have logged in")
    else: 
        typer.echo("Not yet supported")

@app.command(help="Authenitcate with doppler for developmet with ctz.")
def doppler_auth():
    """
    """
     

@app.command(help="Authenitcate with docker for developmet with ctz.")
def docker_auth():
    """
    Authenticate with a secure token. 
    """
    if not service: 
        if service: 
            typer.echo("# Sign in with the AZ CLI. For development only.")
            subprocess.run( ['az', 'login', '--use-device-code'])
            credential = DefaultAzureCredential()
            if credential: 
                typer.echo("You have logged in")
    else: 
        typer.echo("Not yet supported")


@app.command(help="Deploy a container to docker hub and az container apps.")
def deploy(container_repo_url: str, launch_location: str):
    """
    Deploy your image to Azure Container Apps. This uses az cli underhood so your must be authenticated. 
    Use the command `ctz az_auth` for authenitcation with a device. 
    For more information, see microsoft docs. https://docs.microsoft.com/en-us/azure/developer/python/sdk/authentication-overview
    """
    typer.echo(f"Hello {name}")

@app.command(help="Pull a container & run locally.")
def run(container_repo_url: str):
    """
    Run your container locally for debugging. You must have docker enabled.
    """
    typer.echo(f"Hello {name}")

if __name__ == "__main__":
    app()
