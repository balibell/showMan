
```
 python train_network.py
  --enable_bucket
  --pretrained_model_name_or_path="chilloutmix-Ni.safetensors"
  --resolution=512,512
  --network_module=lycoris.kohya
  --max_train_epochs=100
  --learning_rate=2e-4
  --unet_lr=2e-4
  --text_encoder_lr=2e-5
  --lr_scheduler=constant
  --lr_warmup_steps=0
  --lr_scheduler_num_cycles=1
  --network_dim=128
  --network_alpha=128
  --train_batch_size=2
  --save_every_n_epochs=1
  --mixed_precision="fp16"
  --save_precision="fp16"
  --seed="1234"
  --cache_latents
  --clip_skip=1
  --prior_loss_weight=1
  --max_token_length=225
  --caption_extension=".txt"
  --save_model_as=safetensors
  --min_bucket_reso=256
  --max_bucket_reso=1024
  --xformers
  --shuffle_caption 
  --use_lion_optimizer
  --network_args conv_dim=4 conv_alpha=4 algo=lora dropout=0
  --multires_noise_iterations=6
  --multires_noise_discount=0.1
  --gradient_accumulation_steps=2
```

## optimizer 取值
optimizer_type = "AdamW8bit"
optimizer_type = "DAaptation"

## network_module 取值
networks.lora
networks.dylora
lycoris.kohya

## 分层训练参数
network_args = [ "conv_dim=32", "unit=4", "down_lr_weight=1,1,1,1,1,1,1,1,1,1,1,1", "mid_lr_weight=1", "up_lr_weight=1,1,1,1,1,1,1,1,1,1,1,1", "block_dims=32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32", "block_alphas=4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4",]

## 推荐降低脸部权重
network_args = [ "conv_dim=32", "unit=4", "down_lr_weight=1,0.2,1,1,0.2,1,1,0.2,1,1,1,1", "mid_lr_weight=1", "up_lr_weight=1,1,1,1,1,1,1,1,1,1,1,1", "block_dims=32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32", "block_alphas=4,4,8,4,8,8,8,4,4,8,8,8  ,4,  8,4,8,4,4,4,8,4,4,4,8,4", "conv_block_dims=8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8", "conv_block_alpha=1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1",]

## 常用模型
/home/admin/models/models/anything-v4.5-pruned.safetensors
/home/admin/models/duitang/ReV_Animated_v1.2.2.safetensors
/home/admin/models/models/v1-5-pruned-emaonly.safetensors
/home/admin/models/models/BraV5_fp16.safetensors
/home/admin/models/models/majicmixrealistic_v6.0.safetensors
/home/admin/models/models/beautiful_realistic_asians_v6.0.safetensors

## lr_scheduler 学习率曲线
lr_scheduler = "cosine_with_restarts"
lr_scheduler = "cosine"
lr_scheduler = "constant"
lr_scheduler = "constant_with_warmup"

## lora训练参数
network_module = "networks.lora"
network_dim = 32
network_alpha = 16

## dylora训练参数
* 首先 network_module = "networks.dylora"
* 其次 network_args 要开启，里面要包含 unit= conv_dim= conv_alpha=   （C3Lier有卷积层）
* 如果要开启分层训练要加上 block_dims= block_alpha= conv_block_dims= conv_block_alpha=

## lycoris训练参数
* 首先 network_module = "lycoris.kohya"
* 其次 network_args 要开启，里面要包含 unit= conv_dim= conv_alpha=   （Lycoris有卷积层）
* 跟 dylora 不同之处，network_args 里面要有 algo=loha 这个取值有 lora | locon | loha | lokr | ia3
* 如果要开启分层训练要加上 block_dims= block_alpha= conv_block_dims= conv_block_alpha=

## lycoris训练参数示例（不完整示例）
`network_args = [ "algo=loha", "conv_dim=32", "conv_alpha=16", "unit=4", ]`



## 正则图片，目前已有女性正则大约400张，文件地址：
`/home/admin/github/class/bra_girl_512_682`

## 如何使用？只需要将正则图片目录作为 subsets 加入到 datasets 即可，num_repeats = 1
```
[[datasets.subsets]]
  image_dir = '/home/admin/github/class/bra_girl_512_682'
  is_reg = true
  class_tokens = 'girl'
  caption_extension = '.txt'
  num_repeats = 1
  shuffle_caption = false
```