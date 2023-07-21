import os
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
from PIL import Image
import argparse
from tools import resize_tools
import threading
import time
from PIL import Image, UnidentifiedImageError
from concurrent.futures import ThreadPoolExecutor
import json

PNG_SUFFIX = '.png'  
JPG_SUFFIX = '.jpg' 
JPEG_SUFFIX = '.jpeg' 
TXT_SUFFIX = '.txt'
TIME_FORMAT_STR = "%Y-%m-%d %H:%M:%S"

TAGS_FILE_NAME = 'tags.csv'
MODEL_NAME = 'model.onnx'

tags_white_list = None


def load_string_data(path):
  # 读取文件
  with open(path, 'r') as f:
    content = f.read()
  return content

def load_prompts_arr(path):
  if os.path.exists(path):
    pstr = load_string_data(path)
    print(f"pstr in tagger.py is {pstr}")
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


def convert_img(image: Image, height: int):
  image = image.convert('RGBA')
  new_image = Image.new('RGBA', image.size, 'WHITE')
  new_image.paste(image, mask=image)
  image = new_image.convert('RGB')

  # 基于PIL, 在asarray前重采样
  image = resize_tools.make_squar(image, height)
  image = resize_tools.smart_resize(image, height)
  #-----

  image = np.asarray(image)

  # PIL RGB to OpenCV BGR
  image = image[:, :, ::-1]

  # 原本基于opencv的重采样位置
  #image = resize_tools.make_square(image, height)
  #image = resize_tools.smart_resize(image, height)
  #-----
  image = image.astype(np.float32)
  image = np.expand_dims(image, 0)
  return image


def postprocess_tags(
    tags: Dict[str, float],
    threshold,
    additional_tags: List[str] = [],
    exclude_tags: List[str] = [],
    sort_by_alphabetical_order=False,
    add_confident_as_weight=False,
    replace_underscore=False,
    replace_underscore_excludes: List[str] = [],
    escape_tag=False
) -> Dict[str, float]:
  for t in additional_tags:
    tags[t] = 1.0

  # those lines are totally not "pythonic" but looks better to me
  tags = {
    t: c

    # sort by tag name or confident
    for t, c in sorted(
      tags.items(),
      key=lambda i: i[0 if sort_by_alphabetical_order else 1],
      reverse=not sort_by_alphabetical_order
    )

    # filter tags
    if (
      c >= threshold
      and t not in exclude_tags
      and (tags_white_list == None or len(tags_white_list) <= 0 or t in tags_white_list)
    )
  }
  print(tags)


  new_tags = []
  for tag in list(tags):
    new_tag = tag

    if replace_underscore and tag not in replace_underscore_excludes:
      new_tag = new_tag.replace('_', ' ')

    # if escape_tag:
    #   new_tag = tag_escape_pattern.sub(r'\\\1', new_tag)

    if add_confident_as_weight:
      new_tag = f'({new_tag}:{tags[tag]})'

    new_tags.append((new_tag, tags[tag]))
  tags = dict(new_tags)

  return tags


class WaifuDiffusionInterrogator:
  def __init__(
      self,
      model_path: str,
      tags_path: str,
      **kwargs
  ) -> None:
    self.model_path = model_path
    self.tags_path = tags_path
    self.kwargs = kwargs

  def load(self) -> None:
    from onnxruntime import InferenceSession

    # https://onnxruntime.ai/docs/execution-providers/
    # https://github.com/toriato/stable-diffusion-webui-wd14-tagger/commit/e4ec460122cf674bbf984df30cdb10b4370c1224#r92654958
    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']


    self.model = InferenceSession(self.model_path, providers=providers)
    print(f'Loaded {self.model_path}')
    self.tags = pd.read_csv(self.tags_path)

  def interrogate(
      self,
      image: Image
  ) -> Tuple[
    Dict[str, float],  # rating confidents
    Dict[str, float]  # tag confidents
  ]:
    # init model
    if not hasattr(self, 'model') or self.model is None:
      self.load()

    # code for converting the image and running the model is taken from the link below
    # thanks, SmilingWolf!
    # https://huggingface.co/spaces/SmilingWolf/wd-v1-4-tags/blob/main/app.py

    # convert an image to fit the model
    _, height, _, _ = self.model.get_inputs()[0].shape
    print(f'height is {height}')
    # alpha to white
    image = convert_img(image, height)
    # evaluate model
    input_name = self.model.get_inputs()[0].name
    label_name = self.model.get_outputs()[0].name
    confidents = self.model.run([label_name], {input_name: image})[0]

    tags = self.tags[:][['name']]
    tags['confidents'] = confidents[0]

    # first 4 items are for rating (general, sensitive, questionable, explicit)
    ratings = dict(tags[:4].values)

    # rest are regular tags
    tags = dict(tags[4:].values)

    return ratings, tags
  


