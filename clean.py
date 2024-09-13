
# Imports
from config import *
from src.print import *
import shutil

# Clean folders
for folder in [TRANSCRIPT_FOLDER, AUDIO_FOLDER, OUTPUT_FOLDER]:
	try:
		shutil.rmtree(folder)
	except Exception as e:
		error(f"Error while cleaning the folder: {e}", exit = False)

