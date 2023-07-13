# DanBooru IMage Utility functions

import numpy as np
from PIL import Image

def make_squar(img, target_size):
    old_size = img.size

    desired_size = max(old_size)
    desired_size = max(desired_size, target_size)

    delta_w = desired_size - old_size[0]
    delta_h = desired_size - old_size[1]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)


    color = (255, 255, 255)

    new_im = Image.new('RGB', (desired_size, desired_size), color)
    new_im.paste(img, (left, top))

    return new_im


def smart_resize(img, size):
    # Assumes the image has already gone through make_square
    if img.size[0] > size:
        img = img.resize((size, size), Image.LANCZOS) # LANCZOS vs AREA
        # img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
    elif img.size[0] < size:
        img = img.resize((size, size), Image.BICUBIC) 
        # img = cv2.resize(img, (size, size), interpolation=cv2.INTER_CUBIC)
    return img