def tagger_images(model, image_files, instance_name, ignore_exists, ignore_exists_time, threshold):
  batch_num = len(image_files)
  for index, image_file in enumerate(image_files):
    # 如果是图片，只支持 png jpeg jpg
    file_name_no_ext = os.path.splitext(os.path.basename(image_file))[0]
    file_dir = os.path.dirname(image_file)
    txt_file_path = os.path.join(file_dir, f'{file_name_no_ext}{TXT_SUFFIX}')

    # 如果 ignore_exists=True 并且已经存在txt文件，则直接跳过
    if ignore_exists and os.path.exists(txt_file_path):
      if ignore_exists_time == '':
        continue
      elif ignore_exists_time != '':
        # time_str = "2023-05-21 10:30:00"
        # 比 time_threshold 更新的保留，直接跳过，即不会覆盖
        modification_time = os.path.getmtime(txt_file_path)
        time_threshold = time.mktime(time.strptime(ignore_exists_time, TIME_FORMAT_STR))

        if modification_time > time_threshold:
          print(f'file {txt_file_path} newer than ignore_exists_time skip!!!')
          continue

    tags = []
    if tags_white_list != None and len(tags_white_list) > 0:
      # 如果是做 tags level white list，可直接使用当前的 txt 文件做筛选即可，也不需要 threshold
      tags = read_tags_from_text_file(txt_file_path)
      print(f'=====================read_tags_from_text_file')
    else:
      tags = read_tags_from_image_file(model, image_file, threshold)
      print(f'=====================read_tags_from_image_file')

    tags_arr = []
    if instance_name != '':
      tags_arr.append(instance_name)
    for tag in tags:
      tags_arr.append(tag)
    tags_str = ', '.join(tags_arr)

    with open(txt_file_path, 'w') as file:
      print(f'{index+1} / {batch_num} write to txt_file: {txt_file_path}')
      file.write(tags_str)


def read_tags_from_image_file(model, image_file, threshold):
  tags = []
  try:
    image = Image.open(image_file)
    ratings, origin_tags = model.interrogate(image)
    tags = postprocess_tags(origin_tags, threshold=threshold)
    image.close()
  except UnidentifiedImageError:
    print(f'read tags from image error')
  return tags


def read_tags_from_text_file(txt_file):
  arr = load_prompts_arr(txt_file)
  new_arr = list(filter(lambda y: y in tags_white_list, arr))
  return new_arr

 
