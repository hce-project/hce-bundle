#!/bin/bash

ps aux 2>&1 | grep crawler | tee ps_before_kill.txt | awk '{print $2}' | xargs kill -9
ps aux 2>&1 | grep crawler | tee ps_after_kill.txt | awk '{print $2}' | xargs kill -9
