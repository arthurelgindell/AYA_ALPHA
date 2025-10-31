#!/usr/bin/env python3
"""
Clean workflow JSON for N8N API import
Removes read-only fields and unnecessary properties
"""

import json
import sys
from pathlib import Path

def clean_workflow(workflow_data):
    """Clean workflow data for N8N API import"""
    # Fields to remove (read-only or internal)
    fields_to_remove = [
        'id',           # Read-only, n8n assigns
        'active',       # Read-only, must activate separately
        'createdAt',    # Read-only
        'updatedAt',    # Read-only
        'triggerCount', # Read-only
        'versionId',    # Read-only
        'pinData',      # Not needed for import
        'staticData',   # Can be empty/None
        'tags',         # Can be added later
        'settings.saveManualExecutions',  # Can cause issues
        'settings.saveExecutionProgress', # Can cause issues
    ]
    
    # Create cleaned copy
    cleaned = workflow_data.copy()
    
    # Remove top-level read-only fields
    for field in ['id', 'active', 'createdAt', 'updatedAt', 'triggerCount', 'versionId', 'pinData', 'staticData', 'tags']:
        cleaned.pop(field, None)
    
    # Clean settings - only keep essential ones
    if 'settings' in cleaned:
        settings = cleaned['settings']
        # Keep only essential settings
        cleaned['settings'] = {
            'executionOrder': settings.get('executionOrder', 'v1'),
            # Remove problematic settings
        }
        # Remove if empty
        if not cleaned['settings']:
            del cleaned['settings']
    
    # Ensure nodes have proper structure
    if 'nodes' in cleaned:
        for node in cleaned['nodes']:
            # Remove read-only node fields
            node.pop('id', None)
            # Ensure parameters exist
            if 'parameters' not in node:
                node['parameters'] = {}
    
    return cleaned

def main():
    if len(sys.argv) < 2:
        print("Usage: clean_workflow_for_import.py <workflow.json>")
        sys.exit(1)
    
    workflow_file = Path(sys.argv[1])
    
    if not workflow_file.exists():
        print(f"File not found: {workflow_file}")
        sys.exit(1)
    
    # Load workflow
    with open(workflow_file) as f:
        workflow_data = json.load(f)
    
    # Clean workflow
    cleaned = clean_workflow(workflow_data)
    
    # Output cleaned workflow
    print(json.dumps(cleaned, indent=2))

if __name__ == '__main__':
    main()

