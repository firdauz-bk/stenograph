import math
import cv2
import os
from PIL import Image
from moviepy.editor import VideoFileClip, ImageSequenceClip

# Configuration Variables
video_file = "input_video.mp4"  # Input video file
output_dir = "frames"    # Directory to save extracted frames
data_file = "payload.txt"     # File containing data to hide
start_frame = 1                         # Starting frame index for encoding
end_frame = 30                           # Ending frame index for encoding
output_video = "output_video.mp4"  # Output video file

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
    newdata = []
    for i in data:
        newdata.append(format(ord(i), '08b'))
    return newdata

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

def encode(start, end, data, frame_loc):
    total_frame = end - start + 1
    try:
        with open(data) as fileinput:
            filedata = fileinput.read()
    except FileNotFoundError:
        print("\nFile to hide not found! Exiting...")
        return
    
    datapoints = math.ceil(len(filedata) / total_frame)
    counter = start
    print("Performing Steganography...")
    
    for convnum in range(0, len(filedata), datapoints):
        numbering = os.path.join(frame_loc, f"frame_{counter}.png")
        encodetext = filedata[convnum:convnum + datapoints]
        try:
            image = Image.open(numbering, 'r')
        except FileNotFoundError:
            print(f"\n{counter}.png not found! Exiting...")
            return
        newimage = image.copy()
        encoder(newimage, encodetext)
        newimage.save(numbering, 'PNG')
        counter += 1
    print("Encoding complete!")

# Function to combine frames back into a video with audio
def create_video_with_audio(frames_folder, audio_path, output_video):
    frame_files = [os.path.join(frames_folder, f) for f in sorted(os.listdir(frames_folder), key=lambda x: int(x.split('_')[1].split('.')[0]))]
    clip = ImageSequenceClip(frame_files, fps=30)  # Adjust fps as needed
    video = VideoFileClip(audio_path)
    
    # Combine video and audio
    final_video = clip.set_audio(video.audio)
    final_video.write_videofile(output_video, codec='libx264')

# Main Execution
extract_frames(video_file, output_dir)
encode(start_frame, end_frame, data_file, output_dir)
create_video_with_audio(output_dir, video_file, output_video)
