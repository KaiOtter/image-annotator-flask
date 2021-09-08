from flask import Flask, url_for, render_template, jsonify, request
import os
from PIL import Image
from io import BytesIO
import base64
from tqdm import tqdm
import yaml
import json

app = Flask(__name__, static_url_path='', static_folder='./src/', template_folder='./src/html/')

dataset_list = []
dataset_info = dict()
user_dataset = dict()

with open('./config.yaml') as f:
    content = yaml.load(f, Loader=yaml.FullLoader)
    for k in content['dataset']:
        dataset_list.append(k)
        temp = content['dataset'][k]
        anno_path = temp['anno_path']
        if os.path.isdir(anno_path):
            anno_path = os.path.join(anno_path, 'via.json')

        assert anno_path.endswith('json')
        log_path = os.path.join(os.path.split(anno_path)[0], 'log.txt')

        dataset_info[k] = {
            'key': k,
            'name': temp['name'],
            'img_path': temp['img_path'],
            'anno_path': anno_path,
            'log_path': log_path,
            'extension': temp['extension']
        }

        if temp.get('users') is not None:
            users = temp['users']
            for u in users:
                if user_dataset.get(u) is None:
                    user_dataset[u] = [k]
                else:
                    user_dataset[u].append(k)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/dataInfo', methods=['GET'])
def get_dataset_info():
    user_name = request.args.get('u')
    dataset = []
    if user_dataset.get(user_name) is not None:
        for k in user_dataset[user_name]:
            dataset.append(dataset_info[k])
    return jsonify(dataset)


@app.route('/annotator', methods=['GET'])
def tool():
    return render_template('_via_image_annotator.html')


@app.route('/save', methods=['POST'])
def save_json():
    dataKey = request.args.get('d')
    result = dict()
    temp = dataset_info[dataKey]

    try:
        post_data = request.files
        anno_data = json.load(post_data['anno'])
        log_info = json.load(post_data['log'])
        timeStamp = log_info['time']
        with open(temp['anno_path'], 'w+') as f:
            json.dump(anno_data, f)
            f.close()
        with open(temp['log_path'], 'a+') as f:
            f.write(timeStamp + '\n')
            f.close()
        result['m'] = 'success'
    except Exception as e:
        print(e)
        result['m'] = 'error'
    return result


# Quest for getting images and annotation file (json)
@app.route('/load', methods=['GET'])
def load_dataset():
    dataKey = request.args.get('d')
    root = dataset_info[dataKey]['img_path']
    legal_ext = []
    if dataset_info[dataKey].get('extension') is not None:
        legal_ext = dataset_info[dataKey]['extension']

    result = dict()
    result['img'] = []
    _raw = sorted(os.listdir(root))
    image_list = []
    for file in _raw:
        if len(legal_ext) > 0:
            if file.split('.')[-1] not in legal_ext:
                continue
        image_list.append(file)


    # return id-0 image for showing
    image = Image.open(os.path.join(root, image_list[0]))
    output_buffer = BytesIO()
    image.save(output_buffer, format='JPEG')
    data = {
        'image': base64.b64encode(output_buffer.getvalue()).decode('ascii'),
        'filename': image_list[0]
    }
    result['img'].append(data)

    for file in tqdm(image_list[1:]):
        data = {
            # 'image': base64.b64encode(output_buffer.getvalue()).decode('ascii'),
            'filename': file
        }
        result['img'].append(data)

    a_path = dataset_info[dataKey]['anno_path']
    if os.path.exists(a_path):
        with open(a_path, 'r') as f:
            j = json.load(f)
            result['anno'] = j
            f.close()
    else:
        result['anno'] = None

    return jsonify(result)


@app.route('/pullImg', methods=['GET'])
def get_images():
    dataKey = request.args.get('d')
    fname = request.args.get('f')
    root = dataset_info[dataKey]['img_path']

    result = dict()
    result['img'] = []

    image = Image.open(os.path.join(root, fname))

    output_buffer = BytesIO()
    image.save(output_buffer, format='JPEG')
    data = {
        'image': base64.b64encode(output_buffer.getvalue()).decode('ascii'),
    }
    result['img'].append(data)

    return jsonify(result)


@app.route('/rotImg', methods=['GET'])
def rotate_image():
    dataKey = request.args.get('d')
    fname = request.args.get('f')
    isClockWise = request.args.get('c')
    root = dataset_info[dataKey]['img_path']

    result = dict()
    result['img'] = []

    image = Image.open(os.path.join(root, fname))

    if int(isClockWise) == 1:
        image = image.rotate(-90, expand=True)
    else:
        image = image.rotate(90, expand=True)

    image.save(os.path.join(root, fname))

    output_buffer = BytesIO()
    image.save(output_buffer, format='JPEG')
    data = {
        'image': base64.b64encode(output_buffer.getvalue()).decode('ascii'),
    }
    result['img'].append(data)

    return jsonify(result)
