import json
import os
import cv2
import numpy as np


def do():
    json_file = "/workspace/meters/data/two_meters/Segment_DBNet/dongfeng/images_480_refine.json"
    save_dir = "/workspace/meters/data/two_meters/Segment_DBNet/dongfeng/labels_480_refine"
    os.makedirs(save_dir, exist_ok=True)

    with open(json_file, 'r') as f:
        content = json.load(f)
        f.close()

    fname_dict = {}
    ann_dict = {}

    for vid in content['file'].keys():
        fname_dict[vid] = content['file'][vid]['fname']

    for tag in content['metadata'].keys():
        vid = content['metadata'][tag]['vid']
        poly = content['metadata'][tag]['xy'][1:]
        poly = [int(p) for p in poly]
        if ann_dict.get(vid) is None:
            ann_dict[vid] = [poly]
        else:
            ann_dict[vid].append(poly)


    for vid in fname_dict.keys():
        fname = fname_dict[vid]
        with open(os.path.join(save_dir, fname.replace('jpg', 'txt')), 'w+') as f:
            cnt = 0
            for poly in ann_dict[vid]:
                s = ''
                for p in poly:
                    s += str(p)
                    s += ','
                s += 'cao\n'
                f.write(s)
                cnt += 1
            assert cnt == 3, fname
            f.close()

    print('done')


def draw():
    img_p = "/workspace/meters/data/two_meters/Segment_DBNet/dongfeng/images_480/0024.jpg"
    label_p = "/workspace/meters/data/two_meters/Segment_DBNet/dongfeng/labels_480_refine/0024.txt"
    image = cv2.imread(img_p)
    with open(label_p, 'r') as f:
        for line in f.readlines():
            poly = line.split(',')[:-1]
            poly = np.array(poly, dtype=np.float).astype(np.int).reshape([4, 2])
            cv2.polylines(image, [poly], True, (0, 0, 255), thickness=2)

    cv2.imwrite('/workspace/meters/data/two_meters/Segment_DBNet/dongfeng/debug.jpg', image)

def modify_list():
    a = "/workspace/meters/data/two_meters/Segment_DBNet/train_pad1d5.list"
    b = "/workspace/meters/data/two_meters/Segment_DBNet/train_pad1d5_refine.list"
    new_lines = []
    with open(a, 'r') as f:
        for line in f.readlines():
            if "/labels_480" in line:
                temp = line.replace('/labels_480', '/labels_480_refine')
                new_lines.append(temp)
            else:
                new_lines.append(line)
        f.close()

    with open(b, 'w+') as f:
        for n in new_lines:
            f.write(n)

    print('done')

if __name__ == "__main__":
    modify_list()
