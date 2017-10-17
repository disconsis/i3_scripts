#!/bin/bash

# /proc/net/dev output for wlp58s0 interface
networkInformation=$(cat /proc/net/dev | grep wlp58s0);

# received bytes at time T
receivedBytes=$(cat /proc/net/dev | grep wlp58s0 | awk -v N=2 '{print $2}');

# Transmitted bytes at time T
transmittedBytes=$(cat /proc/net/dev | grep wlp58s0 | awk -v N=2 '{print $10}');

# pause for 1 second
sleep 1s

# received bytes at time T + 1
newReceivedBytes=$(cat /proc/net/dev | grep wlp58s0 | awk -v N=2 '{print $2}');

# Transmitted bytes at times T + 1
newTransmittedBytes=$(cat /proc/net/dev | grep wlp58s0 | awk -v N=2 '{print $10}');

# Convertion to KiloBytes
receivedKBs=$(echo "($newReceivedBytes-$receivedBytes)/1024" | bc -l | awk '{print int($1)}');

# Convertion to KiloBytes
transmittedKBs=$(echo "($newTransmittedBytes-$transmittedBytes)/1024" | bc -l | awk '{print int($1)}');

# fullname
echo " $transmittedKBs KB/s   $receivedKBs KB/s";

# shortname
echo " $transmittedKBs KB/s   $receivedKBs KB/s";

# color
echo "#EEFF41"