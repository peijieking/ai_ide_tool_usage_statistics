import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from collections import defaultdict

class ToolUsageAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("AI编程IDE工具使用统计分析")
        self.root.geometry("1200x800")
        
        # 初始化变量
        self.current_file = None
        self.tool_data = []
        self.stats_data = {}
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.rowconfigure(4, weight=1)
        
        # 第一部分：文件选择
        self.create_file_selection_frame()
        
        # 第二部分：Treeview显示工具信息
        self.create_treeview_frame()
        
        # 第三部分：详细信息显示
        self.create_detail_frame()
        
        # 第四部分：统计信息
        self.create_stats_frame()
        
    def create_file_selection_frame(self):
        """创建文件选择区域"""
        self.file_frame = ttk.LabelFrame(self.main_frame, text="Log文件选择", padding="10")
        self.file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        self.file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.file_frame, text="选择文件:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path_var, state="readonly", width=80)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        self.browse_btn = ttk.Button(self.file_frame, text="浏览", command=self.browse_file)
        self.browse_btn.grid(row=0, column=2, padx=5)
        
        self.analyze_btn = ttk.Button(self.file_frame, text="分析", command=self.analyze_file, state="disabled")
        self.analyze_btn.grid(row=0, column=3, padx=5)
        
    def create_treeview_frame(self):
        """创建Treeview显示区域"""
        self.tree_frame = ttk.LabelFrame(self.main_frame, text="工具使用详情", padding="10")
        self.tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ("序号", "思考", "工具名称", "状态", "其它信息")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        
        # 设置列属性
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=100)
            
        self.tree.column("序号", width=50)
        self.tree.column("思考", width=300)
        self.tree.column("工具名称", width=150)
        self.tree.column("状态", width=100)
        self.tree.column("其它信息", width=400)
        
        # 添加滚动条
        self.tree_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 绑定点击事件
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
    def create_detail_frame(self):
        """创建详细信息显示区域"""
        self.detail_frame = ttk.LabelFrame(self.main_frame, text="详细信息", padding="10")
        self.detail_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        self.detail_frame.columnconfigure(0, weight=1)
        
        self.detail_text = tk.Text(self.detail_frame, wrap=tk.WORD, height=10)
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.detail_scroll = ttk.Scrollbar(self.detail_frame, orient="vertical", command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=self.detail_scroll.set)
        self.detail_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def create_stats_frame(self):
        """创建统计信息区域"""
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="工具使用统计", padding="10")
        self.stats_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.stats_frame.columnconfigure(0, weight=1)
        
        # 统计文本
        self.stats_text = tk.Text(self.stats_frame, wrap=tk.WORD, height=15)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.stats_scroll = ttk.Scrollbar(self.stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=self.stats_scroll.set)
        self.stats_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def browse_file(self):
        """浏览选择log文件"""
        filetypes = [
            ("Markdown Files", "*.md"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            initialdir="c:\\D\\18_trae\\蜜蜂_Buzzer_1223\\ai_ide_tool_usage_statistics\\seed-S80",
            title="选择log文件",
            filetypes=filetypes
        )
        
        if file_path:
            self.current_file = file_path
            self.file_path_var.set(file_path)
            self.analyze_btn.config(state="normal")
            
    def analyze_file(self):
        """分析选定的log文件"""
        if not self.current_file:
            messagebox.showerror("错误", "请先选择要分析的文件")
            return
            
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.parse_log_content(content)
            self.update_treeview()
            self.update_stats()
            messagebox.showinfo("成功", "文件分析完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"分析文件时出错: {str(e)}")
            
    def parse_log_content(self, content):
        """解析log文件内容"""
        self.tool_data = []
        self.stats_data = defaultdict(lambda: {'count': 0, 'success': 0, 'failure': 0, 'other': 0})
        
        # 按toolName:分割，第一个元素是初始思考部分
        parts = re.split(r'(?=toolName:)', content)
        
        # 初始思考部分（第一个工具调用之前的内容）
        initial_thought = parts[0].strip() if parts else ""
        
        # 处理每个工具调用
        for i in range(1, len(parts)):
            block = parts[i]
            if not block.strip():
                continue
                
            # 提取工具名称
            tool_name_match = re.search(r'toolName:\s*(\w+)', block)
            tool_name = tool_name_match.group(1) if tool_name_match else "未知"
            
            # 提取状态
            status_match = re.search(r'status:\s*(\w+)', block)
            status = status_match.group(1) if status_match else "未知"
            
            # 提取思考内容
            # 第一个工具调用使用初始思考部分，后续工具调用使用前一个工具调用块的非工具部分
            if i == 1:
                thought = initial_thought
            else:
                # 找到前一个块中的非工具部分（即上一个工具调用之后，当前工具调用之前的内容）
                prev_block = parts[i-1]
                # 从prev_block中提取工具调用之后的内容
                if tool_name_match:
                    prev_thought_part = prev_block[tool_name_match.end():].strip()
                else:
                    prev_thought_part = prev_block.strip()
                # 找到最后一个非空句子
                sentences = re.split(r'[。！？\n]', prev_thought_part)
                thought = ""
                for sentence in reversed(sentences):
                    sentence = sentence.strip()
                    if sentence and not re.search(r'toolName|status', sentence):
                        thought = sentence
                        break
            
            # 提取其它信息
            other_info = block
            if tool_name_match:
                other_info = other_info[tool_name_match.end():].strip()
            if status_match:
                other_info = other_info[status_match.end():].strip()
            
            # 清理其它信息
            other_info = re.sub(r'^\s*\n+', '', other_info)
            other_info = re.sub(r'\n+\s*$', '', other_info)
            other_info = re.sub(r'\n{2,}', '\n', other_info)
            
            # 添加到工具数据
            self.tool_data.append({
                'index': i,
                'thought': thought,
                'tool_name': tool_name,
                'status': status,
                'other_info': other_info,
                'full_info': block
            })
            
            # 更新统计数据
            self.stats_data[tool_name]['count'] += 1
            if status.lower() == 'success':
                self.stats_data[tool_name]['success'] += 1
            elif status.lower() == 'failure':
                self.stats_data[tool_name]['failure'] += 1
            else:
                self.stats_data[tool_name]['other'] += 1
                
    def update_treeview(self):
        """更新Treeview显示"""
        # 清空现有内容
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 添加新内容
        for data in self.tool_data:
            self.tree.insert('', tk.END, values=(
                data['index'],
                data['thought'],
                data['tool_name'],
                data['status'],
                data['other_info']
            ))
            
    def update_stats(self):
        """更新统计信息"""
        self.stats_text.delete(1.0, tk.END)
        
        if not self.stats_data:
            self.stats_text.insert(tk.END, "没有统计数据")
            return
            
        # 计算总计
        total_count = sum(data['count'] for data in self.stats_data.values())
        total_success = sum(data['success'] for data in self.stats_data.values())
        total_failure = sum(data['failure'] for data in self.stats_data.values())
        total_other = sum(data['other'] for data in self.stats_data.values())
        
        # 写入总计
        self.stats_text.insert(tk.END, "=== 工具使用统计 ===\n\n")
        self.stats_text.insert(tk.END, f"总工具调用次数: {total_count}\n")
        self.stats_text.insert(tk.END, f"成功次数: {total_success}\n")
        self.stats_text.insert(tk.END, f"失败次数: {total_failure}\n")
        self.stats_text.insert(tk.END, f"其他状态次数: {total_other}\n\n")
        
        # 写入每个工具的统计
        self.stats_text.insert(tk.END, "=== 各工具详细统计 ===\n\n")
        for tool_name, data in sorted(self.stats_data.items()):
            self.stats_text.insert(tk.END, f"工具名称: {tool_name}\n")
            self.stats_text.insert(tk.END, f"  调用次数: {data['count']}\n")
            self.stats_text.insert(tk.END, f"  成功次数: {data['success']}\n")
            self.stats_text.insert(tk.END, f"  失败次数: {data['failure']}\n")
            self.stats_text.insert(tk.END, f"  其他状态: {data['other']}\n\n")
            
    def on_tree_select(self, event):
        """处理Treeview选择事件"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        # 获取选中项的索引
        item = self.tree.item(selected_item)
        index = item['values'][0]
        
        # 找到对应的详细信息
        for data in self.tool_data:
            if data['index'] == index:
                self.detail_text.delete(1.0, tk.END)
                # 按照序号、思考、工具名称、状态、其他信息的顺序显示
                detail_content = f"序号: {data['index']}\n"
                detail_content += f"思考: {data['thought']}\n\n"
                detail_content += f"工具名称: {data['tool_name']}\n"
                detail_content += f"状态: {data['status']}\n\n"
                detail_content += f"其他信息:\n{data['other_info']}\n"
                self.detail_text.insert(tk.END, detail_content)
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ToolUsageAnalyzer(root)
    root.mainloop()