import requests

url = 'http://localhost:8080'
data = {
    'prompt': 'Write a Python function to add two numbers.',
    'language': 'python'
}

response = requests.post(url, json=data)
print(response.text)
