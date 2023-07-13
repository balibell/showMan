import os
import sys
import json

PNG_SUFFIX = '.png'  
JPG_SUFFIX = '.jpg' 
JPEG_SUFFIX = '.jpeg' 
TXT_SUFFIX = '.txt'

KEY_FILE_NAME = 'file_name'
KEY_PROMPTS = 'prompts'
KEY_PROMPTS_ARR = 'prompts_arr'

metadata = []


def load_string_data(path):
  # 读取文件
  with open(path, 'r') as f:
    content = f.read()
  return content

def load_prompts_arr(path):
  if os.path.exists(path):
    pstr = load_string_data(path)
    print(f"pstr in genMetadata.py is {pstr}")
    parr = pstr.split(',')
    prompts_arr = list(filter(lambda y: y != '', list(map(lambda x: x.strip(), parr))))
    return prompts_arr
  return []

def load_json_data(path):
  data = None
  # 读取JSON文件
  with open(path, 'r') as f:
    data = json.load(f)
  return data


def save_json_data(path, json_object):
  with open(path, "w") as file:
    file.write(json.dumps(json_object, indent=2))


# 目标 images 目录下的图片、文本转成json，同时保留 prompt 权重信息
def main_entry(directory, save_metadata_path):
  for dir, dirs, files in os.walk(directory):
    relative_path = os.path.relpath(dir, directory)
    opt_relative_str = ''
    if relative_path != '.' and relative_path != '':
      opt_relative_str = f'{relative_path}/'
    for file in files:
      lower_file = file.lower()
      fname = os.path.splitext(file)[0]
      if lower_file.endswith(PNG_SUFFIX) or lower_file.endswith(JPG_SUFFIX) or lower_file.endswith(JPEG_SUFFIX):
        text_fname = f"{fname}{TXT_SUFFIX}"
        file_path = os.path.abspath(os.path.join(dir, file))
        text_file_path =  os.path.abspath(os.path.join(dir, text_fname))

        item = {
          "file_name": f"{opt_relative_str}{file}",
          "img_dir": directory
        }

        prompts_arr = load_prompts_arr(text_file_path)

        # 数组赋值
        item[KEY_PROMPTS_ARR] = prompts_arr

        # item[KEY_PROMPTS] = prompts_arr
        metadata.append(item)

        print(f"relative_path:{relative_path}   file_path:{file_path}  text_file_path:{text_file_path}")
        print(item)

  save_json_data(save_metadata_path, metadata)
  print(f"save to local file {save_metadata_path} total num: {len(metadata)}")


if __name__ == "__main__":
  img_dir = sys.argv[1]
  save_metadata_path = sys.argv[2]

  main_entry(img_dir, save_metadata_path)
