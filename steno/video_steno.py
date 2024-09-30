import math
import cv2
import os
from PIL import Image
from moviepy.editor import VideoFileClip, ImageSequenceClip

EOF_MARKER = "$$$###$$$"

# Get the directory of the current file (video_steno.py)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Set BASE_DIR to the parent directory of 'steno/', which is the project root
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))

# Define the frames directory in the project root
FRAMES_DIR = os.path.join(BASE_DIR, 'frames')

def extract_frames(video_path, output_folder=FRAMES_DIR):
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
    
    cap.release()

def generate_data(data_file):
    with open(data_file, 'r', encoding='utf8') as file:
        text = file.read()

    binary_string = ''.join(format(ord(char), '08b') for char in text)
    binary_eof_marker = ''.join(format(ord(char), '08b') for char in EOF_MARKER)
    return binary_string + binary_eof_marker

def lsb_encode(frame_number, lsb_bits, data_file, frames_folder=FRAMES_DIR):
    spec_frame = os.path.join(frames_folder, f'frame_{frame_number}.png')
    if not os.path.exists(spec_frame):
        raise FileNotFoundError(f"Frame {spec_frame} not found.")
    
    image = Image.open(spec_frame)
    pixels = image.load()
    binary_message = generate_data(data_file)
    
    data_index = 0
    total_bits = len(binary_message)
    width, height = image.size
    
    for i in range(width):
        for j in range(height):
            if data_index < total_bits:
                r, g, b = pixels[i, j]
                r_bin = format(r, '08b')
                bits_to_embed = binary_message[data_index:data_index + lsb_bits]
                bits_to_embed = bits_to_embed.ljust(lsb_bits, '0')
                r_bin = r_bin[:-lsb_bits] + bits_to_embed
                pixels[i, j] = (int(r_bin, 2), g, b)
                data_index += lsb_bits
            if data_index >= total_bits:
                break
        if data_index >= total_bits:
            break
    
    image.save(spec_frame)

def create_video_with_audio(audio_path, output_video, fps, frames_folder=FRAMES_DIR):
    frame_files = [
        os.path.join(frames_folder, f)
        for f in sorted(
            os.listdir(frames_folder),
            key=lambda x: int(x.split('_')[1].split('.')[0])
        )
    ]
    clip = ImageSequenceClip(frame_files, fps=fps)
    video = VideoFileClip(audio_path)
    final_video = clip.set_audio(video.audio)
    output_video = output_video.rsplit('.', 1)[0] + '.avi'
    final_video.write_videofile(output_video, codec='ffv1')
    final_video.close()
    clip.close()
    video.close()

def clear_output_directory(output_folder=FRAMES_DIR):
    if os.path.exists(output_folder):
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(output_folder)

def encode_video(video_file, data_file, frame_number, lsb_bits, output_video, frames_folder=FRAMES_DIR):
    clear_output_directory(frames_folder)
    extract_frames(video_file, frames_folder)
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    lsb_encode(frame_number, lsb_bits, data_file, frames_folder)
    # Corrected the order of arguments in the function call below
    create_video_with_audio(video_file, output_video, fps, frames_folder)
    clear_output_directory(frames_folder)

################################### DECODE SECTION #######################################

def lsb_decode(frame_number, lsb_bits, frames_folder=FRAMES_DIR):
    # Open the image
    img_path = os.path.join(frames_folder, f'frame_{frame_number}.png')
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Frame image not found: {img_path}")
    
    image = Image.open(img_path)
    pixels = image.load()
    
    binary_message = ''
    width, height = image.size

    for i in range(width):
        for j in range(height):
            r, g, b = pixels[i, j]
            # Extract LSBs from red channel
            r_bin = format(r, '08b')
            binary_message += r_bin[-lsb_bits:]
    
    # Convert binary data to text
    decoded_message = ''
    binary_eof_marker = ''.join(format(ord(char), '08b') for char in EOF_MARKER)
    eof_index = binary_message.find(binary_eof_marker)
    
    if eof_index != -1:
        binary_message = binary_message[:eof_index]
    else:
        # If EOF marker not found, decode all available data
        pass
    
    # Split into 8-bit chunks and convert to characters
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        if len(byte) < 8:
            continue  # Skip incomplete byte
        decoded_char = chr(int(byte, 2))
        decoded_message += decoded_char
    
    return decoded_message

def decode_video(video_file, frame_number, lsb_bits, frames_folder=FRAMES_DIR):

    clear_output_directory(frames_folder)
    extract_frames(video_file, frames_folder)
    cap = cv2.VideoCapture(video_file)
    cap.release()
    decoded_data = lsb_decode(frame_number, lsb_bits, frames_folder)

    # Clean up and return
    clear_output_directory(frames_folder)
    return decoded_data
