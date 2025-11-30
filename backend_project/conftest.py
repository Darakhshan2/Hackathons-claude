import sys
import os
import pytest

# Add the parent directory of backend-project (i.e., hackathon/) to sys.path
# This makes 'backend_project' module discoverable when running pytest from the root.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# You can add other fixtures or hooks here if needed
