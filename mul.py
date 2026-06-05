import os
import re

# 需要全局排除的文件名
EXCLUDE_FILES = {'README.md', '直接目录.txt', '树形目录.txt', 'mul.py'}

def natural_sort_key(s):
    """
    实现自然数字排序（Natural Sort），确保 "第2卷" 排在 "第10卷" 前面。
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def should_exclude(name):
    """判断文件或文件夹是否需要排除（隐藏文件或特定保留文件）"""
    if name.startswith('.'):
        return True
    if name in EXCLUDE_FILES:
        return True
    return False

def build_tree_lines(current_dir, prefix=""):
    """递归生成当前文件夹的树形目录文本行"""
    try:
        names = os.listdir(current_dir)
    except PermissionError:
        return []
        
    # 过滤隐藏文件和指定排查的文件
    filtered_names = [n for n in names if not should_exclude(n)]
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
            lines.extend(build_tree_lines(path, new_prefix))
            
    return lines

def main():
    # 1. 获取脚本当前所在文件夹作为根目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取当前文件夹的名称作为树状图的起点
    root_name = os.path.basename(base_dir) or "Root"
    
    print(f"开始处理当前文件夹: {base_dir}")
    
    # 2. 生成树形目录
    print("正在构建树形目录...")
    tree_lines = [root_name] + build_tree_lines(base_dir)
    
    # 3. 生成直接目录（相对当前文件夹的整平路径，开头带 ./）
    print("正在构建直接目录...")
    flat_lines = []
    for root, dirs, files in os.walk(base_dir):
        # 动态过滤隐藏文件夹，防止 os.walk 深入其中
        dirs[:] = [d for d in dirs if not should_exclude(d)]
        dirs.sort(key=natural_sort_key)
        
        # 过滤并排序文件
        filtered_files = [f for f in files if not should_exclude(f)]
        filtered_files.sort(key=natural_sort_key)
        
        for file in filtered_files:
            full_path = os.path.join(root, file)
            # 计算相对于根目录的相对路径 (例如: 文件夹A/子文件.pdf)
            rel_path = os.path.relpath(full_path, base_dir)
            
            # 【核心修改点】在这里强制为每一行开头加上 ./
            # 使用正斜杠替换 Windows 系统可能产生的反斜杠 \，确保跨平台通用性
            standard_path = f"./{rel_path}".replace('\\', '/')
            flat_lines.append(standard_path)
            
    # 4. 在当前文件夹下写入结果文件
    tree_file_path = os.path.join(base_dir, "树形目录.txt")
    flat_file_path = os.path.join(base_dir, "直接目录.txt")
    
    with open(tree_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tree_lines) + "\n")
        
    with open(flat_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(flat_lines) + "\n")
        
    print("\n处理完毕！已在当前目录下生成：")
    print(f" -> {tree_file_path}")
    print(f" -> {flat_file_path}")

if __name__ == "__main__":
    main()
