#!/bin/bash
# Demo Tests Suit files permissions set

GOOSE='/tmp/goose'

if [[ ! -d $GOOSE ]]
then
    mkdir $GOOSE
fi

chmod 777 ~/hce-node-bundle/usr/bin/*.sh
chmod 777 ~/hce-node-bundle/api/php/manage/*.sh
chmod 777 ~/hce-node-bundle/api/php/tests/*.sh
chmod 777 ~/hce-node-bundle/api/php/cfg/*.sh
chmod 777 ~/hce-node-bundle/api/php/bin/*
chmod 777 ~/hce-node-bundle/api/python/bin/*
chmod 777 ~/hce-node-bundle/api/python/manage/*
chmod 777 ~/hce-node-bundle/api/python/ftests/*
chmod 777 ~/hce-node-bundle/api/python/tests/*
chmod 777 /tmp/goose
chmod 777 ~/hce-node-bundle/usr/bin/deploy/*.sh
chmod 777 ~/hce-node-bundle/usr/bin/deploy/cfg/*.sh
chmod 777 ~/hce-node-bundle/usr/bin/deploy/php/*.php
chmod 777 ~/hce-node-bundle/usr/bin/deploy/python/*.py
