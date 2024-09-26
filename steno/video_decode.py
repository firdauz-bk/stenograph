import cv2
import numpy as np
from PIL import Image
import os

# Configuration Variables
frame_number = 10           # Frame index for decoding (change this as needed)
frame_location = "frames"
output_file = "decoded_frame.txt"
eof_marker = "$$$###$$$"
video_file = "output.mkv"

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


def decode(frame_number, num_bits=3):
    frame_path = f"{frame_location}/frame_{frame_number}.png"
    
    try:
        image = Image.open(frame_path, 'r')
    except FileNotFoundError:
        print(f"Frame {frame_number} not found.")
        return ""
    
    data = ''
    imgdata = iter(image.getdata())

    while True:
        # Collect pixel values from 3 sets of RGB triplets
        pixels = [value for value in next(imgdata, (0, 0, 0))[:3] +
                  next(imgdata, (0, 0, 0))[:3] +
                  next(imgdata, (0, 0, 0))[:3]]
        
        # If all pixel values are 0, break the loop (end of image)
        if pixels == [0, 0, 0, 0, 0, 0, 0, 0, 0]:
            break

        # Decode one byte (8 bits) from the LSBs of the current pixels
        binstr = ''
        for j in range(8):
            bit_value = 0
            for b in range(num_bits):
                bit_value |= (pixels[j] & (1 << b)) >> b  # Extract the bit at position `b`
            binstr += '1' if bit_value != 0 else '0'

        # Convert the binary string to a character
        data += chr(int(binstr, 2))
        
        # Check if the last pixel's LSB indicates the end of the message
        end_marker = True
        for b in range(num_bits):
            if (pixels[-1] & (1 << b)) == 0:
                end_marker = False
                break
        if end_marker:
            break

    return data


# Main Execution
extract_frames(video_file, frame_location)
print("Extracting Data...")
with open(output_file, 'w', encoding='utf-8') as decoded_text_file:
    decoded_text_file.write('Decoded Text:\n')
    full_data = ''
    
    extracted_data = decode(frame_number)
    if extracted_data:
        full_data += extracted_data
        print(f"Data found in Frame {frame_number}")
        print(f"Sample decoded text from this frame: {extracted_data[:50]}...")
        
        if eof_marker in full_data:
            print("EOF marker found. Stopping extraction.")
    else:
        print(f"No data found in Frame {frame_number}")

    # Remove everything after the EOF marker
    if eof_marker in full_data:
        full_data = full_data.split(eof_marker)[0]
    
    decoded_text_file.write(full_data)

print("\nExtraction Complete! Decoded text saved to", output_file)
print(full_data)
