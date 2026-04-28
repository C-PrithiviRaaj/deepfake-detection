import os
import hashlib
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags

# Import custom modules
from model_utils import detect_image
from blockchain import deepfake_blockchain
from aws_s3 import upload_to_s3

app = Flask(__name__)
app.secret_key = "super_secret_deepfake_key"
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def fix_image_orientation(image_path):
    """ Fixes image orientation based on EXIF data """
    try:
        image = Image.open(image_path)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        
        exif = image._getexif()
        if exif is not None and orientation in exif:
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        image.save(image_path)
    except (AttributeError, KeyError, IndexError, Exception) as e:
        # Image doesn't have EXIF data or error occurred
        pass

def generate_file_hash(filepath):
    """ Generates SHA256 hash of a file """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    # 1. Check if file is uploaded
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # 2. Fix Orientation
        fix_image_orientation(filepath)
        
        # 3. Generate File Hash
        file_hash = generate_file_hash(filepath)
        
        # 4. Predict
        label, confidence = detect_image(filepath)
        
        # 5. Store in Blockchain
        block_data = {
            'filename': filename,
            'prediction': label,
            'confidence': confidence,
            'file_hash': file_hash
        }
        new_block = deepfake_blockchain.add_block(block_data)
        
        # 6. Upload to AWS S3
        s3_url = upload_to_s3(filepath, filename)
        
        return render_template('result.html', 
                               filename=filename,
                               label=label,
                               confidence=confidence,
                               file_hash=file_hash,
                               block_hash=new_block.hash,
                               s3_url=s3_url)
    else:
        flash('Allowed file types are png, jpg, jpeg')
        return redirect(url_for('index'))

@app.route('/predict', methods=['POST'])
def predict_api():
    if 'image' not in request.files:
        return "No image uploaded", 400
    
    file = request.files['image']
    if file.filename == '':
        return "No image selected", 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # 2. Predict using our model logic
        label, confidence = detect_image(filepath)
        
        # Return simple string as requested by the user snippet
        return label.lower()
    
    return "Invalid file type", 400

if __name__ == '__main__':
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Run on 0.0.0.0 to make it accessible on the local network
    app.run(host='0.0.0.0', port=5000, debug=True)
