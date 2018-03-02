#!/bin/bash

./config.sh r s

./stop_replicas.sh

./config.sh n s
