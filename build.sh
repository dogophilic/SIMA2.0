#!/bin/bash
# Create bin directory if not present
mkdir -p bin

# Download precompiled wkhtmltopdf binary
curl -L https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6/wkhtmltox-0.12.6-1.bionic_amd64.deb -o wkhtmltox.deb

# Extract only the binary without root access
ar x wkhtmltox.deb
tar -xJf data.tar.xz

# Move wkhtmltopdf binary to bin/ so we can call it
mv usr/local/bin/wkhtmltopdf bin/
chmod +x bin/wkhtmltopdf

# Cleanup
rm -rf usr/ wkhtmltox.deb control.tar.gz data.tar.xz debian-binary
