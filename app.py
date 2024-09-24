from flask import Flask, render_template, redirect, url_for, request, send_file, flash
from werkzeug.utils import secure_filename
import os
from encoder.image_steno import encode_image, decode_image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Set a secret key for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'images'

# Ensure the upload and output folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audio')
def audio():
    return render_template('encode_audio.html')

@app.route('/image')
def image():
    return render_template('encode_image.html')

@app.route('/video')
def video():
    return render_template('encode_video.html')

@app.route('/encode_image', methods=['POST'])
def encode_image_route():
    if 'payload' not in request.files or 'cover' not in request.files:
        flash('Both payload and cover files are required')
        return redirect(url_for('image'))
    
    payload = request.files['payload']
    cover = request.files['cover']
    
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
            output_path = encode_image(cover_path, payload_path, output_filename)
            flash('Encoding successful')
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            flash(f'Encoding failed: {str(e)}')
            return redirect(url_for('image'))

@app.route('/decode')
def decode():
    return render_template('decode.html')

@app.route('/decode', methods=['POST'])
def decode_post():
    if 'image' not in request.files:
        flash('No file part')
        return redirect(url_for('decode'))
    
    image = request.files['image']
    
    if image.filename == '':
        flash('No selected file')
        return redirect(url_for('decode'))
    
    if image:
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        
        try:
            decoded_text = decode_image(filepath)
            return render_template('decode.html', decoded_text=decoded_text)
        except Exception as e:
            flash(f'Decoding failed: {str(e)}')
            return redirect(url_for('decode'))

if __name__ == '__main__':
    app.run(debug=True)