import json
import boto3
import cfnresponse

s3 = boto3.resource('s3')

def create(properties, physical_id):
  userPoolId = properties['UserPool']
  clientId = properties['Client']
  region = properties['Region']
  bucket = properties['Bucket']

  object = s3.Object(bucket, 'js/config.js')
  config_content = """

    var _config = {
        cognito: {
            userPoolId: '%s', // e.g. us-east-2_uXboG5pAb
            userPoolClientId: '%s', // e.g. 25ddkmj4v6hfsfvruhpfi7n4hv
            region: '%s', // e.g. us-east-2
        },
        api: {
            invokeUrl: 'Base URL of your API including the stage', // e.g. https://rc7nyt4tql.execute-api.us-west-2.amazonaws.com/prod'
        }
    };
    """
  config_content = config_content % (userPoolId, clientId, region)
  config = s3.Object(bucket,'js/config.js')
  config.put(Body=config_content)
  return cfnresponse.SUCCESS, None

def update(properties, physical_id):
  return create(properties, physical_id)

def delete(properties, physical_id):
  return cfnresponse.SUCCESS, physical_id

def handler(event, context):
  print "Received event: %s" % json.dumps(event)

  status = cfnresponse.FAILED
  new_physical_id = None

  try:
    properties = event.get('ResourceProperties')
    physical_id = event.get('PhysicalResourceId')

    status, new_physical_id = {
      'Create': create,
      'Update': update,
      'Delete': delete
    }.get(event['RequestType'], lambda x, y: (cfnresponse.FAILED, None))(properties, physical_id)
  except Exception as e:
    print "Exception: %s" % e
    status = cfnresponse.FAILED
  finally:
    cfnresponse.send(event, context, status, {}, new_physical_id)