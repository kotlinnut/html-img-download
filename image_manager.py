import os
import re
import shutil
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse


class ImageManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片管理工具")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # 读取保存的目录路径
        self.saved_dirs = self.load_saved_dirs()

        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TNotebook.Tab", font=("SimHei", 10))

        # 创建标签页
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建三个功能标签页
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="从HTML下载图片")
        self.notebook.add(self.tab2, text="图片排列")
        self.notebook.add(self.tab3, text="合并子文件夹图片")

        # 初始化各个标签页的UI
        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()

    def load_saved_dirs(self):
        """加载保存的目录路径"""
        saved_dirs = {}
        try:
            if os.path.exists("saved_dirs.txt"):
                with open("saved_dirs.txt", "r") as f:
                    for line in f:
                        key, value = line.strip().split("=", 1)
                        saved_dirs[key] = value
        except:
            pass
        return saved_dirs

    def save_dir(self, key, path):
        """保存目录路径"""
        if path:
            self.saved_dirs[key] = path
            with open("saved_dirs.txt", "w") as f:
                for k, v in self.saved_dirs.items():
                    f.write(f"{k}={v}\n")

    def setup_tab1(self):
        # 创建下载图片标签页的UI
        frame = ttk.LabelFrame(self.tab1, text="从HTML代码下载图片")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # HTML代码输入
        ttk.Label(frame, text="HTML代码:").grid(row=0, column=0, sticky=tk.NW, pady=5)
        self.html_code_text = tk.Text(frame, height=8, width=70)
        self.html_code_text.grid(row=0, column=1, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(frame, command=self.html_code_text.yview)
        scrollbar.grid(row=0, column=2, sticky=tk.NS)
        self.html_code_text.config(yscrollcommand=scrollbar.set)

        # 保存目录选择
        ttk.Label(frame, text="保存目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.save_dir_entry = ttk.Entry(frame, width=50)
        self.save_dir_entry.grid(row=1, column=1, padx=5, pady=5)

        # 恢复已保存的目录路径
        if "save_dir" in self.saved_dirs:
            self.save_dir_entry.insert(0, self.saved_dirs["save_dir"])

        ttk.Button(frame, text="浏览...", command=self.browse_save_dir).grid(row=1, column=2, padx=5, pady=5)

        # 记住目录勾选框
        self.remember_save_dir_var = tk.BooleanVar(value="save_dir" in self.saved_dirs)
        ttk.Checkbutton(frame, text="记住此目录", variable=self.remember_save_dir_var).grid(row=2, column=1,
                                                                                            sticky=tk.W, pady=2)

        # 显示当前保存目录
        self.current_save_dir_label = ttk.Label(frame,
                                                text="当前保存目录: " + (self.saved_dirs.get("save_dir", "未选择")),
                                                foreground="blue")
        self.current_save_dir_label.grid(row=3, column=1, sticky=tk.W, pady=2)

        # 下载按钮
        ttk.Button(frame, text="开始下载", command=self.download_images).grid(row=4, column=1, pady=10)

        # 日志显示
        ttk.Label(frame, text="下载日志:").grid(row=5, column=0, sticky=tk.NW, pady=5)
        self.log_text = tk.Text(frame, height=15, width=70)
        self.log_text.grid(row=5, column=1, columnspan=2, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(frame, command=self.log_text.yview)
        scrollbar.grid(row=5, column=3, sticky=tk.NS)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def setup_tab2(self):
        # 创建图片排列标签页的UI
        frame = ttk.LabelFrame(self.tab2, text="图片排列")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 选择路径
        ttk.Label(frame, text="图片目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.rename_dir_entry = ttk.Entry(frame, width=50)
        self.rename_dir_entry.grid(row=0, column=1, padx=5, pady=5)

        # 恢复已保存的目录路径
        if "rename_dir" in self.saved_dirs:
            self.rename_dir_entry.insert(0, self.saved_dirs["rename_dir"])

        ttk.Button(frame, text="浏览...", command=lambda: self.browse_dir(self.rename_dir_entry, "rename_dir")).grid(
            row=0, column=2, padx=5, pady=5)

        # 记住目录勾选框
        self.remember_rename_dir_var = tk.BooleanVar(value="rename_dir" in self.saved_dirs)
        ttk.Checkbutton(frame, text="记住此目录", variable=self.remember_rename_dir_var).grid(row=1, column=1,
                                                                                              sticky=tk.W, pady=2)

        # 显示当前目录
        self.current_rename_dir_label = ttk.Label(frame,
                                                  text="当前目录: " + (self.saved_dirs.get("rename_dir", "未选择")),
                                                  foreground="blue")
        self.current_rename_dir_label.grid(row=2, column=1, sticky=tk.W, pady=2)

        ttk.Label(frame, text="此功能会将指定目录下的所有图片按顺序重命名为1.jpg, 2.jpg, ...").grid(row=3, column=0,
                                                                                                    columnspan=2,
                                                                                                    sticky=tk.W,
                                                                                                    pady=10)

        # 重命名按钮
        ttk.Button(frame, text="开始排列", command=self.rename_images).grid(row=4, column=0, pady=10)

        # 日志显示
        ttk.Label(frame, text="操作日志:").grid(row=5, column=0, sticky=tk.NW, pady=5)
        self.rename_log_text = tk.Text(frame, height=15, width=70)
        self.rename_log_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(frame, command=self.rename_log_text.yview)
        scrollbar.grid(row=5, column=2, sticky=tk.NS)
        self.rename_log_text.config(yscrollcommand=scrollbar.set)

    def setup_tab3(self):
        # 创建合并图片标签页的UI
        frame = ttk.LabelFrame(self.tab3, text="合并子文件夹图片")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 选择路径
        ttk.Label(frame, text="根目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.merge_dir_entry = ttk.Entry(frame, width=50)
        self.merge_dir_entry.grid(row=0, column=1, padx=5, pady=5)

        # 恢复已保存的目录路径
        if "merge_dir" in self.saved_dirs:
            self.merge_dir_entry.insert(0, self.saved_dirs["merge_dir"])

        ttk.Button(frame, text="浏览...", command=lambda: self.browse_dir(self.merge_dir_entry, "merge_dir")).grid(
            row=0, column=2, padx=5, pady=5)

        # 记住目录勾选框
        self.remember_merge_dir_var = tk.BooleanVar(value="merge_dir" in self.saved_dirs)
        ttk.Checkbutton(frame, text="记住此目录", variable=self.remember_merge_dir_var).grid(row=1, column=1,
                                                                                             sticky=tk.W, pady=2)

        # 显示当前目录
        self.current_merge_dir_label = ttk.Label(frame,
                                                 text="当前根目录: " + (self.saved_dirs.get("merge_dir", "未选择")),
                                                 foreground="blue")
        self.current_merge_dir_label.grid(row=2, column=1, sticky=tk.W, pady=2)

        ttk.Label(frame, text="此功能会将指定目录下所有子文件夹中的图片整合到一个名为'合集'的新目录中").grid(row=3,
                                                                                                             column=0,
                                                                                                             columnspan=2,
                                                                                                             sticky=tk.W,
                                                                                                             pady=10)

        # 合并按钮
        ttk.Button(frame, text="开始合并", command=self.merge_images).grid(row=4, column=0, pady=10)

        # 日志显示
        ttk.Label(frame, text="操作日志:").grid(row=5, column=0, sticky=tk.NW, pady=5)
        self.merge_log_text = tk.Text(frame, height=15, width=70)
        self.merge_log_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(frame, command=self.merge_log_text.yview)
        scrollbar.grid(row=5, column=2, sticky=tk.NS)
        self.merge_log_text.config(yscrollcommand=scrollbar.set)

    def browse_save_dir(self):
        directory = filedialog.askdirectory(title="选择保存目录")
        if directory:
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(0, directory)
            self.current_save_dir_label.config(text="当前保存目录: " + directory)

    def browse_dir(self, entry_widget, save_key):
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)
            if save_key == "rename_dir":
                self.current_rename_dir_label.config(text="当前目录: " + directory)
            elif save_key == "merge_dir":
                self.current_merge_dir_label.config(text="当前根目录: " + directory)

    def log(self, message, widget=None):
        if widget is None:
            widget = self.log_text
        widget.insert(tk.END, message + "\n")
        widget.see(tk.END)
        self.root.update()

    def get_image_urls(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img')
        image_urls = []
        for img in img_tags:
            src = img.get('src')
            if src:
                # 去掉@xxxw.avif这样的后缀（如果有）
                if '@' in src:
                    src = src.split('@')[0]
                image_urls.append(src)
        return image_urls

    def download_images(self):
        html_content = self.html_code_text.get(1.0, tk.END).strip()
        save_dir = self.save_dir_entry.get().strip()

        if not html_content:
            messagebox.showerror("错误", "请输入HTML代码")
            return

        if not save_dir:
            messagebox.showerror("错误", "请选择保存目录")
            return

        # 保存目录路径（如果勾选了记住目录）
        if self.remember_save_dir_var.get():
            self.save_dir("save_dir", save_dir)

        try:
            # 清空日志
            self.log_text.delete(1.0, tk.END)

            self.log(f"已获取HTML代码，长度: {len(html_content)}")

            # 获取图片URL
            image_urls = self.get_image_urls(html_content)
            self.log(f"共找到 {len(image_urls)} 个图片URL")

            # 创建保存目录
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                self.log(f"已创建保存目录: {save_dir}")

            # 下载图片
            success_count = 0
            fail_count = 0

            for i, url in enumerate(image_urls, 1):
                # 为缺少协议头的链接添加 https://
                if url.startswith('//'):
                    url = 'https:' + url

                try:
                    response = requests.get(url, stream=True, timeout=10)
                    response.raise_for_status()

                    # 获取文件扩展名
                    ext = os.path.splitext(urlparse(url).path)[1].split('?')[0]
                    if not ext:
                        ext = '.jpg'  # 默认使用jpg扩展名

                    # 使用序号命名文件
                    file_name = f"{i}{ext}"
                    save_path = os.path.join(save_dir, file_name)

                    with open(save_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)

                    self.log(f"[{i}/{len(image_urls)}] 下载成功: {url} 保存为: {file_name}")
                    success_count += 1

                except Exception as e:
                    self.log(f"[{i}/{len(image_urls)}] 下载失败: {url}, 原因: {str(e)}", self.log_text)
                    fail_count += 1

            self.log(f"\n下载完成！成功: {success_count}, 失败: {fail_count}")
            messagebox.showinfo("完成", f"下载完成！成功: {success_count}, 失败: {fail_count}")

        except Exception as e:
            self.log(f"发生错误: {str(e)}")
            messagebox.showerror("错误", f"发生错误: {str(e)}")

    def rename_images(self):
        rename_dir = self.rename_dir_entry.get().strip()

        if not rename_dir:
            messagebox.showerror("错误", "请选择图片目录")
            return

        if not os.path.isdir(rename_dir):
            messagebox.showerror("错误", "选择的路径不是有效目录")
            return

        # 保存目录路径（如果勾选了记住目录）
        if self.remember_rename_dir_var.get():
            self.save_dir("rename_dir", rename_dir)

        try:
            # 清空日志
            self.rename_log_text.delete(1.0, tk.END)

            self.log(f"当前目录: {rename_dir}", self.rename_log_text)

            # 定义允许的图片文件扩展名
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.avif']

            # 获取所有图片文件（忽略子目录）
            image_files = []
            for filename in os.listdir(rename_dir):
                file_path = os.path.join(rename_dir, filename)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in image_extensions:
                        image_files.append(file_path)

            # 如果没有找到图片文件，直接退出
            if not image_files:
                self.log("当前目录下未找到图片文件！", self.rename_log_text)
                messagebox.showinfo("提示", "当前目录下未找到图片文件！")
                return

            # 按文件修改时间排序
            image_files.sort(key=os.path.getmtime)
            self.log(f"找到 {len(image_files)} 个图片文件", self.rename_log_text)

            # 创建备份目录
            backup_dir = os.path.join(rename_dir, "image_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
            os.makedirs(backup_dir, exist_ok=True)
            self.log(f"创建备份目录: {backup_dir}", self.rename_log_text)

            # 遍历排序后的文件并重命名
            for i, old_path in enumerate(image_files, 1):
                # 获取文件扩展名
                ext = os.path.splitext(old_path)[1]

                # 构建新文件名
                new_filename = f"{i}{ext}"
                new_path = os.path.join(rename_dir, new_filename)

                # 备份原文件
                backup_path = os.path.join(backup_dir, os.path.basename(old_path))
                shutil.copy2(old_path, backup_path)

                # 重命名文件
                os.rename(old_path, new_path)
                self.log(f"已重命名: {os.path.basename(old_path)} -> {new_filename}", self.rename_log_text)

            self.log(f"\n所有图片已成功重命名！原文件备份在: {backup_dir}", self.rename_log_text)
            messagebox.showinfo("完成", f"所有图片已成功重命名！\n原文件备份在: {backup_dir}")

        except Exception as e:
            self.log(f"发生错误: {str(e)}", self.rename_log_text)
            messagebox.showerror("错误", f"发生错误: {str(e)}")

    def merge_images(self):
        merge_dir = self.merge_dir_entry.get().strip()

        if not merge_dir:
            messagebox.showerror("错误", "请选择根目录")
            return

        if not os.path.isdir(merge_dir):
            messagebox.showerror("错误", "选择的路径不是有效目录")
            return

        # 保存目录路径（如果勾选了记住目录）
        if self.remember_merge_dir_var.get():
            self.save_dir("merge_dir", merge_dir)

        try:
            # 清空日志
            self.merge_log_text.delete(1.0, tk.END)

            self.log(f"当前根目录: {merge_dir}", self.merge_log_text)

            # 创建"合集"目录
            collection_dir = os.path.join(merge_dir, "合集")
            os.makedirs(collection_dir, exist_ok=True)
            self.log(f"创建合集目录: {collection_dir}", self.merge_log_text)

            # 定义允许的图片文件扩展名
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.avif']

            # 获取所有子文件夹（忽略隐藏文件夹）
            subfolders = []
            for item in os.listdir(merge_dir):
                item_path = os.path.join(merge_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.') and item != "合集":
                    subfolders.append(item_path)

            # 如果没有子文件夹，直接退出
            if not subfolders:
                self.log("当前目录下未找到子文件夹！", self.merge_log_text)
                messagebox.showinfo("提示", "当前目录下未找到子文件夹！")
                return

            # 按文件夹名称排序
            subfolders.sort()
            self.log(f"找到 {len(subfolders)} 个子文件夹", self.merge_log_text)

            # 初始化全局计数器
            global_counter = 1

            # 遍历每个子文件夹
            for folder in subfolders:
                folder_name = os.path.basename(folder)
                self.log(f"\n正在处理文件夹: {folder_name}", self.merge_log_text)

                # 获取子文件夹中的所有图片文件
                image_files = []
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        ext = os.path.splitext(filename)[1].lower()
                        if ext in image_extensions:
                            image_files.append(file_path)

                # 如果子文件夹中没有图片，跳过
                if not image_files:
                    self.log(f"文件夹 {folder_name} 中未找到图片文件", self.merge_log_text)
                    continue

                # 按文件名中的数字排序（如果有）
                def get_number(filename):
                    match = re.search(r'\d+', filename)
                    return int(match.group()) if match else 0

                image_files.sort(key=lambda x: get_number(os.path.basename(x)))
                self.log(f"找到 {len(image_files)} 个图片文件", self.merge_log_text)

                # 复制图片到"合集"目录并重命名
                for file_path in image_files:
                    filename = os.path.basename(file_path)
                    ext = os.path.splitext(filename)[1]

                    # 使用全局计数器作为新文件名
                    new_filename = f"{global_counter}{ext}"
                    new_path = os.path.join(collection_dir, new_filename)

                    # 复制文件
                    shutil.copy2(file_path, new_path)
                    self.log(f"已复制: {filename} -> {new_filename}", self.merge_log_text)

                    # 增加全局计数器
                    global_counter += 1

            self.log(f"\n所有图片已成功整合到: {collection_dir}", self.merge_log_text)
            self.log(f"共整合 {global_counter - 1} 张图片", self.merge_log_text)
            messagebox.showinfo("完成", f"所有图片已成功整合到: {collection_dir}\n共整合 {global_counter - 1} 张图片")

        except Exception as e:
            self.log(f"发生错误: {str(e)}", self.merge_log_text)
            messagebox.showerror("错误", f"发生错误: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageManagerApp(root)
    root.mainloop()