import cv2
import numpy as np
from PIL import Image
import os

# Configuration Variables
frame_start = 0
frame_end = 40
frame_location = "frames"
output_file = "decoded_frame.txt"
eof_marker = "$$$###$$$"

def decode(frame_number):
    frame_path = f"{frame_location}/frame_{frame_number}.png"
    
    try:
        image = Image.open(frame_path, 'r')
    except FileNotFoundError:
        print(f"Frame {frame_number} not found.")
        return ""
    
    data = ''
    imgdata = iter(image.getdata())

    while True:
        pixels = [value for value in next(imgdata, (0,0,0))[:3] +
                  next(imgdata, (0,0,0))[:3] +
                  next(imgdata, (0,0,0))[:3]]
        
        # If we're out of pixels, break the loop
        if pixels == [0,0,0,0,0,0,0,0,0]:
            break

        binstr = ''.join(['1' if i % 2 != 0 else '0' for i in pixels[:8]])
        data += chr(int(binstr, 2))
        
        if pixels[-1] % 2 != 0:
            break

    return data

# Main Execution
print("Extracting Data...")
with open(output_file, 'w', encoding='utf-8') as decoded_text_file:
    decoded_text_file.write('Decoded Text:\n')
    full_data = ''
    
    for frame_number in range(frame_start, frame_end + 1):
        extracted_data = decode(frame_number)
        if extracted_data:
            full_data += extracted_data
            print(f"Data found in Frame {frame_number}")
            print(f"Sample decoded text from this frame: {extracted_data[:50]}...")
            if eof_marker in full_data:
                print("EOF marker found. Stopping extraction.")
                break
        else:
            print(f"No data found in Frame {frame_number}")

    # Remove everything after the EOF marker
    if eof_marker in full_data:
        full_data = full_data.split(eof_marker)[0]
    
    decoded_text_file.write(full_data)

print("\nExtraction Complete! Decoded text saved to", output_file)
print(full_data)