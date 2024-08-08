
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.serializers import *
import smtplib
from django.contrib.auth.models import User
from email.message import EmailMessage
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_object_or_404
import json

@api_view(['GET'])
def getWeatherInfo(request):
    q = request.GET.get('q', '')
    days = request.GET.get('days', 5)
    data = requests.get(f'http://api.weatherapi.com/v1/forecast.json?key=c51aaf3dcc494cc8865115316242607&q={q}&days={days}').json()
    return Response(data)
   
@api_view(['GET'])
def getLocationByIP(request):
    cityname = requests.get('https://api.db-ip.com/v2/free/self').json()
    print(cityname)
    return Response(getLocationByCityName(cityname['city']))

@api_view(['POST'])
def register(request):
    try:
        mail_instance = Mail.objects.get(gmail=request.data.get('gmail', ''))  # Use the model class

        mail_instance.name = request.data.get('location', '')
        mail_instance.status = 1
        mail_instance.save()

        sendmail('[Login] Welcome to G-Weather-Forecast', 
                 '''Thank you for your interest and following. Your location has been updated again.''', 
                 mail_instance.gmail)
        serializer = MailSerializer(mail_instance)
        return Response({
            "gmail": request.data.get('gmail', ''),
            "location": request.data.get('location', ''),
            "status": 1,
            "active": 1,
        }, status=status.HTTP_201_CREATED)
    
    except Mail.DoesNotExist: 



        user, created = User.objects.get_or_create(username=request.data.get('gmail', ''))
        print(user)

        if created:
            token = Token.objects.create(user=user)
        else:
            token = Token.objects.get(user=user)
        
        
        sendmail('[Subscribe] Welcome to G-Weather-Forecast', 
                     f'''Please click on the link to confirm your registration, http://localhost:3000/?token={token.key}''', 
                     request.data.get('gmail', ''))

        return Response({
            "gmail": request.data.get('gmail', ''),
            "location": request.data.get('location', ''),
            "status": 0,
            "active": 0,
        }, status=status.HTTP_201_CREATED)
       
        # data = {
        #     "gmail": request.data.get('gmail', ''),
        #     "location": request.data.get('location', ''),
        #     "status": 1
        # }
        
        # serializer = MailSerializer(data=data)
        # if serializer.is_valid():
        #     serializer.save()

        #     sendmail('[Subscribe] Welcome to G-Weather-Forecast', 
        #              '''Thank you for your interest and following, hope to provide useful weather information for you.
        #              Weather information will be announced every day.''', 
        #              data['gmail'])

        #     sendWheatherInfo(data['location'], data['gmail'])
        
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        
@api_view(['POST'])
def emailConfirmation (request):

    gmail = request.data.get('gmail', '')
    token = request.data.get('token', '')
    q = request.data.get('location', '')

    user, created = User.objects.get_or_create(username=gmail)
        
    if created:
        tokenUser = Token.objects.create(user=user)
    else:
        tokenUser = Token.objects.get(user=user)
    
    data = {
            "gmail": gmail,
            "location": q,
            "status": 1,
            "active": 1,
        }
    print(tokenUser.key, token)
    
    if tokenUser.key == token:
       
        
        serializer = MailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            sendmail('[Subscribe] Welcome to G-Weather-Forecast', 
                     '''Thank you for your interest and following, hope to provide useful weather information for you.
                     Weather information will be announced every day.''', 
                     data['gmail'])

            sendWheatherInfo(data['location'], data['gmail'])
        
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)



@api_view(['POST'])
def logout(request):
    mail_instance = Mail.objects.get(gmail=request.data.get('gmail', ''))  # Use the model class

    mail_instance.status = 0
    mail_instance.save()

    user = get_object_or_404(User, username = request.data.get('gmail', ''))
    Token.objects.filter(user=user).delete()

    sendmail('[Unsubscribe] G-Weather-Forecast thank you.', 
                 '''Thank you for your interest and following. See you again one day soon.''', 
                 mail_instance.gmail)
    serializer = MailSerializer(mail_instance)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
    

def sendWheatherInfo(q, mail):
    response_data = requests.get(f'http://api.weatherapi.com/v1/forecast.json?key=c51aaf3dcc494cc8865115316242607&q={q}&days=5').json()
    
    data = {
    'name': response_data['location']['name'],
    'date': response_data['forecast']['forecastday'][0]['date'],
    'forecastday': [
        {'day': day['day'], 'date': day['date']}
        for day in response_data['forecast']['forecastday']
    ]}

    content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Widget</title>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <div class="weather-widget card">
            <div class="card-body">
                <h3 class="card-title">{data["name"]} ({data["date"]})</h3>
                <p class="card-text">Temperature: {data["forecastday"][0]["day"]["avgtemp_c"]}°C</p>
                <p class="card-text">Wind: {data["forecastday"][0]["day"]["avgvis_miles"]}M/S</p>
                <p class="card-text">Humidity: {data["forecastday"][0]["day"]["avghumidity"]}%</p>
                <div class="weather-status">
                    <img src={f"https:{data['forecastday'][0]['day']['condition']['icon']}"}>
                    <p class="status-text">{data['forecastday'][0]['day']['condition']['text']}</p>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script>
</body>
</html>

'''
    
    # sendmail(f'[{data["name"]}] {data["date"]}',
    #          f'''Temperature: {data["forecastday"][0]["day"]["avgtemp_c"]}
    #             Wind: {data["forecastday"][0]["day"]["avgvis_miles"]} M/S
    #             Humidity: {data["forecastday"][0]["day"]["avghumidity"]}%
    #         ''',mail)

    sendmail(f'[{data["name"]}] {data["date"]}',content,mail, 1)


def getLocationByCityName(name):
    print(name)
    try:
        url = f'https://api.api-ninjas.com/v1/geocoding?city={name}'
        headers = {
            'X-Api-Key': 'sycEOmug3GpUajiEHTFeUw==pSeXtHtQGiOYhBHS',
        }

        response = requests.get(url, headers=headers)
        # response.raise_for_status() 

        print(response.json())

        data = response.json()
        if data:
            coordinates = {
                'lat': data[0]['latitude'],
                'lng': data[0]['longitude']
            }
            return f'{coordinates["lat"]},{coordinates["lng"]}'
        else:
            print("No data found for the city.")
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

def sendmail(subject, content, mail, type = 0):

    EMAIL_ADDRESS = 'taitran3006@gmail.com'
    EMAIL_PASSWORD = 'rpspaukfdyftvnyc'
 
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'taitran3006@gmail.com'
    msg['To'] = mail
    if type == 1:
        msg.set_content(content, subtype='html')
    else:
        msg.set_content(content)
 
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


    
