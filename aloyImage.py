from PIL import Image
import numpy as np
import os

# Function to convert text to binary
def text_to_binary(text):
    binary = ''.join([format(ord(char), '08b') for char in text])
    return binary

# Function to convert binary data to text
def binary_to_text(binary_data):
    text = ''
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        text += chr(int(byte, 2))
    return text

# Function to encode data into the image
def encode_image(image_path, text_file, output_image):
    # Load the image
    image = Image.open(image_path)
    image_array = np.array(image)

    # Read the text from file
    with open(text_file, 'r') as file:
        text = file.read()

    # Append a delimiter to mark the end of the message
    text += "###END###"

    # Convert the text to binary
    binary_text = text_to_binary(text)
    
    binary_index = 0
    binary_len = len(binary_text)

    # Iterate through pixels and encode binary data
    for row in image_array:
        for pixel in row:
            for channel in range(3):  # R, G, B channels
                if binary_index < binary_len:
                    # Change the LSB of the current channel
                    pixel[channel] = (pixel[channel] & ~1) | int(binary_text[binary_index])
                    binary_index += 1

    # If the message is larger than the image can handle
    if binary_index < binary_len:
        raise ValueError("The message is too long to be encoded in the image.")

    # Create the 'images' directory if it doesn't exist
    output_dir = "images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the new image with the hidden message in the 'images' folder
    output_path = os.path.join(output_dir, output_image)
    encoded_image = Image.fromarray(image_array)
    encoded_image.save(output_path)
    print(f"Message successfully encoded into {output_path}")

# Function to decode the hidden text from the image
def decode_image(image_path):
    # Load the image
    image = Image.open(image_path)
    image_array = np.array(image)

    binary_data = ""
    for row in image_array:
        for pixel in row:
            for channel in range(3):  # R, G, B channels
                # Extract the least significant bit and append to binary_data
                binary_data += str(pixel[channel] & 1)

    # Split the binary data into bytes and convert to text
    decoded_text = binary_to_text(binary_data)

    # Look for the delimiter to determine the end of the message
    end_marker = "###END###"
    if end_marker in decoded_text:
        return decoded_text[:decoded_text.index(end_marker)]  # Remove the end marker

    return decoded_text

# Example usage
image_path = "images/ndp at padang-23.jpg"  # Path to the input image file
text_file = "payload.txt"    # Path to the input text file
output_image = "encoded_image.png"  # Output encoded image file

encode_image(image_path, text_file, output_image)
print(f"Decoded message: {decode_image(output_image)}")