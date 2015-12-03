# slack_roller
Dice rolling bot for Slack, using Amazon API Gateway and Lambda microservices

# setup
## lambda function
1. Create a new Lambda function in AWS
2. Skip the blueprint, but make sure the language is set to Python 2.7
3. Zip slack_roller.py and upload it
4. The handler is "slack_roller.roll"
5. Set role as "Basic Execution Role" and allow it when it pops up
6. Click through the "create function" stuff
## API
1. Create a new API in Amazon API Gateway
2. Create a new method
3. In the dropdown that appears, select "POST"
4. Click the checkbox beside POST
5. Select Lambda Function and select your slack_roller lambda
6. Click "Integration Request"
7. Add a mapping template for "application/x-www-form-urlencoded"
8. Make the template the following:
 {
  "formparams" : $input.params()
 }
9. Save that
10. Click "Deploy API"; this should provide you with a url.
## Slack
1. Add a slash command to your integrations
2. Fill in the information it asks for the command you want
3. Provide it with the url your API is at
4. Save it and test your command!
