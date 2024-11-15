
## Imports
from config import *
from src.print import *
from src.audio_stream import AudioStream
from src.audio_utils import find_device
import pyaudiowpatch as pyaudio
import time
import numpy as np

def test_volume():
    # Initialize the audio port
    p: pyaudio.PyAudio = pyaudio.PyAudio()

    ## Find devices
    # Find the recording device
    recorder_index, recorder_name = find_device(p, RECORDING_DEVICE_NAME)
    if recorder_index is None:
        error(f"Recording device '{RECORDING_DEVICE_NAME}' not found, exiting...")
        return
    info(f"Recording device '{recorder_name}' found at index {recorder_index}!")

    # Initialize the audio stream
    stream = AudioStream(recorder_index, RATE, CHUNK_SIZE)
    stream.start()

    # Start the main loop
    debug("Starting the volume test, press Ctrl+C to stop...")
    try:
        while True:
            # Get frames
            frames: bytes = stream.get_frames()
            
            # Calculate volume
            if frames:
                audio_data: np.ndarray = np.frombuffer(frames, np.int16)
                volume: float = np.abs(audio_data).mean()
                print(f"\rCurrent volume: {volume:.2f}", end="")
            
            # Sleep for a short time
            time.sleep(SLEEP_INTERVAL)

    except KeyboardInterrupt:
        print()
        info("Stopping the volume test...")

    # Stop the audio stream and terminate the audio port
    stream.stop()
    p.terminate()

if __name__ == "__main__":
    test_volume()
