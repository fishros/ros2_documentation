"""
处理PO文件
1.从po生成 poconfig.json，并删除po下的配置
2.生成原始文档并发布
3.生成dev文档并发布
"""
import os
from datetime import datetime

def read_po_file(po):
    """ Add [source, msgid, msgstr] from .po to left side ListBox """
    heading = True
    selfmessages = []
    selfpo_header = ''
    with open(po, "r", encoding="utf-8") as f:
        message = ["", "", ""]
        source = False
        msgid = False
        msgstr = False
        for line in f:

            if heading:
                if not line.startswith("#: "):
                    selfpo_header += line
                    continue
                else:
                    heading = False
            if not heading:
                if line.startswith("#: "):
                    source = True

                elif line.startswith("msgid"):
                    source = False
                    msgid = True
                    msgstr = False

                elif line.startswith("msgstr"):
                    source = False
                    msgid = False
                    msgstr = True

                elif line=='\n':
                    if msgstr == True:
                        message[2] += line
                        selfmessages.append(message)
                        message = ["", "", ""]
                    msgid = False
                    msgstr = False
                    source = False

                if source:
                    message[0] = line
                elif msgid:
                    message[1] += line
                elif msgstr:
                    message[2] += line
                
    return selfmessages, selfpo_header, po[po.rfind("\\")+1:]


def get_file_lists(path, pattern):
    reults = []
    for root, dirs, files in os.walk(path):
        for f in files:
            is_file = False
            file_path = os.path.join(root, f)
            if file_path.endswith(pattern):
                reults.append(file_path)
        # 遍历所有的文件夹
        for d in dirs:
            os.path.join(root, d)
    return reults


import argparse
import json
import os
import re
import json


def extract_json_data(text):
    parsed_data = {}
    # 找到最后一个 @ 符号的位置
    last_at_index = text.rfind('@')
    if last_at_index >= 0:
        # 从最后一个 @ 符号往前找另一个 @ 符号的位置
        second_last_at_index = text.rfind('@', 0, last_at_index)
        if second_last_at_index >= 0:
            # 提取两个 @ 符号之间的数据
            extracted_data = text[second_last_at_index + 1:last_at_index]
            parsed_data = json.loads(extracted_data)
            parsed_data['msgzh'] =  text.replace('@' + extracted_data + '@', '')
        else:
            parsed_data['msgzh'] = text
    else:
        parsed_data['msgzh'] = text
    return parsed_data


def generate_original_docs(out_path,popath=".temp"):
    # 生成原始文档并发布的逻辑
    files = get_file_lists(popath, ".po")
    for path in files:
        messages, header, name = read_po_file(path)
        file = {'filename': path,
            'path': path[path.rfind("/"):], "header": header}
        new_file_path = f"{out_path}{file['path']}"
        new_file_content = file['header']
        for msg in messages:
            new_msgzh = extract_json_data(msg[2])
            new_file_content += f'\n{msg[0]}{msg[1]}{new_msgzh["msgzh"]}\n'
        with open(new_file_path,"w") as f:
            f.write(new_file_content)


def generate_dev_docs(out_path,popath=".temp"):
    # 生成dev文档并发布的逻辑
    files = get_file_lists(popath, ".po")
    for path in files:
        messages, header, name = read_po_file(path)
        file = {'filename': path,
            'path': path[path.rfind("/"):], "header": header}
        new_file_path = f"{out_path}{file['path']}"
        new_file_content = file['header']
        for msg in messages:
            new_msg = extract_json_data(msg[2])
            new_msgzh = new_msg["msgzh"][:-3]+new_msg["calib_text"].replace("\n","")+'"'
            new_file_content += f'\n{msg[0]}{msg[1]}{new_msgzh}\n'
        with open(new_file_path,"w") as f:
            f.write(new_file_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script with three functionalities")
    parser.add_argument("-f", "--function", choices=["doc", "dev_doc"], required=True,
                        help="Choose the function to execute")
    parser.add_argument("-p", "--path", default="poconfig.json", help="Path to the generated poconfig.json file")
    args = parser.parse_args()
    if args.function == "doc":
        generate_original_docs(out_path=args.path)
    elif args.function == "dev_doc":
        generate_dev_docs(out_path=args.path)




