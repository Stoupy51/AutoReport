
## Imports
from config import *
import threading
import pyaudiowpatch as pyaudio
import numpy as np

# AudioStream class to handle audio input from a device
class AudioStream:
	def __init__(self, device_index: int, rate: int, chunk: int):
		""" Initialize the audio stream with the given parameters\n
		Args:
			device_index	(int):	Index of the audio device to use
			rate			(int):	Sample rate (Hz)
			chunk			(int):	Buffer size
		"""
		# Initialize the audio stream
		self.p: pyaudio.PyAudio = pyaudio.PyAudio()

		# Check if the device supports the specified number of channels
		device_info: pyaudio._PaDeviceInfo = self.p.get_device_info_by_index(device_index)
		self.channels: int = device_info.get("maxInputChannels", 0)
		if self.channels == 0:
			message: str = f"Device '{device_info['name']}' does not support input channels!"
			raise ValueError(message)
		else:
			print(f"Device '{device_info['name']}' supports {self.channels} input channels")

		# Open the audio stream
		self.stream: pyaudio.Stream = self.p.open(
			format = FORMAT,
			channels = self.channels,
			rate = rate,
			input = True,
			frames_per_buffer = chunk,
			input_device_index = device_index
		)

		# Initialize the frames and threading lock
		self.frames: bytes = b""
		self.lock: threading.Lock = threading.Lock()

		# Set the running flag to False
		self.is_running: bool = False

	def start(self) -> None:
		""" Start the audio thread to listen to the audio stream """
		self.is_running = True
		self.thread: threading.Thread = threading.Thread(target = self.listen)
		self.thread.start()

	def listen(self) -> None:
		""" Listen to the audio stream and store the frames """
		while self.is_running:

			# Read the audio data from the stream
			data: bytes = self.stream.read(CHUNK_SIZE, exception_on_overflow = False)

			if self.channels > 1:
				# Convert byte data to numpy array
				audio_data: np.ndarray = np.frombuffer(data, np.int16)

				# Force the audio data to be mono
				mono_data: np.ndarray = audio_data.reshape(-1, self.channels).mean(axis = 1).astype(np.int16)

				# Convert the mono data back to bytes
				data: bytes = mono_data.tobytes()

			# Store the audio data in the frames list
			with self.lock:
				self.frames += data

	def stop(self) -> None:
		""" Stop the audio thread and close the audio stream """
		# Stop the thread and join it
		self.is_running = False
		self.thread.join(timeout = 1.0)

		# Stop and close the audio stream
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()

	def get_frames(self) -> bytes:
		""" Get the frames stored in the audio stream and clear the frames list """
		with self.lock:
			frames: bytes = self.frames
			self.frames = b""
		return frames

