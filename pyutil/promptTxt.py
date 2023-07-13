import sys
import os
import argparse
import shutil

PNG_SUFFIX = '.png'  
JPG_SUFFIX = '.jpg' 
JPEG_SUFFIX = '.jpeg' 
TXT_SUFFIX = '.txt'

def do_generate_propmt_file(path, prefix, prompt, class_name):
  for filename in os.listdir(path):
    fname = os.path.splitext(filename)[0]
    if not filename.startswith('.'):
      if filename.lower().endswith(PNG_SUFFIX) or filename.lower().endswith(JPG_SUFFIX) or filename.lower().endswith(JPEG_SUFFIX):
        txtfilepath = '%s/%s%s' % (path, fname, TXT_SUFFIX)
        print('new file path is %s' % txtfilepath)
        # 打开一个文件，并以写入模式打开
        with open(txtfilepath, 'w') as file:
          file.write('%s %s %s' % (prefix, prompt, class_name))

def do_check_path(path, move_dir):
  for filename in os.listdir(path):
    filepath = '%s/%s' % (path, filename)
    fname = os.path.splitext(filename)[0]
    if not filename.startswith('.'):
      if filename.lower().endswith(PNG_SUFFIX) or filename.lower().endswith(JPG_SUFFIX) or filename.lower().endswith(JPEG_SUFFIX):
        txtfilepath = '%s/%s%s' % (path, fname, TXT_SUFFIX)
        if not os.path.exists(txtfilepath):
          # 如果图片对应的文本文件不存在
          print(f"txt file not found for img {filename}")

          # move to
          if move_dir != '':
            shutil.move(filepath, os.path.join(move_dir,filename))
      elif filename.lower().endswith(TXT_SUFFIX):
        if not os.path.exists(f"{path}/{fname}{PNG_SUFFIX}") and not os.path.exists(f"{path}/{fname}{JPEG_SUFFIX}") and not os.path.exists(f"{path}/{fname}{JPG_SUFFIX}"):
          # 如果文本文件对应的图片不存在
          print(f"image file not found for txt {filename}")



def do_check_lossimg(inpath, outpath, move_dir):
  for filename in os.listdir(inpath):
    fname = os.path.splitext(filename)[0]
    if not filename.startswith('.'):
      if filename.lower().endswith(PNG_SUFFIX) or filename.lower().endswith(JPG_SUFFIX) or filename.lower().endswith(JPEG_SUFFIX):
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





if __name__ == "__main__":
  # create parser
  parser = argparse.ArgumentParser()
  parser.add_argument('-pa', '--path', type=str, dest='path', default='')
  parser.add_argument('-pr', '--prefix', type=str, dest='prefix', default='')
  parser.add_argument('-pp', '--prompt', type=str, dest='prompt', default='')
  parser.add_argument('-cl', '--class_name', type=str, dest='class_name', default='')
  parser.add_argument('-ck', '--check', dest='check', default=False)
  parser.add_argument('-lc', '--loss_check', dest='loss_check', default=False)
  parser.add_argument('-po', '--path_out', type=str, dest='path_out', default='')
  parser.add_argument('-md', '--move_dir', type=str, dest='move_dir', default='')


  args = parser.parse_args()
  path = args.path
  prefix = args.prefix
  prompt = args.prompt
  class_name = args.class_name
  check = args.check
  loss_check = args.loss_check
  path_out = args.path_out
  move_dir = args.move_dir

  if path != '' and check:
    do_check_path(path, move_dir)
  elif path != '' and path_out != '' and loss_check:
    do_check_lossimg(path, path_out, move_dir)
  elif path != '':
    do_generate_propmt_file(path, prefix, prompt, class_name)
