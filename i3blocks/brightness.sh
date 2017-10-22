#!/bin/bash

# getting input from xbacklight
brightness=$(xbacklight -get);

# full name
printf " %.0f%%\n" $brightness;

# short name
printf " %.0f%%\n" $brightness;