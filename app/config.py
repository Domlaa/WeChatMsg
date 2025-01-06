import os

version = '2.0.5'

# 数据存放文件路径
INFO_FILE_PATH = './app/data/info.json'  # 个人信息文件
DB_DIR = './app/Database/Msg'
OUTPUT_DIR = './data/'  # 输出文件夹
os.makedirs('./app/data', exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)