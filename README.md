# tmc-cloud-engineer-challenge

Simple serverless app

![Alt text](webapp/webapp.png?raw=true "frontend")


How to use it -

1. update settings.env with corresponding bucket name, upload location
2. run ./script.sh <path-to-pace-data.txt or url> <output-file-name>
    2.1 This will create a bucket on aws
    2.2 Upload the file to specified folder in settings.env
3. cd devops-test-serverless
4. configure serverless framework with correct IAM user and following permissions
    4.1 S3
    4.2 RDS
    4.3 APIGATEWAY
5. serverless deploy
6. run ./script.sh <path-to-pace-data.txt or url> <output-file-name> 
    - to trigger the lambda functions
7. open webapp/index.html


Demo - https://gautammd.github.io/tmc-cloud-engineer-challenge/webapp/index.html