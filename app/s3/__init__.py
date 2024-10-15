# import boto3
# from app.config import Config
# import requests
# import hashlib
# from werkzeug.utils import secure_filename
# from app.logger import logger
# S3_BUCKET_NAME = "bucket"  # Config.IMAGE_BUCKET_NAME
# S3_CLIENT = boto3.client("s3")
# def upload_ai_generated_images_to_s3(response):
#     image_urls = []
#     image_ids = []
#     for image in response["data"]:
#         image_url = image["url"]
#         image_response = requests.get(image_url)
#         image_data = image_response.content
#         image_id = hashlib.md5(image_data).hexdigest()  # Generate image hash
#         image_ids.append(image_id)
#         s3_key = f"generated_images/{image_id}"
#         S3_CLIENT.put_object(Body=image_data, Bucket=S3_BUCKET_NAME, Key=s3_key)
#         image_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
#         image_urls.append(image_url)
#     return image_ids, image_urls
# def upload_image_to_s3(image, type="uploaded"):
#     filename = secure_filename(image.filename)
#     img_extension = filename.rsplit(".", 1)[1].lower()
#     content_type = image.content_type
#     image_data = image.file
#     image_id = hashlib.md5(
#         str(image_data).encode("utf-8")
#     ).hexdigest()  # Generate image hash
#     s3_key = f"{type}/{image_id}.{img_extension}"
#     image_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
#     try:
#         S3_CLIENT.put_object(
#             Body=image_data, Bucket=S3_BUCKET_NAME, Key=s3_key, ContentType=content_type
#         )
#     except Exception as e:
#         logger.info(str(e))
#     return image_id, image_url
# def upload_temp_image_to_s3(image, type="tmp"):
#     filename = secure_filename(image.filename)
#     img_extension = filename.rsplit(".", 1)[1].lower()
#     content_type = image.content_type
#     image_data = image.file
#     image_hash = hashlib.md5(
#         str(image_data).encode("utf-8")
#     ).hexdigest()  # Generate image hash
#     s3_key = f"{type}/{image_hash}.{img_extension}"
#     image_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
#     S3_CLIENT.put_object(
#         Body=image_data, Bucket=S3_BUCKET_NAME, Key=s3_key, ContentType=content_type
#     )
#     return image_url, s3_key
# def delete_item_s3(s3_key, S3BUCKEt=S3_BUCKET_NAME):
#     S3_CLIENT.delete_object(Bucket=S3BUCKEt, Key=s3_key)
from __future__ import annotations
