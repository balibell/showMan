import sys
import os
import argparse
import shutil
import json


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

# deprecated
def do_generate_propmt_file(path, prompt, class_name):
  for filename in os.listdir(path):
    fname = os.path.splitext(filename)[0]
    if not filename.startswith('.'):
      if is_normal_image(filename):
        txtfilepath = '%s/%s%s' % (path, fname, TXT_SUFFIX)
        print('new file path is %s' % txtfilepath)
        # 打开一个文件，并以写入模式打开
        with open(txtfilepath, 'w') as file:
          file.write('photo of %s %s' % (prompt, class_name))

# deprecated
def do_check_path(path, move_dir):
  for filename in os.listdir(path):
    filepath = '%s/%s' % (path, filename)
    fname = os.path.splitext(filename)[0]
    if not filename.startswith('.'):
      if is_normal_image(filename):
        txtfilepath = '%s/%s%s' % (path, fname, TXT_SUFFIX)
        if not os.path.exists(txtfilepath):
          # 如果图片对应的文本文件不存在
          print(f"txt file not found for img {filename}")

          # move to
          if move_dir != '':
            shutil.move(filepath, os.path.join(move_dir,filename))
      elif is_text_file(filename):
        if not os.path.exists(f"{path}/{fname}{PNG_SUFFIX}") and not os.path.exists(f"{path}/{fname}{JPEG_SUFFIX}") and not os.path.exists(f"{path}/{fname}{JPG_SUFFIX}"):
          # 如果文本文件对应的图片不存在
          print(f"image file not found for txt {filename}")

# deprecated
def do_check_lossimg(inpath, outpath, move_dir):
  for filename in os.listdir(inpath):
    fname = os.path.splitext(filename)[0]
    if not filename.startswith('.'):
      if is_normal_image(filename):
        outfilepath = '%s/%s%s' % (outpath, fname, PNG_SUFFIX)
        if not os.path.exists(outfilepath):
          # 如果outpath对应的图片不存在
          print(f"image file not found in outpath {filename}")

          # move to
          if move_dir != '':
            infilepath = '%s/%s' % (inpath, filename)
            shutil.move(infilepath, os.path.join(move_dir,filename))
            print(f"move image file {infilepath}")


            txtfname = '%s%s' % (fname, TXT_SUFFIX)
            txtfilepath = '%s/%s' % (inpath, txtfname)
            if os.path.exists(txtfilepath):
              print(f"move txt file {txtfilepath}")
              shutil.move(txtfilepath, os.path.join(move_dir,txtfname))


# 6月download 女性数据时，只拷贝了一半，所以写了这个脚本把剩下的一半分离出来重新下载，而不是全量下载
# 此方法将 data_file 读取为 json 数组，遍历这个数组找到 img_dir 下这些图片，转移到另一个目录，起到分离的效果
# 传入的 data_file 可以是一个 metadata.json (showMan 里一直用的)，也可以是一个字符串数组，字符串即文件相对路径
def seperate_images(data_file, img_dir, out_dir):
  with open(data_file) as json_data:
    json_data_arr = json.load(json_data)
    
  for json_item in json_data_arr:
    img_file = json_item if isinstance(json_item, str) else json_item['file_name']
    img_path = os.path.join(img_dir, img_file)
    print(f'img_file is {img_file} img_path is {img_path}')
    if os.path.exists(img_path):
      print(img_path)
      dest_img_path = os.path.join(out_dir, img_file)
      # 如果 dest 路径不存在，则创建
      dest_directory = os.path.dirname(dest_img_path)
      if not os.path.exists(dest_directory):
        os.makedirs(dest_directory)
      shutil.copy2(img_path, dest_img_path)


if __name__ == "__main__":
  # create parser
  parser = argparse.ArgumentParser()
  parser.add_argument('-da', '--data_file', type=str, dest='data_file', default='')
  parser.add_argument('-dr', '--dir', type=str, dest='dir', default='')
  parser.add_argument('-od', '--out_dir', type=str, dest='out_dir', default='')

  args = parser.parse_args()
  data_file = args.data_file
  dir = args.dir
  out_dir = args.out_dir

  seperate_images(data_file, dir, out_dir)

