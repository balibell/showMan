import os

import torch
from diffusers import AutoencoderKL
import numpy as np
from PIL import Image
# use proxy
os.environ['HTTP_PROXY'] = 'http://192.168.126.12:12798'
os.environ['HTTPS_PROXY'] = 'http://192.168.126.12:12798'
# 加载模型: autoencoder可以通过SD权重指定subfolder来单独加载
autoencoder = AutoencoderKL.from_pretrained("runwayml/stable-diffusion-v1-5", subfolder="vae")

autoencoder.to("cuda", dtype=torch.float16)

print(autoencoder)
