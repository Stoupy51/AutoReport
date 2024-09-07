
## Configuration file for the application
import os
import pyaudiowpatch as pyaudio

# Basic configuration here
LANGUAGE: str = "fr"							# Language of the audio files and transcripts
KEEP_TRANSCRIPTS: bool = True					# Keep generated transcripts files
KEEP_AUDIO_FILES: bool = False					# Keep generated audio files
UPDATE_REPORT_EVERY_X_SECONDS: int = 60			# Update the report every X seconds (0 to disable: only update at the end of the transcription)
ENABLE_PLAYBACK_DEVICE: bool = True				# Enable the playback device (if False, only the recording device will be used)
DEBUG_MODE: bool = True							# Enable debug mode (more verbose output)
DEBUG_VOLUME: bool = False						# Enable volume debug mode (show the volume of the audio data in comparison to the threshold)

# Technical configuration
RECORDING_DEVICE_NAME: str = "microphone sur"	# Name of the microphone device to search for
PLAYBACK_DEVICE_NAME: str = "casque pour"		# Name of the speakers device to search for (must have input capabilities, e.g., "Stereo Mix")
PLAYBACK_DEVICE_NAME: str = "2nd"
FORMAT = pyaudio.paInt16						# Sample format
RATE = 48000									# Sample rate (Hz)
CHUNK_SIZE = 1024									# Buffer size
SILENCE_THRESHOLD: int = 650					# Threshold for silence detection (to adjust depending on ambient noise)
SILENCE_DURATION: float = 1.0					# Duration (in seconds) of the pause needed to consider a new sentence in the audio file
MINIMUM_DURATION: float = 1.2					# Minimum duration (in seconds) of a sentence in the audio file
MAXIMUM_DURATION: float = 60.0					# Maximum duration (in seconds) of a sentence in the audio file

# Folders
ROOT: str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")	# Root folder of the application (where the py files are located)
TRANSCRIPT_FOLDER: str = f"{ROOT}/transcripts"	# Folder where the transcripts files are stored (temporary or not depending on KEEP_TRANSCRIPTS)
AUDIO_FOLDER: str = f"{ROOT}/audio"				# Folder where the audio files are stored (temporary or not depending on KEEP_AUDIO_FILES)

# Configuration for the report generation
REPORT_EXTENSION: str = "md"					# File extension of the report file (md, txt, ...)
OUTPUT_FOLDER: str = "output"					# Folder where the reports are stored with format "report_YYYY-MM-DD_HH-MM-SS.md"

# Constants for API calls
TRANSCRIPT_API_URL: str = ""					# URL of the API to call for the transcription

