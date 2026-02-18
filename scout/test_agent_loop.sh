#!/bin/bash
# Quick test script for agent loop

echo "🧪 Testing Scout Agent Loop (No Docker)"
echo "========================================"
echo ""

# Check if workspace exists
if [ ! -d "workspace-test" ]; then
    echo "✅ Creating workspace-test/"
    mkdir -p workspace-test
fi

# Check if PRD exists
if [ ! -f "workspace-test/PRD.md" ]; then
    echo "✅ PRD.md already exists in workspace-test/"
else
    echo "✅ PRD.md found"
fi

echo ""
echo "📋 PRD Summary:"
echo "---------------"
head -5 workspace-test/PRD.md
echo "..."
echo ""

# Check dependencies
echo "🔍 Checking dependencies..."
if python -c "import anthropic" 2>/dev/null; then
    echo "   ✅ anthropic package installed"
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "   ⚠️  ANTHROPIC_API_KEY not set (will use simulation mode)"
    else
        echo "   ✅ ANTHROPIC_API_KEY is set"
    fi
else
    echo "   ⚠️  anthropic package not installed (will use simulation mode)"
fi

echo ""
echo "🚀 Running agent loop..."
echo "   Workspace: ./workspace-test"
echo "   Cycles: 3"
echo "   Interval: 5 seconds"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

# Run agent loop
python agent_loop.py --workspace ./workspace-test --cycles 3 --interval 5

echo ""
echo "✅ Test complete!"
echo ""
echo "📊 Results:"
echo "----------"

if [ -f "workspace-test/TODO.md" ]; then
    echo "✅ TODO.md created"
    completed=$(grep -c "\[x\]" workspace-test/TODO.md || echo "0")
    remaining=$(grep -c "\[ \]" workspace-test/TODO.md || echo "0")
    echo "   Completed tasks: $completed"
    echo "   Remaining tasks: $remaining"
else
    echo "⚠️  TODO.md not created"
fi

if [ -d "workspace-test/.git" ]; then
    echo "✅ Git repository initialized"
    commit_count=$(cd workspace-test && git log --oneline 2>/dev/null | wc -l)
    echo "   Commits: $commit_count"
else
    echo "⚠️  Git not initialized"
fi

echo ""
echo "📁 View results:"
echo "   cat workspace-test/TODO.md"
echo "   cd workspace-test && git log --oneline"
echo ""
