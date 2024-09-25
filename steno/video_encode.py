import math
import cv2
import os
from PIL import Image
from moviepy.editor import VideoFileClip, ImageSequenceClip

# Configuration Variables
video_file = "input.mp4"  # Input video file
output_dir = "frames"      # Directory to save extracted frames
data_file = "payload.txt"  # File containing data to hide
target_frame = 10           # Frame index for encoding (change this as needed)
output_video = "output_video.mp4"  # Output video file
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

# Convert encoding data into 8-bit binary ASCII
def generateData(data):
    return [format(ord(i), '08b') for i in data]

# Modify pixels according to encoding data
def modifyPixel(pixel, data):
    datalist = generateData(data)
    lengthofdata = len(datalist)
    imagedata = iter(pixel)
    
    for i in range(lengthofdata):
        pixel = [value for value in imagedata.__next__()[:3] + imagedata.__next__()[:3] + imagedata.__next__()[:3]]
        
        for j in range(0, 8):
            if (datalist[i][j] == '0' and pixel[j] % 2 != 0):
                pixel[j] -= 1
            elif (datalist[i][j] == '1' and pixel[j] % 2 == 0):
                pixel[j] += 1 if pixel[j] == 0 else -1
        
        if (i == lengthofdata - 1):
            pixel[-1] -= 1 if pixel[-1] % 2 == 0 else 0
        else:
            pixel[-1] -= 1 if pixel[-1] % 2 != 0 else 0
        
        pixel = tuple(pixel)
        yield pixel[0:3]
        yield pixel[3:6]
        yield pixel[6:9]

# Main encoding function
def encoder(newimage, data):
    w = newimage.size[0]
    (x, y) = (0, 0)
    for pixel in modifyPixel(newimage.getdata(), data):
        newimage.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1

# Function to perform encoding
def encode(target_frame, data, frame_loc):
    try:
        with open(data) as fileinput:
            filedata = fileinput.read()
    except FileNotFoundError:
        print("\nFile to hide not found! Exiting...")
        return
    
    # Append the EOF marker
    filedata += eof_marker

    numbering = os.path.join(frame_loc, f"frame_{target_frame}.png")
    
    try:
        image = Image.open(numbering, 'r')
    except FileNotFoundError:
        print(f"\n{target_frame}.png not found! Exiting...")
        return
    
    newimage = image.copy()
    encoder(newimage, filedata)
    newimage.save(numbering, 'PNG')
    print("Encoding complete!")

# Function to combine frames back into a video with audio
def create_video_with_audio(frames_folder, audio_path, output_video, fps):
    frame_files = [os.path.join(frames_folder, f) for f in sorted(os.listdir(frames_folder), key=lambda x: int(x.split('_')[1].split('.')[0]))]
    clip = ImageSequenceClip(frame_files, fps=fps)  # Use the original fps
    video = VideoFileClip(audio_path)
    
    # Combine video and audio
    final_video = clip.set_audio(video.audio)
    final_video.write_videofile(output_video, codec='libx264')

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

# Encode the message into the specified frame
encode(target_frame, data_file, output_dir)
create_video_with_audio(output_dir, video_file, output_video, fps)  # Pass the fps to the function
