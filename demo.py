from flask import Flask, url_for, render_template, jsonify, request
from markupsafe import escape
from werkzeug.datastructures import ImmutableMultiDict
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


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/dataInfo', methods=['GET'])
def get_dataset_info():
    dataset = []
    for k in dataset_list:
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

# import codecs
# import hashlib
# import json
# import threading
# import time
# import os
# import argparse
# import traceback
# import requests
# from flask import Flask, render_template, jsonify, send_file
# from flask import request
# from io import BytesIO
# import base64
# from PIL import Image
# import lmdb
#
# import config as sys_config
# import utils.tool as tool
#
# app = Flask(__name__)
# app.config.from_object('config')
#
# mu = threading.Lock()  # 创建一个锁
# labels = dict()
#
# # Route to any template
# @app.route('/')
# def index():
#     names = [name for name in os.listdir(sys_config.SAMPLE_FILE_PATH) \
#              if name.split('.')[-1].lower() in sys_config.SAMPLE_TYPE_SET]
#     return render_template('index.html', \
#                            sample_count=len(names), \
#                            sample_type=sys_config.SAMPLE_FILE_TYPE)
#
#
# @app.route('/<template>')
# def route_template(template):
#     return render_template(template)
#
#
# # 读取类别标签
# @app.route('/api/annotation/labels', methods=['GET'])
# def get_sample():
#     label_json = tool.get_labels()
#     result = dict()
#     result['message'] = 'success'
#     result['data'] = label_json
#     return jsonify(result)
#
#
# # 读取文件列表
# @app.route('/api/annotation/names', methods=['GET'])
# def get_names():
#     img_names = os.listdir(sys_config.SAMPLE_FILE_PATH)
#     result = dict()
#     result['message'] = 'success'
#     result['data'] = sorted(img_names)              #
#     return jsonify(result)
#
#
#
# # 读取标注样本
# @app.route('/api/annotation/sample', methods=['GET'])
# def get_labels():
#     if 'index' in request.args:
#         # img_name = request.args['index'] + '.' + sys_config.SAMPLE_FILE_TYPE
#         img_name = request.args['index']
#         img_path = os.path.join(sys_config.SAMPLE_FILE_PATH, img_name)
#         image = Image.open(img_path).resize((800,600))
#         output_buffer = BytesIO()
#         image.save(output_buffer, format='JPEG')
#         result = dict()
#         result['img'] = base64.b64encode(output_buffer.getvalue()).decode('ascii')
#
#         env_db = lmdb.Environment(sys_config.SAMPLE_LABLE_PATH)     # 读取数据库
#         txn = env_db.begin()
#         if txn.get(img_name.encode()) == None:          # 没有标注信息的时候，调取百度的api接口
#             # 标注信息返回的格式为：result['coor_label'] = result['coor_label'] = '10,10,150,150,chenjun'   //x1,y1,x2,y2
#             result['coor_label'] = 'none'
#
#             # 调百度的api//如果误检的框多的话，还不如直接标注来的快
#             # request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"
#             # # f = open('./dataset/images/─■A0C93F.jpg', 'rb')
#             # # img = base64.b64encode(f.read())
#             # img = result['img']
#
#             # params = {"image":img}
#             # access_token = '....'
#             # request_url = request_url + "?access_token=" + access_token
#             # headers = {'content-type': 'application/x-www-form-urlencoded'}
#             # response = requests.post(request_url, data=params, headers=headers)
#             # if response:
#             #     b = response.json()['words_result']
#             #     c = [[str(tb['location']['left']),
#             #         str(tb['location']['top']),
#             #         str(tb['location']['left']+tb['location']['width']),
#             #         str(tb['location']['top']+tb['location']['height']),
#             #         tb['words']]for tb in b]
#             #     d = '\n'.join([','.join(tc) for tc in c])
#             #     result['coor_label'] = d
#             # else:
#             #     result['coor_label'] = 'none'
#         else:                                           # 直接传回图片和以前的标注
#             result['coor_label'] = txn.get(img_name.encode()).decode('utf-8')
#         env_db.close()
#         return jsonify(result)
#     else:
#         result = dict()
#         result['message'] = 'failure'
#         return jsonify(result)
#
#
# # save api
# @app.route('/api/annotation/save', methods=['POST'])
# def save_annotation():
#     result = dict()
#     try:
#         tags = request.form['tags']
#         t = tags.split(',', maxsplit=1)
#         if mu.acquire(True):                    # 避免同时写入
#             env_db = lmdb.open(sys_config.SAMPLE_LABLE_PATH)
#             txn = env_db.begin(write=True)
#             txn.put(key=t[0].encode(), value=t[1].encode())
#             txn.commit()
#             env_db.close()
#             mu.release()
#         result['message'] = 'success'
#     except Exception as e:
#         print(e)
#         result['message'] = 'error'
#     return jsonify(result)
#
#
# # Errors
# @app.errorhandler(403)
# def not_found_error(error):
#     return render_template('page_403.html'), 403
#
#
# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('page_404.html'), 404
#
#
# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('page_500.html'), 500
#
#
# def run():
#     app.run(debug=sys_config.DEBUG, host='0.0.0.0', port=sys_config.SERVER_PORT, threaded=True)         # 开启多线程
#
#
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Object detection annotation service.')
#     parser.add_argument('--start', action='store_true', help='running background')
#     parser.add_argument('--stop', action='store_true',  help='shutdown process')
#     parser.add_argument('--restart', action='store_true',  help='restart process')
#     parser.add_argument('--daemon', action='store_true', help='restart process')
#     parser.add_argument('--convert2voc', action='store_true', help='restart process')
#
#     # whether create dataset
#     if os.path.exists(sys_config.SAMPLE_LABLE_PATH+'/data.mdb'):
#         pass
#     else:
#         env = lmdb.open(sys_config.SAMPLE_LABLE_PATH)
#         env.close()
#
#     FLAGS = parser.parse_args()
#     if FLAGS.start:
#         if FLAGS.daemon:
#             tool.start_daemon_service(run, sys_config.PID_FILE)
#         else:
#             tool.start_service(run, sys_config.PID_FILE)
#     elif FLAGS.stop:
#         tool.shutdown_service(sys_config.PID_FILE)
#     elif FLAGS.restart:
#         tool.shutdown_service(sys_config.PID_FILE)
#         if FLAGS.daemon:
#             tool.start_daemon_service(run, sys_config.PID_FILE)
#         else:
#             tool.start_service(run, sys_config.PID_FILE)
#     elif FLAGS.convert2voc:
#         tool.convert_to_voc2007()
