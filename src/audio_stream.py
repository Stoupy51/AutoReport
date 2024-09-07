
## Imports
from config import *
import threading

# AudioStream class to handle audio input from a device
class AudioStream:
	def __init__(self, device_index: int, rate: int, chunk: int, channels: int):
		""" Initialize the audio stream with the given parameters\n
		Args:
			device_index	(int):	Index of the audio device to use
			rate			(int):	Sample rate (Hz)
			chunk			(int):	Buffer size
			channels		(int):	Number of channels
		"""
		# Initialize the audio stream
		self.p: pyaudio.PyAudio = pyaudio.PyAudio()

		# Check if the device supports the specified number of channels
		device_info: pyaudio.PaDeviceInfo = self.p.get_device_info_by_index(device_index)
		max_input_channels: int = device_info.get("maxInputChannels", 0)
		if channels > max_input_channels:
			raise ValueError(f"Device '{device_info['name']}' supports only {max_input_channels} channel(s), {channels} channel(s) requested!")

		# Open the audio stream
		self.stream: pyaudio.Stream = self.p.open(
			format = FORMAT,
			channels = channels,
			rate = rate,
			input = True,
			frames_per_buffer = chunk,
			input_device_index = device_index
		)

		# Initialize the frames and threading lock
		self.frames: list[bytes] = []
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
			data: bytes = self.stream.read(CHUNK, exception_on_overflow=False)

			# Store the audio data in the frames list
			with self.lock:
				self.frames.append(data)

	def stop(self) -> None:
		""" Stop the audio thread and close the audio stream """
		# Stop the thread and join it
		self.is_running = False
		self.thread.join()

		# Stop and close the audio stream
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()

	def get_frames(self) -> list[bytes]:
		""" Get the frames stored in the audio stream and clear the frames list """
		with self.lock:
			frames: list[bytes] = self.frames.copy()
			self.frames = []
		return frames

