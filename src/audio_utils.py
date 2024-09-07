
## Imports
from config import *
import numpy as np
import wave

# Silence detection function
def is_silent(data: list[bytes], threshold: int = SILENCE_THRESHOLD) -> bool:
	""" Check if the mean volume of the audio data is below the threshold\n
	Args:
		data		(list[bytes]):	List of audio data
		threshold	(int):			Threshold for silence detection
	Returns:
		bool: True if the mean volume is below the threshold, False otherwise
	"""
	# Convert the audio data to a numpy array
	data: bytes = b''.join(data)
	audio_data: np.ndarray = np.frombuffer(data, np.int16)

	# Return True if the mean volume is below the threshold
	return np.abs(audio_data).mean() < threshold


# Audio saving function
def save_audio(frames: list[bytes], filename: str, rate: int = RATE, channels: int = CHANNELS) -> None:
	""" Save the audio data to a WAV file\n
	Args:
		frames		(list[bytes]):	List of audio data
		filename	(str):			Name of the file to save
		rate		(int):			Sample rate (Hz)
		channels	(int):			Number of channels
	"""
	# Create the audio folder if it does not exist
	if not os.path.exists(AUDIO_FOLDER):
		os.makedirs(AUDIO_FOLDER)

	# Create the file path
	filepath: str = os.path.join(AUDIO_FOLDER, filename)

	# Open the WAV file and write the frames
	with wave.open(filepath, 'wb') as wf:
		wf.setnchannels(channels)
		wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
		wf.setframerate(rate)
		wf.writeframes(b''.join(frames))


# Device finding function
def find_device(p: pyaudio.PyAudio, name_substring: str) -> tuple[int, str]:
	""" Find the index of the audio device containing the given substring\n
	Args:
		p				(pyaudio.PyAudio):	PyAudio instance
		name_substring	(str):				Substring to search for in the device name
	Returns:
		tuple[int, str]: Index of the device and its name if found, None otherwise
	"""
	# Make sure the substring is lowercase
	name_substring: str = name_substring.lower()

	# Loop through the audio devices
	for i in range(p.get_device_count()):
		
		# Get the device info
		info: pyaudio._PaDeviceInfo = p.get_device_info_by_index(i)

		# Return the index if the substring is found in the device name
		if name_substring in info['name'].lower():
			return i, info['name']

	# Return None if the device is not found
	return None

