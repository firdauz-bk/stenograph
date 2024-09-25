def encode_image_with_size(png_file: str, audio_file: str, bit_size: int = 1, output_dir: str = "encoded"):
    if not (1 <= bit_size <= 8):
        raise ValueError("bit_size must be between 1 and 8")

    # Read the binary content of the image file
    with open(png_file, 'rb') as file:
        img_data = file.read()

    # Get the image size in bytes
    img_size = len(img_data)
    print(f"Original image size (bytes): {img_size}")

    # Convert the image size to a fixed length (32 bits) binary string
    img_size_bits = bin(img_size)[2:].zfill(32)  # Ensure it's 32 bits by using zfill
    print(f"Encoded image size in bits: {img_size_bits}")

    # Open the audio file
    audio = wave.open(audio_file, mode="rb")
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

    # Ensure the audio file can hold the image payload and the size metadata
    total_bits_required = (len(img_data) * 8) + 32
    available_bits = len(frame_bytes) * bit_size
    if total_bits_required > available_bits:
        raise ValueError(f"The audio file is too small to hold the PNG payload and size metadata. Required: {total_bits_required} bits, Available: {available_bits} bits.")

    # Convert image data to bit representation
    bits = ''.join([bin(byte)[2:].rjust(8, '0') for byte in img_data])

    # Prepend the image size bits to the image data bits
    all_bits = img_size_bits + bits
    bit_chunks = [all_bits[i:i + bit_size] for i in range(0, len(all_bits), bit_size)]
    print(f"Total number of bits to encode: {len(all_bits)}")

    # Replace LSBs of each byte of the audio file with the bits of the image and size
    for i, bit_chunk in enumerate(bit_chunks):
        byte = frame_bytes[i]
        mask = 255 - (2 ** bit_size - 1)
        frame_bytes[i] = (byte & mask) | int(bit_chunk, 2)

    # Create a new wave file with the modified frames
    frame_modified = bytes(frame_bytes)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"encoded_image_{os.path.basename(audio_file)}"
    new_audio = wave.open(str(output_path), 'wb')
    new_audio.setparams(audio.getparams())
    new_audio.writeframes(frame_modified)
    new_audio.close()
    audio.close()

    return str(output_path)


def decode_image_with_size(audio_file: str, bit_size: int = 1, output_image_file: str = "decoded_image.png"):
    if not (1 <= bit_size <= 8):
        raise ValueError("bit_size must be between 1 and 8")

    # Open the encoded audio file
    audio = wave.open(audio_file, mode='rb')
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

    # Extract exactly the first 32 bits to determine the image size
    size_bits = []
    bit_index = 0

    # Extract 32 bits for the size from the LSBs of the audio bytes
    for i in range(32):
        byte = frame_bytes[bit_index // 8]
        bit = (byte >> (7 - (bit_index % 8))) & 1  # Extract the specific bit
        size_bits.append(str(bit))
        bit_index += 1

    # Convert the extracted bits back to an integer (image size in bytes)
    img_size = int(''.join(size_bits), 2)
    print(f"Decoded image size (bytes): {img_size}")

    # Now extract the remaining bits for the image data (limit based on image size)
    total_bits = img_size * 8
    extracted_bits = []
    
    for i in range(32, 32 + total_bits):  # Start after the 32 size bits
        byte_index = i // 8
        bit_position = 7 - (i % 8)
        bit = (frame_bytes[byte_index] >> bit_position) & 1
        extracted_bits.append(bit)

    print(f"Total extracted bits: {len(extracted_bits)}")

    # Convert the extracted bits back to bytes (limit to the correct number of bits)
    byte_array = bytearray()
    for i in range(0, len(extracted_bits), 8):
        byte_chunk = extracted_bits[i:i + 8]
        if len(byte_chunk) == 8:  # Only process full byte chunks
            byte_str = ''.join([str(bit) for bit in byte_chunk])
            byte_array.append(int(byte_str, 2))

    print(f"Final decoded byte array length: {len(byte_array)}")

    # Write the extracted bytes to an image file
    with open(output_image_file, 'wb') as output:
        output.write(byte_array)

    audio.close()

    return output_image_file


encoded_image_path = encode_image_with_size("C:/Users/School/Desktop/CyberSecruity/image.png", "C:/Users/School/Desktop/CyberSecruity/GOT_Theme.wav", 2)
print(f"Encoded image audio saved at: {encoded_image_path}")


decoded_image_path = decode_image_with_size("C:/Users/School/Desktop/CyberSecruity/encoded/encoded_image_GOT_Theme.wav", 2, "output_image.png")
print(f"Decoded image saved at: {decoded_image_path}")
