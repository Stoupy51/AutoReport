
## Imports
from config import *
from src.print import *
from src.silence import *
from src.transcript_utils import *
from datetime import datetime
import pydub
import wave
import os
import io

from flask import Flask
from flask_socketio import SocketIO, emit

# Initialize the Flask app and the SocketIO connection
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
joined_chunks = b''  # To accumulate audio chunks
START_TIME: float = time.perf_counter()			# Start time of the application
START_TIME_STR = datetime.now().strftime("%Y-%m-%d") + "_" + time.strftime("%H-%M-%S", time.localtime(START_TIME))
SERVER_FOLDER: str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

# Variables for silence detection
chunks_per_second: float = RATE									# Number of chunks per second
minimum_chunks: float = MINIMUM_DURATION * chunks_per_second	# Number of chunks needed to reach the minimum duration
maximum_chunks: float = MAXIMUM_DURATION * chunks_per_second	# Number of chunks needed to reach the maximum duration
no_silence: int = -10000000										# Value to avoid saving the same silence multiple times
silence_counter: int = no_silence								# Counter for the silence detection
total_files: int = 0											# Total number of files saved


# Function to convert webm frames to wav
def convert_to_wav(frames: bytes) -> bytes:
	""" Convert webm frames to wav
	Args:
		frames (bytes): Webm frames
	Returns:
		bytes: Wav frames
	"""
	bytes_io: io.BytesIO = io.BytesIO(frames)
	audio: pydub.AudioSegment = pydub.AudioSegment.from_file(bytes_io, format="webm")
	with io.BytesIO() as output:
		audio.export(output, format="wav")
		return output.getvalue()

@app.route('/')
def index():
	index_file: str = f"{SERVER_FOLDER}/index.html"
	with open(index_file, "r") as f:
		return f.read()

@app.route('/new_iteration')
def new_iteration():
	""" Move all the transcripts to a subfolder and update the start time """
	global START_TIME
	global START_TIME_STR

	# Move all the transcripts to a subfolder
	files: list[str] = [f"{TRANSCRIPT_FOLDER}/{f}" for f in os.listdir(TRANSCRIPT_FOLDER) if os.path.isfile(f"{TRANSCRIPT_FOLDER}/{f}") and all([c not in f for c in "/\\"])]
	subfolder: str = f"{TRANSCRIPT_FOLDER}/{START_TIME_STR}"
	os.makedirs(subfolder, exist_ok = True)
	for file in files:
		os.replace(file, f"{subfolder}/{os.path.basename(file)}")

	# Update the start time
	old_start_time: str = START_TIME_STR
	START_TIME = time.perf_counter()			# Start time of the application
	START_TIME_STR = datetime.now().strftime("%Y-%m-%d") + "_" + time.strftime("%H-%M-%S", time.localtime(START_TIME))

	# Return the message
	return f"Start time updated from {old_start_time} to {START_TIME_STR}, and moved {len(files)} transcripts to the subfolder '{subfolder}'!"

@app.route('/request_report')
def request_report():
	""" Request the report to be generated and send to the client """
	return make_the_report(START_TIME_STR, not_final = True)

@socketio.on('connect')
def handle_connect():
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
	global silence_counter, joined_chunks, total_files
	frames = convert_to_wav(frames)

	# Check if the audio is silent
	if is_silent(frames):
		if silence_counter != no_silence:
			silence_counter += SLEEP_INTERVAL
			if DEBUG_MODE:
				debug(f"Silence detected (counter: {silence_counter})")
	else:
		joined_chunks += frames
		silence_counter = 0
		if DEBUG_MODE:
			debug(f"Audio detected (adding {len(frames)} chunks to join, now {len(joined_chunks)} chunks)")

	# Check if the silence duration is reached
	if silence_counter >= SILENCE_DURATION:
		joined_chunks += frames

		# If the minimum duration is reached, save the audio to a file
		if len(joined_chunks) >= minimum_chunks:

			# Save the audio to a file
			total_files += 1
			audio_file: str = f"{AUDIO_FOLDER}/server_{total_files}.wav"
			with wave.open(audio_file, 'wb') as wf:
				wf.setnchannels(1)
				wf.setsampwidth(2)
				wf.setframerate(RATE)
				wf.writeframes(joined_chunks)

			# Transcript the audio
			if not DEBUG_MODE:
				debug(f"Silence detected stream, transcripting the audio...")
			else:
				debug(f"Silence detected stream, transcripting the audio ({len(joined_chunks)} chunks > {minimum_chunks} chunks)...")
			manage_new_audios(START_TIME_STR)

			# Get the big transcript and send it to the client
			emit('transcript', make_the_big_transcript(START_TIME_STR))

		# Reset the silence counter and the chunks to join
		silence_counter = no_silence
		joined_chunks = b""


# Main function
def server_main():

	# If OpenAI API is used but no key is provided, exit the application
	if USE_OPENAI_API and len(OPENAI_KEYS) == 0:
		error("No OpenAI API key provided, please add at least one key to the 'open_ai.keys' file or disable the API in the configuration file")
		return

	# Make folders if they do not exist
	for folder in [TRANSCRIPT_FOLDER, AUDIO_FOLDER, OUTPUT_FOLDER]:
		os.makedirs(folder, exist_ok = True)
	
	# For the transcript and audio folders, move all the files into a subfolder "unknown"
	for folder in [TRANSCRIPT_FOLDER, AUDIO_FOLDER]:
		os.makedirs(f"{folder}/unknown", exist_ok = True)
		files: list[str] = [f"{folder}/{f}" for f in os.listdir(folder) if os.path.isfile(f"{folder}/{f}") and all([c not in f for c in "/\\"])]
		for file in files:
			os.replace(file, f"{folder}/unknown/{os.path.basename(file)}")

	# Start the main loop
	socketio.run(app, port=SERVER_PORT, debug=True)
	
	# End of the application
	END_TIME: float = time.perf_counter()			# End time of the application
	info(f"Application ended in {END_TIME - START_TIME:.2f} seconds")
	return

