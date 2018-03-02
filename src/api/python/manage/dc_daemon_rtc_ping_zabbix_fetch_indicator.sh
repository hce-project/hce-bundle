#!/bin/bash


LOG_FILE="../log/$0.log"
OUT_FILE="../log/ping.json"

cd /home/hce/hce-node-bundle/api/python/bin

if [ "$1" = "U" ]; then
  #Update counters
  (wget -O "$OUT_FILE.tmp" "http://127.0.0.1/dc-rtg.php?r=%7B%0A%20%20%20%20%22urls%22%3A%20%5B%0A%20%20%20%20%20%20%20%20%7B%0A%20%20%20%20%20%20%20%20%20%20%20%20%22url%22%3A%20%22http%3A%2F%2F127.0.0.1%2Fping.html%22%0A%20%20%20%20%20%20%20%20%7D%0A%20%20%20%20%5D%2C%0A%20%20%20%20%22site_id%22%3A%20%22b85ab149a528bd0a024fa0f43e80b5fc%22%2C%0A%20%20%20%20%22tags%22%3A%20%5B%0A%20%20%20%20%20%20%20%20%22title%22%2C%0A%20%20%20%20%20%20%20%20%22description%22%2C%0A%20%20%20%20%20%20%20%20%22content_encoded%22%2C%0A%20%20%20%20%20%20%20%20%22pdate%22%0A%20%20%20%20%5D%2C%0A%20%20%20%20%22id%22%3A%20%2212345%22%2C%0A%20%20%20%20%22extended%22%3A%20true%0A%7D%0A") 2> $LOG_FILE
  mv $OUT_FILE.tmp $OUT_FILE
else
  ./json-field.py -f "contents:0:data:tagList:__LEN__" < $OUT_FILE
fi
