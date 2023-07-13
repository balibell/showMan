import json
from time import sleep
import os
import win32clipboard
import win32con


CONFIRM_DELETE = 'confirmDelete.json'
CONFIRM_EDIT_MAP = 'confirmEditMap.json'
CONFIRM_CROPPED = 'confirmCropped.txt'

def load_string_data(path):
  # 读取文件
  with open(path, 'r') as f:
    content = f.read()
  return content

def load_json_data(path):
  data = None
  # 读取JSON文件
  with open(path, 'r') as f:
    data = json.load(f)
  return data

def main_entry():
  old_delete_array = load_json_data(CONFIRM_DELETE)
  old_edit_map = load_json_data(CONFIRM_EDIT_MAP)

  oldstr = ''
  while True:
    try:

      # win32clipboard.OpenClipboard()
      # pbstring = win32clipboard.GetClipboardData()
      # win32clipboard.CloseClipboard()

      pbstring = None
      win32clipboard.OpenClipboard()
      if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
        pbstring = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        print("剪贴板中的文本:", pbstring)
      else:
        print("剪贴板中不包含文本格式的数据")
      win32clipboard.CloseClipboard()



      if pbstring != None and pbstring != oldstr and 'modifymap' in pbstring:
        oldstr = pbstring
        json_obj = json.loads(pbstring)

        cropstr = load_string_data(CONFIRM_CROPPED)
        croparr = cropstr.split('\n')
        cropset = set(croparr)
        cropset = {x for x in cropset if x.strip()}


        json_arr = json_obj['singleclicked']
        if json_arr != None and type(json_arr) == list and len(json_arr) > 0:
          old_delete_array = list(set(json_arr).union(set(old_delete_array)))
          with open(CONFIRM_DELETE, 'w') as file:
            json.dump(old_delete_array, file)

        json_map = json_obj['modifymap']
        if json_map != None and len(json_map) > 0:
          print(f'bali json map found')
          old_edit_map.update(json_map)
          with open(CONFIRM_EDIT_MAP, 'w') as file:
            json.dump(old_edit_map, file)

          cropchange = False

          for map_key, map_value in json_map.items():
            if 'crop_arr_1' in map_value or 'crop_arr_2' in map_value:
              cropset.add(map_key)
              cropchange = True
          
          if cropchange:
            # 打开文件，如果文件不存在则创建
            joinedstr = '\n'.join(list(cropset))
            with open(CONFIRM_CROPPED, 'w') as f:
              # 写入字符串到文件
              f.write(joinedstr)
        
          # 清除剪贴板
          win32clipboard.OpenClipboard()
          win32clipboard.EmptyClipboard()
          win32clipboard.CloseClipboard()
    except Exception as error:
      print(error)
    sleep(1)



if __name__ == "__main__":
  main_entry()
  

