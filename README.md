# School-Fees-Payment-System
A school fees payment system where admins can register new users and schools, and the registered users can use mobile payment options like mpesa to pay for their school fees. School fee payment is just a modeled proof of concept as this project can be used to implement mobile payment in other fields or applications.
Note that this project exists in two branches:
- main
- master

The main branch contains this README markdown file to explain the code, but the actual code is found in the master branch.
Note that if you clone this project directly to your system and run it in your local environment, it won't start as it requires some changes to start. 

## Input required
Some of the information required to get this project up and running on your local machine should be provided either through environment variables or actual editing *settings.py*

### Django-specific information
1. Your custom SECRET_KEY for Django. It doesn't matter what it is as long as it remains secret and with you.
2. Your list of ALLOWED_HOSTS for the project to run on. You can comment line 37 and uncomment line 38 of *settings.py* to enable the server to run anywhere.
3. If you have another database, you can provide its connection string through DATABASES in the environment variables. You can also comment line 97 and use the development database that was created with this project.

### MPESA-specific information
1. Your Daraja API MPESA_CONSUMER_KEY.
2. Your Daraja API MPESA_CONSUMER_SECRET.
3. Your Daraja API MPESA_PASSKEY.

If you don't have the above-mentioned information specific to MPESA, head on to https://developer.safaricom.co.ke/ and log in. Then you can choose one of your old apps and use its credentials or create a new app altogether. You will find this data in the Mpesa Express simulation. Also please note that this project should be able to work for you in mpesa sandbox, otherwise in production, you'd need some changes in the settings.
