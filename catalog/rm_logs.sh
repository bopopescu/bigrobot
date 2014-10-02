#!/bin/sh
# Permanently remove the old data logs to recover the disk space.

if [ ! -x ../bin/gobot ]; then
    echo "Error: This script must be executed in the bigrobot/catalog/ directory."
    exit 1
fi

rm -rf data.*
