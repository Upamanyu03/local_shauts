import sys
import os

# Define the interpreter path relative to the current directory
# INTERP = "/home/mechmanager/workshop/Workshop_backend/bin/python3.11"
INTERP = os.path.join(os.getcwd(), 'bin', 'python3.11')

# Check if the current Python interpreter matches INTERP
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Import and run your application
from run import app as application
