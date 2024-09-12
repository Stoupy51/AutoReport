from flask import Flask, render_template
from flask_socketio import SocketIO
import os
import wave
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variables to store audio chunks
audio_chunks = []
start_time = time.time()

# Directory to save audio files
audio_dir = "audio_files"
if not os.path.exists(audio_dir):
	os.makedirs(audio_dir)

@app.route('/')
def index():
	with open('test/index.html', 'r') as f:
		return f.read()

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
	global audio_chunks, start_time

	# Append incoming audio data chunk
	audio_chunks.append(data)

	# Check if 5 seconds have passed
	if time.time() - start_time >= 5:
		# Save the audio file
		save_audio_file(audio_chunks)
		audio_chunks = []  # Reset chunks
		start_time = time.time()  # Reset timer

def convert_to_wav(frames: bytes) -> bytes:
	import random
	random_number = random.randint(0, 1000000)
	raw_filename: str = f"audio_{random_number}.webm"
	wav_filename: str = f"audio_{random_number}.wav"
	
	# Save the audio data to a file
	with open(raw_filename, "wb") as f:
		f.write(frames)
	
	# Convert the audio file to .wav format
	import subprocess
	subprocess.run(["ffmpeg", "-i", raw_filename, wav_filename])

	# Read the .wav file
	with open(wav_filename, "rb") as f:
		wav_data = f.read()
	os.remove(raw_filename)
	os.remove(wav_filename)
	return wav_data
	

def save_audio_file(chunks):
	from pydub import AudioSegment
	from io import BytesIO
	# Save audio as .wav file
	timestamp = int(time.time())
	filename = os.path.join(audio_dir, f"audio_{timestamp}.wav")

	# Combine chunks into a single bytes stream
	combined_audio = b''.join(chunks)

	# Convert the audio to .wav format
	converted_audio = convert_to_wav(combined_audio)

	# Save the audio to a file
	with open(filename, 'wb') as f:
		f.write(converted_audio)
	

	print(f"Saved {filename}")

if __name__ == '__main__':
	socketio.run(app, debug=True)

