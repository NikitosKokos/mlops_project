#!/bin/bash

# Clean script to list jobs without warnings

echo "📋 Listing training jobs in gun-detection-exp..."
echo ""

# Method 1: Suppress stderr warnings
az ml job list --query "[?experiment_name=='gun-detection-exp' && type=='command'].{Name:name, DisplayName:display_name, Status:status}" -o table 2>/dev/null

echo ""
echo "💡 If no jobs shown, they might be child jobs of pipeline jobs."
echo "   Try listing all jobs:"
echo "   az ml job list --query \"[?experiment_name=='gun-detection-exp'].{Name:name, Type:type, DisplayName:display_name, Status:status}\" -o table 2>/dev/null"
