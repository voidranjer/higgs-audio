import subprocess
import requests

messages = []

def query_qwen(prompt):
    messages.append({"role":"user","content":f"{prompt}"})
    headers = {"Content-Type": "application/json"}
    data = {
            "model": "qwen3-30b-a3b-thinking-fp8",
            "messages": messages,
            # "max_tokens": 256
            }
    response = requests.post("http://20.66.111.167:31022/v1/chat/completions", headers=headers, json=data)
    # print(response.status_code)
    response = response.json()
    message = response['choices'][0]['message']
    messages.append(message)
    response_text = message['content']
    response_text = response_text[response_text.find("</think>") + 8:]
    print(response_text)

with open("llm.md", "r") as f:
    initial_prompt = f.read()
# print(initial_prompt)

query_qwen(initial_prompt)
while True:
    user_response = input()
    query_qwen(user_response)
