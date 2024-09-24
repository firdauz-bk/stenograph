from flask import Flask, render_template, redirect, url_for, request, send_file, flash
from werkzeug.utils import secure_filename
import os
from steno.image_steno import encode_image, decode_image
from steno.audio_steno import encode_audio, decode_audio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ILOVEINF2005!'  # Set a secret key for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'encoded_files'

# Ensure the upload and output folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

#################### INDEX PAGE ########################
@app.route('/')                                        # 
def index():                                           #
    return render_template('index.html')               #
########################################################

################################# AUDIO ENCODING PAGE #####################################################################################
                     # Render encode_audio.html #                                                                                         #
@app.route('/audio')                                                                                                                      #
def audio():                                                                                                                              #
    return render_template('encode_audio.html')                                                                                           #
                                                                                                                                          #
@app.route('/encode_audio', methods=['POST'])                                                                                             #
def encode_audio_route():                                                                                                                 #
    if 'payload' not in request.files or 'cover' not in request.files:                                                                    #
        flash('Both payload and cover files are required')                                                                                #
        return redirect(url_for('audio'))                                                                                                 #
                                                                                                                                          #
    payload = request.files['payload']                                                                                                    #
    cover = request.files['cover']                                                                                                        #
    bit_size = int(request.form.get('bit_size', 1))                                                                                       #
                                                                                                                                          #
    if payload.filename == '' or cover.filename == '':                                                                                    #
        flash('Both payload and cover files are required')                                                                                #
        return redirect(url_for('audio'))                                                                                                 #
                                                                                                                                          #
    if payload and cover:                                                                                                                 #
        payload_filename = secure_filename(payload.filename)                                                                              #
        cover_filename = secure_filename(cover.filename)                                                                                  #
                                                                                                                                          #
        payload_path = os.path.join(app.config['UPLOAD_FOLDER'], payload_filename)                                                        #
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)                                                            #
                                                                                                                                          #
        payload.save(payload_path)                                                                                                        #
        cover.save(cover_path)                                                                                                            #
        try:                                                                                                                              #
            output_path = encode_audio(payload_path, cover_path, bit_size=bit_size, output_dir=app.config['OUTPUT_FOLDER'])               #
            flash('Encoding successful')                                                                                                  #
            return send_file(output_path, as_attachment=True)                                                                             #
        except Exception as e:                                                                                                            #
            flash(f'Encoding failed: {str(e)}')                                                                                           #
            return redirect(url_for('audio'))                                                                                             #
###########################################################################################################################################

################################# VIDEO ENCODING PAGE #####################################################################################
@app.route('/video')
def video():
    return render_template('encode_video.html')

@app.route('/encode_video', methods=['POST'])
def encode_audio_video():
    if 'payload' not in request.files or 'cover' not in request.files:
        flash('Both payload and cover files are required')
        return redirect(url_for('video'))
    
    payload = request.files['payload']
    cover = request.files['cover']
    bit_size = int(request.form.get('bit_size', 1))
    
    if payload.filename == '' or cover.filename == '':
        flash('Both payload and cover files are required')
        return redirect(url_for('video'))
    
    if payload and cover:
        payload_filename = secure_filename(payload.filename)
        cover_filename = secure_filename(cover.filename)
        
        payload_path = os.path.join(app.config['UPLOAD_FOLDER'], payload_filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)
        
        payload.save(payload_path)
        cover.save(cover_path)
        try:
            output_path = encode_audio(payload_path, cover_path, bit_size=bit_size, output_dir=app.config['OUTPUT_FOLDER'])
            flash('Encoding successful')
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            flash(f'Encoding failed: {str(e)}')
            return redirect(url_for('video'))
###########################################################################################################################################

################################# IMAGE ENCODING PAGE #####################################################################################
@app.route('/image')
def image():
    return render_template('encode_image.html')

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
###########################################################################################################################################

################################# DECODING PAGE ###########################################################################################
@app.route('/decode')
def decode():
    return render_template('decode.html')

@app.route('/decode', methods=['GET','POST'])
def decode_post():
    if request.method == 'POST':
        if 'stego_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        stego_file = request.files['stego_file']
        
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
                    decoded_message = decode_image(file_path)

                elif file_extension in ['.mp3', '.wav']:
                    bit_size = int(request.form.get('bit_size', 1))
                    decoded_message = decode_audio(file_path, bit_size=bit_size)

                elif file_extension in ['.mp4', '.avi']:
                    # decoded_message = decode_video(file_path)
                    decoded_message = "insert video decoding function later here"
                else:
                    raise ValueError("Unsupported file type")
                
                return render_template('decode.html', decoded_message=decoded_message)
            except Exception as e:
                flash(f'Error decoding file: {str(e)}')
                return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
