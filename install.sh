#!/usr/bin/env bash
set -euo pipefail

CANVAS_DIR="$(cd "$(dirname "$0")" && pwd)"

# Install command
mkdir -p ~/.claude/commands/canvas
sed "s|{{CANVAS_DIR}}|${CANVAS_DIR}|g" \
  "${CANVAS_DIR}/install/commands/canvas/startup.md" \
  > ~/.claude/commands/canvas/startup.md

# Install skill
mkdir -p ~/.claude/skills/canvas
sed "s|{{CANVAS_DIR}}|${CANVAS_DIR}|g" \
  "${CANVAS_DIR}/install/skills/canvas/SKILL.md" \
  > ~/.claude/skills/canvas/SKILL.md

echo "Canvas installed from ${CANVAS_DIR}"
echo ""
echo "Add to ~/.claude/CLAUDE.md:"
echo ""
echo "  ## Canvas — Browser Visualization"
echo "  Use \`/canvas:startup\` to launch a browser canvas for charts, tables, and metrics."
echo "  The canvas server lives at \`${CANVAS_DIR}\` — invoke the skill for API details."
