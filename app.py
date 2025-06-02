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
    try:
        print("\n=== New Upload Request ===")
        print(f"Request form data: {request.form}")
        print(f"Request files: {request.files}")
        
        if 'files' not in request.files:
            print("Error: No files part in request")
            return jsonify({'error': 'No files part'}), 400
        
        files = request.files.getlist('files')
        print(f"Number of files received: {len(files)}")
        
        if not files or all(file.filename == '' for file in files):
            print("Error: No selected files")
            return jsonify({'error': 'No selected files'}), 400
        
        results = []
        for file in files:
            filename = secure_filename(file.filename)
            print(f"\nProcessing file: {filename}")
            
            if not file or not allowed_file(filename):
                print(f"Error: Invalid file type for {filename}")
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': 'Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)
                })
                continue
                
            try:
                # Process the image
                print(f"Opening image: {filename}")
                img = Image.open(file)
                print(f"Original size: {img.size}")
                
                processed_img = resize_and_process_image(img)
                print(f"Processed size: {processed_img.size}")
                
                # Save to a BytesIO object
                img_io = io.BytesIO()
                processed_img.save(img_io, 'JPEG', quality=95, optimize=True)
                img_io.seek(0)
                
                # Convert to base64
                import base64
                img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
                
                results.append({
                    'filename': f'processed_{filename}',
                    'status': 'success',
                    'image_data': f'data:image/jpeg;base64,{img_data}'
                })
                print(f"Successfully processed: {filename}")
                
            except Exception as e:
                import traceback
                error_msg = f"Error processing {filename}: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': f'Error processing image: {str(e)}'
                })
        
        print(f"\nReturning {len([r for r in results if r['status'] == 'success'])} successful results")
        return jsonify(results)
        
    except Exception as e:
        import traceback
        error_msg = f"Unexpected error in upload_files: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

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
