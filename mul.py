import os
import re

# 需要全局排除的文件名
EXCLUDE_FILES = {'README.md', '直接目录.txt', '树形目录.txt'}

def natural_sort_key(s):
    """
    实现自然数字排序（Natural Sort），确保 "第2卷" 排在 "第10卷" 前面，
    而不是让 "第10卷" 因为字符编码跑到 "第1卷" 后面。
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def should_exclude(name):
    """判断文件或文件夹是否需要排除（隐藏文件或特定保留文件）"""
    if name.startswith('.'):
        return True
    if name in EXCLUDE_FILES:
        return True
    return False

def build_tree_lines(dir_path, current_dir, prefix=""):
    """递归生成树形目录的文本行列表"""
    try:
        names = os.listdir(current_dir)
    except PermissionError:
        return []
        
    # 过滤隐藏文件和指定排查的文件
    filtered_names = [n for n in names if not should_exclude(n)]
    # 采用自然排序
    filtered_names.sort(key=natural_sort_key)
    
    lines = []
    count = len(filtered_names)
    
    for i, name in enumerate(filtered_names):
        path = os.path.join(current_dir, name)
        is_last = (i == count - 1)
        
        # 添加当前节点的连线
        lines.append(f"{prefix}{'└── ' if is_last else '├── '}{name}")
        
        # 如果是文件夹，则递归深入
        if os.path.isdir(path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            lines.extend(build_tree_lines(dir_path, path, new_prefix))
            
    return lines

def process_subfolder(subfolder_path, subfolder_name):
    """为单个子文件夹生成对应的两个目录文件"""
    print(f"正在处理文件夹: {subfolder_name} ...")
    
    # 1. 生成树形目录数据
    # 第一行通常为该文件夹自身的名称
    tree_lines = [subfolder_name] + build_tree_lines(subfolder_path, subfolder_path)
    
    # 2. 生成直接目录数据（展平的标准相对路径）
    flat_lines = []
    for root, dirs, files in os.walk(subfolder_path):
        # 过滤掉隐藏文件夹
        dirs[:] = [d for d in dirs if not should_exclude(d)]
        dirs.sort(key=natural_sort_key)
        
        # 过滤并排序文件
        filtered_files = [f for f in files if not should_exclude(f)]
        filtered_files.sort(key=natural_sort_key)
        
        for file in filtered_files:
            full_path = os.path.join(root, file)
            # 如果你希望计算相对于当前子文件夹的相对路径，更方便迁移查看，可以改用：
            # rel_path = os.path.relpath(full_path, subfolder_path)
            # 如果你希望直接目录里带有子文件夹名字本身作为前缀，可以改用：
            rel_path = os.path.join(subfolder_name, os.path.relpath(full_path, subfolder_path))
            flat_lines.append(rel_path)
            
    # 3. 将结果写入到该子文件夹内部
    tree_file_path = os.path.join(subfolder_path, "树形目录.txt")
    flat_file_path = os.path.join(subfolder_path, "直接目录.txt")
    
    with open(tree_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tree_lines) + "\n")
        
    with open(flat_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(flat_lines) + "\n")

def main():
    # 获取脚本当前所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 列出当前目录下所有的子项目
    try:
        items = os.listdir(base_dir)
    except Exception as e:
        print(f"无法读取目录: {e}")
        return

    # 过滤出非隐藏的子文件夹
    subfolders = [item for item in items if os.path.isdir(os.path.join(base_dir, item)) and not item.startswith('.')]
    subfolders.sort(key=natural_sort_key)
    
    if not subfolders:
        print("未检测到有效的同级子文件夹。")
        return
        
    for folder in subfolders:
        folder_path = os.path.join(base_dir, folder)
        process_subfolder(folder_path, folder)
        
    print("\n所有文件夹处理完毕！")

if __name__ == "__main__":
    main()
