#! /bin/bash

#load environment varialbes file
set -o allexport; source settings.env; set +o allexport

echo $BUCKET_NAME

#download the file from the url and save it to the file
curl -o $2 $1

#check if the file is downloaded
if [ -f $2 ]
then
    echo "File downloaded successfully"
    # create aws s3 bucket
    echo "Creating S3 bucket $BUCKET_NAME"
    S3_BUCKET=$(aws s3api create-bucket --bucket $BUCKET_NAME --region $BUCKET_LOCATION --output text)
    S3_BUCKET="/data-engineer-test-upwork"
    echo $S3_BUCKET

    #upload the file to the bucket
    echo "Uploading file to S3 bucket"
    aws s3 cp $2 "s3:/$S3_BUCKET/$UPLOAD_PATH"
    echo "File uploaded successfully"
else
    echo "File not downloaded"
fi