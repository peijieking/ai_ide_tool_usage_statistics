
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re

class ToolUsageAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("AI IDE 工具使用统计分析器")
        self.root.geometry("1200x800")
        
        # 当前选中的日志文件
        self.selected_file = None
        # 工具使用数据
        self.tool_data = []
        # 上一个思考内容
        self.last_thought = ""
        # 统计信息
        self.statistics = {}
        
        self.create_widgets()
        self.load_default_files()
        
    def create_widgets(self):
        # 第一部分：文件选择
        file_frame = ttk.LabelFrame(self.root, text="日志文件选择", padding=(10, 5))
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_var = tk.StringVar()
        self.file_combo = ttk.Combobox(file_frame, textvariable=self.file_var, state="readonly")
        self.file_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.file_combo.bind("<<ComboboxSelected>>", self.on_file_selected)
        
        browse_btn = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT)
        
        # 第二部分：Treeview 显示工具信息
        tree_frame = ttk.LabelFrame(self.root, text="工具使用记录", padding=(10, 5))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建 Treeview
        columns = ("序号", "思考", "工具名称", "状态", "其它信息")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # 设置列属性
        self.tree.heading("序号", text="序号", anchor=tk.CENTER)
        self.tree.heading("思考", text="思考", anchor=tk.W)
        self.tree.heading("工具名称", text="工具名称", anchor=tk.W)
        self.tree.heading("状态", text="状态", anchor=tk.CENTER)
        self.tree.heading("其它信息", text="其它信息", anchor=tk.W)
        
        self.tree.column("序号", width=60, anchor=tk.CENTER)
        self.tree.column("思考", width=200, anchor=tk.W)
        self.tree.column("工具名称", width=150, anchor=tk.W)
        self.tree.column("状态", width=100, anchor=tk.CENTER)
        self.tree.column("其它信息", width=600, anchor=tk.W)
        
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定点击事件
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)
        
        # 第三部分：完整信息显示
        detail_frame = ttk.LabelFrame(self.root, text="详细信息", padding=(10, 5))
        detail_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.detail_text = tk.Text(detail_frame, height=8, wrap=tk.WORD)
        self.detail_text.pack(fill=tk.X, expand=True)
        
        # 第四部分：统计信息
        stat_frame = ttk.LabelFrame(self.root, text="工具使用统计", padding=(10, 5))
        stat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 统计 Treeview
        stat_columns = ("工具名称", "使用次数", "成功次数", "失败次数")
        self.stat_tree = ttk.Treeview(stat_frame, columns=stat_columns, show="headings")
        
        self.stat_tree.heading("工具名称", text="工具名称", anchor=tk.W)
        self.stat_tree.heading("使用次数", text="使用次数", anchor=tk.CENTER)
        self.stat_tree.heading("成功次数", text="成功次数", anchor=tk.CENTER)
        self.stat_tree.heading("失败次数", text="失败次数", anchor=tk.CENTER)
        
        self.stat_tree.column("工具名称", width=150, anchor=tk.W)
        self.stat_tree.column("使用次数", width=100, anchor=tk.CENTER)
        self.stat_tree.column("成功次数", width=100, anchor=tk.CENTER)
        self.stat_tree.column("失败次数", width=100, anchor=tk.CENTER)
        
        self.stat_tree.pack(fill=tk.BOTH, expand=True)
        
    def load_default_files(self):
        """加载当前目录下的日志文件"""
        current_dir = os.getcwd()
        log_files = [f for f in os.listdir(current_dir) if f.endswith("_model_log.md")]
        log_files.sort()
        self.file_combo['values'] = log_files
        if log_files:
            self.file_combo.current(0)
            self.on_file_selected(None)
        
    def browse_file(self):
        """浏览选择日志文件"""
        file_path = filedialog.askopenfilename(
            title="选择日志文件",
            filetypes=[("Markdown 文件", "*.md"), ("所有文件", "*.*")]
        )
        if file_path:
            self.selected_file = file_path
            self.file_var.set(os.path.basename(file_path))
            self.analyze_log_file(file_path)
        
    def on_file_selected(self, event):
        """当选择文件时触发"""
        selected = self.file_combo.get()
        if selected:
            file_path = os.path.join(os.getcwd(), selected)
            self.analyze_log_file(file_path)
        
    def analyze_log_file(self, file_path):
        """分析日志文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件: {e}")
            return
        
        # 重置数据
        self.tool_data = []
        self.last_thought = ""
        self.statistics = {}
        
        sections = []
        current_section = None
        current_content = []
        
        # 按行处理日志
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是工具名称行
            if line.startswith('toolName:'):
                # 保存上一个分段
                if current_section:
                    current_section['content'] = '\n'.join(current_content).strip()
                    current_section['thought'] = self.last_thought  # 保存当前分段的思考内容
                    sections.append(current_section)
                    current_content = []
                
                # 开始新分段
                tool_name = line.replace('toolName:', '').strip()
                current_section = {
                    'tool_name': tool_name,
                    'status': '',
                    'content': '',
                    'thought': ''
                }
            
            # 检查是否是状态行
            elif line.startswith('status:'):
                if current_section:
                    current_section['status'] = line.replace('status:', '').strip()
            
            else:
                # 如果当前没有工具分段，这是思考内容
                if not current_section:
                    self.last_thought = line  # 更新思考内容为当前行
                # 收集内容
                current_content.append(line)
        
        # 添加最后一个分段
        if current_section:
            current_section['content'] = '\n'.join(current_content).strip()
            current_section['thought'] = self.last_thought  # 保存最后一个分段的思考内容
            sections.append(current_section)
        
        # 处理分段数据
        for idx, section in enumerate(sections, 1):
            tool_name = section['tool_name']
            status = section['status']
            content = section['content']
            thought = section['thought']
            
            # 保存到工具数据
            self.tool_data.append({
                '序号': idx,
                '思考': thought,
                '工具名称': tool_name,
                '状态': status,
                '其它信息': content
            })
            
            # 更新统计信息
            if tool_name not in self.statistics:
                self.statistics[tool_name] = {
                    'total': 0,
                    'success': 0,
                    'failed': 0
                }
            
            self.statistics[tool_name]['total'] += 1
            if status == 'success' or status == '完成' or status == '成功':
                self.statistics[tool_name]['success'] += 1
            else:
                self.statistics[tool_name]['failed'] += 1
        
        # 更新界面
        self.update_treeview()
        self.update_statistics()
        
    def update_treeview(self):
        """更新 Treeview 显示"""
        # 清空现有内容
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加新内容
        for data in self.tool_data:
            self.tree.insert("", tk.END, values=(
                data['序号'],
                data['思考'],
                data['工具名称'],
                data['状态'],
                data['其它信息']
            ))
        
    def update_statistics(self):
        """更新统计信息"""
        # 清空现有内容
        for item in self.stat_tree.get_children():
            self.stat_tree.delete(item)
        
        # 添加统计数据
        for tool_name, stats in self.statistics.items():
            self.stat_tree.insert("", tk.END, values=(
                tool_name,
                stats['total'],
                stats['success'],
                stats['failed']
            ))
        
    def on_item_selected(self, event):
        """当选择 Treeview 条目时显示详细信息"""
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            values = self.tree.item(item, 'values')
            
            # 清空详细信息
            self.detail_text.delete(1.0, tk.END)
            
            # 显示完整信息
            detail = f"序号: {values[0]}\n"
            detail += f"思考: {values[1]}\n"
            detail += f"工具名称: {values[2]}\n"
            detail += f"状态: {values[3]}\n"
            detail += f"其它信息: {values[4]}\n"
            
            self.detail_text.insert(1.0, detail)

if __name__ == "__main__":
    root = tk.Tk()
    app = ToolUsageAnalyzer(root)
    root.mainloop()
