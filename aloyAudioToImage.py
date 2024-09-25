from PIL import Image
import numpy as np
import wave
import os
from pydub import AudioSegment

# Function to convert MP3 to WAV
def convert_mp3_to_wav(mp3_path, wav_path):
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")
    print(f"Converted {mp3_path} to {wav_path}")

# Function to convert bytes to binary
def bytes_to_binary(data):
    binary = ''.join([format(byte, '08b') for byte in data])
    return binary

def binary_to_bytes(binary_data):
    byte_array = bytearray()
    for i in range(0, len(binary_data), 8):
        byte_array.append(int(binary_data[i:i+8], 2))
    return bytes(byte_array)

# Function to encode audio data into the image
def encode_audio_into_image(image_path, audio_path, output_image):
    # Check if the audio file is in MP3 format, convert it to WAV
    if audio_path.endswith(".mp3"):
        wav_path = "temp_audio.wav"  # Temporary path for the converted WAV file
        convert_mp3_to_wav(audio_path, wav_path)
        audio_path = wav_path

    # Load the image
    image = Image.open(image_path)
    image_array = np.array(image)

    # Open the audio file and read it in binary
    with wave.open(audio_path, 'rb') as audio_file:
        frames = audio_file.readframes(audio_file.getnframes())
        binary_audio = bytes_to_binary(frames)

    # Append the end marker "###END###" to the binary audio data
    end_marker = "###END###"
    binary_marker = ''.join(format(ord(char), '08b') for char in end_marker)
    binary_audio += binary_marker  # Add the marker at the end

    # Check if the image can store the audio data
    max_bytes = image_array.size // 3  # One bit per RGB channel
    if len(binary_audio) > max_bytes:
        raise ValueError("The audio file is too large to encode into this image.")

    binary_index = 0
    binary_len = len(binary_audio)

    # Iterate through the image's pixels and encode the audio data
    for row in image_array:
        for pixel in row:
            for channel in range(3):  # R, G, B channels
                if binary_index < binary_len:
                    # Modify the LSB of the pixel to encode the audio bit
                    pixel[channel] = (pixel[channel] & ~1) | int(binary_audio[binary_index])
                    binary_index += 1

    # Save the modified image
    output_dir = "images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, output_image)
    encoded_image = Image.fromarray(image_array)
    encoded_image.save(output_path)

    print(f"Audio successfully encoded into {output_path}")

# Function to decode audio data from the image
def decode_audio_from_image(encoded_image, output_audio):
    # Load the image
    image = Image.open(encoded_image)
    image_array = np.array(image)

    binary_data = ""
    for row in image_array:
        for pixel in row:
            for channel in range(3):  # R, G, B channels
                # Extract the least significant bit and append to binary_data
                binary_data += str(pixel[channel] & 1)

    # Find the end marker "###END###" in the binary data and truncate
    end_marker = "###END###"
    binary_marker = ''.join(format(ord(char), '08b') for char in end_marker)
    
    # If end marker is found, cut off the data after the end marker
    if binary_marker in binary_data:
        binary_data = binary_data[:binary_data.index(binary_marker)]

    # Convert the binary string back into bytes
    audio_data = binary_to_bytes(binary_data)

    temp_audio = "temp_audio.wav"

    # Extract audio properties from the input file
    with wave.open(temp_audio, 'rb') as input_audio_file:
        n_channels = input_audio_file.getnchannels()  # Number of channels (e.g., mono or stereo)
        sampwidth = input_audio_file.getsampwidth()   # Sample width in bytes (e.g., 2 bytes for 16-bit audio)
        framerate = input_audio_file.getframerate()   # Frame rate (sample rate, e.g., 44100 Hz)

    # Write the decoded audio data to a new WAV file with the same properties
    with wave.open(output_audio, 'wb') as output_audio_file:
        output_audio_file.setnchannels(n_channels)
        output_audio_file.setsampwidth(sampwidth)
        output_audio_file.setframerate(framerate)
        output_audio_file.writeframes(audio_data)
    
    # Cleanup the temporary WAV file if it was created
    if os.path.exists("temp_audio.wav"):
        os.remove("temp_audio.wav")

    print(f"Audio successfully decoded and saved to {output_audio}")

# Testing of encoding the audio into the image
image_path = "images/targetImage.jpg"  # Path to the input image file
audio_path = "audio/magicSpellAudio.mp3"  # Path to the input audio file
output_image = "audio_encoded_image.png"  # Output encoded image file

encode_audio_into_image(image_path, audio_path, output_image)

# Testing of decoding the audio from the encoded image
encoded_image = "images/audio_encoded_image.png"  # Path to the encoded image file
output_audio = "decoded_audio.wav"  # Output decoded audio file

decode_audio_from_image(encoded_image, output_audio)