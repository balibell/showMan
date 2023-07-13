import pyinotify
import os
import sys
import subprocess
import shutil

EXT_SAFETENSORS='.safetensors'
EXT_CKPT='.ckpt'
EXT_JSON='.json'

CONFIRM_EDITMAP='confirmEditMap'
CONFIRM_DELETE='confirmDelete'

#***** 不支持 mac arm64
#***** 不需要支持 mac 因为最终是在服务器上运行

# 自定义事件处理类
class EventHandler(pyinotify.ProcessEvent, pyinotify.WatchManager):
  def __init__(self, path, wm, mask):
    self.path = path
    self.watchManager = wm
    self.mask = mask
  def process_default(self, event):
    # 处理文件变化事件
    filepath = event.pathname
    if not event.dir:
      print(f"file changed {filepath}")
      if filepath.endswith(EXT_SAFETENSORS) or filepath.endswith(EXT_CKPT):
        do_copy_model(filepath)
    else:
      dir_exists = os.path.exists(filepath)
      if dir_exists:
        print(f"dir changed {filepath}")
        self.watchManager.add_watch(self.path, self.mask, rec=True)




def do_copy_model(file):
  dirname = os.path.basename(os.path.dirname(file))
  target_dir = f'/home/admin/models/train/{dirname}'
  if 'network' in file:
    target_dir = f'/home/admin/lora/train/{dirname}'

  filename = os.path.basename(file)
  mvfile = os.path.join(target_dir, filename)
  shutil.move(file, mvfile)

  # 执行 scp 命令
  if 'network' in file:
    try:
      command = f"scp {mvfile} 44://{target_dir}/{filename}"
      print(command)
      subprocess.run(command, shell=True, check=True)
      print("SCP 命令执行成功")
    except subprocess.CalledProcessError as e:
      print(f"SCP 命令执行失败: {e}")




if __name__ == "__main__":
  path = sys.argv[1]

  # 创建 inotify 实例
  wm = pyinotify.WatchManager()

  # 添加要监听的事件类型
  # mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_DELETE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO
  mask = pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO

  # 创建事件处理器实例
  event_handler = EventHandler(path, wm, mask)

  wm.add_watch(path, mask, rec=True)

  # 创建 notifier 实例
  notifier = pyinotify.Notifier(wm, event_handler)

  # 启动监听
  notifier.loop()

