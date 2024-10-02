from flask import Flask, render_template, redirect, url_for, request, send_file, flash, session
from werkzeug.utils import secure_filename
import os
from io import BytesIO
import zipfile
from steno.image_steno import encode_image, decode_image
from steno.audio_steno import encode_audio, decode_audio, encode_image_in_audio, decode_image_in_audio
from steno.video_steno import encode_video, decode_video, FRAMES_DIR
import cv2
import base64

app = Flask(__name__)
app.secret_key = 'ILOVEINF2005!'  # Set a secret key for flashing messages

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'encoded_files'

# Ensure the upload and output folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Allowed file extensions
def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

#################### INDEX PAGE ########################
@app.route('/')                                        
def index():                                           
    return render_template('index.html')              

################################# AUDIO ENCODING PAGE #####################################################################################
@app.route('/audio')
def audio():
    return render_template('encode_audio.html')

@app.route('/encode_audio', methods=['GET', 'POST'])
def encode_audio_route():
    if request.method == 'POST':
        if 'payload_audio' not in request.files or 'cover_audio' not in request.files:
            flash('Both payload and cover files are required', 'error')
            return redirect(url_for('audio'))
        
        payload = request.files['payload_audio']
        cover = request.files['cover_audio']
        bit_size = request.form.get('bit_size', 1)

        if payload.filename == '' or cover.filename == '':
            flash('Both payload and cover files are required', 'error')
            return redirect(url_for('audio'))

        # Validate bit_size
        try:
            bit_size = int(bit_size)
            if not (1 <= bit_size <= 8):
                flash('Bit size must be between 1 and 8', 'error')
                return redirect(url_for('audio'))
        except ValueError:
            flash('Invalid bit size', 'error')
            return redirect(url_for('audio'))

        # Validate file types using allowed_file function
        if not allowed_file(payload.filename, {'txt', 'png'}):
            flash('Unsupported payload file type. Allowed types: .txt, .png', 'error')
            return redirect(url_for('audio'))
        if not allowed_file(cover.filename, {'wav', 'mp3'}):
            flash('Unsupported cover file type. Allowed type: .wav, .mp3', 'error')
            return redirect(url_for('audio'))

        payload_filename = secure_filename(payload.filename)
        cover_filename = secure_filename(cover.filename)

        payload_path = os.path.join(app.config['UPLOAD_FOLDER'], payload_filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)

        payload.save(payload_path)
        cover.save(cover_path)

        try:
            # Process based on payload file extension
            payload_extension = os.path.splitext(payload_filename)[1].lower()

            if payload_extension == '.txt':
                # Call the encode_audio function for text payloads
                output_path = encode_audio(payload_path, cover_path, bit_size=bit_size, output_dir=app.config['OUTPUT_FOLDER'])
                flash('Encoding successful!', 'success')
                return send_file(output_path, as_attachment=True,
                                download_name=os.path.basename(output_path))
            elif payload_extension == '.png':
                # Call the encode_image_in_audio function for image payloads
                output_path, payload_size = encode_image_in_audio(
                    png_file=payload_path,
                    audio_file=cover_path,
                    bit_size=bit_size,
                    output_dir=app.config['OUTPUT_FOLDER']
                )
                flash(f'Encoding successful! Payload size: {payload_size} bytes', 'success')

                # Clean up uploaded files
                if os.path.exists(payload_path):
                    os.remove(payload_path)
                if os.path.exists(cover_path):
                    os.remove(cover_path)

                return send_file(output_path, as_attachment=True,
                                download_name=os.path.basename(output_path))
                # Render the result template and pass the filename
                #return render_template('encode_image_in_audio_result.html', download_name=os.path.basename(output_path))
                    
            else:
                flash('Unsupported payload file type', 'error')
                return redirect(url_for('audio'))

        except ValueError as e:
            flash(f'Encoding failed: {str(e)}', 'error')
            return redirect(url_for('audio'))
        except Exception as e:
            flash(f'An unexpected error occurred: {str(e)}', 'error')
            return redirect(url_for('audio'))
        finally:
            # Clean up uploaded files
            if os.path.exists(payload_path):
                os.remove(payload_path)
            if os.path.exists(cover_path):
                os.remove(cover_path)
    else:
        return render_template('encode_image_in_audio.html')
################################# VIDEO ENCODING PAGE #####################################################################################
@app.route('/video')
def video():
    
    return render_template('encode_video.html')


