
## Configuration file for the application
import os
import pyaudio

# Basic configuration here
LANGUAGE: str = "fr"							# Language of the audio files and transcripts
KEEP_TRANSCRIPTS: bool = True					# Keep generated transcripts files
KEEP_AUDIO_FILES: bool = False					# Keep generated audio files
UPDATE_REPORT_EVERY_X_SECONDS: int = 60			# Update the report every X seconds (0 to disable: only update at the end of the transcription)

# Technical configuration
RECORDING_DEVICE_NAME: str = "microphone sur"	# Name of the microphone device to search for
PLAYBACK_DEVICE_NAME: str = "casque pour"		# Name of the speakers device to search for
FORMAT = pyaudio.paInt16						# Sample format
CHANNELS = 1									# Mono channel
RATE = 44100									# Sample rate (Hz)
CHUNK = 1024									# Buffer size
SILENCE_THRESHOLD: int = 1000					# Threshold for silence detection (to adjust depending on ambient noise)
SILENCE_DURATION: float = 1.0					# Duration (in seconds) of the pause needed to consider a new sentence in the audio file
MINIMUM_DURATION: float = 1.2					# Minimum duration (in seconds) of a sentence in the audio file

# Folders
ROOT: str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")	# Root folder of the application (where the py files are located)
TRANSCRIPT_FOLDER: str = f"{ROOT}/transcripts"	# Folder where the transcripts files are stored (temporary or not depending on KEEP_TRANSCRIPTS)
AUDIO_FOLDER: str = f"{ROOT}/audio"				# Folder where the audio files are stored (temporary or not depending on KEEP_AUDIO_FILES)

# Configuration for the report generation
REPORT_EXTENSION: str = "md"					# File extension of the report file (md, txt, ...)
OUTPUT_FOLDER: str = "output"					# Folder where the reports are stored with format "report_YYYY-MM-DD_HH-MM-SS.md"

# Constants for API calls
TRANSCRIPT_API_URL: str = ""					# URL of the API to call for the transcription

