
# Imports
from config import *
from src.print import *
import numpy as np

# Silence detection function
def is_silent(data: bytes, threshold: int = SILENCE_THRESHOLD) -> bool:
	""" Check if the mean volume of the audio data is below the threshold\n
	Args:
		data		(bytes):	Audio data
		threshold	(int):		Threshold for silence detection
	Returns:
		bool: True if the mean volume is below the threshold, False otherwise
	"""
	if not data:
		return True
	
	# Convert the audio data to a numpy array
	try:
		audio_data: np.ndarray = np.frombuffer(data, np.int16)
	except ValueError as e:
		warning(f"Error while converting the audio data to a numpy array: {e}")
		return True

	# Return True if the mean volume is below the threshold
	volume: float = np.abs(audio_data).mean()
	if DEBUG_VOLUME:
		debug(f"Volume: {volume:.2f} (Threshold: {threshold})")
	return volume < threshold

