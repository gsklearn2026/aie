#!/bin/bash

echo "Rolling back to blue environment..."

sed -i 's/backend_green/backend_blue/g' nginx/nginx.conf
docker-compose restart nginx

echo "Rollback complete! Traffic back on blue."
