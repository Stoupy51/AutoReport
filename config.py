
## Configuration file for the application
import os

# Basic configuration here
LANGUAGE: str = "fr-FR"							# Language of the audio files and transcripts, an RFC5646 language tag like 'en-US' or 'fr-FR'
KEEP_TRANSCRIPTS: bool = True					# Keep generated transcripts files
KEEP_AUDIO_FILES: bool = True					# Keep generated audio files
UPDATE_REPORT_EVERY_X_SECONDS: int = 60			# Update the report every X seconds (0 to disable: only update at the end of the transcription)
ENABLE_PLAYBACK_DEVICE: bool = True				# Enable the playback device (if False, only the recording device will be used)
DEBUG_MODE: bool = True							# Enable debug mode (more verbose output)
DEBUG_VOLUME: bool = False						# Enable volume debug mode (show the volume of the audio data in comparison to the threshold)
MAX_WORDS_PER_LINE: int = 20					# Maximum number of words per line in the transcript

# Technical configuration
RECORDING_DEVICE_NAME: str = "microphone sur"	# Name of the microphone device to search for
PLAYBACK_DEVICE_NAME: str = "casque pour"		# Name of the speakers device to search for (must have input capabilities, e.g., "Stereo Mix")
RATE = 48000									# Sample rate (Hz)
CHUNK_SIZE = 1024								# Buffer size
SILENCE_THRESHOLD: int = 650					# Threshold for silence detection (to adjust depending on ambient noise)
SILENCE_DURATION: float = 0.6					# Duration (in seconds) of the pause needed to consider a new sentence in the audio file
MINIMUM_DURATION: float = 1.2					# Minimum duration (in seconds) of a sentence in the audio file
MAXIMUM_DURATION: float = 30.0					# Maximum duration (in seconds) of a sentence in the audio file
SLEEP_INTERVAL: float = 0.2						# Time to sleep between each iteration of the main loop (in seconds)
SERVER_HOST: str = "0.0.0.0"					# Host of the server (if used)
SERVER_PORT: int = 14444						# Port of the server (if used)

# Folders
ROOT: str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")	# Root folder of the application (where the py files are located)
TRANSCRIPT_FOLDER: str = f"{ROOT}/transcripts"	# Folder where the transcripts files are stored (temporary or not depending on KEEP_TRANSCRIPTS)
AUDIO_FOLDER: str = f"{ROOT}/audio"				# Folder where the audio files are stored (temporary or not depending on KEEP_AUDIO_FILES)

# Configuration for the report generation
REPORT_EXTENSION: str = "md"					# File extension of the report file (md, txt, ...)
OUTPUT_FOLDER: str = f"{ROOT}/output"			# Folder where the reports are stored with format "report_YYYY-MM-DD_HH-MM-SS.md"

# OpenAI API configuration
USE_OPENAI_API: bool = False						# Use the OpenAI API to generate the transcripts and the report (requires API keys)
OPENAI_API_KEYS: str = f"{ROOT}/open_ai.keys"	# Path to a file containing a list of API keys to use (one per line), if the first one is exhausted, the next one will be used
OPENAI_KEYS: list[str] = []						# List of API keys to use
if USE_OPENAI_API and os.path.exists(OPENAI_API_KEYS):
	with open(OPENAI_API_KEYS, "r") as f:
		OPENAI_KEYS += f.read().strip().split("\n")

