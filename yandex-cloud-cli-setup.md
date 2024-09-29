# 🚀 Установка Yandex.Cloud CLI и создание ключей для Yandex SpeechKit и Object Storage (Windows)

Это руководство поможет вам установить Yandex.Cloud CLI на Windows и настроить все необходимое для работы с Yandex SpeechKit и Yandex Object Storage.

## 📥 Установка Yandex.Cloud CLI (Windows)

1. 🖥️ Откройте PowerShell от имени администратора и выполните следующую команду:

   ```powershell
   Invoke-WebRequest -Uri https://storage.yandexcloud.net/yandexcloud-yc/install.ps1 -OutFile install.ps1; ./install.ps1
   ```

2. 🔄 После установки перезагрузите PowerShell, затем настройте CLI:

   ```powershell
   yc init
   ```

   Следуйте инструкциям для авторизации, выбора каталога и создания профиля.

## 👤 Шаг 1: Создание сервисного аккаунта

1. 🆕 Создайте сервисный аккаунт:

   ```powershell
   yc iam service-account create --name speechkit-sa --description "Service account for SpeechKit"
   ```

2. 🔍 Получите ID созданного сервисного аккаунта:

   ```powershell
   yc iam service-account get --name speechkit-sa
   ```

3. 🔑 Назначьте роли сервисному аккаунту:

   ```powershell
   yc iam service-account add-access-binding --id <SERVICE_ACCOUNT_ID> --role editor --subject serviceAccount:<SERVICE_ACCOUNT_ID>
   ```

## 🔐 Шаг 2: Создание ключа API для сервисного аккаунта

1. 🔑 Создайте ключ API:

   ```powershell
   yc iam access-key create --service-account-name speechkit-sa
   ```

2. 📝 Сохраните полученные `access_key_id` и `secret_access_key`.

## 📄 Шаг 3: Создание ключа сервисного аккаунта

1. 🔑 Сгенерируйте ключ сервисного аккаунта:

   ```powershell
   yc iam key create --service-account-name speechkit-sa --output service_account_key.json
   ```

2. 💾 Сохраните файл `service_account_key.json` в директории вашего проекта.

## 🪣 Шаг 4: Создание бакета в Yandex Object Storage

1. 🆕 Создайте бакет:

   ```powershell
   yc storage bucket create --name <BUCKET_NAME>
   ```

2. 🔒 Настройте доступ для сервисного аккаунта к бакету:

   ```powershell
   yc storage bucket update --name <BUCKET_NAME> --default-acl=private
   ```

## 🔑 Шаг 5: Генерация ключа доступа для работы с бакетом

1. 🔐 Сгенерируйте ключи доступа:

   ```powershell
   yc iam access-key create --service-account-name speechkit-sa
   ```

2. 📝 Сохраните `AWS_ACCESS_KEY_ID` и `AWS_SECRET_ACCESS_KEY` из вывода команды.

## ⚙️ Шаг 6: Настройка переменных окружения

После создания ключей добавьте следующие переменные в файл `.env`:

```
FOLDER_ID=ваш_folder_id
AWS_ACCESS_KEY_ID=ваш_access_key_id
AWS_SECRET_ACCESS_KEY=ваш_secret_access_key
BUCKET_NAME=имя_вашего_бакета
```

### 🔍 Как получить `FOLDER_ID`:

1. Используйте команду:

   ```powershell
   yc resource-manager folder get --name default
   ```

2. 📋 Скопируйте `FOLDER_ID` из вывода команды.

## ⚠️ Важные замечания

- 🔒 **Защита учетных данных**: Не добавляйте файл `.env` или `service_account_key.json` в систему контроля версий. Добавьте их в `.gitignore`.
  
- 🔐 **Настройка прав доступа**: Убедитесь, что сервисный аккаунт имеет необходимые права для доступа к Yandex SpeechKit и Yandex Object Storage.

- 🌍 **Регион бакета**: Убедитесь, что бакет создан в регионе `ru-central1`, если вы используете этот регион в своем коде.

## 📚 Дополнительные ресурсы

- [Документация Yandex.Cloud CLI](https://cloud.yandex.ru/docs/cli/)
- [Документация Yandex Object Storage](https://cloud.yandex.ru/docs/storage/)
- [Документация Yandex SpeechKit](https://cloud.yandex.ru/docs/speechkit/)