@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'cover_video' not in request.files:
        flash('No video file uploaded', 'error')
        return redirect(url_for('video'))
    
    video = request.files['cover_video']
    
    if video.filename == '':
        flash('No video file selected', 'error')
        return redirect(url_for('video'))
    
    if video and allowed_file(video.filename, {'mp4', 'avi', 'mkv'}):
        filename = secure_filename(video.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(video_path)
        
        # Get total frames and frame rate
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        session['video_path'] = video_path
        session['total_frames'] = total_frames
        session['fps'] = fps
        session['video_uploaded'] = True

        flash(f'Video uploaded successfully. {total_frames} frames detected.', 'success')
        return redirect(url_for('video'))
    
    flash('Invalid file type. Please upload an MP4 or AVI file.', 'error')
    return redirect(url_for('video'))

@app.route('/encode_video', methods=['POST'])
def encode_video_route():
    if 'video_path' not in session:
        flash('Please upload a video first', 'error')
        return redirect(url_for('video'))
    
    if 'payload_video' not in request.files:
        flash('No payload file uploaded', 'error')
        return redirect(url_for('video'))
    
    payload = request.files['payload_video']
    frame_number = int(request.form.get('frame_number', 1))
    lsb_bits = int(request.form.get('bit_size', 1))
    
    total_frames = session.get('total_frames', 0)
    if frame_number < 0 or frame_number >= total_frames:
        flash('Invalid frame number', 'error')
        return redirect(url_for('video'))
    
    if payload.filename == '':
        flash('No payload file selected', 'error')
        return redirect(url_for('video'))
    
    if payload and payload.filename.lower().endswith('.txt'):
        payload_filename = secure_filename(payload.filename)
        payload_path = os.path.join(app.config['UPLOAD_FOLDER'], payload_filename)
        payload.save(payload_path)
    
        try:
            video_path = session['video_path']
            video_extension = os.path.splitext(video_path)[1].lower()
            if video_extension == '.mkv':
                output_video_name = f"encoded_{os.path.splitext(os.path.basename(video_path))[0]}.mkv"
            elif video_extension == '.avi':
                output_video_name = f"encoded_{os.path.splitext(os.path.basename(video_path))[0]}.avi"
            else:
                # Default to .avi if no valid extension is provided
                output_video_name = f"encoded_{os.path.splitext(os.path.basename(video_path))[0]}.avi"

            output_video_path = os.path.join(app.config['OUTPUT_FOLDER'], output_video_name)
            # Call the encode_video function
            encode_video(
                video_file=video_path,
                data_file=payload_path,
                frame_number=frame_number,
                lsb_bits=lsb_bits,
                output_video=output_video_path,
                frames_folder=FRAMES_DIR
            )
            
            flash('Encoding successful!', 'success')
            # Send the output video file to the user
            return send_file(output_video_path, as_attachment=True, download_name=output_video_name)
        
        except Exception as e:
            flash(f'Encoding failed: {str(e)}', 'error')
            return redirect(url_for('video'))
        
        finally:
            # Clean up temporary files
            os.remove(payload_path)
            os.remove(video_path)
            session.pop('video_path', None)
            session.pop('total_frames', None)
            session.pop('fps', None)
            session.pop('video_uploaded', None)

    else:
        flash('Invalid payload file type. Please upload a .txt file.', 'error')
        return redirect(url_for('video'))

################################# IMAGE ENCODING PAGE #####################################################################################
@app.route('/image')
def image():
    return render_template('encode_image.html')

@app.route('/encode_image', methods=['POST'])
def encode_image_route():
    if 'payload_image' not in request.files or 'cover_image' not in request.files:
        flash('Both payload and cover files are required')
        return redirect(url_for('image'))
    
    payload = request.files['payload_image']
    cover = request.files['cover_image']
    bit_size = int(request.form.get('bit_size', 1))
    
    if payload.filename == '' or cover.filename == '':
        flash('Both payload and cover files are required')
        return redirect(url_for('image'))
    
    if payload and cover:
        payload_filename = secure_filename(payload.filename)
        cover_filename = secure_filename(cover.filename)
        
        payload_path = os.path.join(app.config['UPLOAD_FOLDER'], payload_filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)
        
        payload.save(payload_path)
        cover.save(cover_path)
        
        output_filename = f"encoded_{cover_filename}"
        
        try:
            output_path = encode_image(cover_path, payload_path, output_filename, lsb_count=bit_size)
            return send_file(output_path, as_attachment=True)
        
        except Exception as e:
            flash(f'Encoding failed: {str(e)}')
            return redirect(url_for('image'))


################################# DECODING PAGE ###########################################################################################
@app.route('/decoder')                                        
def decode():                                           
    return render_template('decode.html')  

@app.route('/decode_text')
def decode_text_page():
    return render_template('decode_text.html')

@app.route('/decode_text', methods=['GET','POST'])
def decode_text_post():
    if request.method == 'POST':
        if 'decode_payload_text' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        stego_file = request.files['decode_payload_text']
        
        if stego_file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if stego_file:
            filename = secure_filename(stego_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            stego_file.save(file_path)
                    
            try:
            #### DETERMINE THE FILETYPE TO USE THEIR RESPECTIVE FUNCTION ####
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in ['.png', '.gif', '.bmp', '.jpg']:
                    bit_size = int(request.form.get('bit_size', 1))
                    decoded_message = decode_image(file_path, lsb_count=bit_size)

                elif file_extension in ['.mp3', '.wav']:
                    bit_size = int(request.form.get('bit_size', 1))
                    decoded_message = decode_audio(file_path, bit_size=bit_size)

                elif file_extension in ['.mp4', '.avi', '.mkv']:
                    bit_size = int(request.form.get('bit_size', 1))
                    frame_number = int(request.form.get('frame_number', 1))

                    # Get total number of frames in the video
                    cap = cv2.VideoCapture(file_path)
                    if not cap.isOpened():
                        cap.release()
                        os.remove(file_path)
                        flash('Error opening video file', 'error')
                        return redirect(request.url)
                    
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    cap.release()

                    if frame_number < 0 or frame_number >= total_frames:
                        os.remove(file_path)
                        flash(f'Invalid frame number. The video has {total_frames} frames.', 'error')
                        return redirect(request.url)

                    decoded_message = decode_video(
                        video_file=file_path,
                        frame_number=frame_number,
                        lsb_bits=bit_size,
                        frames_folder=FRAMES_DIR
                    )
                else:
                    os.remove(file_path)
                    flash('Unsupported file type', 'error')
                    return redirect(request.url)
                
                # Remove the uploaded file after processing
                os.remove(file_path)
                
                return render_template('decode_text.html', decoded_message=decoded_message)
            except Exception as e:
                flash(f'Error decoding file: {str(e)}')
                return redirect(request.url)
        else:
            return render_template('decode_text.html')

@app.route('/decode_image')
def decode_image_page():
    return render_template('decode_image.html')

@app.route('/decode_image', methods=['GET','POST'])
def decode_image_post():
    if request.method == 'POST':
        if 'decode_payload_image' not in request.files:
            flash('No audio file uploaded', 'error')
            return redirect(request.url)

        audio_file = request.files['decode_payload_image']
        bit_size = request.form.get('bit_size', 1)
        payload_size = request.form.get('payload_size', None)

        if audio_file.filename == '':
            flash('No audio file selected', 'error')
            return redirect(request.url)

        # Validate bit_size
        try:
            bit_size = int(bit_size)
            if not (1 <= bit_size <= 8):
                flash('Bit size must be between 1 and 8', 'error')
                return redirect(request.url)
        except ValueError:
            flash('Invalid bit size', 'error')
            return redirect(request.url)

        # Validate payload_size
        if payload_size is None or payload_size == '':
            flash('Payload size is required for decoding.', 'error')
            return redirect(request.url)
        try:
            payload_size = int(payload_size)
            if payload_size <= 0:
                flash('Payload size must be a positive integer.', 'error')
                return redirect(request.url)
        except ValueError:
            flash('Invalid payload size.', 'error')
            return redirect(request.url)

        # Validate audio file type
        if not allowed_file(audio_file.filename, {'wav'}):
            flash('Unsupported audio file type. Only WAV files are allowed.', 'error')
            return redirect(request.url)

        # Save the uploaded audio file
        audio_filename = secure_filename(audio_file.filename)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        audio_file.save(audio_path)

        try:
            # Call the decode_image_in_audio function
            output_image_path = decode_image_in_audio(
                audio_file=audio_path,
                bit_size=bit_size,
                payload_size=payload_size
            )

            # Send the decoded image file to the user
            return send_file(output_image_path, as_attachment=True,
                             download_name=os.path.basename(output_image_path))
        except Exception as e:
            flash(f'Decoding failed: {str(e)}', 'error')
            return redirect(request.url)
        finally:
            # Clean up uploaded files
            if os.path.exists(audio_path):
                os.remove(audio_path)
            # Remove the output image after sending

    else:
        return render_template('decode_image_in_audio.html')


@app.route('/decode_audio')
def decode_audio_page():
    return render_template('decode_audio.html')

@app.route('/decode_audio', methods=['GET','POST'])
def decode_audio_post():
    return render_template('decode_audio.html')

if __name__ == '__main__':
    app.run(debug=True)
