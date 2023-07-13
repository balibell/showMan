import random
import string
import os
import sys
from datetime import datetime

PNG_SUFFIX = '.png'  
JPG_SUFFIX = '.jpg' 
JPEG_SUFFIX = '.jpeg' 
TXT_SUFFIX = '.txt'

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    result = ''.join(random.choice(letters) for _ in range(length))
    return result

random_string = generate_random_string(16)



def walk_and_rename(directory, usetime):
  for dir, dirs, files in os.walk(directory):
    for file in files:
      if file.lower().endswith(PNG_SUFFIX) or file.lower().endswith(JPG_SUFFIX) or file.lower().endswith(JPEG_SUFFIX):
        fpath = os.path.join(dir, file)
        fname = os.path.splitext(file)[0]
        ext = os.path.splitext(file)[1]
        txt_fname = f"{fname}{TXT_SUFFIX}"
        txt_fpath = os.path.join(dir, txt_fname)

        formatted_date = datetime.now().strftime("%Y%m%d")[2:]
        random_str = generate_random_string(8)
        new_fname = f'{formatted_date}_{random_str}' if usetime else random_str
        new_fpath = os.path.join(dir, f"{new_fname}{ext}")
        new_txt_fpath = os.path.join(dir, f"{new_fname}{TXT_SUFFIX}")
        print(f"new path is {new_fpath}")


        os.rename(fpath, new_fpath)
        if os.path.isfile(txt_fpath):
          os.rename(txt_fpath, new_txt_fpath)

if __name__ == "__main__":
    dir = sys.argv[1]
    usetime = int(sys.argv[2])
    walk_and_rename(dir, usetime)