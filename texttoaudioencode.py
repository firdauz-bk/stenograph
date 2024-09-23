import wave
import os

def encode(byte_array, message, bits):
    message_bin = ''.join([bin(ord(c)).lstrip('0b').rjust(8,'0') for c in message])
    message = [int(message_bin[i:i+bits], 2) for i in range(0, len(message_bin), bits)]

    message_len = len(message)

    message_len_bin = bin(message_len)[2:].zfill(32)
    message_len_bin = list(message_len_bin)
    
    for i in range(0,32):
      byte_array[i] = ((byte_array[i] & (255 << bits)) | int(message_len_bin[i]))

    for i in range(len(message)):
        byte_array[i+32] = ((byte_array[i+32] & (255 << bits)) | message[i])

    return byte_array

def run_encode(audio_path, message, audio_output_path, bits):
    with wave.open(audio_path, "rb") as audio_file:
        frames = audio_file.readframes(-1)
        byte_array = bytearray(frames)
        byte_array = encode(byte_array, message, bits)
  
        with wave.open(audio_output_path, "wb") as hidden_audio:
            hidden_audio.setparams(audio_file.getparams())
            hidden_audio.writeframes(byte_array)
  
    return "The data has been hidden successfully"

audio_path = input("Enter audio path:")
message = input("Enter message:")
audio_output_path = input("Enter output directory for audio:")
output_file_name = input("Enter output file name (with .wav extension):")
bits = int(input("Enter number of bits for steganography (1-8):"))

audio_output_path = os.path.join(audio_output_path, output_file_name)

print(run_encode(audio_path, message, audio_output_path, bits))