#!/usr/bin/env python3
import os
import sys
from src import loader
from src.utils.logger import logger, NO_FLAGS

dir_path = os.path.abspath(sys.argv[0])
if os.path.isdir(dir_path): # if user ran "python ~/path/to/pytris-effect/"
	os.chdir(dir_path)
else: # if user ran "python ~/path/to/pytris-effect/__main__.py"
	os.chdir(os.path.dirname(dir_path))

logger.set_flags(NO_FLAGS)

game = loader.Loader()
game.run()
