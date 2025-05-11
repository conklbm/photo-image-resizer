from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from PIL import Image
import tempfile
import io

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'tiff'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper functions from your existing code
def add_border(image, border_width=1, border_color=(0, 0, 0)):
    width, height = image.size
    new_width = width + border_width * 2
    new_height = height + border_width * 2
    
    bordered_image = Image.new('RGB', (new_width, new_height), border_color)
    bordered_image.paste(image, (border_width, border_width))
    return bordered_image

def resize_and_process_image(image):
    # Calculate new dimensions while maintaining aspect ratio
    original_width, original_height = image.size
    new_width = 1200
    new_height = int((new_width / original_width) * original_height)
    
    # Resize the image
    resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Add 1-pixel black border
    bordered_img = add_border(resized_img)
    
    return bordered_img

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Process the image
            img = Image.open(file)
            processed_img = resize_and_process_image(img)
            
            # Save to a BytesIO object
            img_io = io.BytesIO()
            processed_img.save(img_io, 'JPEG', quality=95)
            img_io.seek(0)
            
            return send_file(
                img_io,
                mimetype='image/jpeg',
                as_attachment=True,
                download_name=f'processed_{secure_filename(file.filename)}'
            )
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
