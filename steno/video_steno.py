import cv2
import numpy as np
from PIL import Image
import os
from moviepy.editor import VideoFileClip, ImageSequenceClip

eof_marker = "$$$###$$$"

def extract_frames(video_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError("Error: Could not open video.")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_filename = os.path.join(output_folder, f"frame_{frame_count}.png")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1
    
    cap.release()
    return frame_count

def generateData(data):
    with open(data, 'r', encoding='utf8') as file:
        text = file.read()
    binary_string = ''.join(format(ord(char), '08b') for char in text)
    binary_eof_marker = ''.join(format(ord(char), '08b') for char in eof_marker)
    return binary_string + binary_eof_marker

def lsb_encode(image_path, binary_message, lsb_bits):
    image = Image.open(image_path)
    pixels = image.load()
    
    data_index = 0
    total_bits = len(binary_message)

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if data_index < total_bits:
                r, g, b = pixels[i, j]
                r_bin = format(r, '08b')
                r_bin = r_bin[:-lsb_bits] + binary_message[data_index:data_index + lsb_bits]
                pixels[i, j] = (int(r_bin, 2), g, b)
                data_index += lsb_bits
            
            if data_index >= total_bits:
                break
    
    image.save(image_path)

def lsb_decode(image_path, lsb_bits):
    image = Image.open(image_path)
    pixels = image.load()
    
    binary_message = ''
    
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            r, g, b = pixels[i, j]
            r_bin = format(r, '08b')
            binary_message += r_bin[-lsb_bits:]
    
    decoded_message = ''
    for i in range(0, len(binary_message), 8):
        char_bin = binary_message[i:i+8]
        if len(char_bin) < 8:
            continue
        decoded_char = chr(int(char_bin, 2))
        decoded_message += decoded_char
        
        if decoded_message.endswith(eof_marker):
            return decoded_message[:-len(eof_marker)]
    
    return decoded_message

def encode_video(video_path, payload_path, frame_number, lsb_bits, output_dir):
    temp_dir = os.path.join(output_dir, 'temp_frames')
    extract_frames(video_path, temp_dir)
    
    binary_message = generateData(payload_path)
    
    frame_path = os.path.join(temp_dir, f"frame_{frame_number}.png")
    lsb_encode(frame_path, binary_message, lsb_bits)
    
    # Recombine frames into video
    frame_files = [os.path.join(temp_dir, f) for f in sorted(os.listdir(temp_dir), key=lambda x: int(x.split('_')[1].split('.')[0]))]
    
    clip = ImageSequenceClip(frame_files, fps=VideoFileClip(video_path).fps)
    output_path = os.path.join(output_dir, 'encoded_video.mp4')
    clip.write_videofile(output_path, codec='libx264')
    
    # Clean up temporary files
    for file in frame_files:
        os.remove(file)
    os.rmdir(temp_dir)
    
    return output_path

def decode_video(video_path, frame_number, lsb_bits, output_dir):
    temp_dir = os.path.join(output_dir, 'temp_frames')
    extract_frames(video_path, temp_dir)
    
    frame_path = os.path.join(temp_dir, f"frame_{frame_number}.png")
    decoded_message = lsb_decode(frame_path, lsb_bits)
    
    # Clean up temporary files
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)
    
    return decoded_message