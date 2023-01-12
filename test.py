from translatepy import Translator
from pyowm import OWM

def get_translation(term: str):
    google_translator = Translator()
    translation_result = google_translator.translate(term,"Russian")  
    if translation_result:
        return translation_result    
    else:
        print("не получилось перевести")

def get_weather_forecast():
    city_name = "Novosibirsk,RU"

    open_weather_map = OWM("815d4b7da2fe4f888c984ec0d92c6405")
    weather_manager = open_weather_map.weather_manager()
    observation = weather_manager.weather_at_place(city_name)
    weather = observation.weather
    print(weather.detailed_status)
    translation = get_translation(weather.detailed_status)
    print(translation)
    

get_weather_forecast()
