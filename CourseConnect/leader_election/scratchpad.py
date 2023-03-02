import requests

def get_public_ip():
    url = 'https://api.ipify.org'
    response = requests.get(url)
    return response.text
print(get_public_ip())