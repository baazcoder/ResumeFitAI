import requests
import json

url = "http://localhost:11434/api/generate"

payload = {
    "model": "llama2",
    "prompt": "Say hello from Llama 2"
}

response = requests.post(url, json=payload, stream=True)

full = ""

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode())
        full += data.get("response","")

print(full)
