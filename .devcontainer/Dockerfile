FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

USER root

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

USER vscode
