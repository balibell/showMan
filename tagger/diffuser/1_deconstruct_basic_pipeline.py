import os

from diffusers import DDPMPipeline
from diffusers import DDPMScheduler, UNet2DModel
import torch
from PIL import Image
import torch
from transformers import CLIPTextModel, CLIPTokenizer
from diffusers import AutoencoderKL, UNet2DConditionModel, PNDMScheduler, UniPCMultistepScheduler
from inner.tools.image_tools import show_img, show_np

# use proxy
os.environ['HTTP_PROXY'] = 'http://192.168.126.12:12798'
os.environ['HTTPS_PROXY'] = 'http://192.168.126.12:12798'


def gen_by_pipe():
    ddpm = DDPMPipeline.from_pretrained("google/ddpm-cat-256").to("cuda")
    image = ddpm(num_inference_steps=25).images[0]
    show_img(image)


def gen_by_steps():
    global sample_size
    scheduler = DDPMScheduler.from_pretrained("google/ddpm-cat-256")
    model = UNet2DModel.from_pretrained("google/ddpm-cat-256").to("cuda")
    # 1. Set the number of timesteps to run the denoising process for
    scheduler.set_timesteps(50)
    # 2. 随机化初始化一个噪音 当作输入图片的代表, 符合模型 shape 要求即可
    sample_size = model.config.sample_size
    noise = torch.randn((1, 3, sample_size, sample_size)).to("cuda")
    input = noise
    # 3. At each timestamp, the mode UNet model will output a noisy residual
    for t in scheduler.timesteps:
        with torch.no_grad():
            ## 3.1 传入 timestep, 和 input, 会返回 剩余的噪音
            noisy_residual = model(input, t).sample

            ## 3.2 传入 timestep 和模型返回的剩余噪音 就返回上一次的 sample,
            previous_noisy_sample = scheduler.step(noisy_residual, t, input).prev_sample
            input = previous_noisy_sample
    # 4. 把最后的 一步的 noisy_sample 作为最终的输出
    image = (input / 2 + 0.5).clamp(0, 1)
    image = image.cpu().permute(0, 2, 3, 1).numpy()[0]
    show_np(image)


SD_MODEL = "runwayml/stable-diffusion-v1-5"

if __name__ == '__main__':
    # AutoEncoder 用来实现和 latent  的交互
    vae = AutoencoderKL.from_pretrained(SD_MODEL, subfolder="vae")

    # CLIP tokenizer 用来 分词 把文字转为 token 向量
    tokenizer = CLIPTokenizer.from_pretrained(SD_MODEL, subfolder="tokenizer")

    # CLIP text 文本 embedding 模型
    text_encoder = CLIPTextModel.from_pretrained(SD_MODEL, subfolder="text_encoder")

    # UNet2DConditionModel 扩散模型
    unet = UNet2DConditionModel.from_pretrained(SD_MODEL, subfolder="unet")

    # 调度器
    scheduler = UniPCMultistepScheduler.from_pretrained(SD_MODEL, subfolder="scheduler")

    torch_device = "cuda"
    vae.to(torch_device)
    text_encoder.to(torch_device)
    unet.to(torch_device)

    prompt = ["a photograph of an astronaut riding a horse"]
    height = 512  # default height of Stable Diffusion
    width = 512  # default width of Stable Diffusion
    num_inference_steps = 25  # Number of denoising steps
    guidance_scale = 7.5  # Scale for classifier-free guidance
    generator = torch.manual_seed(0)  # Seed generator to create the inital latent noise
    batch_size = len(prompt)

    text_input = tokenizer(
        prompt, padding="max_length", max_length=tokenizer.model_max_length, truncation=True, return_tensors="pt"
    )

    with torch.no_grad():
        text_embeddings = text_encoder(text_input.input_ids.to(torch_device))[0]

    # You’ll also need to generate the unconditional ƒtext embeddings which are the embeddings for the padding token
    max_length = text_input.input_ids.shape[-1]
    uncond_input = tokenizer([""] * batch_size, padding="max_length", max_length=max_length, return_tensors="pt")
    uncond_embeddings = text_encoder(uncond_input.input_ids.to(torch_device))[0]

    text_embeddings = torch.cat([uncond_embeddings, text_embeddings])

    # generate some initial random noise as a starting point for the diffusion process
    latents = torch.randn(
        (batch_size, unet.in_channels, height // 8, width // 8),
        generator=generator,
    )
    latents = latents.to(torch_device)

    # sigma, the noise scale value, which is required for improved schedulers like UniPCMultistepScheduler:
    latents = latents * scheduler.init_noise_sigma

    from tqdm.auto import tqdm

    scheduler.set_timesteps(num_inference_steps)

    for t in tqdm(scheduler.timesteps):
        # expand the latents if we are doing classifier-free guidance to avoid doing two forward passes.
        latent_model_input = torch.cat([latents] * 2)

        latent_model_input = scheduler.scale_model_input(latent_model_input, timestep=t)

        # predict the noise residual
        with torch.no_grad():
            noise_pred = unet(latent_model_input, t, encoder_hidden_states=text_embeddings).sample

        # perform guidance.
        noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
        noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

        # compute the previous noisy sample x_t -> x_t-1
        latents = scheduler.step(noise_pred, t, latents).prev_sample

    # scale and decode the image latents with vae
    latents = 1 / 0.18215 * latents
    with torch.no_grad():
        image = vae.decode(latents).sample

    # 4. 把最后的 一步的 noisy_sample 作为最终的输出
    image = (image / 2 + 0.5).clamp(0, 1)
    image = image.detach().cpu().permute(0, 2, 3, 1).numpy()
    # images = (image * 255).round().astype("uint8")
    show_np(image[0])
