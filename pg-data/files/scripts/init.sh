#!/usr/bin/env bash

if [[ -z $PG_HOST ]];
then
  echo "$PG_HOST is required."
  exit 1
fi

echo "PG_HOST: $PG_HOST"
echo "PG_USER: $PG_USER"

count=0
total=0

for f in $(ls /tmp/data/*.sql);
do
  total=$((total + 1))
  psql -U${PG_USER:-postgres} -h${PG_HOST:-postgres} -f "${f}"
  if [[ $? -eq 0 ]];
  then
    count=$((count + 1))
  fi;
done;

echo "Executed ${count} out of ${total} files"