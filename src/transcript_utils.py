
## Imports
from config import *
from src.print import *
import os
import time
from pydub import AudioSegment
import speech_recognition as sr

# Function to make api call
def call_api(audio_file: str) -> str|None:
	""" Call the API to get the transcript of the audio file\n
	Args:
		audio_file (str): Path to the audio file
	Returns:
		str: Transcript of the audio file if successful
	"""
	try:
		# Call the API to get the transcript
		recognizer: sr.Recognizer = sr.Recognizer()
		with sr.AudioFile(audio_file) as source:
			audio_data = recognizer.record(source)
		
		# Get the transcript
		try:
			transcript: str = recognizer.recognize_google(audio_data, language=LANGUAGE)

			# Add a new line every MAX_WORDS_PER_LINE words
			words: list[str] = transcript.split(" ")
			for i in range(MAX_WORDS_PER_LINE, len(words), MAX_WORDS_PER_LINE):
				words.insert(i, "\n")
			transcript = " ".join(words).replace("\n ", "\n")

			# Return the transcript
			return transcript
		except sr.UnknownValueError as e:
			warning(f"Google Speech Recognition could not understand the audio file '{os.path.basename(audio_file)}': {e}")
			return None
		except Exception as e:
			error(f"Error while recognizing the audio file '{os.path.basename(audio_file)}': {e}", exit = False)
			return None

	except Exception as e:
		error(f"Error while calling the API for the audio file '{os.path.basename(audio_file)}': {e}", exit = False)
		return None

# Function to manage new audios
def manage_new_audios(start_time: str):
	""" Manage the new audio files in the audio folder\n
	Args:
		start_time (str): Start time of the application (for the report generation)
	"""
	# Get the list of audio files ordered by creation date
	audio_files: list[str] = [f"{AUDIO_FOLDER}/{f}" for f in os.listdir(AUDIO_FOLDER) if f.endswith(".wav")]
	audio_files.sort(key=lambda x: os.path.getctime(x))

	# Process the audio files that are not already in the list
	for audio_file in audio_files:
		equivalent_transcript: str = f"{TRANSCRIPT_FOLDER}/{os.path.basename(audio_file).replace('.wav', '.txt')}"
		if DEBUG_MODE:
			debug(f"Processing the audio file '{audio_file}' with the equivalent transcript '{equivalent_transcript}'")
		
		# Check if the transcript already exists
		if os.path.exists(equivalent_transcript):
			continue

		# Call the API to get the transcript
		transcript: str = call_api(audio_file)

		# Remove the audio file if needed
		if not KEEP_AUDIO_FILES:
			os.remove(audio_file)
			info(f"Audio file '{os.path.basename(audio_file)}' removed successfully!")

		# Skip if the transcript is None
		if transcript is None:
			warning(f"Error while calling the API for the audio file '{os.path.basename(audio_file)}', skipping...")
			continue

		# Save the transcript to a file
		with open(equivalent_transcript, "w", encoding="utf-8") as f:
			f.write(transcript)
		info(f"Transcript '{os.path.basename(equivalent_transcript)}' saved successfully!")
	
	# Make one big transcript
	make_the_big_transcript(start_time)


# Function to make one big transcript
def make_the_big_transcript(start_time: str) -> str:
	""" Make one big transcript from the audio files
	Args:
		start_time (str): Start time of the application (for the report generation)
	Returns:
		str: The big transcript
	"""
	# Get the list of transcript files ordered by creation date
	transcript_files: list[str] = [f"{TRANSCRIPT_FOLDER}/{f}" for f in os.listdir(TRANSCRIPT_FOLDER) if f.endswith(".txt")]
	transcript_files.sort(key=lambda x: os.path.getctime(x))

	# Create the big transcript
	big_transcript: str = ""
	previous_type: str = ""
	for transcript_file in transcript_files:

		# Get the type of the transcript (recording or playback)
		transcript_type: str = os.path.basename(transcript_file).split("_")[0]

		# Add a separator if needed
		if previous_type != transcript_type:
			big_transcript += f"\n{transcript_type.title()}:\n"
			previous_type = transcript_type
		
		# Add the transcript to the big transcript
		with open(transcript_file, "r", encoding="utf-8") as f:
			big_transcript += f.read().strip() + "\n"
		
		# Remove the transcript file if needed
		if not KEEP_TRANSCRIPTS:
			os.remove(transcript_file)
			info(f"Transcript file '{os.path.basename(transcript_file)}' removed successfully!")
		
	# Save the big transcript to a file
	with open(f"{OUTPUT_FOLDER}/full_transcript_{start_time}.txt", "w", encoding="utf-8") as f:
		f.write(big_transcript)
	info(f"Big transcript 'full_transcript_{start_time}.txt' saved successfully!")

	# Return the big transcript
	return big_transcript


# Function to make the report
def make_the_report(start_time: str, not_final: bool = True):
	""" Make the report of the application
	Args:
		start_time (str): Start time of the application
		not_final (bool): If the report is not final (if final, we delete the transcript files if needed)
	"""
	# Make the big transcript
	transcript = make_the_big_transcript(start_time)

	# TODO: Use AI to summarize the transcript





