import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os

class ToolAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI IDE工具使用统计分析")
        self.root.geometry("1000x700")
        
        # 变量
        self.current_file = None
        self.tool_entries = []
        self.statistics = {}
        
        # 第一部分：log选择
        self.create_file_selector()
        
        # 第二部分：treeview
        self.create_treeview()
        
        # 第三部分：详细信息显示
        self.create_detail_view()
        
        # 第四部分：统计信息
        self.create_statistics_view()
        
        # 加载默认文件
        self.load_default_files()
    
    def create_file_selector(self):
        """创建文件选择区域"""
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="选择log文件:").pack(side=tk.LEFT, padx=5)
        
        self.file_var = tk.StringVar()
        self.file_combobox = ttk.Combobox(frame, textvariable=self.file_var, state="readonly")
        self.file_combobox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.file_combobox.bind("<<ComboboxSelected>>", self.on_file_selected)
        
        ttk.Button(frame, text="选择文件", command=self.select_file).pack(side=tk.LEFT, padx=5)
    
    def create_treeview(self):
        """创建工具信息显示区域"""
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview
        columns = ("序号", "思考", "工具名称", "状态", "其它信息")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        self.tree.heading("序号", text="序号")
        self.tree.heading("思考", text="思考")
        self.tree.heading("工具名称", text="工具名称")
        self.tree.heading("状态", text="状态")
        self.tree.heading("其它信息", text="其它信息")
        
        self.tree.column("序号", width=50, anchor="center")
        self.tree.column("思考", width=300, anchor="w")
        self.tree.column("工具名称", width=100, anchor="center")
        self.tree.column("状态", width=100, anchor="center")
        self.tree.column("其它信息", width=400, anchor="w")
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_detail_view(self):
        """创建详细信息显示区域"""
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(frame, text="详细信息:").pack(anchor=tk.W, padx=5, pady=5)
        
        self.detail_text = tk.Text(frame, wrap=tk.WORD, height=10)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5)
        self.detail_text.config(state=tk.DISABLED)
    
    def create_statistics_view(self):
        """创建统计信息显示区域"""
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(frame, text="工具使用统计:").pack(anchor=tk.W, padx=5, pady=5)
        
        self.stats_text = tk.Text(frame, wrap=tk.WORD, height=10)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5)
        self.stats_text.config(state=tk.DISABLED)
    
    def load_default_files(self):
        """加载当前目录下的log文件"""
        log_files = [f for f in os.listdir('.') if f.endswith('_model_log.md')]
        if log_files:
            self.file_combobox['values'] = log_files
            if log_files:
                self.file_combobox.current(0)
                self.on_file_selected(None)
    
    def select_file(self):
        """选择单个文件"""
        file_path = filedialog.askopenfilename(filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")])
        if file_path:
            filename = os.path.basename(file_path)
            current_values = list(self.file_combobox['values'])
            if filename not in current_values:
                current_values.append(filename)
                self.file_combobox['values'] = current_values
            self.file_combobox.set(filename)
            self.on_file_selected(None)
    
    def on_file_selected(self, event):
        """文件选择后的处理"""
        filename = self.file_var.get()
        if filename:
            self.current_file = filename
            self.parse_log_file()
            self.update_treeview()
            self.update_statistics()
    
    def parse_log_file(self):
        """解析log文件"""
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.tool_entries = []
            
            # 使用toolName进行分段
            segments = re.split(r'(?=toolName:)', content)
            
            # 处理第一个分段（可能包含思考内容）
            if segments:
                first_segment = segments[0]
                # 查找最后一句非空句子
                lines = [line.strip() for line in first_segment.split('\n') if line.strip()]
                last_thought = lines[-1] if lines else ""
                
                # 处理后续工具分段
                for i, segment in enumerate(segments[1:], 1):
                    # 解析toolName和status
                    tool_name_match = re.search(r'toolName:\s*(.*?)(?=\s*\n|$)', segment)
                    status_match = re.search(r'status:\s*(.*?)(?=\s*\n|$)', segment)
                    
                    tool_name = tool_name_match.group(1).strip() if tool_name_match else "未知"
                    status = status_match.group(1).strip() if status_match else "未知"
                    
                    # 获取其它信息
                    other_info = segment.replace(f'toolName: {tool_name}', '').replace(f'status: {status}', '').strip()
                    
                    # 创建条目
                    entry = {
                        '序号': i,
                        '思考': last_thought,
                        '工具名称': tool_name,
                        '状态': status,
                        '其它信息': other_info,
                        '完整信息': segment.strip()
                    }
                    
                    self.tool_entries.append(entry)
                    
                    # 更新last_thought为当前分段的最后一句非空句子
                    segment_lines = [line.strip() for line in segment.split('\n') if line.strip()]
                    if segment_lines:
                        last_thought = segment_lines[-1]
        
        except Exception as e:
            messagebox.showerror("错误", f"解析文件失败: {str(e)}")
    
    def update_treeview(self):
        """更新treeview显示"""
        # 清空原有内容
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加新内容
        for entry in self.tool_entries:
            self.tree.insert('', tk.END, values=(
                entry['序号'],
                entry['思考'],
                entry['工具名称'],
                entry['状态'],
                entry['其它信息'][:100] + '...' if len(entry['其它信息']) > 100 else entry['其它信息']
            ))
    
    def on_item_selected(self, event):
        """选中条目后的处理"""
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item[0])
            index = int(item['values'][0]) - 1
            if 0 <= index < len(self.tool_entries):
                entry = self.tool_entries[index]
                self.detail_text.config(state=tk.NORMAL)
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.insert(tk.END, f"序号: {entry['序号']}\n")
                self.detail_text.insert(tk.END, f"思考: {entry['思考']}\n")
                self.detail_text.insert(tk.END, f"工具名称: {entry['工具名称']}\n")
                self.detail_text.insert(tk.END, f"状态: {entry['状态']}\n")
                self.detail_text.insert(tk.END, f"其它信息: {entry['其它信息']}\n")
                self.detail_text.config(state=tk.DISABLED)
    
    def update_statistics(self):
        """更新统计信息"""
        if not self.tool_entries:
            return
        
        # 统计工具使用情况
        self.statistics = {}
        for entry in self.tool_entries:
            tool_name = entry['工具名称']
            status = entry['状态']
            
            if tool_name not in self.statistics:
                self.statistics[tool_name] = {
                    'total': 0,
                    'success': 0,
                    'failed': 0,
                    'running': 0
                }
            
            self.statistics[tool_name]['total'] += 1
            if status == 'success':
                self.statistics[tool_name]['success'] += 1
            elif status == 'failed':
                self.statistics[tool_name]['failed'] += 1
            elif status == 'running':
                self.statistics[tool_name]['running'] += 1
        
        # 显示统计信息
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        self.stats_text.insert(tk.END, "工具使用统计:\n")
        self.stats_text.insert(tk.END, "="*50 + "\n")
        
        for tool_name, data in self.statistics.items():
            self.stats_text.insert(tk.END, f"工具名称: {tool_name}\n")
            self.stats_text.insert(tk.END, f"使用次数: {data['total']}\n")
            self.stats_text.insert(tk.END, f"成功: {data['success']}\n")
            self.stats_text.insert(tk.END, f"失败: {data['failed']}\n")
            self.stats_text.insert(tk.END, f"运行中: {data['running']}\n")
            self.stats_text.insert(tk.END, "-"*50 + "\n")
        
        # 总统计
        total_usage = sum(data['total'] for data in self.statistics.values())
        total_success = sum(data['success'] for data in self.statistics.values())
        total_failed = sum(data['failed'] for data in self.statistics.values())
        total_running = sum(data['running'] for data in self.statistics.values())
        
        self.stats_text.insert(tk.END, "\n总统计:\n")
        self.stats_text.insert(tk.END, f"总工具调用次数: {total_usage}\n")
        self.stats_text.insert(tk.END, f"总成功次数: {total_success}\n")
        self.stats_text.insert(tk.END, f"总失败次数: {total_failed}\n")
        self.stats_text.insert(tk.END, f"总运行中次数: {total_running}\n")
        
        self.stats_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ToolAnalyzerApp(root)
    root.mainloop()