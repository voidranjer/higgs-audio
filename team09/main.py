import subprocess
import requests
import re
import shutil
import os
from generation import main as generate, HiggsAudioModelClient

model_client = HiggsAudioModelClient(
        model_path="bosonai/higgs-audio-v2-generation-3B-base",
        audio_tokenizer="bosonai/higgs-audio-v2-tokenizer",
        device="cuda:0",
        device_id=0,
        max_new_tokens=2048,
        use_static_kv_cache=1,
    )

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
    return response_text

def script_to_lines(script):
    # Clean up newlines and join wrapped lines
    text = re.sub(r'\n\s+', ' ', script.strip())

    # Split while keeping the speaker tags
    parts = re.split(r'\[(\w+)\]', text)

    # Build a list of (speaker, line) tuples
    lines = []
    for i in range(1, len(parts), 2):
        speaker = parts[i].lower()
        line = parts[i + 1].strip()
        lines.append((speaker, line))

    # Example: print the result
    # for speaker, line in lines:
    #     print(f"{speaker}: {line}")
    
    return lines

with open("llm.md", "r") as f:
    initial_prompt = f.read()
# print(initial_prompt)

# recreate tmp directory
if os.path.exists("tmp") and os.path.isdir("tmp"):
    shutil.rmtree("tmp")
os.makedirs("tmp")

# get script lines
script = query_qwen(initial_prompt)
lines = script_to_lines(script)

# generate .wav files
for i, (speaker, line) in enumerate(lines):
    with open(f'tmp/{i}.txt', 'w') as f:
       f.write(line) 
    generate(model_client, 
             scene_prompt="../examples/transcript/express.txt",
             transcript='tmp/transcript.txt',
             ref_audio=speaker,
             chunk_method='speaker',
             seed=12345,
             out_path='tmp/{i}.wav'
            )
    # subprocess.run(f"python3 ../examples/generation.py --scene_prompt ../examples/transcript/express.txt --transcript tmp/transcript.txt --ref_audio {speaker} --chunk_method speaker --seed 12345 --out_path tmp/{i}.wav", shell=True)

while True:
    user_response = input()
    response_text = query_qwen(user_response)
    lines = script_to_lines(response_text)
    for i, (speaker, line) in enumerate(lines):
        with open('tmp/transcript.txt', 'w') as f:
            f.write(line) 
        subprocess.run(f"python3 ../examples/generation.py --scene_prompt ../examples/transcript/express.txt --transcript tmp/transcript.txt --ref_audio {speaker} --chunk_method speaker --seed 12345 --out_path tmp/{i}.wav", shell=True)

if __name__ == '__main__':
    print('hi')