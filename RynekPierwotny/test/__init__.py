import sys
from pathlib import Path

try:   
    sys.path.append(str(Path(sys.path[0]).parent))
    from . import test_RynekPierwotny 
except: 
    from RynekPierwotny.test import test_RynekPierwotny    