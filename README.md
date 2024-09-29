# Yandex TTS-STT Example 🎙️📝

Это демонстрационный пример того, как сгенерировать аудио по тексту с помощью Yandex SpeechKit Text-to-Speech, а затем получить текст с таймкодами с помощью Speech-to-Text.

## 📋 Содержание
- [Описание](#описание)
- [Особенности](#особенности)
- [Используемые технологии](#используемые-технологии)
- [Требования](#требования)
- [Установка](#установка)
- [Использование](#использование)
- [Конфигурация](#конфигурация)
  - [Получение необходимых переменных](#получение-необходимых-переменных)
    - [1. FOLDER_ID](#1-folder_id)
    - [2. Ключ сервисного аккаунта](#2-ключ-сервисного-аккаунта)
    - [3. AWS_ACCESS_KEY_ID и AWS_SECRET_ACCESS_KEY](#3-aws_access_key_id-и-aws_secret_access_key)
    - [4. BUCKET_NAME](#4-bucket_name)
- [Документация](#документация)
- [Лицензия](#лицензия)

## 📖 Описание

Этот проект демонстрирует, как использовать сервисы Yandex.Cloud для преобразования текста в речь, а затем распознать речь с получением временных меток для каждого слова. Это полезно для приложений, которым требуется синхронизация текста и аудио, таких как субтитры или интерактивные голосовые помощники.

## ✨ Особенности

- **Синтез речи**: Преобразование текста в аудио с помощью Yandex SpeechKit.
- **Загрузка в Object Storage**: Автоматическая загрузка сгенерированного аудио в Yandex Object Storage.
- **Распознавание речи**: Распознавание речи с получением временных меток для каждого слова.
- **Аутентификация**: Использование сервисных аккаунтов и IAM-токенов для безопасного доступа к API.

## Используемые технологии

- Язык программирования: Python 3.7+
- Сервисы Yandex.Cloud:
  - Yandex SpeechKit
  - Yandex Object Storage
  - Yandex Identity and Access Management (IAM)
- Библиотеки Python:
  - requests
  - boto3
  - PyJWT
  - python-dotenv
  - colorama

## Требования

- Python: версия 3.7 или выше
- Аккаунт в Yandex.Cloud
- Yandex.Cloud CLI: для настройки и управления ресурсами

## 🛠 Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/yourusername/yandex-tts-stt-example.git
   cd yandex-tts-stt-example
   ```

2. Создайте виртуальное окружение (рекомендуется):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Windows: venv\Scripts\activate
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Использование

1. Настройте переменные окружения (см. раздел [Конфигурация](#конфигурация)).

2. Запустите скрипт:

   ```bash
   python yandex_tts_stt.py
   ```

## Формат вывода

Результат работы скрипта выводится в формате JSON, который содержит оригинальный текст и список распознанных слов с их временными метками. Пример вывода:

```bash
✅  IAM-токен успешно получен.
✅  Аудио сохранено в output.ogg
✅  Аудиофайл загружен в Object Storage.
✅  Получен URI аудиофайла.
📝  Операция запущена с ID: e03igrvpvnjfomk0cs6s
🎉  Распознавание успешно завершено.

{
  "original_text": "Привет, как твои дела?",
  "words": [
    {
      "word": "привет",
      "start_time": 160,
      "end_time": 659
    },
    {
      "word": "как",
      "start_time": 740,
      "end_time": 859
    },
    {
      "word": "твои",
      "start_time": 919,
      "end_time": 1120
    },
    {
      "word": "дела",
      "start_time": 1180,
      "end_time": 1540
    }
  ]
}
```

Этот формат удобен для дальнейшей обработки на фронтенде, например, для подсветки слов в соответствии с их произношением в аудио.

🕒 Временные метки указаны в миллисекундах для удобства использования в веб-разработке.


## ⚙️ Конфигурация

Необходимо настроить несколько переменных окружения в файле `.env`. Следуйте инструкциям ниже:

1. Создайте файл `.env` в директории проекта:

   ```bash
   touch .env
   ```

2. Добавьте в файл `.env` следующие переменные:

   ```dotenv
   FOLDER_ID=ваш_folder_id
   AWS_ACCESS_KEY_ID=ваш_access_key_id
   AWS_SECRET_ACCESS_KEY=ваш_secret_access_key
   BUCKET_NAME=имя_вашего_бакета
   ```

### Получение необходимых переменных

#### 1. FOLDER_ID

Как получить:
- Войдите в консоль управления Yandex.Cloud.
- Выберите нужный каталог (folder).
- FOLDER_ID отображается в URL браузера после `/folders/`.

#### 2. Ключ сервисного аккаунта

1. Создайте сервисный аккаунт:
   - Перейдите в раздел IAM -> Сервисные аккаунты.
   - Нажмите "Создать сервисный аккаунт".
   - Укажите имя (например, speechkit-sa).

2. Назначьте роли сервисному аккаунту:
   - Перейдите во вкладку "Роли сервисного аккаунта".
   - Нажмите "Назначить роль" и добавьте следующие роли:
     - `editor` (или более конкретные, такие как `speechkit.tts.user`, `speechkit.stt.user`, `storage.uploader`).

3. Создайте ключ сервисного аккаунта:
   - Перейдите во вкладку "Ключи API сервисного аккаунта".
   - Нажмите "Создать новый ключ".
   - Выберите "Ключ для доступа к API Yandex.Cloud".
   - Скачайте файл `service_account_key.json`.
   - Поместите его в директорию проекта.

#### 3. AWS_ACCESS_KEY_ID и AWS_SECRET_ACCESS_KEY

Создайте ключи доступа для Object Storage:
- Перейдите во вкладку "Ключи доступа сервисного аккаунта".
- Нажмите "Создать ключ доступа".
- Сохраните значения "Идентификатор ключа доступа" (AWS_ACCESS_KEY_ID) и "Секретный ключ доступа" (AWS_SECRET_ACCESS_KEY).

**Примечание:** Секретный ключ доступа отображается только один раз. Убедитесь, что вы его сохранили.

#### 4. BUCKET_NAME

Создайте бакет в Object Storage:
1. Перейдите в раздел Object Storage.
2. Нажмите "Создать бакет".
3. Укажите уникальное имя бакета (например, my-audio-bucket).
4. Настройте права доступа, чтобы ваш сервисный аккаунт имел доступ к бакету.

**Важные замечания:**

- Защитите ваши учетные данные:
  - Не добавляйте файл `.env` или `service_account_key.json` в систему контроля версий.
  - Добавьте их в `.gitignore`.
- Права доступа:
  - Убедитесь, что сервисный аккаунт имеет необходимые роли для доступа к сервисам SpeechKit и Object Storage.
- Регион бакета:
  - Убедитесь, что бакет создан в регионе `ru-central1`, если используете его в коде.



> Также необходимые ключи и идентификаторы можно сгенерировать через Yandex Cloud CLI, подбробнее смотреть [инструкцию](yandex-cloud-cli-setup.md)



## Документация

- Yandex SpeechKit:
  - [Обзор SpeechKit](https://cloud.yandex.ru/docs/speechkit/)
  - [Text-to-Speech API](https://cloud.yandex.ru/docs/speechkit/tts/)
  - [Speech-to-Text API](https://cloud.yandex.ru/docs/speechkit/stt/)
- Yandex Object Storage:
  - [Обзор Object Storage](https://cloud.yandex.ru/docs/storage/)
  - [Документация по S3 API](https://cloud.yandex.ru/docs/storage/s3/)
- Yandex Identity and Access Management (IAM):
  - [Обзор IAM](https://cloud.yandex.ru/docs/iam/)
  - [Сервисные аккаунты](https://cloud.yandex.ru/docs/iam/concepts/users/service-accounts)
- Yandex.Cloud CLI:
  - [Установка и настройка CLI](https://cloud.yandex.ru/docs/cli/quickstart)
- Библиотеки Python:
  - [requests](https://docs.python-requests.org/)
  - [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
  - [PyJWT](https://pyjwt.readthedocs.io/)
  - [python-dotenv](https://github.com/theskumar/python-dotenv)
  - [colorama](https://github.com/tartley/colorama)

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).
