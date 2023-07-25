import sys
import cv2
import numpy as np
import shutil
from skimage.metrics import structural_similarity as ssim
from skimage import io
from PIL import Image
import os

PNG_SUFFIX = '.png'  
JPG_SUFFIX = '.jpg' 
JPEG_SUFFIX = '.jpeg' 
TXT_SUFFIX = '.txt'


prompts_file_map = {}



image_file_list = []
np_image_list = []
handled_set = set()

def load_string_data(path):
  # 读取文件
  with open(path, 'r') as f:
    content = f.read()
  return content

def load_prompts_arr(path):
  if os.path.exists(path):
    pstr = load_string_data(path)
    print(f"pstr in trimSameImage.py is {pstr}")
    parr = pstr.split(',')
    prompts_arr = list(filter(lambda y: y != '', list(map(lambda x: x.strip(), parr))))
    return prompts_arr
  return []


def crop_center_square(image):
  width, height = image.size
  size = min(width, height)
  left = (width - size) // 2
  top = (height - size) // 2
  right = left + size
  bottom = top + size
  return image.crop((left, top, right, bottom))


def resize_image(image, size):
  (width, height) = image.size
  max_size = max(width, height)
  if max_size < size[0] or max_size < size[1]:
    ratio = size[0] / max_size
    new_width = int(width * ratio)
    new_height = int(height * ratio)
    image = image.resize((new_width, new_height))
  image.thumbnail(size)
  return image

def check_prompts_similarity(prompts1, prompts2, threshold):
  len1 = len(prompts1)
  len2 = len(prompts2)

  prompts_min = []
  prompts_max = []
  if len1 < len2:
    prompts_min = prompts1
    prompts_max = prompts2
  else:
    prompts_min = prompts2
    prompts_max = prompts1

  miss_num = 0
  for pro_min in prompts_min:
    if miss_num > threshold:
      break
    if not pro_min in prompts_max:
      miss_num += 1
  return miss_num <= threshold



def check_image_similarity(image1, image2, threshold):
  image_center1 = crop_center_square(image1)
  image_center2 = crop_center_square(image2)

  (width1, height1) = image_center1.size
  (width2, height2) = image_center2.size

  big_center = None
  small_center = None
  if width1 < width2:
    big_center = image_center2
    small_center = image_center1
  else:
    big_center = image_center1
    small_center = image_center2

  # 将 big 图缩略成 small 图
  (width_small, height_small) = small_center.size
  big_center = resize_image(big_center, (width_small, height_small) )

  np_image1 = np.array(big_center)
  np_image2 = np.array(small_center)

  # 转换为灰度图像
  cvt_image1 = cv2.cvtColor(np_image1, cv2.COLOR_BGR2GRAY)
  cvt_image2 = cv2.cvtColor(np_image2, cv2.COLOR_BGR2GRAY)

  # 计算结构相似性指数
  similarity = ssim(cvt_image1, cvt_image2)
  return similarity >= threshold

def is_normal_image(file):
  lower_file = file.lower()
  return lower_file.endswith(PNG_SUFFIX) or lower_file.endswith(JPG_SUFFIX) or lower_file.endswith(JPEG_SUFFIX)

def is_text_file(file):
  lower_file = file.lower()
  return lower_file.endswith(TXT_SUFFIX)

def cache_images_in_memery(image_dir):
  for file in os.listdir(image_dir):
    file_path = os.path.join(image_dir, file)
    if is_normal_image(file):
      # 将图片读入内存
      image = Image.open(file_path)
      image_rgb = image.convert('RGB')

      np_image = np.array(image_rgb)
      image_file_list.append(file_path)
      np_image_list.append(np_image)
      image.close()
      image_rgb.close()

def cache_prompts_in_memery(image_dir):
  for file in os.listdir(image_dir):
    if is_text_file(file):
      # 提词信息
      file_path = os.path.join(image_dir, file)
      fname = os.path.splitext(file)[0]
      prompts_arr = load_prompts_arr(file_path)
      prompts_file_map[fname] = prompts_arr

      

def loop_images_in_memery(image_dir, out_dir, threshold):
  for index, np_image in enumerate(np_image_list):
    if index in handled_set:
      continue
    has_sim = False
    for j in range(index + 1, len(np_image_list)):
      if j in handled_set:
        continue
      image_j = Image.fromarray(np_image_list[j])
      image_index = Image.fromarray(np_image)
      sim = check_image_similarity(image_j, image_index, threshold)
      # print(f'sim is {sim}')
      if sim >= threshold:
        has_sim = True
        # 移动文件到指定目录
        file_path_j = image_file_list[j]
        file_name_j = os.path.basename(file_path_j)
        fname_j = os.path.splitext(file_name_j)[0]
        target_file_j = os.path.join(out_dir, file_name_j)
        print(f'shutil.copy {file_path_j} to {target_file_j}')
        shutil.copy(file_path_j, target_file_j)

        txt_file_name_j = f'{fname_j}{TXT_SUFFIX}'
        txt_file_path_j = os.path.join(image_dir, txt_file_name_j)
        if os.path.exists(txt_file_path_j):
          target_txt_file_path_j = os.path.join(out_dir, txt_file_name_j)
          shutil.copy(txt_file_path_j, target_txt_file_path_j)


        handled_set.add(j)

    # 最后处理第一层循环的 index
    if has_sim:
      file_path_i = image_file_list[index]
      file_name_i = os.path.basename(file_path_i)
      fname_i = os.path.splitext(file_name_i)[0]
      target_file_i = os.path.join(out_dir, file_name_i)
      shutil.copy(file_path_i, target_file_i)

      txt_file_name_i = f'{fname_i}{TXT_SUFFIX}'
      txt_file_path_i = os.path.join(image_dir, txt_file_name_i)
      if os.path.exists(txt_file_path_i):
        target_txt_file_path_i = os.path.join(out_dir, txt_file_name_i)
        shutil.copy(txt_file_path_i, target_txt_file_path_i)

  return



