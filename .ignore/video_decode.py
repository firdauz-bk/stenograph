import cv2
import numpy as np
from PIL import Image
import os

# Configuration Variables
lsb_bits = 1
frame_location = "frames"
eof_marker = "$$$###$$$"
video = 'output.avi'
def extract_frames(video_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_filename = os.path.join(output_folder, f"frame_{frame_count}.png")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1
        print(f"Extracted frame {frame_count}")
    
    cap.release()
    print("Frame extraction complete!")

def lsb_decode(frame, lsb_bits):
    # Open the image
    img_path = os.path.join(frame_location, f'frame_{frame}.png')
    image = Image.open(img_path)
    pixels = image.load()
    
    binary_message = ''
    
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            r, g, b = pixels[i, j]
            
            # Extract LSBs from red channel
            r_bin = format(r, '08b')
            binary_message += r_bin[-lsb_bits:]
    
    # Split into 8-bit chunks and convert to characters
    decoded_message = ''
    for i in range(0, len(binary_message), 8):
        char_bin = binary_message[i:i+8]
        if len(char_bin) < 8:
            continue  # Skip incomplete byte
        decoded_char = chr(int(char_bin, 2))
        decoded_message += decoded_char
        
        # Stop decoding if we hit the EOF marker
        if decoded_message.endswith(eof_marker):  # Use the actual EOF marker
            decoded_message = decoded_message[:-len(eof_marker)]
            break
    
    return decoded_message

# Main Execution
frame_number = 1  # Specify the frame you want to decode
extract_frames(video, frame_location)
decoded_data = lsb_decode(frame_number, lsb_bits)

# Print the decoded data
print(f"Decoded Data from Frame {frame_number}:\n{decoded_data}")