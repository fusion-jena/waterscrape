#!/usr/bin/env bash
# Run one full cycle from KSZ.
set -euo pipefail

DRACO="qe75hep@login1.draco.uni-jena.de"
SNAP_ROOT="$HOME/snapshots"
REMOTE_SNAP_ROOT="~/snapshots"
REMOTE_RUN="cd ~/yannick_hiwi/code/code_yannick && sbatch --wait run_slurm.sh"

echo "[1/4] exporting snapshot on KSZ"
/usr/users/lqe75hep/yannick_hiwi/code/code_yannick/venv/bin/python fetch_posts.py

id="$(basename "$(ls -1d "$SNAP_ROOT"/*/ | sort | tail -1)")"
echo "snapshot: $id"

echo "DRACO=[$DRACO] SNAP_ROOT=[$SNAP_ROOT] id=[$id]"
echo "[2/4] pushing to Draco"
rsync -az "$SNAP_ROOT/$id" "$DRACO:$REMOTE_SNAP_ROOT/"

echo "[3/4] running sentiment on Draco"
ssh "$DRACO" "$REMOTE_RUN ~/REMOTE_SNAP_ROOT/$id/data.csv"

echo "[4/4] pulling sentiment.csv back"
rsync -az "$DRACO:$REMOTE_SNAP_ROOT/$id/sentiment.csv" "$SNAP_ROOT/$id/"

echo "done: $SNAP_ROOT/$id now has data.csv + sentiment.csv" 
