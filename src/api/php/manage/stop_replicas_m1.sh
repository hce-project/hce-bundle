#!/bin/bash

./config.sh m1 s

./stop_replicas.sh

./config.sh n s