# 主入口函数
def main_entry(model, thread_num: int, data_dir, instance_name, ignore_exists, ignore_exists_time, threshold):
  image_files = []
  print(f"walk dir: {data_dir}")
  for dir, dirs, files in os.walk(data_dir):
    print(dir)
    for file in files:
      lower_file_name = file.lower()
      file_path = os.path.join(dir, file)
      # 如果是图片，只支持 png jpeg jpg
      if lower_file_name.endswith(PNG_SUFFIX) or lower_file_name.endswith(JPG_SUFFIX) or lower_file_name.endswith(JPEG_SUFFIX):
        print(f"file path is {file_path} lower name is {lower_file_name}")
        image_files.append(file_path)

  total_item_num = len(image_files)
  print(f"got total image num {total_item_num}")


  thread_arr = []
  for i in range(0, thread_num):
    thread_arr.append([])
  for j in range(0, total_item_num):
    # 初始化 batch_page_map
    thread_arr[j%thread_num].append(image_files[j])

  # print(thread_arr)

  # 创建线程池
  pool = ThreadPoolExecutor(max_workers=thread_num)
  futurelist = []
  for thread_items in thread_arr:
    futurelist.append(pool.submit(tagger_images, model, thread_items, instance_name, ignore_exists, ignore_exists_time, threshold))

  while True:
    # 检查 futurelist 状态
    all_done = True
    for future in futurelist:
      if not future.done():
        all_done = False
        break
        
    if all_done:
      # 如果所有线程任务都结束了
      # 整体去重前的统计数据
      print(f"all done! total_item_num({total_item_num})")
      pool.shutdown()
      break

    print(f"sleep for next checking futurelist")
    time.sleep(2)



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-t', '--thread_num', type=int, dest='thread_num', default=3)
  parser.add_argument('-im', '--image_path', type=str, dest='image_path', default='')
  parser.add_argument('-da', '--data_dir', type=str, dest='data_dir', default='')
  parser.add_argument('-in', '--instance_name', type=str, dest='instance_name', default='')
  parser.add_argument('-ig', '--ignore_exists', type=bool, dest='ignore_exists', default=False)
  parser.add_argument('-igt', '--ignore_exists_time', type=str, dest='ignore_exists_time', default='2023-05-30 10:30:00')
  parser.add_argument('-th', '--threshold', type=float, dest='threshold', default=0.35)
  parser.add_argument('-md', '--model_dir', type=str, dest='model_dir', default='./tagmodel/wd-v1-4-vit-tagger-v2')
  parser.add_argument('-lv', '--tags_level', type=int, dest='tags_level', default=0)
  args = parser.parse_args()
  thread_num = args.thread_num
  image_path = args.image_path  # 单图测试
  data_dir = args.data_dir
  instance_name = args.instance_name
  ignore_exists = args.ignore_exists # 如果提词文件已经存在，则跳过
  ignore_exists_time = args.ignore_exists_time # 如果提词文件已经存在，则比这个时间要新的跳过
  threshold = args.threshold # 如果提词文件已经存在，则比这个时间要新的跳过
  model_dir = args.model_dir # tagger model 所存放的位置
  tags_level = args.tags_level # tagger 词汇总表的级别，目前 0 和 9，越大的话词汇越少


  print('--------------------------------- tagger.py')
  print(f'ignore_exists: {ignore_exists}')

  # 参数校验
  if ignore_exists_time != '':
    try:
      time.strptime(ignore_exists_time, TIME_FORMAT_STR)
    except Exception as e:
      print(f"Params Error: --ignore_exists_time must be like '2023-05-30 10:30:00'")
      exit()
  print(f'ignore exists? [{ignore_exists}]')
  print(f'ignore_exists_time is {ignore_exists_time}')


  model_path = None
  tags_path = None
  level_path = None
  print(model_dir)
  if model_dir.startswith('./'):
    real_dir = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
    normal_dir = os.path.normpath(model_dir)
    model_path = os.path.join(real_dir, normal_dir, MODEL_NAME)
    tags_path = os.path.join(real_dir, normal_dir, TAGS_FILE_NAME)
    level_path = os.path.join(real_dir, normal_dir, f'{tags_level}.json')
    print(f'default model path is {model_path}')
  else:
    model_path = os.path.join(model_dir, MODEL_NAME)
    tags_path = os.path.join(model_dir, TAGS_FILE_NAME)
    level_path = os.path.join(model_dir, f'{tags_level}.json')
    print(f'input model path is {model_path}')

  if tags_level > 0 and os.path.exists(level_path):
    print(f'load level_path: {level_path} into tags_white_list')
    tags_white_list = load_json_data(level_path)
    print(f'white list: {tags_white_list}')

  model = WaifuDiffusionInterrogator(model_path=model_path, tags_path=tags_path)
  model.load()

  if image_path != '':
    image = Image.open(image_path)
    ratings, tags = model.interrogate(image)
    # result = [k for k, v in tags.items() if v >= 0.35]
    new_tags = postprocess_tags(tags, threshold=threshold)
    for item in new_tags:
      print(item)
    image.close()
  else:
    main_entry(model, thread_num, data_dir, instance_name, ignore_exists, ignore_exists_time, threshold)
