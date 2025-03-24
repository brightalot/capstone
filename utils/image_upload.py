import boto3
from botocore.exceptions import NoCredentialsError
import os
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_S3_REGION_NAME')
BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
CLOUDFRONT_DOMAIN = os.getenv('AWS_CLOUDFRONT_DOMAIN')  # CloudFront 도메인

# S3 클라이언트 초기화
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)
def upload_to_s3(file_path, object_name):
    """
    로컬 파일을 S3에 업로드하고 URL 반환
    """
    bucket_name = BUCKET_NAME
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        MEDIA_URL = f'https://{CLOUDFRONT_DOMAIN}/{object_name}'
        return MEDIA_URL
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except NoCredentialsError:
        print("Credentials not available.")
        return None
