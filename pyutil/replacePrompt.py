import os
import sys
import re


# 将目标词替换成输入的新词

folder_path = sys.argv[1]
targetword = sys.argv[2]
replacement = sys.argv[3]

num = 0
for dir, dirs, files in os.walk(folder_path):
  for file in files:
    file_path = os.path.join(dir, file)
    if os.path.isfile(file_path) and file_path.endswith(".txt"):
      # 处理文件，例如打印文件路径
      print(file_path)
      with open(file_path, 'r') as file:
        prompt = file.read()

      print('read prompt: %s' % prompt)

      print('target word is %s and replacement is %s' % (targetword, replacement))


      # 做正则替换
      pattern = re.compile(rf"{targetword}")
      newprompt = pattern.sub(replacement, prompt)
      print('after replace: %s' % newprompt)
      if newprompt != prompt:
        num += 1

      with open(file_path, 'w') as file:
        file.write(newprompt)


print(f'total replaced num is {num}')
