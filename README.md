# image-annotator-flask
A customized version of VIA image annotator which supports server deployment (python-flask backend).

## Description
在VIA的图像标注工具上做了升级，增加了flask后端。没用数据库，只配置文件夹来管理数据。增加了自动保存和逐张加载的功能。

A lightweight version for deployment image annotator on server. Without database plugin, it only uses a config file with directory paths. Auto-save and download images one by one when browse.

## Requirements
flask, tqdm, yaml, PIL, etc.

## UI
![page]("./src/pic/a.jpg")

## How to use?
learn from VIA image annotator version 3 
https://www.robots.ox.ac.uk/~vgg/software/via/


## Start
run with script run.sh


## TODO
- [ ] 用户管理系统和任务分割 (User management system / tasks split)
- [ ] 图片序列变化后自动更新标注文件 (Update annotation json file when images are modified by someone automatically)
- [ ] 支持一键转化输出voc/coco等格式 (Support convert annotation file to voc/coco or any other formats by one-click)
