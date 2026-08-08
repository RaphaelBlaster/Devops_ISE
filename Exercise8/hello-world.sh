#!/bin/sh
# Build step script for the Freestyle job Hello-World-Job.
# The job runs it with: sh hello-world.sh
set -eu

echo "Hello, Jenkins!"
echo "Current date: $(date '+%Y-%m-%d %H:%M:%S %Z')"
