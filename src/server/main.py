
## Imports
from config import *
from src.print import *
from src.silence import *
from src.folder_utils import move_transcripts_and_audio_files
from src.transcript_utils import *
from datetime import datetime
import pydub
import wave
import os
import io

from flask import Flask
from flask_socketio import SocketIO, emit

# Initialize the Flask app and the SocketIO connection
app: Flask = Flask(__name__)
socketio: SocketIO = SocketIO(app, cors_allowed_origins="*")
joined_chunks: bytes = b''						# To accumulate audio chunks (webm format)
total_audio_duration: float = 0.0				# Total duration of the audio
start_audio_time: float = 0.0					# Start time of the audio (updated when the audio is saved to not save the same audio multiple times)
START_TIME: float = time.perf_counter()			# Start time of the application
START_TIME_STR = datetime.now().strftime("%Y-%m-%d") + "_" + time.strftime("%H-%M-%S", time.localtime(START_TIME))
SERVER_FOLDER: str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

# Get index page
with open(f"{SERVER_FOLDER}/index.html", "r") as f:
	INDEX_PAGE: str = f.read()

# Variables for silence detection
no_silence: int = -10000000										# Value to avoid saving the same silence multiple times
silence_counter: int = no_silence								# Counter for the silence detection
total_files: int = 0											# Total number of files saved
info(f"Server started at {START_TIME_STR}, minimum duration: {MINIMUM_DURATION}s, maximum duration: {MAXIMUM_DURATION}s")


# Function to convert webm frames to wav
def convert_to_wav(frames: bytes, start_duration: float = 0.0) -> tuple[bytes, float]:
	""" Convert webm frames to wav
	Args:
		frames			(bytes):	Webm frames
		start_duration	(float):	Start duration of the audio
	Returns:
		tuple[bytes, float]:		Wav frames and the duration of the audio
	"""
	bytes_io: io.BytesIO = io.BytesIO(frames)
	audio: pydub.AudioSegment = pydub.AudioSegment.from_file(bytes_io, format="webm", start_second=start_duration)
	with io.BytesIO() as output:
		audio.export(output, format="wav")
		return output.getvalue(), len(audio) / 1000

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

@socketio.on('connect')
def handle_connect():
	new_iteration()
	global joined_chunks, total_audio_duration, start_audio_time
	joined_chunks = b""
	total_audio_duration = 0.0
	start_audio_time = 0.0
	print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
	print("Client disconnected")



@socketio.on('audio_stream')
def handle_audio_stream(frames: bytes):
	""" Accumulate the incoming audio data
	Args:
		frames (bytes): Audio data
	"""
	global silence_counter, joined_chunks, total_files, total_audio_duration, start_audio_time
	joined_chunks += frames		# Accumulate the audio frames (webm format)

	# Convert the audio to wav
	try:
		converted_frames, duration = convert_to_wav(joined_chunks, start_duration = total_audio_duration)
		total_audio_duration += duration
	except Exception as e:
		# If an error occurs, reset everything and send errors to the client
		error(f"Error while converting the audio to wav: {e}", exit = False)
		silence_counter = no_silence
		joined_chunks = b""
		total_audio_duration = 0.0
		start_audio_time = 0.0
		emit('error', str(e), broadcast=True)

	# Check if the audio is silent
	if is_silent_wav_bytes(converted_frames):
		if silence_counter != no_silence:
			silence_counter += duration		# Add the duration to the silence counter
			if DEBUG_MODE:
				debug(f"Silence detected (counter: {silence_counter})")
	else:
		silence_counter = 0
		if DEBUG_MODE:
			debug(f"Audio detected (adding {len(frames)} chunks to join, now {len(joined_chunks)} chunks)")

	# Check if the silence duration is reached
	if silence_counter >= SILENCE_DURATION:
		silence_counter = no_silence		# Reset the silence counter

		# If the minimum duration is reached, save the audio to a file
		if (total_audio_duration - start_audio_time) >= MINIMUM_DURATION:

			# Get the audio data as cutted webm from the start time
			bytes_io: io.BytesIO = io.BytesIO(joined_chunks)
			audio_segment: pydub.AudioSegment = pydub.AudioSegment.from_file(bytes_io, format="webm", start_second=start_audio_time)

			# Save the audio to a file
			total_files += 1
			audio_file: str = f"{AUDIO_FOLDER}/server_{total_files}.wav"
			audio_segment.export(audio_file, format="wav")
			info(f"Audio file '{os.path.basename(audio_file)}' saved successfully! Now transcribing...")

			# Reset the start time of the audio
			start_audio_time = total_audio_duration

			# Get the big transcript and send it to the client
			emit('transcript', manage_new_audios(START_TIME_STR))
		


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
	socketio.run(app, port=SERVER_PORT)

	# Move every transcript and audio files in subfolders
	move_transcripts_and_audio_files(START_TIME, START_TIME_STR)
	
	# End of the application
	END_TIME: float = time.perf_counter()			# End time of the application
	info(f"Application ended in {END_TIME - START_TIME:.2f} seconds")
	return

