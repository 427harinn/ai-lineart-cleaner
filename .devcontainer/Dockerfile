FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

USER root
WORKDIR /workspaces/ai-lineart-cleaner

COPY requirements.txt requirements-dev.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-dev.txt

USER vscode
