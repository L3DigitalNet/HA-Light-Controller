#!/bin/bash
# Install Home Assistant Development Skills for Claude Code
# Usage: ./install.sh [project|user]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SOURCE="$SCRIPT_DIR/.claude/skills"

if [ ! -d "$SKILLS_SOURCE" ]; then
    echo "Error: Skills directory not found at $SKILLS_SOURCE"
    exit 1
fi

MODE="${1:-project}"

case "$MODE" in
    project)
        TARGET=".claude/skills"
        echo "Installing skills to project directory: $(pwd)/$TARGET"
        ;;
    user)
        TARGET="$HOME/.claude/skills"
        echo "Installing skills to user directory: $TARGET"
        ;;
    *)
        echo "Usage: $0 [project|user]"
        echo "  project  Install to .claude/skills/ in current directory (default)"
        echo "  user     Install to ~/.claude/skills/ for all projects"
        exit 1
        ;;
esac

mkdir -p "$TARGET"

SKILL_COUNT=0
for skill_dir in "$SKILLS_SOURCE"/*/; do
    skill_name=$(basename "$skill_dir")
    echo "  Installing: $skill_name"
    cp -r "$skill_dir" "$TARGET/"
    SKILL_COUNT=$((SKILL_COUNT + 1))
done

echo ""
echo "Installed $SKILL_COUNT skills to $TARGET"
echo ""
echo "Skills available:"
for skill_dir in "$TARGET"/*/; do
    name=$(grep '^name:' "$skill_dir/SKILL.md" 2>/dev/null | head -1 | sed 's/name: *//')
    desc=$(grep '^description:' "$skill_dir/SKILL.md" 2>/dev/null | head -1 | sed 's/description: *//' | cut -c1-80)
    if [ -n "$name" ]; then
        printf "  /%s\n    %s...\n" "$name" "$desc"
    fi
done
echo ""
echo "Restart Claude Code to load the new skills."
