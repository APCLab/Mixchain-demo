#!/bin/sh

while [ 1 ]
do
    bitcoin-cli -datadir=. generate 1
    sleep 300
done
