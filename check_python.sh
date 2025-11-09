#!/bin/bash
# check_python.sh
# Check Python version and architecture compatibility

echo "=== Python Environment Check ==="
echo ""
echo "Python version:"
python3 --version
echo ""
echo "Python path:"
which python3
echo ""
echo "Architecture:"
uname -m
echo ""
echo "OS info:"
cat /etc/os-release 2>/dev/null | head -5 || echo "OS info not available"
echo ""
echo "Pip version:"
pip --version
echo ""
echo "Pip cache info:"
pip cache info 2>/dev/null || echo "No pip cache info"
echo ""

