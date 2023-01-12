import speech_recognition as sr
import pyaudio as pa
import wave
import os
import json
from vosk import Model, KaldiRecognizer
from pyttsx3 import engine, Engine, init
from enum import Enum
from commands import commands as c
import random
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
import wikipedia
import webbrowser
from pyowm import OWM

class VoiceAssistant:
    name: str = "негр"
    sex: str = "male"
    speech_language: str = "ru"
    recognition_language: str = 'ru-RU'
    Eng: Engine = None 
    mode: str = "free"
    isActive: bool = False

    def change_mode(self):
        if self.mode == "free":
            self.mode = "command"
            return "командный"
        else:
            self.mode = "free"
            return "свободный"

    def setup(self):
        with open(r'./prop', 'r+') as file:
            prop_json = json.load(file)
            self.say("Вас приветствует программа настройки голосового ассистента " + self.name)
            self.say("Пожалуйста, скажите что вы хотите изменить - имя или пол?")
            setup_state = record_and_recognize()
            if "имя" in setup_state:
                self.say("Как вы хотите, чтобы меня звали?")
                new_name = ""
                while new_name == "":
                    new_name = record_and_recognize()
                    self.say("Теперь можете называть меня " + new_name)
                    self.name = new_name.lower()
            elif "пол" in setup_state:
                self.say("Какой пол вы хотите задать - мужской или женский?")
                new_sex = ""
                while new_sex == "":
                    new_sex = record_and_recognize()
                    returned = False
                    while not returned:
                        if "мужской" in new_sex:
                            self.sex = "male"
                            returned = True
                        elif "женский" in new_sex:
                            self.sex = "female"
                            returned = True
                        elif "женский или мужской" in new_sex:
                            self.say("Вы всё неправильно поняли, я имею в виду выберите")
                        else:
                            self.say("Не понимаю что вы хотите выбрать, скажите, женский или мужской")
                    
                self.setup_voice()
                self.say("Хорошо")
                    
            self.save_settings()

    

    def load_properties(self):
        if os.path.exists(r'./prop'):
            with open(r'./prop') as file:
                prop_json: json = json.load(file)
                self.name = prop_json['name']
                self.sex = prop_json['sex']
                print(prop_json['sex'])
                self.speech_language = prop_json['speech_language']
                self.recognition_language = prop_json['recognition_language']
                self.setup_voice() 
        elif not os.path.exists(r'./prop'):
            self.save_settings()
            self.say("При первом запуске были установлены настройки по умолчанию, скажите настроить чтобы изменить настройки")


    def save_settings(self):
        with open(r'./prop', 'w+') as file:
            prop_str = '"name": "{}", "sex": "{}", "speech_language": "{}", "recognition_language": "{}"'.format(self.name, self.sex, self.speech_language, self.recognition_language)
            prop_str = '{' + prop_str + '}'
            file.write(prop_str)
            self.setup_voice()

    def __init__(self):
        self.Eng = init()

    def setup_voice(self):
        voices = self.Eng.getProperty('voices')

        if(self.speech_language == "ru"):
            if(self.sex == "male"):
                self.Eng.setProperty('voice', voices[3].id)
            else:
                self.Eng.setProperty('voice', voices[0].id)
        elif(self.speech_language == "en"):
            if self.sex == "male":
                self.Eng.setProperty('voice', voices[1].id)
            else:
                self.Eng.setProperty('voice', voices[2].id)

    def demonstrate_voices(self):
        voices: list = self.Eng.getProperty('voices')

        for voice in range(len(voices)):
            self.Eng.setProperty('voice', voices[voice].id)
            self.Eng.say("Тест голоса номер " + str(voice))
            self.Eng.runAndWait()
            print(voices[voice])

    def say(self, to_say: str):
        self.Eng.say(to_say)
        self.Eng.runAndWait()

    def wait_for_input(self):
        while True:
            if not self.isActive:
                print("Жду ввода")
                input = record_and_recognize()
                print(input)
                if self.name in input:
                    self.say(random.choice(['слушаю, сэр', "слушаю вас", "говорите", "говорите, сэр"]))
                    self.isActive = True
                    return record_and_recognize()
            else:
                input = record_and_recognize()
                if input != "":
                    return input

def wiki_search(request: str, text: str, assistant: VoiceAssistant):
    wikipedia.set_lang("ru")
    result = wikipedia.search(text)
    print(result)

