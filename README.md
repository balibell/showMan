# bash 下需要安装

node
python3
md5sha1sum
git



### 要正常使用 sed -i 先要装 coreutils 然后装 gnu-sed
brew install gnu-sed
### 然后在 .zshrc 里写入 export PATH="$(brew --prefix)/opt/gnu-sed/libexec/gnubin:$PATH"
  



# python 依赖安装
`pip install -r requirements.txt`


# node 依赖安装
`npm install sharp`