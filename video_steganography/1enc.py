import math
import cv2
import os
from PIL import Image
from moviepy.editor import VideoFileClip, ImageSequenceClip

# Configuration Variables
video_file = "input.avi"  # Input video file
output_dir = "frames"            # Directory to save extracted frames
data_file = "payload.txt"        # File containing data to hide
frame = 10
output_video = "output.avi"  # Output video file
eof_marker = "$$$###$$$"

# Function to extract frames from video
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

def generateData(data):
    # Read the text from the file
    with open(data, 'r', encoding='utf8') as file:
        text = file.read()

    # Convert each character in the text to its binary representation
    binary_string = ''.join(format(ord(char), '08b') for char in text)

    # Convert the EOF marker to its binary representation
    binary_eof_marker = ''.join(format(ord(char), '08b') for char in eof_marker)

    # Append the EOF marker binary representation to the main binary string
    return binary_string + binary_eof_marker

def lsb_encode(frame, lsb_bits, text):
    # Open the image
    specFrame = 'frames/frame_' + str(frame) + '.png'
    image = Image.open(specFrame)
    pixels = image.load()
    
    # Convert the message and EOF marker to binary
    binary_message = generateData(text) 
    
    data_index = 0
    total_bits = len(binary_message)

    # Iterate through pixels to encode the message
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if data_index < total_bits:
                r, g, b = pixels[i, j]
                
                # Get the current pixel's red channel in binary
                r_bin = format(r, '08b')
                
                # Replace the last 'lsb_bits' bits with the binary message bits
                r_bin = r_bin[:-lsb_bits] + binary_message[data_index:data_index + lsb_bits]
                pixels[i, j] = (int(r_bin, 2), g, b)  # Update pixel with new red channel value
                
                data_index += lsb_bits
            
            if data_index >= total_bits:
                break  # Stop if all data is encoded
    
    # Save the image, overwriting the original
    image.save(specFrame)


# Function to combine frames back into a video with audio
def create_video_with_audio(frames_folder, audio_path, output_video, fps):
    frame_files = [os.path.join(frames_folder, f) for f in sorted(os.listdir(frames_folder), key=lambda x: int(x.split('_')[1].split('.')[0]))]
    clip = ImageSequenceClip(frame_files, fps=fps)  # Use the original fps
    video = VideoFileClip(audio_path)
    
    # Combine video and audio
    final_video = clip.set_audio(video.audio)
    
    # Ensure the output file has .avi extension
    output_video = output_video.rsplit('.', 1)[0] + '.avi'
    
    # Write directly to AVI using Huffyuv codec
    final_video.write_videofile(output_video, codec='ffv1')


def clear_output_directory(output_folder):
    if os.path.exists(output_folder):
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted frame: {file_path}")
    else:
        os.makedirs(output_folder)

# Main Execution
clear_output_directory(output_dir)
extract_frames(video_file, output_dir)

# Get the frame rate of the original video
cap = cv2.VideoCapture(video_file)
fps = cap.get(cv2.CAP_PROP_FPS)
cap.release()

lsb_encode(frame, 2, 'payload.txt')
create_video_with_audio(output_dir, video_file, output_video, fps)  # Pass the fps to the function
clear_output_directory(output_dir)
