import json


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


if __name__ == "__main__":
    parse('./sample/label/via.json')
