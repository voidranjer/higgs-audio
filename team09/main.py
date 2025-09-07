import subprocess
import requests

def query_qwen(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
            "model": "qwen3-30b-a3b-thinking-fp8",
            "messages": [{"role":"user","content":f"{prompt}"}],
            "max_tokens": 256
            }
    response = requests.post("http://20.66.111.167:31022/v1/chat/completions", headers=headers, json=data)
    print(response.status_code)
    print(response.json()['choices'][0]['message']['content'])  # If the response is JSON

with open("llm.md", "r") as f:
    initial_prompt = f.read()
# print(initial_prompt)

query_qwen("initial_prompt")
