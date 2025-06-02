from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
from PIL import Image
import tempfile
import io

app = Flask(__name__, static_folder='static')

# Configure upload settings
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'tiff'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

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
def upload_files():
    print("Upload endpoint called")  # Debug log
    print(f"Request files: {request.files}")  # Debug log
    
    if 'files' not in request.files:
        print("No files part in request")  # Debug log
        return jsonify({'error': 'No files part'}), 400
    
    files = request.files.getlist('files')
    print(f"Number of files: {len(files)}")  # Debug log
    if not files or all(file.filename == '' for file in files):
        print("No valid files found")  # Debug log
        return jsonify({'error': 'No selected files'}), 400
    
    results = []
    for file in files:
        print(f"Processing file: {file.filename}")  # Debug log
        if file and allowed_file(file.filename):
            try:
                # Process the image
                img = Image.open(file)
                processed_img = resize_and_process_image(img)
                
                # Save to a BytesIO object
                img_io = io.BytesIO()
                processed_img.save(img_io, 'JPEG', quality=95)
                img_io.seek(0)
                
                # Convert to base64
                import base64
                img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
                
                results.append({
                    'filename': f'processed_{secure_filename(file.filename)}',
                    'status': 'success',
                    'image_data': f'data:image/jpeg;base64,{img_data}'
                })
                
            except Exception as e:
                print(f"Error processing {file.filename}: {str(e)}")  # Debug log
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': str(e)
                })
        else:
            print(f"Invalid file: {file.filename}")  # Debug log
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': 'Invalid file type'
            })
    
    print(f"Returning results: {results}")  # Debug log
    return jsonify(results)

@app.route('/temp/<filename>')
def get_processed_image(filename):
    try:
        temp_file = os.path.join(tempfile.gettempdir(), filename)
        return send_file(temp_file, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
