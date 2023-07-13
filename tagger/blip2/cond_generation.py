from PIL import Image
import requests
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
import os

# 1. 你懂得佛跳墙 god need vpn
os.environ['HTTP_PROXY'] = 'http://192.168.126.12:12798'
os.environ['HTTPS_PROXY'] = 'http://192.168.126.12:12798'

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"device:{device}")

MODEL_NAME = "Salesforce/blip2-opt-2.7b"
processor = Blip2Processor.from_pretrained(MODEL_NAME)
model = Blip2ForConditionalGeneration.from_pretrained(
    MODEL_NAME, torch_dtype=torch.float16
)
model = model.to(device)

url = "https://c-ssl.duitang.com/uploads/blog/202304/16/20230416133750_10806.jpeg"



def hello_blip2():
    image = Image.open(requests.get(url, stream=True).raw)
    prompt = "Question: how many cats are there? Answer:"
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(device, torch.float16)
    generated_ids = model.generate(**inputs)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    print(generated_text)


def image_captioning():
    image = Image.open(requests.get(url, stream=True).raw)
    inputs = processor(image, return_tensors="pt").to(device, torch.float16)
    # we pass a maximum of 20 new tokens for the image and the text
    # generated_ids = model.generate(**inputs, max_new_tokens=20)
    generated_ids = model.generate(**inputs)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    print(generated_text)


if __name__ == '__main__':
    # https://colab.research.google.com/github/NielsRogge/Transformers-Tutorials/blob/master/BLIP-2/Chat_with_BLIP_2.ipynb#scrollTo=24jOWISkfeHA
    # hello_blip2()
    image_captioning()

