
# Import the PyAudio module
import pyaudiowpatch as pyaudio

# Print the detailed system information
with pyaudio.PyAudio() as p:
    p.print_detailed_system_info()

