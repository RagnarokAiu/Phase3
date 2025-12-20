import os
import tempfile
from typing import Optional, BinaryIO
from botocore.exceptions import ClientError, NoCredentialsError

import boto3
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class S3Client:
    """S3 client for handling file operations."""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize S3 client with credentials."""
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                aws_session_token=settings.AWS_SESSION_TOKEN,
                region_name=settings.AWS_DEFAULT_REGION
            )
            logger.info("S3 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    async def upload_file(
        self,
        file_content: BinaryIO,
        bucket_name: str,
        object_key: str,
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file to S3."""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_fileobj(
                file_content,
                bucket_name,
                object_key,
                ExtraArgs=extra_args
            )
            
            s3_url = f"s3://{bucket_name}/{object_key}"
            logger.info(f"File uploaded to S3: {s3_url}")
            return s3_url
            
        except NoCredentialsError:
            logger.error("AWS credentials not available")
            raise PermissionError("AWS credentials not configured")
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise
    
    async def upload_text(
        self,
        text: str,
        bucket_name: str,
        object_key: str,
        content_type: str = "text/plain"
    ) -> str:
        """Upload text content to S3."""
        try:
            self.client.put_object(
                Body=text.encode('utf-8'),
                Bucket=bucket_name,
                Key=object_key,
                ContentType=content_type
            )
            
            s3_url = f"s3://{bucket_name}/{object_key}"
            logger.info(f"Text uploaded to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to upload text to S3: {e}")
            raise
    
    def generate_presigned_url(
        self,
        bucket_name: str,
        object_key: str,
        expiration: int = 3600
    ) -> str:
        """Generate a presigned URL for S3 object access."""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            logger.info(f"Generated presigned URL for {bucket_name}/{object_key}")
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
    
    def download_file(
        self,
        bucket_name: str,
        object_key: str,
        local_path: Optional[str] = None
    ) -> str:
        """Download a file from S3 to local storage."""
        try:
            if not local_path:
                local_path = os.path.join(
                    tempfile.gettempdir(),
                    os.path.basename(object_key)
                )
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            self.client.download_file(bucket_name, object_key, local_path)
            logger.info(f"File downloaded from S3 to {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download file from S3: {e}")
            raise
    
    def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None
    ) -> list:
        """List objects in an S3 bucket."""
        try:
            params = {'Bucket': bucket_name}
            if prefix:
                params['Prefix'] = prefix
            
            response = self.client.list_objects_v2(**params)
            return response.get('Contents', [])
            
        except Exception as e:
            logger.error(f"Failed to list objects in S3 bucket: {e}")
            return []
    
    def delete_object(self, bucket_name: str, object_key: str) -> bool:
        """Delete an object from S3."""
        try:
            self.client.delete_object(Bucket=bucket_name, Key=object_key)
            logger.info(f"Deleted object from S3: {bucket_name}/{object_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete object from S3: {e}")
            return False


# Global S3 client instance
s3_client = S3Client()