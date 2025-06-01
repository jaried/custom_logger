#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本功能：
1. 将 src 目录下所有 .py、.cmd、.ini、.yaml 文件合并到根目录下的 所有的源代码.txt，
   并在每个文件内容前添加注释标明源文件相对路径。
2. 将 test 或 tests 目录下所有 .py、.cmd、.ini、.yaml 文件合并到根目录下的 所有的测试用例.txt，
   并在每个文件内容前添加注释标明源文件相对路径。
3. 输出前删除已存在的输出文件（所有的源代码.txt、所有的测试用例.txt）。

用法：在项目根目录下执行 `python collect_py.py`
"""

import os


def collect_files(source_dir: str, output_file: str, exts):
    """
    将 source_dir 下所有指定扩展名文件内容追加写入 output_file，
    每个文件前添加注释说明源文件路径。
    """
    with open(output_file, 'a', encoding='utf-8') as fout:
        for root, _, files in os.walk(source_dir):
            for fname in sorted(files):
                if any(fname.endswith(ext) for ext in exts):
                    full_path = os.path.join(root, fname)
                    rel_path = os.path.relpath(full_path, os.getcwd())
                    fout.write(f"# ======= 源文件: {rel_path} =======\n")
                    with open(full_path, 'r', encoding='utf-8') as fin:
                        fout.write(fin.read())
                    fout.write("\n\n")

if __name__ == "__main__":
    # 定义输出文件名
    output_src = "所有的源代码.txt"
    output_test = "所有的测试用例.txt"
    # 需要合并的文件扩展名列表
    exts = ['.py', '.ini', '.yaml','yml']

    # 删除已存在的输出文件
    for f in (output_src, output_test):
        if os.path.exists(f):
            os.remove(f)
            print(f"已删除已存在文件：{f}")

    # 定义输入输出目录映射
    mappings = [
        (['src'], output_src),
        (['test', 'tests'], output_test),
    ]

    # 遍历映射并处理
    for src_dirs, out_file in mappings:
        found = False
        for src_dir in src_dirs:
            if os.path.isdir(src_dir):
                found = True
                print(f"正在处理目录 `{src_dir}/` → 输出文件 `{out_file}`")
                collect_files(src_dir, out_file, exts)
        if not found:
            dirs = ' 或 '.join([f"`{d}/`" for d in src_dirs])
            print(f"警告：目录 {dirs} 不存在，跳过。")
