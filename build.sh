#!/usr/bin/env bash

# Install wkhtmltopdf manually from local .deb file
apt-get update
apt-get install -y xfonts-75dpi xfonts-base
dpkg -i ./bin/wkhtmltox_0.12.6-1.bionic_amd64.deb
