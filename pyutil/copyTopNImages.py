import sys
import shutil
import os

PNG_SUFFIX = '.png'  
JPG_SUFFIX = '.jpg' 
JPEG_SUFFIX = '.jpeg' 
TXT_SUFFIX = '.txt'


def is_normal_image(file):
  lower_file = file.lower()
  return lower_file.endswith(PNG_SUFFIX) or lower_file.endswith(JPG_SUFFIX) or lower_file.endswith(JPEG_SUFFIX)

def is_text_file(file):
  lower_file = file.lower()
  return lower_file.endswith(TXT_SUFFIX)


def main_entry(image_dir, out_dir, top_n):
  file_list = os.listdir(image_dir)
  num = 0
  for i, file_i in enumerate(file_list):
    if num >= top_n:
      break

    is_image = is_normal_image(file_i)
    if is_image:
      num += 1
      file_path_i = os.path.join(image_dir, file_i)
      target_file_path_i = os.path.join(out_dir, file_i)
      shutil.copy(file_path_i, target_file_path_i)

      fname_i = os.path.splitext(file_i)[0]
      txt_file_name_i = f'{fname_i}{TXT_SUFFIX}'
      txt_file_path_i = os.path.join(image_dir, txt_file_name_i)
      if os.path.exists(txt_file_path_i):
        target_txt_file_path_i = os.path.join(out_dir, txt_file_name_i)
        shutil.copy(txt_file_path_i, target_txt_file_path_i)
  return


# python copyTopNImages.py /home/admin/github/class/bra_girl_512_682 /home/admin/github/class/bra_girl_512_682_new 400
# 将一个目录里面的前400张图拷贝到新目录里去
if __name__ == "__main__":
  image_dir = sys.argv[1]
  out_dir = sys.argv[2]
  top_n = float(sys.argv[3])

  if not os.path.exists(out_dir):
    os.makedirs(out_dir)

  # 不能直接比较，因为尺寸不对，需要先居中裁剪，然后将大图缩略到小图的尺寸进行比较
  main_entry(image_dir, out_dir, top_n)