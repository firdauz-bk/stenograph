import os
import wave
from pathlib import Path
from pydub import AudioSegment

# Create function to convert audio file to wav
def convert_to_wav(filename):
    """Takes an audio file of non .wav format and converts it to .wav"""
    try:
        # Import audio file
        audio = AudioSegment.from_file(filename)
        
        # Create new filename
        new_filename = filename.rsplit(".", 1)[0] + ".wav"
        
        # Export file as .wav
        audio.export(new_filename, format="wav")
        print(f"Converting {filename} to {new_filename}...")
        
        return new_filename
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

def convert_mp3_to_wav(mp3_path, wav_path):
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")
    print(f"Converted {mp3_path} to {wav_path}")


def encode_audio(txt_file: str, audio_file: str, bit_size: int = 1, output_dir: str = "encoded"):
    # Ensure bit_size is between 1 and 8
    if not (1 <= bit_size <= 8):
        raise ValueError("bit_size must be between 1 and 8")

    # Read the content of the text file
    with open(txt_file, 'r') as file:
        txt = file.read()

    # Append the end-of-message marker
    end_marker = '$$###$$'
    txt += end_marker

    # Open the audio file
    try:
        if not audio_file.endswith(".wav"):
            wav_path = convert_to_wav(audio_file)
            audio = wave.open(wav_path, mode="rb")
        else:
            audio = wave.open(audio_file, mode="rb")
    except Exception as e:
        print(f"Error with file type: {e}")
        return

    # Read frames and convert them to a bytearray
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

    # Convert text to bit representation
    bits = ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in txt])
    bit_chunks = [bits[i:i + bit_size] for i in range(0, len(bits), bit_size)]

    # Ensure the message fits within the audio file
    if len(bit_chunks) > len(frame_bytes):
        print("Error: Text is too long to encode in the provided audio file.")
        return

    # Replace LSBs of each byte of the audio file with the bits of the text
    for i, bit_chunk in enumerate(bit_chunks):
        byte = frame_bytes[i]
        # Create a mask to clear out the last 'bit_size' bits and set them to the new bit_chunk
        mask = 255 - (2 ** bit_size - 1)
        frame_bytes[i] = (byte & mask) | int(bit_chunk, 2)

    # Create a new wave file with the modified frames
    frame_modified = bytes(frame_bytes)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"encoded_{os.path.basename(audio_file)}"
    with wave.open(str(output_path), 'wb') as new_audio:
        new_audio.setparams(audio.getparams())
        new_audio.writeframes(frame_modified)

    audio.close()
    return str(output_path)

def decode_audio(audio_file: str, bit_size: int = 1, output_txt_file: str = None) -> str:
    # Ensure bit_size is between 1 and 8
    if not (1 <= bit_size <= 8):
        raise ValueError("bit_size must be between 1 and 8")

    # Open the encoded audio file
    audio = wave.open(audio_file, mode='rb')
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

    # Extract the specified bits from each byte
    extracted_bits = ''.join([bin(byte & (2 ** bit_size - 1)).lstrip('0b').rjust(bit_size, '0') for byte in frame_bytes])

    # Group extracted bits into bytes (8 bits)
    byte_chunks = [extracted_bits[i:i + 8] for i in range(0, len(extracted_bits), 8)]

    # Convert byte bits back to characters
    txt = ''.join([chr(int(byte_chunk, 2)) for byte_chunk in byte_chunks])

    # Define the end-of-message marker
    end_marker = '$$###$$'

    # Find the position of the end marker
    end_pos = txt.find(end_marker)

    # Extract the original message
    if end_pos != -1:
        decoded_message = txt[:end_pos]
    else:
        decoded_message = txt

    # Optionally save the decoded message to a file
    if output_txt_file:
        with open(output_txt_file, 'w') as file:
            file.write(decoded_message)

    return decoded_message


#Function to encode an image into an audio file
def encode_image_in_audio(png_file: str, audio_file: str, bit_size: int = 1, output_dir: str = "encoded"):
    if not (1 <= bit_size <= 8):
        raise ValueError("bit_size must be between 1 and 8")

    # Read the binary content of the image file
    with open(png_file, 'rb') as file:
        img_data = file.read()

    payload_size = len(img_data)  # Get the size of the image file in bytes

    # Convert payload_size to 32-bit binary string
    size_bits = format(payload_size, '032b')

    # Open the audio file
    audio = wave.open(audio_file, mode="rb")
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
    params = audio.getparams()
    audio.close()

    # Ensure the audio file can hold the image payload
    total_bits_needed = len(size_bits) + len(img_data) * 8  # Total bits needed (size bits + image bits)
    available_bits = len(frame_bytes) * bit_size

    if total_bits_needed > available_bits:
        raise ValueError("The audio file is too small to hold the PNG payload.")

    # Convert image data to bit representation
    bits = ''.join([format(byte, '08b') for byte in img_data])

    # Combine size_bits and bits
    total_bits = size_bits + bits

    # Create bit chunks according to bit_size
    bit_chunks = [total_bits[i:i + bit_size] for i in range(0, len(total_bits), bit_size)]

    # Replace LSBs of each byte of the audio file with the bits of the image
    for i, bit_chunk in enumerate(bit_chunks):
        byte = frame_bytes[i]
        mask = 255 - (2 ** bit_size - 1)
        frame_bytes[i] = (byte & mask) | int(bit_chunk, 2)

    # Create a new wave file with the modified frames
    frame_modified = bytes(frame_bytes)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_basename = os.path.basename(audio_file)
    audio_name, audio_ext = os.path.splitext(audio_basename)
    output_filename = f"{payload_size}_encoded_{audio_name}{audio_ext}"
    output_path = output_dir / output_filename

    new_audio = wave.open(str(output_path), 'wb')
    new_audio.setparams(params)
    new_audio.writeframes(frame_modified)
    new_audio.close()

    # Return the output audio file path
    return str(output_path), payload_size

def decode_image_in_audio(audio_file: str, bit_size: int = 1, payload_size: int = None):
    if not (1 <= bit_size <= 8):
        raise ValueError("bit_size must be between 1 and 8")

    # Open the encoded audio file
    with wave.open(audio_file, mode='rb') as audio:
        frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

    # Calculate the total number of bits available
    total_bits_available = len(frame_bytes) * bit_size

    # Extract bits from the audio file
    extracted_bits = ''
    for byte in frame_bytes:
        bits = bin(byte & (2 ** bit_size - 1))[2:].rjust(bit_size, '0')
        extracted_bits += bits

    # Ensure we have enough bits
    if len(extracted_bits) < 32:
        raise ValueError("Audio file is too small to contain the payload size.")

    # Extract the payload size (first 32 bits)
    size_bits = extracted_bits[:32]
    payload_size = int(size_bits, 2)

    # Now extract the image bits
    image_bits = extracted_bits[32:32 + payload_size * 8]

    if len(image_bits) < payload_size * 8:
        raise ValueError("Audio file does not contain enough data for the payload.")

    # Convert bits to bytes
    byte_array = bytearray()
    for i in range(0, len(image_bits), 8):
        byte_chunk = image_bits[i:i + 8]
        byte_array.append(int(byte_chunk, 2))

    # Write the extracted bytes to an image file
    audio_basename = os.path.basename(audio_file)
    audio_name, _ = os.path.splitext(audio_basename)
    output_image_path = f"decoded_image_{audio_name}.png"

    with open(output_image_path, 'wb') as img_file:
        img_file.write(byte_array)

    return output_image_path