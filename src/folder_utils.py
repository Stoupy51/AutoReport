
# Imports
from config import *

"""
for folder in [TRANSCRIPT_FOLDER, AUDIO_FOLDER]:
	os.makedirs(f"{folder}/{START_TIME_STR}", exist_ok = True)
	files: list[str] = [f"{folder}/{f}" for f in os.listdir(folder) if os.path.isfile(f"{folder}/{f}") and all([c not in f for c in "/\\"])]
	for file in files:
		os.replace(file, f"{folder}/{START_TIME_STR}/{os.path.basename(file)}")

"""
# Function to move folders contents to subfolders
def move_transcripts_and_audio_files(start_time: float, start_time_str: str) -> None:
	""" Move all the transcripts and audio files to subfolders.\n
	If some files cannot be moved, they are moved to a subfolder "unknown".\n
	Args:
		start_time		(float):	Start time of the application
		start_time_str	(str):		Start time of the application as a string
	"""
	for folder in [TRANSCRIPT_FOLDER, AUDIO_FOLDER]:
		
		# Get all the files in the folder
		files: list[str] = [f"{folder}/{f}" for f in os.listdir(folder) if os.path.isfile(f"{folder}/{f}") and all([c not in f for c in "/\\"])]
		
		# Get all files where the date > start_time
		files_to_move: list[str] = [f for f in files if os.path.getctime(f) > start_time]
		if files_to_move:
			os.makedirs(f"{folder}/{start_time_str}", exist_ok = True)
			for file in files_to_move:
				os.replace(file, f"{folder}/{start_time_str}/{os.path.basename(file)}")
		
		# Get all remaining files
		files_to_move = [f for f in files if f not in files_to_move]
		if files_to_move:
			os.makedirs(f"{folder}/{start_time_str}/unknown", exist_ok = True)
			for file in files_to_move:
				os.replace(file, f"{folder}/{start_time_str}/unknown/{os.path.basename(file)}")


