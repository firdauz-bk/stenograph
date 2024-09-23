import wave

def run_decode(audio_output_path, bits):
    with wave.open(audio_output_path, "rb") as audio_file:
        frames = audio_file.readframes(-1)
        byte_array = bytearray(frames)

    # Extract the message length stored in the first 32 bits
    message_len_bin = ""
    for i in range(0, 32):
        bit = bin(byte_array[i])[2:].zfill(8)
        message_len_bin += bit[-bits:]

    message_len = int(message_len_bin, 2)  # Message length in characters

    # Check if the message length fits within the available bytes
    if message_len * 8 > (len(byte_array) - 32) * bits:
        return "Error: Message length exceeds the audio file capacity."

    message_bits = []
    for i in range(32, 32 + (message_len * 8) // bits):
        bit = bin(byte_array[i])[2:].zfill(8)[-bits:]
        message_bits.append(bit)

    # Convert the message bits into a binary string
    message_bin = ''.join(message_bits)

    # Ensure that we only take the necessary number of bits
    message_bin = message_bin[:message_len * 8]

    # Convert the binary string back into characters
    text = ''.join([chr(int(message_bin[i:i + 8], 2)) for i in range(0, len(message_bin), 8)])

    return text

audio_output_path = input("Enter path to the encoded audio file:")
bits = int(input("Enter number of bits used for steganography (1-8):"))

print("The decoded text from the audio is:", run_decode(audio_output_path, bits))