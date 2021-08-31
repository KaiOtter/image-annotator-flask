import xml.etree.ElementTree as ET
import json
import os
import string
import random

import cv2
from tqdm import tqdm


def create_voc_xml(save, fname, objects, dir_name, W, H, D=3):
    root = ET.Element('annotation')
    root.text = '\n\t'
    tree = ET.ElementTree(root)

    folder_node = ET.Element('folder')
    folder_node.text = dir_name
    folder_node.tail = '\n\t'
    root.append(folder_node)

    filename_node = ET.Element('filename')
    filename_node.text = fname
    filename_node.tail = '\n\t'
    root.append(filename_node)

    path_node = ET.Element('path')
    path_node.text = os.path.join(dir_name, fname)
    path_node.tail = '\n\t'
    root.append(path_node)

    source_node = ET.Element('source')
    source_node.tail = '\n\t'
    source_node.text = '\n\t\t'
    database_node = ET.Element('database')
    database_node.text = 'Unknown'
    database_node.tail = '\n\t'
    source_node.append(database_node)
    root.append(source_node)

    '''
        <size>
            <width>1920</width>
            <height>1080</height>
            <depth>3</depth>
	    </size>
    '''

    size_node = ET.Element('size')
    size_node.text = '\n\t\t'
    size_node.tail = '\n\t'
    width_node = ET.Element('width')
    width_node.text = str(W)
    width_node.tail = '\n\t\t'
    height_node = ET.Element('height')
    height_node.text = str(H)
    height_node.tail = '\n\t\t'
    depth_node = ET.Element('depth')
    depth_node.text = str(D)
    depth_node.tail = '\n\t'
    size_node.append(width_node)
    size_node.append(height_node)
    size_node.append(depth_node)
    root.append(size_node)

    segmented_node = ET.Element('segmented')
    segmented_node.text = '0'
    segmented_node.tail = '\n\t'
    root.append(segmented_node)

    for idx, obj in enumerate(objects):
        obj_node = ET.Element('object')
        obj_node.text = '\n\t\t'
        if idx < len(objects) - 1:
            obj_node.tail = '\n\t'
        else:
            obj_node.tail = '\n'
        root.append(obj_node)

        n_node = ET.Element('name')
        n_node.text = obj[0]
        n_node.tail = '\n\t\t'
        obj_node.append(n_node)

        p_node = ET.Element('pose')
        p_node.text = 'Unspecified'
        p_node.tail = '\n\t\t'
        obj_node.append(p_node)

        t_node = ET.Element('truncated')
        t_node.text = '0'
        t_node.tail = '\n\t\t'
        obj_node.append(t_node)

        d_node = ET.Element('difficult')
        d_node.text = '0'
        d_node.tail = '\n\t\t'
        obj_node.append(t_node)

        bnb_node = ET.Element('bndbox')
        bnb_node.text = '\n\t\t\t'
        bnb_node.tail = '\n\t'
        obj_node.append(bnb_node)

        xmin_node = ET.Element('xmin')
        xmin_node.text = str(int(obj[1]))
        xmin_node.tail = '\n\t\t\t'
        ymin_node = ET.Element('ymin')
        ymin_node.text = str(int(obj[2]))
        ymin_node.tail = '\n\t\t\t'
        xmax_node = ET.Element('xmax')
        xmax_node.text = str(int(obj[3]))
        xmax_node.tail = '\n\t\t\t'
        ymax_node = ET.Element('ymax')
        ymax_node.text = str(int(obj[4]))
        ymax_node.tail = '\n\t\t'
        bnb_node.append(xmin_node)
        bnb_node.append(ymin_node)
        bnb_node.append(xmax_node)
        bnb_node.append(ymax_node)

    tree.write(save, encoding="utf-8", xml_declaration=False)


def via_to_voc_bnbbox(json_p: str, image_root: str, save_dir: str, class_map: dict):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)

    with open(json_p, 'r') as f:
        content = json.load(f)
        f.close()

    """
        poly: 7
        rectangle: 2
    """

    # dict_keys(['project', 'config', 'attribute', 'file', 'metadata', 'view'])
    class_name_map = content['attribute']['1']['options']

    # fname_dict = {}
    # for vid in content['file'].keys():
    #     fname_dict[content['file'][vid]['fname']] = vid

    '''
        {'1_ywe4vIqZ': {'vid': '1', 'flg': 0, 'z': [], 'xy': [7, 144.539, 74.441, 274.81, 81.264, 271.708, 124.688, 140.817, 117.864], 'av': {'1': '0'}}}
    '''

    obj_dict = {}
    for o in content['metadata'].keys():
        vid = content['metadata'][o]['vid']
        fname = content['file'][vid]['fname']
        cls_id = content['metadata'][o]['av']['1']
        cls_name = class_map[class_name_map[cls_id]]
        bbox = content['metadata'][o]['xy'][1:]
        x0 = bbox[0]
        y0 = bbox[1]
        x1 = bbox[0] + bbox[2]
        y1 = bbox[1] + bbox[3]

        x0 = int(x0)
        y0 = int(y0)
        x1 = int(x1)
        y1 = int(y1)

        if obj_dict.get(fname) is None:
            obj_dict[fname] = [[cls_name, x0, y0, x1, y1]]
        else:
            obj_dict[fname].append([cls_name, x0, y0, x1, y1])

    for fname in tqdm(obj_dict.keys()):
        save = os.path.join(save_dir, fname.replace('jpg', 'xml'))

        # save, fname, dir_name, W, H, D = 3
        image = cv2.imread(os.path.join(image_root, fname))
        assert image is not None
        if len(image.shape) == 3:
            H, W, D = image.shape
        else:
            H, W = image.shape
            D = 1

        create_voc_xml(save, fname, obj_dict[fname], os.path.split(image_root)[-1], W, H, D)

        # exit(0)

    # cnt = 1
    # for fname in tqdm(label_dict.keys()):
    #     labels = label_dict[fname]
    #     for label in labels:
    #         cls_name = class_map[label[0]]
    #         cls_id = class_id_map[cls_name]
    #         bbox = label[1:]
    #         x0 = int(bbox[0])
    #         y0 = int(bbox[1])
    #         w = int(bbox[2]) - int(bbox[0])
    #         h = int(bbox[3]) - int(bbox[1])
    #
    #         vid = fname_dict[fname]
    #         random_s = ''
    #         for _ in range(8):
    #             random_s += random.choice(chars)
    #         new_tag = '{}_{}'.format(cnt, random_s)
    #         content['metadata'][new_tag] = {
    #             'vid': str(vid),
    #             'flg': 0,
    #             'z': [],
    #             'xy': [2, x0, y0, w, h],
    #             'av': {'1': cls_id}
    #         }
    #
    #         # print(new_tag, content['metadata'][new_tag])
    #         cnt += 1
    #
    # with open(json_p, 'w+') as f:
    #     json.dump(content, f)


if __name__ == "__main__":
    a = "xx.json"
    b = 'xxxxx/images'
    s = "xxxx/labels"

    label_map = {
        'A': 'a',
        'B': "b",
        'C': 'c',
        'D': 'd'
    }

    via_to_voc_bnbbox(a, b, s, label_map)
