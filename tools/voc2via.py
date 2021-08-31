import xml.etree.ElementTree as ET
import json
import os
import string
import random
from tqdm import tqdm


def parse_voc_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()

    filename_node = root.find('filename')
    image_name = filename_node.text

    objects = root.findall('object')
    bboxes = []
    for obj in objects:
        cls = obj.find('name').text
        bbox_node = obj.find('bndbox')
        xmin = int(bbox_node.find('xmin').text)
        ymin = int(bbox_node.find('ymin').text)
        xmax = int(bbox_node.find('xmax').text)
        ymax = int(bbox_node.find('ymax').text)
        bboxes.append([cls, xmin, ymin, xmax, ymax])

    return image_name, bboxes


def parse(path):
    with open(path, 'r') as f:
        content = json.load(f)

    '''
        ['attribute', 'config', 'file', 'metadata', 'project', 'view']
    '''
    fname_dict = {}
    for vid in content['file'].keys():
        fname = content['file'][vid]['fname']
        fname_dict[fname] = vid

    obj_dict = {}

    '''
        {
            'av': {'1': '0'},    # category info
            'flg': 0, 
            'vid': '1',  
            'xy': [2, 208.171, 66.488, 386.265, 321.359], 
            'z': []
        }
    '''

    for obj_id in content['metadata'].keys():
        vid = content['metadata'][obj_id]['vid']
        pts = content['metadata'][obj_id]['xy']
        if obj_dict.get(vid) is None:
            obj_dict[vid] = [pts]
        else:
            obj_dict[vid].append(pts)


def fill_empty_json_with_voc_bbox(json_p, label_dict: dict, class_map: dict):
    with open(json_p, 'r') as f:
        content = json.load(f)
        f.close()

    """
        poly: 7
        rectangle: 2
    """

    # dict_keys(['project', 'config', 'attribute', 'file', 'metadata', 'view'])
    option_info = content['attribute']['1']['options']
    class_id_map = {}
    for i in option_info.keys():
        class_id_map[option_info[i]] = i

    fname_dict = {}
    for vid in content['file'].keys():
        fname_dict[content['file'][vid]['fname']] = vid

    '''
        {'1_ywe4vIqZ': {'vid': '1', 'flg': 0, 'z': [], 'xy': [7, 144.539, 74.441, 274.81, 81.264, 271.708, 124.688, 140.817, 117.864], 'av': {'1': '0'}}}
    '''
    chars = string.ascii_letters + string.digits
    chars = list(chars)

    cnt = 1
    for fname in tqdm(label_dict.keys()):
        labels = label_dict[fname]
        for label in labels:
            cls_name = class_map[label[0]]
            cls_id = class_id_map[cls_name]
            bbox = label[1:]
            x0 = int(bbox[0])
            y0 = int(bbox[1])
            w = int(bbox[2]) - int(bbox[0])
            h = int(bbox[3]) - int(bbox[1])

            vid = fname_dict[fname]
            random_s = ''
            for _ in range(8):
                random_s += random.choice(chars)
            new_tag = '{}_{}'.format(cnt, random_s)
            content['metadata'][new_tag] = {
                'vid': str(vid),
                'flg': 0,
                'z': [],
                'xy': [2, x0, y0, w, h],
                'av': {'1': cls_id}
            }

            # print(new_tag, content['metadata'][new_tag])
            cnt += 1

    with open(json_p, 'w+') as f:
        json.dump(content, f)


if __name__ == "__main__":
    a = 'xxx.json'
    label_dir = ['xxx/voc_labels']

    label_dict = {}

    cls_set = set()
    for ld in label_dir:
        for file in os.listdir(ld):
            f_path = os.path.join(ld, file)
            _, bboxes = parse_voc_xml(f_path)
            img_name = file.replace('xml', 'jpg')
            assert label_dict.get(img_name) is None
            label_dict[img_name] = bboxes
            for b in bboxes:
                cls_set.add(b[0])

    print(cls_set)
    label_map = {
        'A': 'a',
        "B": 'b',
        'C': 'c',
        'D': 'd'
    }

    fill_empty_json_with_voc_bbox(a, label_dict, label_map)
