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
    # Ensure bit_size is between 1 and 8, as a byte has 8 bits
    if not (1 <= bit_size <= 8):
        raise ValueError("bit_size must be between 1 and 8")

    # Read the content of the text file
    with open(txt_file, 'r') as file:
        txt = file.read()


    try:
        if not audio_file.endswith(".wav"):
            #wav_path = "temp_audio.wav"  # Temporary path for the converted WAV file
            wav_path = convert_to_wav(audio_file)
            audio = wave.open(wav_path, mode="rb")
        else:
        # Open the audio file
            audio = wave.open(audio_file, mode="rb")
    except:
        print("Error with file type, please check")

    
    # if not audio_file.endswith(".wav"):
    #     #wav_path = "temp_audio.wav"  # Temporary path for the converted WAV file
    #     wav_path = convert_to_wav(audio_file)
    #     audio = wave.open(wav_path, mode="rb")
    # else:
    #     # Open the audio file
    #     audio = wave.open(audio_file, mode="rb")


    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

    # Padding the text with '#' to fill the rest of the audio file
    required_padding = int((len(frame_bytes) * bit_size - len(txt) * 8) / 8)
    txt = txt + required_padding * '#'

    # Convert text to bit representation
    bits = ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in txt])
    bit_chunks = [bits[i:i + bit_size] for i in range(0, len(bits), bit_size)]

    # Replace LSBs (or more significant bits, depending on bit_size) of each byte of the audio file with the bits of the text
    for i, bit_chunk in enumerate(bit_chunks):
        byte = frame_bytes[i]
        # Create a mask to clear out the last 'bit_size' bits and set them to the new bit_chunk
        mask = 255 - (2 ** bit_size - 1)
        frame_bytes[i] = (byte & mask) | int(bit_chunk, 2)

    # Create a new wave file with the modified frames
    frame_modified = bytes(frame_bytes)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = f"encoded_{os.path.basename(audio_file)}"
    new_audio = wave.open(str(output_path), 'wb')
    new_audio.setparams(audio.getparams())
    new_audio.writeframes(frame_modified)
    new_audio.close()
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

    # Split the text at the padding delimiter '###'
    decoded_audio = txt.split("###")[0]

    # Save the decoded message to a file if the file path is provided
    if output_txt_file:
        with open(output_txt_file, 'w') as file:
            file.write(decoded_audio)

    return decoded_audio


#Function to encode an image into an audio file
def encode_image_in_audio(png_file: str, audio_file: str, bit_size: int = 1, output_dir: str = "encoded"):
    if not (1 <= bit_size <= 8):
        raise ValueError("bit_size must be between 1 and 8")
    
    # Read the binary content of the image file
    try:
        with open(png_file, 'rb') as file:
            img_data = file.read()
    except Exception as e:
        raise ValueError(f"Failed to read image file: {str(e)}")
    
    payload_size = len(img_data)  # Get the size of the image file in bytes

    # Convert payload_size to 32-bit binary string
    size_bits = format(payload_size, '032b')

    # Open the audio file
    try:
        audio = wave.open(audio_file, mode="rb")
    except Exception as e:
        raise ValueError(f"Failed to open audio file: {str(e)}")
    
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
    audio.close()

    # Ensure the audio file can hold the image payload
    total_bits_needed = len(size_bits) + len(img_data) * 8  # Size bits + image data bits
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
    output_path = output_dir / f"{payload_size}_encoded_image_{os.path.basename(audio_file)}"
    try:
        new_audio = wave.open(str(output_path), 'wb')
        new_audio.setparams((audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), 0, 'NONE', 'not compressed'))
        new_audio.writeframes(frame_modified)
        new_audio.close()
    except Exception as e:
        raise ValueError(f"Failed to write encoded audio file: {str(e)}")

    return str(output_path), payload_size

def decode_image_in_audio(audio_file: str, bit_size: int = 1, payload_size: int = None):
    if not (1 <= bit_size <= 8):
        raise ValueError("bit_size must be between 1 and 8")

    if payload_size is None:
        raise ValueError("Payload size is required for decoding.")

    # Open the encoded audio file
    audio = wave.open(audio_file, mode='rb')
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
    audio.close()

    # Extract the specified bits from each byte
    extracted_bits = ''.join([bin(byte & (2 ** bit_size - 1)).lstrip('0b').rjust(bit_size, '0') for byte in frame_bytes])

    # Convert the extracted bits back to bytes
    byte_array = bytearray()
    for i in range(0, len(extracted_bits), 8):
        byte_chunk = extracted_bits[i:i + 8]
        if len(byte_chunk) == 8:
            byte_array.append(int(byte_chunk, 2))

    # Limit extraction to the payload size
    byte_array = byte_array[:payload_size]

    # Write the extracted bytes to an image file
    audio_basename = os.path.basename(audio_file)
    audio_name, _ = os.path.splitext(audio_basename)
    output_image_path = f"decoded_image_{audio_name}.png"

    try:
        with open(output_image_path, 'wb') as img_file:
            img_file.write(byte_array)
    except Exception as e:
        raise ValueError(f"Failed to write image file: {str(e)}")

    return output_image_path