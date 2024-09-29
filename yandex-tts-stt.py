# yandex_tts_stt.py

import requests
import json
import time
import os
import datetime
import jwt
import boto3
from botocore.client import Config
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Инициализация colorama
init(autoreset=True)

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значений из переменных окружения
FOLDER_ID = os.getenv('FOLDER_ID')
IAM_ENDPOINT = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
TTS_URL = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
STT_URL = 'https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize'
OPERATION_URL = 'https://operation.api.cloud.yandex.net/operations/'

# Функция для получения IAM-токена с помощью сервисного аккаунта
def get_iam_token_from_sa_key():
    try:
        with open('service_account_key.json') as infile:
            key_data = json.load(infile)
    except FileNotFoundError:
        print(f"{Fore.RED}⚠️  Файл service_account_key.json не найден.")
        return None
    except json.JSONDecodeError:
        print(f"{Fore.RED}⚠️  Ошибка при чтении service_account_key.json.")
        return None

    service_account_id = key_data['service_account_id']
    key_id = key_data['id']
    private_key_raw = key_data['private_key']

    # Извлечение PEM-форматированного закрытого ключа
    private_key_lines = private_key_raw.split('\n')
    pem_start = '-----BEGIN PRIVATE KEY-----'
    pem_end = '-----END PRIVATE KEY-----'

    try:
        start_index = private_key_lines.index(pem_start)
        end_index = private_key_lines.index(pem_end)
        pem_lines = private_key_lines[start_index:end_index + 1]
        private_key = '\n'.join(pem_lines) + '\n'
    except ValueError:
        print(f"{Fore.RED}⚠️  Неправильный формат закрытого ключа.")
        return None

    now = datetime.datetime.now(datetime.timezone.utc)

    payload = {
        'aud': IAM_ENDPOINT,
        'iss': service_account_id,
        'iat': int(now.timestamp()),
        'exp': int((now + datetime.timedelta(minutes=1)).timestamp()),
    }

    additional_headers = {
        'kid': key_id,
    }

    try:
        encoded_jwt = jwt.encode(
            payload,
            private_key,
            algorithm='PS256',
            headers=additional_headers,
        )
    except Exception as e:
        print(f"{Fore.RED}⚠️  Ошибка при создании JWT: {e}")
        return None

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'jwt': encoded_jwt
    }

    response = requests.post(IAM_ENDPOINT, headers=headers, json=data)

    if response.status_code == 200:
        iam_token = response.json()['iamToken']
        print(f"{Fore.GREEN}✅  IAM-токен успешно получен.")
        return iam_token
    else:
        print(f"{Fore.RED}⚠️  Ошибка при получении IAM-токена: {response.text}")
        return None

# Функция для синтеза речи
def synthesize_text(iam_token, text, output_audio_file='output.ogg'):
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'oksana',
        'speed': '1.0',
        'format': 'oggopus',
        'folderId': FOLDER_ID,
    }

    response = requests.post(TTS_URL, headers=headers, data=data)

    if response.status_code == 200:
        with open(output_audio_file, 'wb') as f:
            f.write(response.content)
        print(f"{Fore.GREEN}✅  Аудио сохранено в {output_audio_file}")
        return output_audio_file
    else:
        print(f"{Fore.RED}⚠️  Ошибка при синтезе речи:")
        print(f"Статус код: {response.status_code}")
        print(f"Ответ: {response.text}")
        return None

# Функция для загрузки аудиофайла в Object Storage и получения URI
def upload_audio_to_object_storage(audio_file):
    # Получение данных доступа из переменных окружения
    ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    BUCKET_NAME = os.getenv('BUCKET_NAME')

    if not ACCESS_KEY or not SECRET_KEY or not BUCKET_NAME:
        print(f"{Fore.RED}⚠️  Необходимо установить ACCESS_KEY, SECRET_KEY и BUCKET_NAME в файле .env")
        return None

    s3 = boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='ru-central1',
    )

    try:
        s3.upload_file(audio_file, BUCKET_NAME, audio_file)
        print(f"{Fore.GREEN}✅  Аудиофайл загружен в Object Storage.")
    except Exception as e:
        print(f"{Fore.RED}⚠️  Ошибка при загрузке аудиофайла: {e}")
        return None

    # Генерация временной ссылки
    try:
        audio_uri = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': audio_file,
            },
            ExpiresIn=3600,  # Ссылка действительна 1 час
        )
        print(f"{Fore.GREEN}✅  Получен URI аудиофайла.")
        return audio_uri
    except Exception as e:
        print(f"{Fore.RED}⚠️  Ошибка при генерации URI: {e}")
        return None

# Функция для запуска распознавания речи
def recognize_speech_long_running(iam_token, audio_uri):
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json',
    }

    data = {
        "folderId": FOLDER_ID,
        "config": {
            "specification": {
                "languageCode": "ru-RU",
                "audioEncoding": "OGG_OPUS",
                "enableWordTimeOffsets": True,
            }
        },
        "audio": {
            "uri": audio_uri
        }
    }

    response = requests.post(STT_URL, headers=headers, json=data)

    if response.status_code == 200:
        operation_id = response.json().get('id')
        print(f"{Fore.GREEN}📝 Операция запущена с ID: {operation_id}")
        return operation_id
    else:
        print(f"{Fore.RED}⚠️  Ошибка при распознавании речи:")
        print(f"Статус код: {response.status_code}")
        print(f"Ответ: {response.text}")
        return None

# Функция для получения результата распознавания
def get_recognition_result(iam_token, operation_id):
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json',
    }
    while True:
        response = requests.get(f'{OPERATION_URL}{operation_id}', headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get('done', False):
                if 'response' in result:
                    print(f"{Fore.GREEN}🎉 Распознавание успешно завершено.")
                    return result['response']['chunks']
                else:
                    print(f"{Fore.RED}⚠️ Распознавание завершилось с ошибкой: {result}")
                    return None
            else:
                print(f"{Fore.CYAN}⏳ Ожидание завершения операции...")
                time.sleep(5)
        else:
            print(f"{Fore.RED}⚠️  Ошибка при получении статуса операции:")
            print(f"Статус код: {response.status_code}")
            print(f"Ответ: {response.text}")
            return None

# Главная функция
def main():
    # Получение IAM-токена
    iam_token = get_iam_token_from_sa_key()

    if iam_token:
        # Текст для синтеза
        text = "Привет, как твои дела?"

        # Шаг 1: Синтез речи
        audio_file = synthesize_text(iam_token, text)

        if audio_file:
            # Шаг 2: Загрузка аудиофайла и получение URI
            audio_uri = upload_audio_to_object_storage(audio_file)

            if audio_uri:
                # Шаг 3: Запуск распознавания речи
                operation_id = recognize_speech_long_running(iam_token, audio_uri)

                if operation_id:
                    # Шаг 4: Получение результата распознавания
                    recognition_result = get_recognition_result(iam_token, operation_id)

                    if recognition_result:
                        for chunk in recognition_result:
                            alternatives = chunk.get('alternatives', [])
                            for alternative in alternatives:
                                words = alternative.get('words', [])
                                for word_info in words:
                                    word = word_info['word']
                                    start_time = word_info['startTime']
                                    end_time = word_info['endTime']
                                    print(f"{Fore.GREEN}🗣️ {word}: начало {start_time}, конец {end_time}")

if __name__ == '__main__':
    main()
