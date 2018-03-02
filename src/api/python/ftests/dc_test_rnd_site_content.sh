#!/bin/bash

echo "Test fetch content automation script" > ../log/$0.log 2>&1
cd ../ftests && ./dc-kvdb-resource.sh b85ab149a528bd0a024fa0f43e80b5fc b85ab149a528bd0a024fa0f43e80b5fc >> ../log/$0.log 2>&1
