import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

load_dotenv()

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )

def create_bucket_if_not_exists(s3_client, bucket_name, region):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"Bucket {bucket_name} does not exist. Creating it...")
            if region == 'us-east-1':
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
        else:
            print(f"Error checking bucket: {e}")

def upload_to_s3(file_path, filename):
    """
    Uploads a file to AWS S3 and returns the public URL.
    """
    bucket_name = os.getenv('S3_BUCKET_NAME', 'deepfake-detection-bucket')
    region = os.getenv('AWS_REGION', 'us-east-1')
    s3_client = get_s3_client()
    
    try:
        # Check if bucket exists, create if it doesn't
        create_bucket_if_not_exists(s3_client, bucket_name, region)

        # Upload the file
        s3_client.upload_file(
            file_path,
            bucket_name,
            filename,
            # ExtraArgs={'ACL': 'public-read'} # Requires ACL to be enabled on bucket, often disabled by default now.
        )
        # Generate a pre-signed URL valid for 1 hour (3600 seconds)
        # This allows viewing the image even if the S3 bucket is private
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': filename},
            ExpiresIn=3600
        )
        print(f"[SUCCESS] Uploaded to S3: {url}")
        return url
    except FileNotFoundError:
        print("[ERROR] File not found.")
        return None
    except NoCredentialsError:
        print("[ERROR] AWS credentials not available.")
        return None
    except Exception as e:
        print(f"[ERROR] S3 Upload failed: {e}")
        return None
