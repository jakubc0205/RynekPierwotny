import sys  

from .RynekPierwotny import __main 

try:  
    sys.exit(__main()) 
except Exception as e: 
    print(e)    