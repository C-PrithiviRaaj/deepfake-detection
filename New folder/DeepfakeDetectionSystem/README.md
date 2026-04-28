# Deepfake Image Detection System with Blockchain and Cloud Integration

This is a complete end-to-end Deepfake Detection System. It uses a Convolutional Neural Network (Transfer Learning via MobileNetV2) to classify images as **REAL** or **FAKE**. 

Every prediction is logged into a custom **Blockchain** to ensure data immutability and provenance (logging the file hash, prediction, and confidence). Finally, the analyzed image is uploaded to **AWS S3** for secure cloud storage.

## Features
- **Deep Learning Model:** Built with TensorFlow/Keras using MobileNetV2.
- **Web Interface:** Modern, responsive Flask UI with drag-and-drop file upload.
- **Blockchain Verification:** Generates blocks containing image metadata and SHA-256 hashes.
- **Cloud Storage:** Automatically uploads processed images to AWS S3 using `boto3`.

## Project Structure
```text
DeepfakeDetectionSystem/
│
├── app.py                  # Main Flask application
├── aws_s3.py               # AWS S3 upload functions
├── blockchain.py           # Blockchain classes and logic
├── dataset_manager.py      # Helper to generate dummy dataset
├── model_utils.py          # Model loading and prediction logic
├── train_model.ipynb       # Jupyter notebook for training the model
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (AWS keys)
│
├── model/                  # Directory to store trained .h5 models
├── dataset/                # Directory for training data (real/fake)
├── static/
│   ├── style.css           # Frontend styling
│   └── uploads/            # Temporary storage for uploaded images
└── templates/
    ├── index.html          # Upload page
    └── result.html         # Results page
```

## Setup Instructions

### 1. Install Dependencies
Make sure you have Python 3.8+ installed. Run:
```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials
Edit the `.env` file and insert your AWS credentials:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

### 3. Prepare the Dataset
Real datasets like **FaceForensics++** or **Celeb-DF** require manual request forms. 
If you have them, extract them into `dataset/real` and `dataset/fake`.

**For quick testing**, generate a dummy dataset:
```bash
python dataset_manager.py
```

### 4. Train the Model
You can train the model by running the Jupyter Notebook:
```bash
jupyter notebook train_model.ipynb
```
*(Run all cells to train the model and save it to `model/deepfake_model.h5`)*

*Note: If no model is found during runtime, the app will gracefully fallback to a dummy prediction mode for testing the pipeline.*

### 5. Run the Application
Start the Flask server:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

## Deployment

### Local Access via ngrok
To share your local server with others securely:
1. Install [ngrok](https://ngrok.com/).
2. Run: `ngrok http 5000`
3. Share the generated HTTPS forwarding URL.

### AWS EC2 Deployment
1. Launch an Ubuntu EC2 instance.
2. Clone this repository onto the instance.
3. Install dependencies: `sudo apt update && sudo apt install python3-pip && pip3 install -r requirements.txt`
4. Run the app using `gunicorn`:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:80 app:app
```
5. Ensure your EC2 Security Group allows inbound traffic on port 80.
