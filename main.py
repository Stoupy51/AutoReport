
## Imports
from config import *
from src.print import *
from src.audio_stream import AudioStream
from src.audio_utils import is_silent, save_audio, find_device
from src.transcript_utils import manage_new_audios

# Main function
def main():
	START_TIME: float = time.perf_counter()			# Start time of the application
	START_TIME_STR: str = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(START_TIME))

	# Ask to delete previous audio and transcript folders
	if os.path.exists(TRANSCRIPT_FOLDER) or os.path.exists(AUDIO_FOLDER):
		if input("Do you want to delete the previous audio and transcript folders? (y/N) ").lower() == "y":
			import shutil
			for folder in [TRANSCRIPT_FOLDER, AUDIO_FOLDER]:
				if os.path.exists(folder):
					shutil.rmtree(folder)
					info(f"Folder '{folder}' deleted!")

	# Make folders if they do not exist
	for folder in [TRANSCRIPT_FOLDER, AUDIO_FOLDER, OUTPUT_FOLDER]:
		os.makedirs(folder, exist_ok = True)

	# Initialize the audio port
	p: pyaudio.PyAudio = pyaudio.PyAudio()

	## Find devices
	# Find the recording device
	recorder_index, recorder_name = find_device(p, RECORDING_DEVICE_NAME)
	if recorder_index is None:
		warning(f"Recording device '{RECORDING_DEVICE_NAME}' not found, ignoring...")
	else:
		info(f"Recording device '{recorder_name}' found at index {recorder_index}!")
	
	# Find the playback device
	playback_index, playback_name = find_device(p, PLAYBACK_DEVICE_NAME)
	if playback_index is None:
		warning(f"Playback device '{PLAYBACK_DEVICE_NAME}' not found, ignoring...")
	else:
		info(f"Playback device '{playback_name}' found at index {playback_index}!")
	
	# If no device was found, exit the application
	if recorder_index is None and playback_index is None:
		error("No recording device found, exiting...")
	
	# Initialize the audio streams
	audio_streams: dict[str, dict] = {}
	if recorder_index is not None:
		audio_streams["recorder"] = {"stream": AudioStream(recorder_index, RATE, CHUNK_SIZE)}
	if playback_index is not None:
		audio_streams["playback"] = {"stream": AudioStream(playback_index, RATE, CHUNK_SIZE), "threshold": 100}	# Threshold for playback is lower as it is usually quieter
	
	# Start the audio streams
	for stream in audio_streams.values():
		stream["stream"].start()

	# Variables for silence detection
	chunks_per_second: float = RATE									# Number of chunks per second
	silence_time: float = 0.25										# Time to sleep between each iteration
	minimum_chunks: float = MINIMUM_DURATION * chunks_per_second	# Number of chunks needed to reach the minimum duration
	maximum_chunks: float = MAXIMUM_DURATION * chunks_per_second	# Number of chunks needed to reach the maximum duration
	no_silence: int = -10000000										# Value to avoid saving the same silence multiple times
	for stream in audio_streams.values():
		stream["silence_counter"] = no_silence
		stream["saved_files"] = 0
		stream["chunks_to_join"] = b""
		if not stream.get("threshold"):
			stream["threshold"] = SILENCE_THRESHOLD
	info(f"Chunks per second: {chunks_per_second} - Silence time: {silence_time} - Minimum chunks: {minimum_chunks} - Maximum chunks: {maximum_chunks}")
	
	# Start the main loop
	debug("Starting the main loop, press Ctrl+C to stop the application...")
	try:
		saved_files_on_this_iteration: int = 0
		time_since_last_report: float = 0
		while True:

			# Sleep for a short time
			time.sleep(silence_time)

			# Check the audio streams
			for name, items in audio_streams.items():
				stream: AudioStream = items["stream"]

				# Get frames and append them to the already stored frames
				frames: bytes = stream.get_frames()
					
				# Check if the audio is silent
				if is_silent(frames, threshold = items["threshold"]):
					if items["silence_counter"] != no_silence:
						items["silence_counter"] += silence_time
						if DEBUG_MODE:
							debug(f"Silence detected on the '{name}' stream (counter: {items['silence_counter']})")
				else:
					items["chunks_to_join"] += frames
					items["silence_counter"] = 0
					if DEBUG_MODE:
						debug(f"Audio detected on the '{name}' stream (adding {len(frames)} chunks to join, now {len(items['chunks_to_join'])} chunks)")
				
				# Check if the silence duration is reached
				if items["silence_counter"] >= SILENCE_DURATION:
					items["chunks_to_join"] += frames

					# If the minimum duration is reached, save the audio to a file
					if len(items["chunks_to_join"]) >= minimum_chunks:

						# Save the audio to a file
						if not DEBUG_MODE:
							debug(f"Silence detected on the '{name}' stream, saving the audio...")
						else:
							debug(f"Silence detected on the '{name}' stream, saving the audio ({len(items['chunks_to_join'])} chunks > {minimum_chunks} chunks)...")
						items["saved_files"] += 1
						filename: str = f"{name}_{items['saved_files']}.wav"
						save_audio(items["chunks_to_join"], filename)
						debug(f"Audio saved to '{filename}' for the '{name}' stream")
						saved_files_on_this_iteration += 1

					# Reset the silence counter and the chunks to join
					items["silence_counter"] = no_silence
					items["chunks_to_join"] = b""
			
			# Transcription of the saved files
			if saved_files_on_this_iteration > 0:
				saved_files_on_this_iteration = 0	# Reset the counter
				manage_new_audios(START_TIME_STR)		# Manage the new audio files

				# Update the report if needed
				now: float = time.perf_counter()
				if (now - time_since_last_report) >= UPDATE_REPORT_EVERY_X_SECONDS:
					time_since_last_report = now
					pass	# TODO: Update the report here


				
	
	except KeyboardInterrupt:
		info("Keyboard interrupt detected, stopping the application...")

	# Stop the audio streams and terminate the audio port
	for stream in audio_streams.values():
		stream["stream"].stop()
	p.terminate()
	
	# End of the application
	END_TIME: float = time.perf_counter()			# End time of the application
	info(f"Application ended in {END_TIME - START_TIME:.2f} seconds")
	return


# Main entry point
if __name__ == "__main__":
	main()

