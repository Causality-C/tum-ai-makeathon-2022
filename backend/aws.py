"""Module for all AWS Stuff """
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
SECRET_KEY = os.environ["AWS_SECRET_KEY"]

# Resources/ Clients
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name="us-east-1",
)
dynamo_client = boto3.client(
    "dynamodb",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name="us-east-1",
)
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
    aws_secret_access_key=os.environ["AWS_SECRET_KEY"],
    region_name="us-east-1",
)
# Tables
user_table = dynamodb.Table("tumaiusers")
dataset_table = dynamodb.Table("tumaidatasets")
game_table = dynamodb.Table("tumaiduelgames")

# S3 Buckets
s3_dataset_bucket = "tumai-uploads"
s3_dataset_url = f"https://{s3_dataset_bucket}.s3.us-east-1.amazonaws.com/"


def scan_table(dyn_client, table_name):
    paginator = dyn_client.get_paginator("scan")

    for page in paginator.paginate(TableName=table_name):
        yield from page["Items"]
