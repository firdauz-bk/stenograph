import re
from PIL import Image
import os

# Configuration Variables
frame_start = 0                          # Starting frame index for decoding
frame_end = 30                           # Ending frame index for decoding
frame_location = "frames"        # Path to the directory containing the frames
output_file = "decoded_frame.txt" # Output file for the decoded text

# Decode the data in the image
def decode(frame_number):
    data = ''
    frame_path = f"{frame_location}/frame_{frame_number}.png"
    
    try:
        image = Image.open(frame_path, 'r')
    except FileNotFoundError:
        print(f"Frame {frame_number} not found.")
        return ""
    
    imagedata = iter(image.getdata())
    
    while True:
        # Extract pixels
        pixels = [value for _ in range(3) for value in imagedata.__next__()[:3]]
        if not pixels:
            break  # No more pixels to read
        
        # Build the binary string
        binstr = ''.join('1' if pixel % 2 else '0' for pixel in pixels[:8])
        
        # Decode to character
        char = chr(int(binstr, 2))
        
        # Debug output to check binary string and character
        print(f"Frame {frame_number}: Binary = {binstr}, Char = {char}")
        
        if char == '$':  # Check for the EOF marker (adjust this if you're using a different marker)
            break
        
        if re.match("[ -~]", char):  # Check if it's a printable character
            data += char

    return data# Main Execution

print("Extracting Data...")
with open(output_file, 'w', encoding='utf-8') as decoded_text_file:
    decoded_text_file.write('Decoded Text:\n')
    
    for frame_number in range(frame_start, frame_end + 1):
        extracted_data = decode(frame_number)
        if extracted_data:
            decoded_text_file.write(extracted_data)
            print(f"Data found in Frame {frame_number}")
        else:
            print(f"No data found in Frame {frame_number}")

print("\nExtraction Complete! Decoded text saved to", output_file)
