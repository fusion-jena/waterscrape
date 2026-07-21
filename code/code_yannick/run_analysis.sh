#!/usr/bin/env bash
# Auxiliary scrip to _run_analysis.sh in the background, logging into the snapshot's folder.
set -euo pipefail

SNAP_ROOT="$HOME/snapshots"
id="$(basename "$(ls -1d "$SNAP_ROOT"/*/ | sort | tail -1)")"

nohup bash _run_analysis.sh "$id" > "$SNAP_ROOT/$id/analysis.log" 2>&1 &

echo "launched analysis for $id"
echo "log: $SNAP_ROOT/$id/analysis.log"