def search_for_video_on_youtube(line: str, assistant: VoiceAssistant):
    """
    Поиск видео на YouTube с автоматическим открытием ссылки на список результатов
    :param args: фраза поискового запроса
    """
    if not line: return
    search_term = "".join(line)
    url = "https://www.youtube.com/results?search_query=" + search_term
    webbrowser.get().open(url)
    assistant.say("Вот, что было найдено по запросу " + line)
    
def get_weather_forecast(assistant: VoiceAssistant):
    city_name = "Novosibirsk,RU"

    try:
        open_weather_map = OWM("815d4b7da2fe4f888c984ec0d92c6405")

        weather_manager = open_weather_map.weather_manager()
        observation = weather_manager.weather_at_place(city_name)
        weather = observation.weather
        assistant.say(weather)
    except Exception as ex:
        print(ex)
        return

def record_and_recognize():
    with microphone:
        recognized_data = ""
        recognizer.adjust_for_ambient_noise(microphone, duration=0)
        
        try:
            print("Слушаю...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())
            
            print("Распознаю...")
            recognized_data = recognizer.recognize_google(audio, language='ru').lower()

        except sr.WaitTimeoutError:
            print("Ничего не услышал")

        except sr.RequestError:
            print("Trying to use offline recognition...")
            recognized_data = use_offline_recognition()

        except Exception as ex:
            print(ex)

        return recognized_data

def define_command(text: str, assistant: VoiceAssistant):
    if assistant.mode == "command":
        for command in c.commands:
            for exact_command in command:
                if exact_command in text:
                    print(c.commands[command])
                    proceed_command(c.commands[command], assistant, text)
                    break
    elif assistant.mode == "free":
        arguments = text.split(" ")
        for guess in range(len(arguments)):
            intent = get_intent(("".join(arguments[0:len(arguments)])).strip())
            if intent:
                command_arguments = [arguments[guess:len(arguments)]]
                proceed_command(intent, assistant,text,command_arguments)
                break

def proceed_command(command: str, assistant: VoiceAssistant, line: str, arguments = [] ):
    if command == "setup":
        assistant.setup()
    elif command == "weather":
        get_weather_forecast(assistant)
    elif command == "goodbye":
        assistant.isActive = False
        assistant.say("До свидания")
    elif command == "hello":
        assistant.say(random.choice(["Приветствую", "Здравствуйте, сэр", "Добро пожаловать"]))
    elif command == "mode":
        new_mode = assistant.change_mode()
        assistant.say("Хорошо, теперь установлен " + new_mode + "режим")
    elif command == "youtube":
        search_for_video_on_youtube(line, assistant)
    elif command == "shutdown":
        assistant.say(random.choice(["Аллах акбар, выключаю компьютер", "Выключаю, до скорого", "Хорошо, выключаю, до встречи"]))
        os.system("shutdown /s /t 10")
        

def use_offline_recognition():
    recognized_data = ""
    try:
        if not os.path.exists("./model"):
            pass
            exit(1)

        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model(r"./model")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except:
        print("Щас ничего не работает, попробуй позже")

    return recognized_data

def prepare_model():
    model = []
    target_vector = []
    for intent_name, intent_data in c.dialogue["intents"].items():
        for example in intent_data["examples"]:
            model.append(example)
            target_vector.append(intent_name)
    training_model = vectorizer.fit_transform(model)
    classifier_probability.fit(training_model, target_vector)
    classifier.fit(training_model, target_vector)

def get_intent(request):
    best_intent = classifier.predict(vectorizer.transform([request]))[0]
    index_of_best_intent = list(classifier_probability.classes_).index(best_intent)
    probabilities = classifier_probability.predict_proba(vectorizer.transform([request]))[0]
    best_intent_probability = probabilities[index_of_best_intent]
    print(best_intent_probability, best_intent)
    if best_intent_probability > 0.27:
        return c.dialogue["intents"][best_intent]["response"]
    elif c.dialogue["intents"][best_intent]["response"] == "youtube":
        return c.dialogue["intents"][best_intent]["response"]
    
        
    

if __name__ == "__main__":
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range= (2,3))
    classifier_probability = LogisticRegression()
    classifier = LinearSVC()
    prepare_model()

    assistant = VoiceAssistant()
    assistant.load_properties()
    print(assistant.name)
    while True:
        voice_input = assistant.wait_for_input()
        try:
            os.remove(r"./microphone-results.wav")
        except:
            pass
        define_command(voice_input, assistant)



