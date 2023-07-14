# 安装
```
node
python3
md5sha1sum
git
```
** 确保命令行 python 指向 python3 **


** mac 系统要正常使用 sed -i 先要装 coreutils 然后装 gnu-sed 
然后在 .bashrc 或 .zshrc 里写入 export PATH="$(brew --prefix)/opt/gnu-sed/libexec/gnubin:$PATH" **

`brew install gnu-sed`  for mac OS
  

# python 依赖安装
```
pip install numpy
pip install pandas
pip install pillow
pip install onnxruntime
# win系统适用，含 win32clipboard win32con
pip install pywin32
# mac系统适用，含 AppKit
pip install pyobjc
```


# node 依赖安装
`npm install sharp`


# 下载 tagger 模型文件

用于给图片打标签，这个模型文件356M，可以去炼丹阁 [下载](https://www.liandange.com/models/10001285/detail/) 

下载到（注意最终名字要是 model.onnx）

./tagger/tagmodel/wd-v1-4-vit-tagger-v2/model.onnx

 

# 如何使用？

1. 新素材添加

- 新建文件夹 ~/Downloads/tempfile/xaff ➡️将素材图放进去➡️确定素材图路径➡️备份一个压缩包（创建实例过程会把里面图片转移走而不是copy走，所以备份一个是防止图片丢失）

![](images/3.png#pic_left)

- 第一次执行 open.sh 会创建一个 training/xaff 配置目录，里面有训练所需要的配置。

- `sh open.sh ~/Downloads/tempfile/xaff` 参数如果为完整路径，即为添加素材，如果是第二次添加素材，会提示已经创建过 xaff 实例，是否继续添加，如图：

![](images/5.png#pic_left)

- `sh open.sh xaff` 参数如果为实例名 xaff，则进入编辑流程

- 如果是新图添加，会使用 tagger 自动打标签，生成跟图片同名的 txt 文件。无论是添加还是编辑，最终都会进入这个页面：

![](images/6.jpeg#pic_left)

- open.sh 执行后，会进入持续监听状态，监听剪贴板的变化，在标签编辑页面导出弹框里，点击`同步`按钮会改变剪贴板内容

- ** 快捷键了解：Control+C（中断命令） **，中断监听状态，会将本次所做的修改固定，并同步到远端。

- `sh clear_inst.sh 1 xaff` 可快速清除掉实例，调试过程中需要经常用到，清除之后从头开始重新添加。

2. 命令行训练

- 编辑 training/xaff 里的训练参数文件，如果是训练 lora，则应该编辑 train_network_config.toml 文件

![](images/7.jpeg#pic_left)

- 编辑 training/xaff 里的数据配置文件，如果是训练 lora，则应该编辑 dataset_config.toml

![](images/8.jpeg#pic_left)

- 执行 `sh train_short.sh xaff` 进行远程训练。

- 如果重复训练同一个实例，会将上次训练的结果日志、模型文件删除，所以要注意保存训练结果。

3. 训练服务器

- 44训练服务器上搭建好 sd-scripts [地址](https://github.com/kohya-ss/sd-scripts) 训练环境，路径 /home/admin/github/sd-scripts

- 44训练服务器上搭建好 LyCORIS [地址](https://github.com/KohakuBlueleaf/LyCORIS) 训练环境，路径 /home/admin/github/LyCORIS

- 44训练服务器上装好TensorBoard，进入 /home/admin/github/showMan，执行 `tensorboard --logdir=training/log --bind_all --port=6006`

- 44训练服务器上监听 training/output 文件夹变化，进入 /home/admin/github/showMan，执行 `python pyutil/watchdog.py /home/admin/github/showMan/training/output`

** 监听到新产出的模型文件会 scp 同步到 45生图服务器 **

4. 生图服务器

- 45生图服务器上搭建好 Stable Diffusion 生图环境

- 45生图服务器 checkpoint 训练产出模型目录设定为 /home/admin/models/train

- 45生图服务器 lora 训练产出模型目录设定为 /home/admin/lora/train







   




# Windows用户安装指南（windows11系统64位上进行的）

1. 安装 gitbash

之后所有的命令都是gitbash里面完成的，截图左上角会有 MINGW 标志

 ![](images/1.jpeg#pic_left)
 
 


1. 安装 python3.9 或以上，同时装 pip （用安装包要选择pip以及添加PATH）

python 以及 pip 进入gitbash验收，截图：
 
  ![](images/2.jpeg#pic_left)

相关指令，含镜像设置：
```
python --version

python -m pip --version

# 设置pip镜像，这个最好设置一下，不然下载不动
pip config set global.index-url "https://pypi.tuna.tsinghua.edu.cn/simple"
```


1. Node 以及 nvm 安装

建议走下载安装流程

Node v17.6.0 (Current) | Node.js [地址](https://nodejs.org/en/blog/release/v17.6.0)

nvm [地址](https://github.com/coreybutler/nvm-windows/releases)

node 以及 nvm 进入gitbash 验收，截图：

  ![](images/4.jpeg#pic_left)

   

相关指令，含镜像设置： 

```
nvm --version

node --version

npm --version

# 设置npm镜像，这个最好设置一下，不然下载不动，url地址要带引号
npm config set registry "https://registry.npmmirror.com/"

# 查看npm镜像设置
npm config get registry
```

1. 生成sshkey
```
ssh-keygen
```

后面一路回车即可，最后会生成一个 ~/.ssh/id_rsa.pub 文件

将 pub 文件里的内容复制交给管理员

1. 编辑ssh config文件
```
Host 44
        HostName 123.123.123.123
        User root
        Port 11000

Host 45
        HostName 123.123.123.124
        User root
        Port 12000
```

编号45服务器为生图服务器，训练过程会将模型文件 scp 同步到这台服务器上

编号44服务器为训练服务器

（访问这两台服务器，需要管理员给你权限）

1. 拉取代码安装依赖

```
git clone git@github.com:balibell/showMan.git

# 安装依赖（省略）
```








