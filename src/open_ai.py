
## Imports
from config import *
from src.print import *
from openai import OpenAI
from openai.types.audio.transcription import Transcription

# Function to call the transcript API
def transcript_api(audio_file: str) -> str|None:
	""" Call the API to get the transcript of the audio file\n
	Args:
		audio_file (str): Path to the audio file
	Returns:
		str: Transcript of the audio file if successful
	"""
	transcript: str = None
	keys: list[str] = OPENAI_KEYS.copy()

	# Load the audio file
	with open(audio_file, "rb") as audio_data:

		# Try to get the transcript with the API keys
		while transcript is None and len(keys) > 0:
			try:
		
				# Get the API key
				key: str = keys.pop(0)
				client: OpenAI = OpenAI(api_key = key)

				# Get the transcript
				ai_output: Transcription = client.audio.transcriptions.create(file = audio_data, language = LANGUAGE, model = "whisper-1")
				transcript = ai_output.text
			
			except Exception as e:
				warning(f"Error while calling the API for the audio file '{os.path.basename(audio_file)}': {e}")
	
	# Return None if the transcript is still None
	if transcript is None:
		error(f"Could not get the transcript for the audio file '{os.path.basename(audio_file)}'", exit = False)

	# Return the transcript
	return transcript



