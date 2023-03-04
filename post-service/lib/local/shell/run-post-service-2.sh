#!/bin/sh

# When running me:
# - Set FILTER for filtering tests, if desired

if [ -z "${FILTER}" ]; then
  DRIVER=post-service-2 pytest ./post-service
else
  DRIVER=post-service-2 pytest ./post-service -k "${FILTER}"
fi
