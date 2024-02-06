# School-Fees-Payment-System
A school fees payment system where admins can register new users and schools, and the registered users can use mobile payment options like mpesa to pay for their school fees. School fees payment is just a modeled proof of concept as this project can be used to implement mobile payment in other fields or applications.

## Input required
Some of the information required to get this project up and running on your local machine should be provided either through environment variables or actual editing *settings.py*

### Django-specific information
1. Your custom SECRET_KEY for Django. It doesn't matter what it is as long as it remains secret and with you.
2. Your list of ALLOWED_HOSTS for the project to run on. You can comment line 37 and uncomment line 38 of *settings.py* to enable the server to run anywhere.

### MPESA-specific information
1. Your Daraja API MPESA_CONSUMER_KEY.
2. Your Daraja API MPESA_CONSUMER_SECRET.
3. Your Daraja API MPESA_PASSKEY.

If you don't have the above-mentioned information specific to MPESA, head on to https://developer.safaricom.co.ke/ and log in. Then you can choose one of your old apps and use it's credentials or create a new app all together. You will find this data in the mpesa express simulation. Also please not that this project should be able to work for you in mpesa sandbox, otherwise in production, you'd need some changes in the settings.
