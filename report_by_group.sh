#!/bin/bash

cd /opt/Oxya
./manage_group.py  -l | grep -v -e total -e ^- | sed -e "s/   .*//" | while read line
do
  ./report_by_group.py -g "$line" -e
done
