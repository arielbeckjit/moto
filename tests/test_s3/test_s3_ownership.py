import boto3
from botocore.client import ClientError

import pytest
import sure  # noqa # pylint: disable=unused-import
from moto import mock_s3


@mock_s3
def test_create_bucket_with_ownership():
    bucket = "bucket-with-owner"
    ownership = "BucketOwnerPreferred"
    client = boto3.client("s3")
    client.create_bucket(Bucket=bucket, ObjectOwnership=ownership)

    response = client.get_bucket_ownership_controls(Bucket=bucket)
    response["OwnershipControls"]["Rules"][0]["ObjectOwnership"].should.equal(ownership)


@mock_s3
def test_put_ownership_to_bucket():
    bucket = "bucket-updated-with-owner"
    ownership = "ObjectWriter"
    client = boto3.client("s3")
    client.create_bucket(Bucket=bucket)

    client.put_bucket_ownership_controls(
        Bucket=bucket, OwnershipControls={"Rules": [{"ObjectOwnership": ownership}]}
    )

    response = client.get_bucket_ownership_controls(Bucket=bucket)
    response["OwnershipControls"]["Rules"][0]["ObjectOwnership"].should.equal(ownership)


@mock_s3
def test_delete_ownership_from_bucket():
    bucket = "bucket-with-owner-removed"
    ownership = "BucketOwnerEnforced"
    client = boto3.client("s3")
    client.create_bucket(Bucket=bucket, ObjectOwnership=ownership)

    client.delete_bucket_ownership_controls(Bucket=bucket)

    with pytest.raises(ClientError) as ex:
        client.get_bucket_ownership_controls(Bucket=bucket)

    ex.value.response["Error"]["Code"].should.equal("OwnershipControlsNotFoundError")
    ex.value.response["Error"]["Message"].should.equal(
        "The bucket ownership controls were not found"
    )
