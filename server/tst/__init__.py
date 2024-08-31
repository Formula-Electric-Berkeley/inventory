import os
import sys


_project_path = os.getcwd()

_source_path = os.path.join(_project_path, 'src')
sys.path.append(_source_path)

_test_path = os.path.join(_project_path, 'tst')
sys.path.append(_test_path)
