from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from PIL import Image
import io

app = Flask(__name__, static_folder='static')

# Helper function to process a single image
def process_image(image):
    print(f"Processing image with size: {image.size}")  # Debug log
    # Resize to 1200px width while maintaining aspect ratio
    original_width, original_height = image.size
    new_width = 1200
    new_height = int((new_width / original_width) * original_height)
    
    print(f"Resizing to: {new_width}x{new_height}")  # Debug log
    # Resize the image
    resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Add 1-pixel black border
    bordered_img = Image.new('RGB', (new_width + 2, new_height + 2), (0, 0, 0))
    bordered_img.paste(resized_img, (1, 1))
    
    return bordered_img

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload endpoint called")  # Debug log
    print(f"Request files: {request.files}")  # Debug log
    
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        print("No files in request")  # Debug log
        return jsonify({'error': 'No files uploaded'}), 400
    
    file = files[0]  # We're only handling one file at a time
    if file.filename == '':
        print("Empty filename")  # Debug log
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        print(f"Processing file: {file.filename}")  # Debug log
        # Process the image
        img = Image.open(file)
        processed_img = process_image(img)
        
        # Save to a BytesIO object
        img_io = io.BytesIO()
        processed_img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        # Create a filename
        filename = f'processed_{secure_filename(file.filename)}'
        
        print(f"Sending processed image: {filename}")  # Debug log
        return send_file(
            img_io,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    print("Serving index.html")  # Debug log
    return app.send_static_file('index.html')

if __name__ == '__main__':
    print("Starting Flask app")  # Debug log
    app.run(debug=True)
