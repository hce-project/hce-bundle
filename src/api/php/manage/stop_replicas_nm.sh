#!/bin/bash

./config.sh n s

./stop_replicas.sh

./config.sh m s

./stop_replicas.sh

./config.sh n s
