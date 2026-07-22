#!/usr/bin/env bash
# Create a snapshot from the DB and push it to Draco. Run on KSZ.
set -euo pipefail

DRACO="qe75hep@login1.draco.uni-jena.de"
SNAP_ROOT="$HOME/snapshots"
REMOTE_SNAP_ROOT="snapshots"

# Optional: path to the dashboard repo checkout. If unset, the dashboard CSVs
# are simply not produced and the pipeline runs as normal.
DASHBOARD_REPO="${DASHBOARD_REPO:-}"

echo "[1/3] exporting snapshot from DB"
/usr/users/lqe75hep/yannick_hiwi/code/code_yannick/venv/bin/python fetch_posts.py

id="$(basename "$(ls -1d "$SNAP_ROOT"/*/ | sort | tail -1)")"
echo "snapshot: $id"

echo "[2/3] exporting dashboard CSVs"
if [[ -n "$DASHBOARD_REPO" && -f "$DASHBOARD_REPO/export_dashboard.py" ]]; then
  # run from the repo dir so `import queries` and its .env resolve
  (cd "$DASHBOARD_REPO" && /usr/users/lqe75hep/waterviz/venv/bin/python export_dashboard.py "$SNAP_ROOT/$id")
else
  echo "  skipped (DASHBOARD_REPO not set)"
fi

echo "[3/3] pushing to Draco"
rsync -az "$SNAP_ROOT/$id" "$DRACO:$REMOTE_SNAP_ROOT/"

echo "done: pushed $id to Draco"
