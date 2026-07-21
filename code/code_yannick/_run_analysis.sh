#!/usr/bin/env bash
# Run sentiment on the most recent snapshot, pull results back. Run on KSZ.
set -euo pipefail

DRACO="qe75hep@login1.draco.uni-jena.de"
SNAP_ROOT="$HOME/snapshots"
REMOTE_SNAP_ROOT="snapshots"
REMOTE_RUN="cd ~/yannick_hiwi/code/code_yannick && sbatch --wait run_slurm.sh"

id="$(basename "$(ls -1d "$SNAP_ROOT"/*/ | sort | tail -1)")"
echo "analyzing snapshot: $id"

echo "[1/2] running sentiment on Draco"
ssh "$DRACO" "$REMOTE_RUN ~/$REMOTE_SNAP_ROOT/$id/data.csv"

echo "[2/2] pulling sentiment.csv back"
rsync -az "$DRACO:$REMOTE_SNAP_ROOT/$id/sentiment.csv" "$SNAP_ROOT/$id/"

echo "done: $SNAP_ROOT/$id now has data.csv + sentiment.csv"
