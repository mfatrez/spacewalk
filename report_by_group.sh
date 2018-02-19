#!/bin/bash

cd /opt/Oxya
./manage_group.py  -l | grep -v -e total -e ^- | sed -e "s/   .*//" | while read line
do
  echo "start trt : $line"
  ./report_by_group.py -g "$line" -d -e
  echo "end trt  : $line"
  echo ""
done
