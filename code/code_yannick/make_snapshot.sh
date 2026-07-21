#!/usr/bin/env bash
# Create a snapshot from the DB and push it to Draco. Run on KSZ.
set -euo pipefail

DRACO="qe75hep@login1.draco.uni-jena.de"
SNAP_ROOT="$HOME/snapshots"
REMOTE_SNAP_ROOT="snapshots"

echo "[1/2] exporting snapshot from DB"
/usr/users/lqe75hep/yannick_hiwi/code/code_yannick/venv/bin/python fetch_posts.py

id="$(basename "$(ls -1d "$SNAP_ROOT"/*/ | sort | tail -1)")"
echo "snapshot: $id"

echo "[2/2] pushing to Draco"
rsync -az "$SNAP_ROOT/$id" "$DRACO:$REMOTE_SNAP_ROOT/"

echo "done: pushed $id to Draco"
