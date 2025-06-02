from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from PIL import Image
import io

app = Flask(__name__, static_folder='static')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image):
    # Resize to 1200px width while maintaining aspect ratio
    original_width, original_height = image.size
    new_width = 1200
    new_height = int((new_width / original_width) * original_height)
    
    # Resize the image
    resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Add 1-pixel black border
    bordered_img = Image.new('RGB', (new_width + 2, new_height + 2), (0, 0, 0))
    bordered_img.paste(resized_img, (1, 1))
    
    return bordered_img

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['files']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Process the image
        img = Image.open(file)
        processed_img = process_image(img)
        
        # Save to BytesIO
        img_io = io.BytesIO()
        processed_img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        # Create response
        return send_file(
            img_io,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f'processed_{secure_filename(file.filename)}'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
