#!/bin/bash
echo "Starting AUXIP Snapshost cleanup"
  SNAPSHOT_PATH=/adg_data/auxip_snapshot
  num_snaps=$(find $SNAPSHOT_PATH -type f | awk -F _ '{print $NF;}' | sort -u | wc -l)
  if (( $num_snaps > 2 )); then
  	oldest_snap=$(find ${SNAPSHOT_PATH} -type f | awk -F _ '{print $NF;}' | sort -u | head  -1 )
	echo "Oldest snap found: $oldest_snap"
	echo "up to date part: ${oldest_snap:0:8}"
  	find ${SNAPSHOT_PATH} -name \*catalogue_${oldest_snap:0:8}\*.json | xargs sudo rm
	echo "Deleted snap $oldest_snap"
  fi
echo "DONE"
