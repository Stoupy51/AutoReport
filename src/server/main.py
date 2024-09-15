
## Imports
from config import *
from src.print import *
from src.silence import *
from src.folder_utils import move_transcripts_and_audio_files
from src.transcript_utils import *
from datetime import datetime
import zipfile
import pydub
import os
import io

from flask import Flask
from flask_talisman import Talisman
from flask_socketio import SocketIO, emit

# Prepare content security policy
csp = {
	"default-src": ["'self'"],
	"script-src": [
		"'self'",
		"https://cdnjs.cloudflare.com",
		"'unsafe-inline'",			# Allow inline scripts
	],
	"style-src": [
		"'self'",
		"https://cdnjs.cloudflare.com",
		"'unsafe-inline'",			# Allow inline styles
	],
	"connect-src": [
		"'self'",
		"ws://localhost:" + str(SERVER_PORT),
		"https://cdnjs.cloudflare.com",
	]
}

# Initialize the Flask app and the SocketIO connection
app: Flask = Flask(__name__)
Talisman(app, force_https=True, content_security_policy=csp)
socketio: SocketIO = SocketIO(app, cors_allowed_origins="*")
joined_chunks: bytes = b''						# To accumulate audio chunks (mimeType received from the client)
total_audio_duration: float = 0.0				# Total duration of the audio
start_audio_time: float = 0.0					# Start time of the audio (updated when the audio is saved to not save the same audio multiple times)
mimeType: str = "audio/webm"					# MIME type of the audio (webm format by default)
START_TIME: float = time.perf_counter()			# Start time of the application
START_TIME_STR = datetime.now().strftime("%Y-%m-%d") + "_" + time.strftime("%H-%M-%S", time.localtime(START_TIME))
SERVER_FOLDER: str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

# Get index page
with open(f"{SERVER_FOLDER}/index.html", "r") as f:
	INDEX_PAGE: str = f.read().replace("__SLEEP_INTERVAL__", str(int(SLEEP_INTERVAL * 1000)))

# Variables for silence detection
current_threshold: int = -60					# Current threshold for silence detection
not_initialized_silence: int = -10000000		# Value to avoid saving the same silence multiple times
silence_counter: int = not_initialized_silence	# Counter for the silence detection
total_files: int = 0							# Total number of files saved
info(f"Server started at {START_TIME_STR}, minimum duration: {MINIMUM_DURATION}s, maximum duration: {MAXIMUM_DURATION}s")


# Function to convert mimeType frames to wav
def convert_to_wav(frames: bytes, start_duration: float = 0.0) -> tuple[bytes, float]:
	""" Convert the frames of mimeType to wav
	Args:
		frames			(bytes):	Audio frames
		start_duration	(float):	Start duration of the audio
	Returns:
		tuple[bytes, float]:		Wav frames and the duration of the audio
	"""
	bytes_io: io.BytesIO = io.BytesIO(frames)
	audio: pydub.AudioSegment = pydub.AudioSegment.from_file(bytes_io, format=mimeType.split('/')[-1], start_second=start_duration)
	with io.BytesIO() as output:
		audio.export(output, format="wav")
		return output.getvalue(), audio.duration_seconds

@app.route('/')
def index():
	return INDEX_PAGE

@app.route('/new_iteration')
def new_iteration():
	""" Move all the transcripts to a subfolder and update the start time """
	global START_TIME
	global START_TIME_STR

	# Move every transcript and audio files in subfolders
	move_transcripts_and_audio_files(START_TIME, START_TIME_STR)

	# Update the start time
	old_start_time: str = START_TIME_STR
	START_TIME = time.perf_counter()			# Start time of the application
	START_TIME_STR = datetime.now().strftime("%Y-%m-%d") + "_" + time.strftime("%H-%M-%S", time.localtime(START_TIME))

	# Return the message
	return f"Start time updated from {old_start_time} to {START_TIME_STR}!"

@app.route('/request_report')
def request_report():
	""" Request the report to be generated and send to the client """
	return make_the_report(START_TIME_STR, not_final = True)

@app.route('/request_outputs')
def request_outputs():
	""" Request the outputs to be sent to the client (everything in the output folder) """
	# Prepare a zip file with the outputs
	output_zip: str = f"{OUTPUT_FOLDER}/outputs_{START_TIME_STR}.zip"
	with zipfile.ZipFile(output_zip, 'w') as zipf:
		for root, _, files in os.walk(OUTPUT_FOLDER):
			for file in files:
				if not file.endswith(".zip"):
					zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), OUTPUT_FOLDER))
	
	# Send the zip file content to the client
	with open(output_zip, "rb") as f:
		return f.read()
	
	# Remove the zip file
	os.remove(output_zip)

