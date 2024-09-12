
## Imports
from config import *
from src.print import *
import pyaudiowpatch as pyaudio
import wave

# Audio saving function
def save_audio(frames: bytes, filename: str, rate: int = RATE) -> None:
	""" Save the audio data to a WAV file\n
	Args:
		frames		(bytes):	Audio data
		filename	(str):		Name of the file to save
		rate		(int):		Sample rate (Hz)
	"""
	# Create the audio folder if it does not exist
	if not os.path.exists(AUDIO_FOLDER):
		os.makedirs(AUDIO_FOLDER)

	# Create the file path
	filepath: str = os.path.join(AUDIO_FOLDER, filename)

	# Open the WAV file and write the frames
	with wave.open(filepath, 'wb') as wf:
		wf.setnchannels(1)
		wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
		wf.setframerate(rate)
		wf.writeframes(frames)


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
	max_index: int = p.get_device_count()
	for i in range(max_index):
		index = max_index - i - 1
		
		# Get the device info
		info: pyaudio._PaDeviceInfo = p.get_device_info_by_index(index)

		# Return the index if the substring is found in the device name
		if name_substring in info['name'].lower():
			return index, info['name']

	# Return None if the device is not found
	return None