def loop_files(image_dir, tmp_dir, out_dir, threshold, prompts_miss_num):
  file_list = os.listdir(image_dir)
  total_size = len(file_list)
  num = 0
  for i, file_i in enumerate(file_list):
    is_image = is_normal_image(file_i)
    if is_image:
      num += 1
      file_path_i = os.path.join(image_dir, file_i)
      if i not in handled_set:
        has_sim = False
        for j in range(i + 1, total_size):
          file_j = file_list[j]

          if is_normal_image(file_j):
            file_path_j = os.path.join(image_dir, file_j)
            # print(f'file jjj path is {file_path_j}')
            
            fname_i = os.path.splitext(file_i)[0]
            fname_j = os.path.splitext(file_j)[0]

            prompts_simi = True
            if fname_i in prompts_file_map and fname_j in prompts_file_map:
              prompts_i = prompts_file_map[fname_i]
              prompts_j = prompts_file_map[fname_j]
              prompts_simi = check_prompts_similarity(prompts_i, prompts_j, prompts_miss_num)
            if prompts_simi:
              # print(f'two prompts similar i:{file_i} j:{file_j}')

              # 如果 prompts 提词相同，则进一步判断图片是否相似
              image_i = Image.open(file_path_i)
              image_j = Image.open(file_path_j)
              image_i_width, image_i_height = image_i.size
              image_j_width, image_j_height = image_j.size

              image_whratio_i = image_i_width / image_i_height
              image_whratio_j = image_j_width / image_j_height
              if abs(image_whratio_i - image_whratio_j) < 0.1:
                image_simi = check_image_similarity(image_i.convert('RGB'), image_j.convert('RGB'), threshold)
                if image_simi:
                  # print(f'two images similar i:{file_i} j:{file_j}')
                  has_sim = True
                  # 移动文件到指定目录
                  target_file_path_j = os.path.join(out_dir, file_j)
                  shutil.copy(file_path_j, target_file_path_j)

                  txt_file_name_j = f'{fname_j}{TXT_SUFFIX}'
                  txt_file_path_j = os.path.join(image_dir, txt_file_name_j)
                  if os.path.exists(txt_file_path_j):
                    target_txt_file_path_j = os.path.join(out_dir, txt_file_name_j)
                    shutil.copy(txt_file_path_j, target_txt_file_path_j)


                  handled_set.add(j)
                image_i.close()
                image_j.close()

        # 最后处理第一层循环的 index
        if has_sim:
          target_file_path_i = os.path.join(out_dir, file_i)
          shutil.copy(file_path_i, target_file_path_i)

          txt_file_name_i = f'{fname_i}{TXT_SUFFIX}'
          txt_file_path_i = os.path.join(image_dir, txt_file_name_i)
          if os.path.exists(txt_file_path_i):
            target_txt_file_path_i = os.path.join(out_dir, txt_file_name_i)
            shutil.copy(txt_file_path_i, target_txt_file_path_i)



      # 将第一层遍历结束的图片移动到 tmp 目录，节约下一次循环时间
      tmp_file_path_i = os.path.join(tmp_dir, file_i)
      shutil.move(file_path_i, tmp_file_path_i)
      print(f'first level loop num: {num}')

  return


def main_entry(use_image_memery, image_dir, tmp_dir, out_dir, threshold, prompts_miss_num):
  if use_image_memery:
    cache_images_in_memery(image_dir)
    loop_images_in_memery(image_dir, out_dir, threshold)
  else:
    cache_prompts_in_memery(image_dir)
    loop_files(image_dir, tmp_dir, out_dir, threshold, prompts_miss_num)
  return


# python trimSameImage.py '' ./duplicate/asiangirl/selected_01/ ./duplicate/asiangirl/selected_01_tmp ./duplicate/asiangirl/selected_01_dup 0.8 1
# 对单级目录里的图片进行相似度对比，如果是相似图片会 copy 到指定目录 out_dir
if __name__ == "__main__":
  use_image_memery = bool(sys.argv[1])
  image_dir = sys.argv[2]
  tmp_dir = sys.argv[3]
  out_dir = sys.argv[4]
  threshold = float(sys.argv[5])
  prompts_miss_num = int(sys.argv[6])

  print(f'use_image_memery: {use_image_memery}')

  # 不能直接比较，因为尺寸不对，需要先居中裁剪，然后将大图缩略到小图的尺寸进行比较
  main_entry(use_image_memery, image_dir, tmp_dir, out_dir, threshold, prompts_miss_num)