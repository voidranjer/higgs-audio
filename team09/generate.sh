python3 examples/generation.py \
  --scene_prompt examples/scene_prompts/express.txt \
  --transcript examples/transcript/single_speaker/en_express.txt \
  --ref_audio zh_man_sichuan \
  --seed 12345 \
  --out_path generation.wav

# git fetch && git reset --hard origin/main && python3 examples/generation.py --scene_prompt examples/scene_prompts/express.txt --transcript examples/transcript/single_speaker/en_express.txt --ref_audio gollum --seed 12345 --out_path generation.wav
# python3 examples/generation.py --scene_prompt examples/scene_prompts/express.txt --transcript examples/transcript/multi_speaker/en_express.txt --ref_audio walter,shrek_donkey,vex,peter,broom_salesman,bigbang_sheldon,en_man --ref_audio_in_system_message --chunk_method speaker --seed 12345 --out_path generation.wav