@socketio.on('connect')
def handle_connect():
	new_iteration()
	global joined_chunks, total_audio_duration, start_audio_time
	joined_chunks = b""
	total_audio_duration = 0.0
	start_audio_time = 0.0
	print("Client connected")
	emit('threshold', current_threshold)	# Send the current threshold to the client

@socketio.on('disconnect')
def handle_disconnect():
	print("Client disconnected")

@socketio.on('mimeType')
def handle_mimeType(mime: str):
	""" Handle the MIME type of the audio
	Args:
		mime (str): MIME type of the audio
	"""
	global mimeType
	mimeType = mime
	info(f"New MIME type received: {mimeType}")

@socketio.on('update_threshold')
def handle_update_threshold(threshold: str):
	""" Update the threshold for silence detection
	Args:
		threshold (int): New threshold for silence detection
	"""
	global current_threshold
	current_threshold = int(threshold)
	info(f"New threshold received: {current_threshold} dB")


@socketio.on('audio_stream')
def handle_audio_stream(frames: bytes):
	""" Accumulate the incoming audio data
	Args:
		frames (bytes): Audio data
	"""
	global silence_counter, joined_chunks, total_files, total_audio_duration, start_audio_time

	# Convert the audio to wav
	try:
		converted_frames, duration = convert_to_wav(joined_chunks + frames, start_duration = total_audio_duration)
		total_audio_duration += duration
	except Exception as e:
		# If an error occurs, reset everything and send errors to the client
		error(f"Error while converting the audio to wav: {e}", exit = False)
		silence_counter = not_initialized_silence
		joined_chunks = b""
		total_audio_duration = 0.0
		start_audio_time = 0.0
		emit('error', str(e))
		return

	# Accumulate the audio frames (mimeType received from the client)
	joined_chunks += frames

	# Check if the audio is silent
	silence, volume = is_silent_wav_bytes(converted_frames, current_threshold)
	if silence:
		if silence_counter != not_initialized_silence:
			silence_counter += duration		# Add the duration to the silence counter
			if DEBUG_MODE:
				debug(f"Silence detected (counter: {silence_counter})")
		else:
			# Do not register the silence at the beginning of the audio (when silence_counter == not_initialized_silence)
			start_audio_time = total_audio_duration
	else:
		silence_counter = 0
		if DEBUG_MODE:
			debug(f"Audio detected (adding {len(frames)} chunks to join, now {len(joined_chunks)} chunks)")
	
	# Send the volume to the client
	emit('volume', volume)

	# Check if the silence duration is reached, or the maximum duration is reached
	this_chunk_duration: float = (total_audio_duration - start_audio_time)
	if silence_counter >= SILENCE_DURATION or this_chunk_duration >= MAXIMUM_DURATION:
		silence_counter = not_initialized_silence		# Reset the silence counter

		# If the minimum duration is reached, save the audio to a file
		if this_chunk_duration >= MINIMUM_DURATION:

			# Get the audio data as cutted from the start time
			bytes_io: io.BytesIO = io.BytesIO(joined_chunks)
			audio_segment: pydub.AudioSegment = pydub.AudioSegment.from_file(bytes_io, format=mimeType.split('/')[-1], start_second=start_audio_time)

			# Save the audio to a file
			total_files += 1
			audio_file: str = f"{AUDIO_FOLDER}/server_{total_files}.wav"
			audio_segment.export(audio_file, format="wav")
			info(f"Audio file '{os.path.basename(audio_file)}' saved successfully! Now transcribing...")

			# Reset the start time of the audio
			start_audio_time = total_audio_duration

			# Get the big transcript and send it to the client
			emit('transcript', manage_new_audios(START_TIME_STR).strip())
		


# Main function
def server_main():
	global START_TIME, START_TIME_STR

	# If OpenAI API is used but no key is provided, exit the application
	if USE_OPENAI_API and len(OPENAI_KEYS) == 0:
		error("No OpenAI API key provided, please add at least one key to the 'open_ai.keys' file or disable the API in the configuration file")
		return

	# Make folders if they do not exist
	for folder in [TRANSCRIPT_FOLDER, AUDIO_FOLDER, OUTPUT_FOLDER]:
		os.makedirs(folder, exist_ok = True)

	# Move every transcript and audio files in subfolders
	move_transcripts_and_audio_files(START_TIME, START_TIME_STR)

	# Start the main loop
	socketio.run(app, host=SERVER_HOST, port=SERVER_PORT, ssl_context="adhoc")

	# Move every transcript and audio files in subfolders
	move_transcripts_and_audio_files(START_TIME, START_TIME_STR)
	
	# End of the application
	END_TIME: float = time.perf_counter()			# End time of the application
	info(f"Application ended in {END_TIME - START_TIME:.2f} seconds")
	return

