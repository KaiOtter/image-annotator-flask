import os
import json
import string
import random

import cv2
import numpy as np


def fill_json():
    json_p = "/workspace/meters/data/two_meters/Segment_DBNet/dongfeng/images_480_refine.json"
    with open(json_p, 'r') as f:
        content = json.load(f)
        f.close()

    fname_dict = {}
    for vid in content['file'].keys():
        fname_dict[content['file'][vid]['fname']] = vid

    '''
        {'1_ywe4vIqZ': {'vid': '1', 'flg': 0, 'z': [], 'xy': [7, 144.539, 74.441, 274.81, 81.264, 271.708, 124.688, 140.817, 117.864], 'av': {'1': '0'}}}
    '''
    chars = string.ascii_letters + string.digits
    chars = list(chars)

    label_dir = "/workspace/meters/data/two_meters/Segment_DBNet/dongfeng/labels_480"
    cnt = 2
    for file in os.listdir(label_dir):
        with open(os.path.join(label_dir, file), 'r') as f:
            lines = f.readlines()
            f.close()
        for line in lines:
            poly = line.split(',')[:8]
            poly = [float(p) for p in poly]
            fname = file.replace('txt', 'jpg')
            vid = fname_dict[fname]
            random_s = ''
            for _ in range(8):
                random_s += random.choice(chars)
            new_tag = '{}_{}'.format(cnt, random_s)
            content['metadata'][new_tag] = {'vid': str(vid), 'flg': 0, 'z': [],
                                            'xy': [7] + poly, 'av': {'1': '0'}}
            cnt += 1
    with open(json_p, 'w+') as f:
        json.dump(content, f)

if __name__ == "__main__":
    # fill_json()
    # a = './src/pic/load_src.png'
    # import cv2
    #
    # image = cv2.imread(a)
    # image = cv2.resize(image, (24, 24))
    # cv2.imwrite('./src/pic/load.png', image)

    root = './sample/images'
    cnt = 1
    for img in os.listdir(root):
        image = cv2.imread(os.path.join(root, img))
        if image.shape[0] > 800:
            image = cv2.resize(image, None, fx=0.5, fy=0.5)

        cv2.imwrite(os.path.join(root, str(cnt).zfill(2) + '.jpg'), image)
        cnt += 1
