import os
import time
from optimum.onnxruntime import ORTStableDiffusionPipeline
from transformers import CLIPTextModel, CLIPTokenizer
from diffusers import DiffusionPipeline, AutoencoderKL, UNet2DConditionModel, PNDMScheduler, \
    UniPCMultistepScheduler, StableDiffusionLatentUpscalePipeline
from diffusers.models.attention_processor import AttnProcessor2_0
import torch

from inner.tools import image_tools

model_id = "stabilityai/sd-x2-latent-upscaler"

# use proxy
# os.environ['HTTP_PROXY'] = 'http://192.168.126.12:12798'
# os.environ['HTTPS_PROXY'] = 'http://192.168.126.12:12798'

local_model_path = '/root/autodl-tmp/output/rev_diff'

device = 'cuda'

# 1. 使用转换为 diffuser 的 rev 模型
pipe = DiffusionPipeline.from_pretrained(local_model_path, torch_dtype=torch.float16)
# pipe = ORTStableDiffusionPipeline.from_pretrained(local_model_path, export=True)

pipe.to(device)
## optimize
pipe.enable_xformers_memory_efficient_attention()
# pipe.enable_model_cpu_offload()
print(pipe.unet.conv_out.state_dict()["weight"].stride())  # (2880, 9, 3, 1)
pipe.unet.set_attn_processor(AttnProcessor2_0())
pipe.unet.to(memory_format=torch.channels_last)  # in-place operation
print(
    pipe.unet.conv_out.state_dict()["weight"].stride()
)  # (2880, 1, 960, 320) having a stride of 1 for the 2nd dimension proves that it works


# 直接编译有用吗
# pipe.unet = torch.compile(pipe.unet)

## 2. 加载官方推荐的 三方 vae
# vae = AutoencoderKL.from_pretrained("/root/autodl-tmp/output/sd_vae/orangemix")
# pipe.vae = vae


# enable tiling
# pipe.vae.enable_tiling()


def text2img(seed=-1, count=1):
    start_time = time.perf_counter()
    generator = torch.Generator(device).manual_seed(seed)
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        generator=generator,
        num_images_per_prompt=count,
        # width=4096,
        width=512,
        height=512,
    )

    end_time = time.perf_counter()
    print(f"代码执行时间为 {end_time - start_time} 秒")
    for image in result.images:
        image_tools.show_img(image)


if __name__ == '__main__':
    prompt = "((best quality)), ((masterpiece)), (detailed), woman with green hair, holding a sword, (Artgerm inspired:1.2), (pixiv contest winner:1.1), (octopus goddess:1.3), (Berserk art style:1.2), close-up portrait, goddess skull, (Senna from League of Legends:1.1), (Tatsumaki with green curly hair:1.2), card game illustration, thick brush, HD anime wallpaper, (Akali from League of Legends:1.1), 8k resolution"
    negative_prompt = " 3d, cartoon, anime, sketches, (worst quality, bad quality, child, cropped:1.4) ((monochrome)), ((grayscale)),  (bad-hands-5:1.0), (badhandv4:1.0), (easynegative:0.8),  (bad-artist-anime:0.8), (bad-artist:0.8), (bad_prompt:0.8), (bad-picture-chill-75v:0.8), (bad_prompt_version2:0.8),  (bad_quality:0.8)"
    # text2img()
