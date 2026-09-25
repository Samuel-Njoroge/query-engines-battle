#!/bin/sh

set -e

BUCKET_DATA="benchmark-data"
BUCKET_DRUID="druid-deep-storage"
ACCESS_KEY_ID="GK86b64fdb0310ad7397228be5"
SECRET_ACCESS_KEY="4d1395f9529c8e8b9a7f61d1d31bf46714e30fa1a03ee1600c5b1ba599c131b2"

/garage server &
SERVER_PID=$!

echo "garage-entrypoint: waiting for admin API..."
until /garage status >/dev/null 2>&1; do
  sleep 1
done

if /garage layout show 2>/dev/null | grep -q "Current cluster layout version: 0"; then
  NODE_ID=$(/garage node id -q | cut -d'@' -f1)
  echo "garage-entrypoint: assigning single-node layout for $NODE_ID"
  /garage layout assign -z dc1 -c 1G "$NODE_ID"
  /garage layout apply --version 1
fi

/garage bucket create "$BUCKET_DATA" 2>/dev/null || true
/garage bucket create "$BUCKET_DRUID" 2>/dev/null || true

if ! /garage key list 2>/dev/null | grep -q "$ACCESS_KEY_ID"; then
  echo "garage-entrypoint: importing benchmark access key"
  /garage key import "$ACCESS_KEY_ID" "$SECRET_ACCESS_KEY" --yes -n benchmark-key
fi

/garage bucket allow --read --write "$BUCKET_DATA" --key "$ACCESS_KEY_ID" >/dev/null 2>&1 || true
/garage bucket allow --read --write "$BUCKET_DRUID" --key "$ACCESS_KEY_ID" >/dev/null 2>&1 || true

echo "garage-entrypoint: ready (bucket=$BUCKET_DATA access_key=$ACCESS_KEY_ID)"
wait $SERVER_PID
