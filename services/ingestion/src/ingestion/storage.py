import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from ingestion.config import settings


class Storage:
    def __init__(self):
        self.client = boto3.client(
            "s3", endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name="us-east-1", config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.s3_bucket

    def ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket)

    def upload_file(self, path, object_key, content_type):
        self.client.upload_file(str(path), self.bucket, object_key, ExtraArgs={"ContentType": content_type})

    def download_stream(self, object_key):
        return self.client.get_object(Bucket=self.bucket, Key=object_key)["Body"]
