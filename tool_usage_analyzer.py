
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re

class ToolUsageAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("AI IDE 工具使用统计分析")
        self.root.geometry("1200x800")
        
        # 当前分析的数据
        self.tool_data = []
        self.statistics = {}
        
        self.create_widgets()
        self.load_default_files()
        
    def create_widgets(self):
        # 1. Log文件选择区域
        file_frame = ttk.LabelFrame(self.root, text="Log 文件选择")
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_var = tk.StringVar()
        self.file_combo = ttk.Combobox(file_frame, textvariable=self.file_var, state="readonly")
        self.file_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.file_combo.bind("<<ComboboxSelected>>", self.on_file_selected)
        
        browse_btn = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        analyze_btn = ttk.Button(file_frame, text="分析", command=self.analyze_file)
        analyze_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 2. Treeview 显示区域
        tree_frame = ttk.LabelFrame(self.root, text="工具使用记录")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 定义列
        columns = ("序号", "思考", "工具名称", "状态", "其它信息")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # 设置列宽
        self.tree.heading("序号", text="序号", anchor=tk.CENTER)
        self.tree.heading("思考", text="思考", anchor=tk.W)
        self.tree.heading("工具名称", text="工具名称", anchor=tk.CENTER)
        self.tree.heading("状态", text="状态", anchor=tk.CENTER)
        self.tree.heading("其它信息", text="其它信息", anchor=tk.W)
        
        self.tree.column("序号", width=60, anchor=tk.CENTER)
        self.tree.column("思考", width=200, anchor=tk.W)
        self.tree.column("工具名称", width=120, anchor=tk.CENTER)
        self.tree.column("状态", width=100, anchor=tk.CENTER)
        self.tree.column("其它信息", width=400, anchor=tk.W)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)
        
        # 3. 详细信息显示区域
        detail_frame = ttk.LabelFrame(self.root, text="详细信息")
        detail_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.detail_text = tk.Text(detail_frame, height=8, wrap=tk.WORD)
        self.detail_text.pack(fill=tk.X, padx=5, pady=5)
        
        # 4. 统计信息区域
        stat_frame = ttk.LabelFrame(self.root, text="使用统计")
        stat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.stat_text = tk.Text(stat_frame, height=10, wrap=tk.WORD)
        self.stat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def load_default_files(self):
        # 加载当前目录下的 log 文件
        current_dir = os.getcwd()
        log_files = [f for f in os.listdir(current_dir) if re.match(r'.*_model_log\.md', f)]
        self.file_combo['values'] = log_files
        if log_files:
            self.file_var.set(log_files[0])
            self.analyze_file()
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择 Log 文件",
            filetypes=[("Markdown 文件", "*.md"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_var.set(file_path)
            self.analyze_file()
            
    def on_file_selected(self, event):
        self.analyze_file()
        
    def analyze_file(self):
        file_path = self.file_var.get()
        if not file_path:
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件 {file_path} 不存在")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.parse_content(content)
            self.update_treeview()
            self.update_statistics()
            
        except Exception as e:
            messagebox.showerror("错误", f"分析文件时出错: {str(e)}")
            
    def parse_content(self, content):
        self.tool_data = []
        self.statistics = {}
        
        # 使用 toolName: 进行分段
        segments = re.split(r'(toolName:)', content, flags=re.DOTALL)
        
        # 处理分段，提取思考、工具名称、状态和其它信息
        current_thought = ""
        index = 1
        
        # 遍历所有分段，从第一个 toolName: 开始
        for i in range(1, len(segments), 2):
            # 获取当前分段前的文本作为思考内容来源
            # segments[i-1] 是 toolName: 之前的内容
            if i > 0:
                # 从 toolName: 之前的内容中提取最后一句非空句子作为思考
                pre_content = segments[i-1]
                lines = [line.strip() for line in pre_content.split('\n') if line.strip()]
                if lines:
                    current_thought = lines[-1]
            
            # 组合 toolName: 和后面的内容
            tool_segment = segments[i] + (segments[i+1] if i+1 < len(segments) else "")
            
            # 提取工具名称
            tool_name_match = re.search(r'toolName:\s*(\w+)', tool_segment)
            tool_name = tool_name_match.group(1) if tool_name_match else "未知工具"
            
            # 提取状态
            status_match = re.search(r'status:\s*(\w+)', tool_segment)
            status = status_match.group(1) if status_match else "未知状态"
            
            # 提取其它信息
            other_info = tool_segment.strip()
            
            # 创建工具数据条目
            entry = {
                "序号": index,
                "思考": current_thought.strip(),
                "工具名称": tool_name,
                "状态": status,
                "其它信息": other_info,
                "完整信息": tool_segment.strip()
            }
            
            self.tool_data.append(entry)
            
            # 更新统计信息
            if tool_name not in self.statistics:
                self.statistics[tool_name] = {
                    "total": 0,
                    "success": 0,
                    "failed": 0
                }
            
            self.statistics[tool_name]["total"] += 1
            if status.lower() == "success":
                self.statistics[tool_name]["success"] += 1
            elif status.lower() == "failed" or status.lower() == "error":
                self.statistics[tool_name]["failed"] += 1
            
            index += 1
            
    def update_treeview(self):
        # 清空 treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 添加新数据
        for entry in self.tool_data:
            self.tree.insert("", tk.END, values=(
                entry["序号"],
                entry["思考"],
                entry["工具名称"],
                entry["状态"],
                entry["其它信息"]
            ), tags=(entry["序号"],))
            
    def on_item_selected(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            values = self.tree.item(item, "values")
            index = int(values[0]) - 1
            if 0 <= index < len(self.tool_data):
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.insert(tk.END, self.tool_data[index]["完整信息"])
                
    def update_statistics(self):
        self.stat_text.delete(1.0, tk.END)
        
        if not self.statistics:
            self.stat_text.insert(tk.END, "暂无统计数据")
            return
        
        total_tools = 0
        total_uses = 0
        
        for tool, data in self.statistics.items():
            total_tools += 1
            total_uses += data["total"]
            
            self.stat_text.insert(tk.END, f"工具: {tool}\n")
            self.stat_text.insert(tk.END, f"  使用次数: {data['total']}\n")
            self.stat_text.insert(tk.END, f"  成功次数: {data['success']}\n")
            self.stat_text.insert(tk.END, f"  失败次数: {data['failed']}\n\n")
            
        self.stat_text.insert(tk.END, f"\n总计: {total_tools} 种工具, 共使用 {total_uses} 次")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToolUsageAnalyzer(root)
    root.mainloop()
