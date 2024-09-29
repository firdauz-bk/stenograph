from flask import Flask, render_template, redirect, url_for, request, send_file, flash, jsonify, session
from werkzeug.utils import secure_filename
import os
from io import BytesIO
import zipfile
from steno.image_steno import encode_image, decode_image
from steno.audio_steno import encode_audio, decode_audio, encode_image_in_audio, decode_image_in_audio
from steno.video_steno import extract_frames, encode_video, decode_video

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ILOVEINF2005!'  # Set a secret key for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'encoded_files'

# Ensure the upload and output folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

#################### INDEX PAGE ########################
@app.route('/')                                        
def index():                                           
    return render_template('index.html')              

################################# AUDIO ENCODING PAGE #####################################################################################
@app.route('/audio')
def audio():
    return render_template('encode_audio.html')

@app.route('/encode_audio', methods=['POST'])
def encode_audio_route():
    if 'payload_audio' not in request.files or 'cover_audio' not in request.files:
        flash('Both payload and cover files are required')
        return redirect(url_for('audio'))
    
    payload = request.files['payload_audio']
    cover = request.files['cover_audio']
    bit_size = int(request.form.get('bit_size', 1))

    if payload.filename == '' or cover.filename == '':
        flash('Both payload and cover files are required')
        return redirect(url_for('audio'))
    
    if payload and cover:
        payload_filename = secure_filename(payload.filename)
        cover_filename = secure_filename(cover.filename)

        payload_path = os.path.join(app.config['UPLOAD_FOLDER'], payload_filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)

        payload.save(payload_path)
        cover.save(cover_path)

        try:
            file_extension = os.path.splitext(payload_path)[1].lower()
            if file_extension == '.txt':
                output_path = encode_audio(payload_path, cover_path, bit_size=bit_size, output_dir=app.config['OUTPUT_FOLDER'])
                flash('Encoding successful')
                return send_file(output_path, as_attachment=True)
            
            elif file_extension == '.png':
                output_path, json_path = encode_image_in_audio(payload_path, cover_path, bit_size=bit_size, output_dir=app.config['OUTPUT_FOLDER'])
                flash('Encoding successful')
                
                # Create a ZIP file containing both the encoded audio and the JSON file
                memory_file = BytesIO()
                with zipfile.ZipFile(memory_file, 'w') as zf:
                    zf.write(output_path, os.path.basename(output_path))
                    zf.write(json_path, os.path.basename(json_path))
                memory_file.seek(0)
                
                return send_file(
                    memory_file,
                    mimetype='application/zip',
                    as_attachment=True,
                    attachment_filename='encoded_files.zip'
                )
            
            else:
                flash('Unsupported payload file type')
                return redirect(url_for('audio'))

        except Exception as e:
            flash(f'Encoding failed: {str(e)}')
            return redirect(url_for('audio'))

    flash('Invalid file')
    return redirect(url_for('audio'))


################################# VIDEO ENCODING PAGE #####################################################################################
@app.route('/video')
def video():
    return render_template('encode_video.html')


@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'cover_video' not in request.files:
        return jsonify({'error': 'No video file uploaded'}), 400
    
    video = request.files['cover_video']
    
    if video.filename == '':
        return jsonify({'error': 'No video file selected'}), 400
    
    if video(video.filename, {'mp4', 'avi'}):
        filename = secure_filename(video.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(video_path)
        
        # Extract frames
        temp_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'temp_frames')
        frame_count = extract_frames(video_path, temp_dir)
        
        session['video_path'] = video_path
        session['frame_count'] = frame_count
        
        return jsonify({'success': True, 'frame_count': frame_count})
    
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/encode_video', methods=['POST'])
def encode_video_route():
    if 'video_path' not in session or 'frame_count' not in session:
        flash('Please upload a video first')
        return redirect(url_for('video'))
    
    payload = request.files['payload']
    frame_number = int(request.form.get('frame_number'))
    lsb_bits = int(request.form.get('bit_size'))
    
    if payload.filename == '':
        flash('Payload file is required')
        return redirect(url_for('video'))
    
    if payload:
        payload_filename = secure_filename(payload.filename)
        payload_path = os.path.join(app.config['UPLOAD_FOLDER'], payload_filename)
        payload.save(payload_path)

        try:
            output_path = encode_video(session['video_path'], payload_path, frame_number, lsb_bits, app.config['OUTPUT_FOLDER'])
            flash('Encoding successful')
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            flash(f'Encoding failed: {str(e)}')
            return redirect(url_for('video'))

    flash('Invalid file')
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
            flash('No file part')
            return redirect(request.url)
        
        stego_file = request.files['decode_payload_text']
        
        if stego_file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if stego_file:
            filename = secure_filename(stego_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            stego_file.save(file_path)
                    
            try:
            #### DETERMINE THE FILETYPE TO USE THEIR RESPECTIVE FUNCTION ####
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in ['.png', '.gif', '.bmp', '.jpg']:
                    decoded_message = decode_image(file_path, lsb_count=1)

                elif file_extension in ['.mp3', '.wav']:
                    bit_size = int(request.form.get('bit_size', 1))
                    decoded_message = decode_audio(file_path, bit_size=bit_size)

                elif file_extension in ['.mp4', '.avi']:
                    # decoded_message = decode_video(file_path)
                    decoded_message = "insert video decoding function later here"
                else:
                    raise ValueError("Unsupported file type")
                
                return render_template('decode_text.html', decoded_message=decoded_message)
            except Exception as e:
                flash(f'Error decoding file: {str(e)}')
                return redirect(request.url)

@app.route('/decode_image')
def decode_image_page():
    return render_template('decode_image.html')

@app.route('/decode_image', methods=['GET','POST'])
def decode_image_post():
    return render_template('decode_image.html')

@app.route('/decode_audio')
def decode_audio_page():
    return render_template('decode_audio.html')

@app.route('/decode_audio', methods=['GET','POST'])
def decode_audio_post():
    return render_template('decode_audio.html')

if __name__ == '__main__':
    app.run(debug=True)
