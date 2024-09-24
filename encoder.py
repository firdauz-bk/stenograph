import cv2
import numpy as np

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def encode_frame(frame, binary_data, data_index):
    for i in range(frame.shape[0]):
        for j in range(frame.shape[1]):
            for k in range(3):  # RGB channels
                if data_index < len(binary_data):
                    frame[i, j, k] = (frame[i, j, k] & 0xFE) | int(binary_data[data_index])
                    data_index += 1
                else:
                    return frame, data_index
    return frame, data_index

def encode_video(input_video, input_text, output_video):
    # Read the input video
    cap = cv2.VideoCapture(input_video)
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # Read the text file
    with open(input_text, 'r') as file:
        text = file.read()
    
    # Convert text to binary
    binary_data = text_to_binary(text)
    binary_data += '1111111111111110'  # EOF marker
    
    data_index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if data_index < len(binary_data):
            frame, data_index = encode_frame(frame, binary_data, data_index)
        
        out.write(frame)
    
    cap.release()
    out.release()
    print("Encoding complete.")
    
    if data_index < len(binary_data):
        print("Warning: Not all data was encoded. Video too short for the given text.")
    else:
        print("All data successfully encoded.")

# Example usage
input_video = "input.mp4"
input_text = "secret.txt"
output_video = "output_encoded.mp4"

# Encode
encode_video(input_video, input_text, output_video)