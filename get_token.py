import requests

url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
data = {
    "yandexPassportOauthToken": "y0_AgAAAAAEZVGiAATuwQAAAAESnkUFAAB1Pq-bBYdKS63Q7cOtsiJW4uyllQ"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print(response.json()["iamToken"])
else:
    print(f"Error: {response.text}")