import cv2
import numpy as np

def binary_to_text(binary):
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def decode_frame(frame):
    binary_data = ""
    for i in range(frame.shape[0]):
        for j in range(frame.shape[1]):
            for k in range(3):  # RGB channels
                binary_data += str(frame[i, j, k] & 1)
    return binary_data

def decode_video(input_video, output_text):
    # Read the input video
    cap = cv2.VideoCapture(input_video)
    
    binary_data = ""
    eof_marker = '1111111111111110'
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        binary_data += decode_frame(frame)
        
        # Check if we've reached the EOF marker
        if eof_marker in binary_data:
            binary_data = binary_data[:binary_data.index(eof_marker)]
            break
    
    cap.release()
    
    # Convert binary data to text
    decoded_text = binary_to_text(binary_data)
    
    # Write the decoded text to a file
    with open(output_text, 'w', encoding='utf-8') as file:
        file.write(decoded_text)
    
    print("Decoding complete. Text saved to", output_text)

# Example usage
input_video = "output_encoded.mp4"  # This should be the output from the encoder
output_text = "decoded_secret.txt"

# Decode
decode_video(input_video, output_text)