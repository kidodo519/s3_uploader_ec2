import os
import boto3
import yaml
from glob import glob
import shutil
import traceback


def upload_to_s3(path, bucket, facility, object_name=None):

    if object_name is None:
        object_name = path

    s3_client = boto3.client(
        's3',
        aws_access_key_id=config['s3_info'][facility]['access_key_id'],
        aws_secret_access_key=config['s3_info'][facility]['secret_access_key']
    )

    try:
        s3_client.upload_file(path, bucket, object_name)
        print(f"Successfully uploaded {path} to {bucket}/{object_name}")
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return False
    return True


def handle_uploaded_csv(path, output_dir, delete_after_upload):
    if delete_after_upload:
        os.remove(path)
        print(f"Deleted {path}")
    else:
        os.makedirs(output_dir, exist_ok=True)
        shutil.move(path, output_dir)
        print(f"Archived {path} to {output_dir}")


def main(path, bucket, facility, file_name, output_dir, delete_after_upload):
    if upload_to_s3(path, bucket, facility, file_name):
        print("Upload succeeded.")
        handle_uploaded_csv(path, output_dir, delete_after_upload)

    else:
        print("Upload failed.")
        msg = traceback.format_exc()
        print(msg)


if __name__ == "__main__":
    base_path = os.path.dirname(__file__)
    config_path = os.path.join(base_path, 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as fp:
        config = yaml.safe_load(fp)
    facility_list = [
        os.path.basename(os.path.dirname(f))
        for f in glob(os.path.join(base_path, 'facility', '*/'))
        if os.path.isdir(f)
    ]

    for i in facility_list:
        input_dir = os.path.join(base_path, 'facility', i, config['csv']['input_directory'])
        output_dir = os.path.join(base_path, 'facility', i, config['csv']['output_directory'])
        csv_path_list = glob(os.path.join(input_dir, '*.csv'))
        delete_after_upload = config['s3_info'][i].get('delete_after_upload', False)

        for path in csv_path_list:
            file_name = config['s3_info'][i]['file_name'] + os.path.basename(path)
            main(path, config['s3_info'][i]['bucket_name'], i, file_name, output_dir, delete_after_upload)
