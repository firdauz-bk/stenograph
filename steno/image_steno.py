from PIL import Image
import numpy as np
import os
import wave
from pydub import AudioSegment

def text_to_binary(text):
    # Convert the text into a binary string
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary_data):
    # Convert binary string to text, 8 bits at a time
    text = ''
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        text += chr(int(byte, 2))
    return text

def encode_image(image_path, text_file, output_image, lsb_count=1):
    if lsb_count < 1 or lsb_count > 8:
        raise ValueError("LSB count must be between 1 and 8.")
    
    image = Image.open(image_path)
    image_array = np.array(image)

    # Read the text to be encoded from the file
    with open(text_file, 'r') as file:
        text = file.read()
    
    # Append the end marker to the text
    text += "###$$$###"
    binary_text = text_to_binary(text)
    binary_index = 0
    binary_len = len(binary_text)
    
    for row in image_array:
        for pixel in row:
            # Modify R, G, B channels of the pixel
            for channel in range(3):  # 3 channels: Red, Green, Blue
                if binary_index < binary_len:
                    # Extract the next bits to encode (depending on lsb_count)
                    bits_to_encode = binary_text[binary_index:binary_index+lsb_count]
                    if len(bits_to_encode) < lsb_count:
                        bits_to_encode = bits_to_encode.ljust(lsb_count, '0')
                    
                    # Clear the least significant bits in the pixel's channel
                    pixel[channel] &= ~( (1 << lsb_count) - 1 )
                    
                    # Encode the bits in the pixel's channel
                    pixel[channel] |= int(bits_to_encode, 2)
                    
                    # Move to the next bits in the binary text
                    binary_index += lsb_count

            if binary_index >= binary_len:
                break  # Stop if the whole message has been encoded

    if binary_index < binary_len:
        raise ValueError("The message is too long to be encoded in the image.")

    # Save the encoded image
    output_dir = "encoded_files"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, output_image)
    encoded_image = Image.fromarray(image_array)
    encoded_image.save(output_path)
    
    return output_path

def decode_image(image_path, lsb_count=1):
    if lsb_count < 1 or lsb_count > 8:
        raise ValueError("LSB count must be between 1 and 8.")
    
    image = Image.open(image_path)
    image_array = np.array(image)

    binary_data = ""
    end_marker = "###$$$###"
    binary_end_marker = text_to_binary(end_marker)

    for row in image_array:
        for pixel in row:
            for channel in range(3):  # R, G, B channels
                # Extract the least significant bits from the channel value
                # Strip the '0b' prefix by slicing the binary output of bin() directly
                bits_from_channel = format(pixel[channel], '08b')[-lsb_count:]
                
                # Append the bits to the binary data string
                binary_data += bits_from_channel
                
                # Check if we've reached the end of the marker
                if len(binary_data) >= len(binary_end_marker):
                    decoded_text = binary_to_text(binary_data)
                    if end_marker in decoded_text:
                        return decoded_text[:decoded_text.index(end_marker)]

    # If no end marker is found, return the decoded text up to the marker
    return binary_to_text(binary_data)

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
def encode_audio_into_image(image_path, audio_path, output_image, lsb_count=1):
    if lsb_count < 1 or lsb_count > 8:
        raise ValueError("LSB count must be between 1 and 8.")
    
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

    # Append the end marker "###$$$###" to the binary audio data
    end_marker = "###$$$###"
    binary_marker = ''.join(format(ord(char), '08b') for char in end_marker)
    binary_audio += binary_marker  # Add the marker at the end

    # Check if the image can store the audio data
    max_bytes = image_array.size * lsb_count // 3  # lsb_count bits per RGB channel
    if len(binary_audio) > max_bytes:
        raise ValueError("The audio file is too large to encode into this image.")

    binary_index = 0
    binary_len = len(binary_audio)

    # Iterate through the image's pixels and encode the audio data
    for row in image_array:
        for pixel in row:
            for channel in range(3):  # R, G, B channels
                if binary_index < binary_len:
                    # Extract the next `lsb_count` bits to encode
                    bits_to_encode = binary_audio[binary_index:binary_index + lsb_count]
                    if len(bits_to_encode) < lsb_count:
                        bits_to_encode = bits_to_encode.ljust(lsb_count, '0')
                    
                    # Clear the LSBs and set new bits
                    pixel[channel] &= ~( (1 << lsb_count) - 1 )
                    pixel[channel] |= int(bits_to_encode, 2)
                    
                    binary_index += lsb_count

    # Save the modified image
    output_dir = "uploads"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, output_image)
    encoded_image = Image.fromarray(image_array)
    encoded_image.save(output_path)

    return output_path

# Function to decode audio data from the image
def decode_audio_from_image(encoded_image, output_audio=None, lsb_count=1):
    if lsb_count < 1 or lsb_count > 8:
        raise ValueError("LSB count must be between 1 and 8.")
    
    # Load the image
    image = Image.open(encoded_image)
    image_array = np.array(image)

    binary_data = ""
    for row in image_array:
        for pixel in row:
            for channel in range(3):  # R, G, B channels
                # Extract the `lsb_count` least significant bits and append to binary_data
                bits_from_channel = format(pixel[channel], '08b')[-lsb_count:]
                binary_data += bits_from_channel

    # Find the end marker "###$$$###" in the binary data and truncate
    end_marker = "###$$$###"
    binary_marker = ''.join(format(ord(char), '08b') for char in end_marker)
    
    # If end marker is found, cut off the data after the end marker
    if binary_marker in binary_data:
        binary_data = binary_data[:binary_data.index(binary_marker)]

    # Convert the binary string back into bytes
    audio_data = binary_to_bytes(binary_data)

    # If output_audio is not provided, set a default name
    if output_audio is None:
        output_audio = "decoded_audio.wav"

    # Use the temporary WAV file to extract the audio properties if it exists
    temp_audio = "temp_audio.wav"

    if os.path.exists(temp_audio):
        # Extract audio properties from the temporary WAV file
        with wave.open(temp_audio, 'rb') as input_audio_file:
            n_channels = input_audio_file.getnchannels()  # Number of channels (e.g., mono or stereo)
            sampwidth = input_audio_file.getsampwidth()   # Sample width in bytes (e.g., 2 bytes for 16-bit audio)
            framerate = input_audio_file.getframerate()   # Frame rate (sample rate, e.g., 44100 Hz)
    else:
        # If temp_audio.wav doesn't exist, provide some default values
        n_channels = 1  # Mono audio by default
        sampwidth = 2   # 16-bit audio
        framerate = 44100  # Default sample rate

    # Write the decoded audio data to a new WAV file with the same properties
    with wave.open(output_audio, 'wb') as output_audio_file:
        output_audio_file.setnchannels(n_channels)
        output_audio_file.setsampwidth(sampwidth)
        output_audio_file.setframerate(framerate)
        output_audio_file.writeframes(audio_data)
    
    # Cleanup the temporary WAV file if it was created
    if os.path.exists(temp_audio):
        os.remove(temp_audio)

    return output_audio

# # TESTING CODE
# # Encode the text file into the image
# encoded_image = encode_image("images/lion.png", "test.txt", "encoded_lion_image.png", lsb_count=1)
# print(f"Encoded image saved at: {encoded_image}")

# # Decode the text from the encoded image
# decoded_text = decode_image(encoded_image, lsb_count=1)
# print(f"Decoded text: {decoded_text}")