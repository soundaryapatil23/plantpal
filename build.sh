#!/usr/bin/env bash
# Build script (Python equivalent of "mvn clean package").
# Usage: ./build.sh [version]    e.g. ./build.sh 42  or  ./build.sh $(git rev-parse --short HEAD)
set -euo pipefail

VERSION="${1:-dev}"
NAME="plantpal-${VERSION}"

rm -rf dist build
mkdir -p dist build/"${NAME}"

cp app/app.py app/requirements.txt build/"${NAME}"/
echo "${VERSION}" > build/"${NAME}"/VERSION

tar -czf dist/"${NAME}".tar.gz -C build "${NAME}"
echo "Built artifact: dist/${NAME}.tar.gz"
