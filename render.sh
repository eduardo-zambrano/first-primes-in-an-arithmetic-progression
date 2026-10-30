#!/bin/bash
# Build the book outside Dropbox, then update _book in place (Dropbox interferes with Quarto's
# intermediate files). Usage: ./render.sh
set -e
cd "$(dirname "$0")"
TMP="$(mktemp -d)"
rsync -a --exclude _book --exclude .quarto --exclude '*_files' --exclude __pycache__ ./ "$TMP/src/"
(cd "$TMP/src" && quarto render)
mkdir -p _book
rsync -a --inplace --delete "$TMP/src/_book/" _book/
rm -rf "$TMP"
echo "Rendered to $(pwd)/_book/index.html"
