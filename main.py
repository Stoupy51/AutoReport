
## Imports
from config import *
from src.print import *
from src.audio_stream import AudioStream
from src.audio_utils import is_silent, save_audio, find_device

# Main function
def main():
	START_TIME: float = time.perf_counter()			# Start time of the application

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
		audio_streams["recorder"] = {"stream": AudioStream(recorder_index, RATE, CHUNK, CHANNELS)}
	if playback_index is not None:
		audio_streams["playback"] = {"stream": AudioStream(playback_index, RATE, CHUNK, CHANNELS)}
	
	# Start the audio streams
	for stream in audio_streams.values():
		stream["stream"].start()

	# Variables for silence detection
	silence_chunks: float = SILENCE_DURATION * RATE / CHUNK		# Number of chunks needed to reach the silence duration
	for stream in audio_streams.values():
		stream["silence_counter"] = 0
		stream["saved_files"] = 0
	
	# Start the main loop
	debug("Starting the main loop, press Ctrl+C to stop the application...")
	try:
		while True:
			saved_files_on_this_iteration: int = 0
			
			# Sleep for a short time
			time.sleep(0.01)

			# Check the audio streams
			for name, items in audio_streams.items():
				stream: AudioStream = items["stream"]
				
				# Check if the stream has frames
				frames: list[bytes] = stream.get_frames()
				if len(frames) > 0:
					
					# Check if the audio is silent
					if is_silent(frames):
						items["silence_counter"] += 1
					else:
						items["silence_counter"] = 0
					
					# Check if the silence duration is reached
					if items["silence_counter"] >= silence_chunks:
						debug(f"Silence detected on the {name} stream, saving the audio...")
						
						# Save the audio to a file
						items["saved_files"] += 1
						filename: str = f"{name}_{items['saved_files']}.wav"
						save_audio(frames, filename)
						saved_files_on_this_iteration += 1

						# Reset the silence counter
						items["silence_counter"] = 0
			
			# Transcription of the saved files
			if saved_files_on_this_iteration > 0:
				pass	# TODO: Add the transcription part here

				
	
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

