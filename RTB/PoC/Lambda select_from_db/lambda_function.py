import json
import boto3

def lambda_handler(event, context):

    AWS_KEY = 'non possiamo mettere su repo pubblica'
    AWS_PSW = 'non possiamo mettere su repo pubblica'
    AWS_REGION = 'eu-central-1'

    rdsData = boto3.client('rds-data', region_name=AWS_REGION, aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_PSW)
    cluster_arn = 'non possiamo mettere su repo pubblica'
    secret_arn = 'non possiamo mettere su repo pubblica'

    results = rdsData.execute_statement(
            resourceArn = cluster_arn,
            secretArn = secret_arn,
            database = 'sweeat',
            sql = 'select * from db_poc',
            includeResultMetadata = True
            )

    columns = [column['name'] for column in results['columnMetadata']]

    parsed_records = []
    for record in results['records']:
        parsed_record = {}
        for i, cell in enumerate(record):
            key = columns[i]
            value = list(cell.values())[0]
            parsed_record[key] = value
        parsed_records.append(parsed_record)


    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(parsed_records)
    }
