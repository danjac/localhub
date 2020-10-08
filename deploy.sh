#!/usr/bin/env bash

set -e

echo "Building assets..."
docker-compose run --rm -e BASE_URL assets yarn build

echo "Deploying assets to S3..."
docker-compose run --rm \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    -e AWS_STORAGE_BUCKET_NAME \
    -e DJANGO_SETTINGS_MODULE=localhub.config.settings.deploy \
    django ./manage.py collectstatic --noinput

echo "Deploying to Heroku..."
git push heroku master



