from PIL import Image
import numpy as np
import os

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary_data):
    return ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))

def encode_image(image_path, text_file, output_image):
    image = Image.open(image_path)
    image_array = np.array(image)

    with open(text_file, 'r') as file:
        text = file.read()

    text += "###END###"
    binary_text = text_to_binary(text)
    binary_index = 0
    binary_len = len(binary_text)

    for row in image_array:
        for pixel in row:
            for channel in range(3):  # R, G, B channels
                if binary_index < binary_len:
                    pixel[channel] = (pixel[channel] & ~1) | int(binary_text[binary_index])
                    binary_index += 1

    if binary_index < binary_len:
        raise ValueError("The message is too long to be encoded in the image.")

    output_dir = "images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, output_image)
    encoded_image = Image.fromarray(image_array)
    encoded_image.save(output_path)
    return output_path

def decode_image(image_path):
    image = Image.open(image_path)
    image_array = np.array(image)

    binary_data = ""
    for row in image_array:
        for pixel in row:
            for channel in range(3):  # R, G, B channels
                binary_data += str(pixel[channel] & 1)

    decoded_text = binary_to_text(binary_data)
    end_marker = "###END###"
    if end_marker in decoded_text:
        return decoded_text[:decoded_text.index(end_marker)]

    return decoded_text