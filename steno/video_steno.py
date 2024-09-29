# video_steno.py

import math
import cv2
import os
from PIL import Image
from moviepy.editor import VideoFileClip, ImageSequenceClip

EOF_MARKER = "$$$###$$$"

def extract_frames(video_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError("Error: Could not open video.")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_filename = os.path.join(output_folder, f"frame_{frame_count}.png")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1
        #print(f"Extracted frame {frame_count}")
    
    cap.release()
    #print("Frame extraction complete!")

def generate_data(data_file):
    # Read the text from the file
    with open(data_file, 'r', encoding='utf8') as file:
        text = file.read()

    # Convert each character in the text to its binary representation
    binary_string = ''.join(format(ord(char), '08b') for char in text)

    # Convert the EOF marker to its binary representation
    binary_eof_marker = ''.join(format(ord(char), '08b') for char in EOF_MARKER)

    # Append the EOF marker binary representation to the main binary string
    return binary_string + binary_eof_marker

def lsb_encode(frame_number, lsb_bits, data_file, frames_folder):
    # Open the specific frame
    frame_path = os.path.join(frames_folder, f'frame_{frame_number}.png')
    if not os.path.exists(frame_path):
        raise FileNotFoundError(f"Frame {frame_path} not found.")
    
    image = Image.open(frame_path)
    pixels = image.load()
    
    # Convert the message and EOF marker to binary
    binary_message = generate_data(data_file)
    
    data_index = 0
    total_bits = len(binary_message)

    width, height = image.size

    # Iterate through pixels to encode the message
    for y in range(height):
        for x in range(width):
            if data_index < total_bits:
                r, g, b = pixels[x, y]
                
                # Convert to binary
                r_bin = format(r, '08b')
                
                # Modify the LSB bits
                bits_to_embed = binary_message[data_index:data_index + lsb_bits]
                bits_to_embed = bits_to_embed.ljust(lsb_bits, '0')
                r_bin = r_bin[:-lsb_bits] + bits_to_embed

                # Update pixel
                pixels[x, y] = (int(r_bin, 2), g, b)
                
                data_index += lsb_bits
            else:
                break
        if data_index >= total_bits:
            break
    
    # Save the modified frame
    image.save(frame_path)

def create_video_with_audio(frames_folder, audio_path, output_video, fps):
    # Get list of frame files
    frame_files = sorted(
        [f for f in os.listdir(frames_folder) if f.startswith('frame_')],
        key=lambda x: int(x.split('_')[1].split('.')[0])
    )
    frame_paths = [os.path.join(frames_folder, f) for f in frame_files]
    
    # Create video clip from frames
    clip = ImageSequenceClip(frame_paths, fps=fps)
    
    # Load audio from original video
    video = VideoFileClip(audio_path)
    
    # Combine video and audio
    final_video = clip.set_audio(video.audio)
    
    # Write the output video file
    final_video.write_videofile(output_video, codec='libx264', audio_codec='aac')
    
    final_video.close()
    clip.close()
    video.close()
    del final_video
    del clip
    del video

def clear_output_directory(output_folder):
    if os.path.exists(output_folder):
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(output_folder)

def encode_video(video_file, data_file, frame_number, lsb_bits, output_video):
    output_dir = 'frames'
    clear_output_directory(output_dir)
    
    # Extract frames from video
    extract_frames(video_file, output_dir)
    
    # Get the frame rate of the original video
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    # Encode the message into the specified frame
    lsb_encode(frame_number, lsb_bits, data_file, output_dir)
    
    # Recreate the video with audio
    create_video_with_audio(output_dir, video_file, output_video, fps)
    
    # Optionally clear the frames directory after encoding
    clear_output_directory(output_dir)
