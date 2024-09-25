from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/encode', methods=['POST'])
def encode():
    png_file = request.files['image']
    audio_file = request.files['audio']
    bit_size = int(request.form.get('bit_size', 1))

    output_path, json_path = encode_image(png_file.filename, audio_file.filename, bit_size)
    return jsonify({"status": "success", "output_path": output_path, "json_path": json_path})

@app.route('/decode', methods=['POST'])
def decode():
    audio_file = request.files['audio']
    json_file = request.files['json']

    decoded_image = decode_image(audio_file.filename, json_file=json_file.filename)
    return jsonify({"status": "success", "decoded_image": decoded_image})
