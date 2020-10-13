from google.cloud import storage
from pathlib import Path
import datetime
import os
from src.credentials import *


def implicit():
    from google.cloud import storage

    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    storage_client = storage.Client(credentials=credentials)

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)


def create_bucket_class_location(bucket_name):
    """Create a new bucket in specific location with storage class"""
    # bucket_name = "your-new-bucket-name"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = "COLDLINE"
    new_bucket = storage_client.create_bucket(bucket, location="us")

    print(
        "Created bucket {} in {} with storage class {}".format(
            new_bucket.name, new_bucket.location, new_bucket.storage_class
        )
    )
    return new_bucket

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    #storage_client = storage.Client.from_service_account_json(str(path_json))
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name, timeout=1000)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )
    

def is_stored(blob_path, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    stats = storage.Blob(bucket=bucket, name=blob_path).exists(storage_client)
    return stats

def generate_image_url(blob_path, bucket_name):
    """ generate signed URL of a video stored on google storage. 
        Valid for 300 seconds in this case. You can increase this 
        time as per your requirement. 
    """         
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path) 
    return blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')

    
def retry_on_connectionerror(f, max_retries=5):
  retries = 0
  while retries < max_retries:
    try:
      return f()
    except ConnectionError:
      retries += 1
  raise Exception("Maximum retries exceeded")

# def upload_blob(bucket_name, source_file_name, destination_blob_name):
#     """Uploads a file to the bucket."""
#     # bucket_name = "your-bucket-name"
#     # source_file_name = "local/path/to/file"
#     # destination_blob_name = "storage-object-name"

#     #storage_client = storage.Client.from_service_account_json(str(path_json))
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)

#     media = MediaFileUpload(source_file_name, chunksize=4149304, mimetype='video/mp4',
#                         resumable=True)
    
#     req = servise.objects().insert(
#         bucket=bucket_name,
#         name=str(video),
#         media_body=media,
#         body={"cacheControl": "public,max-age=31536000"},
#         predefinedAcl='publicRead'
#     )
#     resp = None
#     while resp is None:
#         status, resp = req.next_chunk()
#     print(resp)




# def upload_blob(bucket_name, source_file_name, destination_blob_name):

#     client = storage.Client()
#     bucket = client.bucket(bucket_name)


#     # Write file if necessary.
#     blob = bucket.blob(destination_blob_name)
#     if not blob.exists():
#         print(f"Writing {destination_blob_name}")
#         start = datetime.datetime.now()
#         blob.upload_from_filename(source_file_name)
#         end = datetime.datetime.now()
#         print(f"Wrote {destination_blob_name} {end-start}")
