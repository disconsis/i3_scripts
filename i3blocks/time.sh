#!/bin/bash

# using date command formatting to extract time in the format of <Hour, Minute, AM/PM>
time=$(date '+%I:%M %p')

# full name
echo $time;

# short name
echo $time;