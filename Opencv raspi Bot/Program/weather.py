import requests
from pushbullet import Pushbullet

i="o.uKPiJUdGXMG5TtpJXtoFc9LOu2yXiljb"

def get_weather(api_key, lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    else:
        print(f'Error: {response.status_code}')
        return None

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def send_notification(api_key, title, message):
    pb = Pushbullet(api_key)
    pb.push_note(title, message)

def main():
    api_key = '42db11405c74755e9a2f8b6fd62d6b2f'
    latitude = 8.1369529
    longitude = 77.5622909

    weather_data = get_weather(api_key, latitude, longitude)
    if weather_data:
        temperature_kelvin = weather_data['main']['temp']
        temperature_celsius = kelvin_to_celsius(temperature_kelvin)

        message = f'Weather in your specified area:\nTemperature: {temperature_celsius} °C\nHumidity: {weather_data["main"]["humidity"]}%'
        print(message)
        send_notification(i, 'Weather Update', message)
    else:
        error_message = 'Failed to retrieve weather data.'
        print(error_message)
        send_notification(i, 'Weather Update Error', error_message)

if __name__ == "__main__":
    main()