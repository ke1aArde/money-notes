"""
记账 + 记事本 桌面应用
Python + Tkinter + SQLite
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import db

# 初始化数据库
db.init_db()

# ===== 颜色主题 =====
BG = "#f8f9fa"
SIDEBAR_BG = "#2c3e50"
SIDEBAR_FG = "#ecf0f1"
SIDEBAR_ACTIVE = "#3498db"
CARD_BG = "#ffffff"
TEXT = "#2c3e50"
TEXT_SECONDARY = "#7f8c8d"
ACCENT = "#3498db"
DANGER = "#e74c3c"
SUCCESS = "#27ae60"
WARNING = "#f39c12"
BORDER = "#e0e0e0"

FONT_TITLE = ("Microsoft YaHei", 16, "bold")
FONT_HEADING = ("Microsoft YaHei", 12, "bold")
FONT_BODY = ("Microsoft YaHei", 10)
FONT_SMALL = ("Microsoft YaHei", 9)
FONT_MONO = ("Consolas", 10)

CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "住房", "医疗", "教育", "其他"]


class MoneyApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("记账本+记事本")
        self.window.geometry("1100x700")
        self.window.configure(bg=BG)
        self.window.minsize(900, 600)
        
        # 居中窗口
        self.window.update_idletasks()
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        w, h = 1100, 700
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")
        
        self.current_page = None
        self.current_frame = None
        
        self._build_sidebar()
        self._build_main_area()
        self.show_ledger()  # 默认显示记账页

    def _build_sidebar(self):
        """左侧导航栏"""
        sidebar = tk.Frame(self.window, bg=SIDEBAR_BG, width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo
        tk.Label(
            sidebar, text="MoneyNotes", font=("Microsoft YaHei", 14, "bold"),
            bg=SIDEBAR_BG, fg=SIDEBAR_FG, pady=20
        ).pack()
        
        # 分割线
        tk.Frame(sidebar, bg="#34495e", height=1).pack(fill="x", padx=20, pady=(0, 10))
        
        # 导航按钮
        nav_items = [
            ("记账", "ledger", "💰"),
            ("记事本", "notes", "📝"),
            ("预算", "budget", "📊"),
            ("进度箭头", "tracker", "🎯"),
        ]
        
        self.nav_buttons = {}
        for text, page, icon in nav_items:
            btn = tk.Button(
                sidebar,
                text=f"  {icon}  {text}",
                font=FONT_BODY,
                bg=SIDEBAR_BG, fg=SIDEBAR_FG,
                activebackground=SIDEBAR_ACTIVE, activeforeground="white",
                bd=0, padx=15, pady=12, anchor="w",
                cursor="hand2",
                command=lambda p=page: self._switch_page(p)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[page] = btn
        
        # 底部版本信息
        tk.Label(
            sidebar, text="v1.0 | 硅 & 小硅",
            font=FONT_SMALL, bg=SIDEBAR_BG, fg="#7f8c8d"
        ).pack(side="bottom", pady=15)

    def _build_main_area(self):
        """右侧主内容区"""
        self.main_frame = tk.Frame(self.window, bg=BG)
        self.main_frame.pack(side="left", fill="both", expand=True)

    def _switch_page(self, page):
        """切换页面"""
        for btn_p, btn in self.nav_buttons.items():
            if btn_p == page:
                btn.configure(bg=SIDEBAR_ACTIVE, fg="white")
            else:
                btn.configure(bg=SIDEBAR_BG, fg=SIDEBAR_FG)
        
        if self.current_frame:
            self.current_frame.destroy()
        
        pages = {
            "ledger": self.show_ledger,
            "notes": self.show_notes,
            "budget": self.show_budget,
            "tracker": self.show_tracker,
        }
        pages[page]()

    # ===== 记账页面 =====
    def show_ledger(self):
        frame = tk.Frame(self.main_frame, bg=BG)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame
        
        # 顶部标题栏
        header = tk.Frame(frame, bg=CARD_BG, height=50)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)
        tk.Label(header, text="💰 记账", font=FONT_TITLE, bg=CARD_BG, fg=TEXT).pack(side="left", padx=20)
        
        now = datetime.now()
        self.current_month = now.strftime("%Y-%m")
        month_label = tk.Label(header, text=now.strftime("%Y年%m月"), font=FONT_HEADING, bg=CARD_BG, fg=TEXT_SECONDARY)
        month_label.pack(side="right", padx=20)
        
        # 内容区：左侧表单 + 右侧列表
        content = tk.Frame(frame, bg=BG)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 左侧：添加记录表单
        left_panel = tk.Frame(content, bg=CARD_BG, width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="添加记录", font=FONT_HEADING, bg=CARD_BG, fg=TEXT).pack(pady=(20, 15))
        
        # 类型选择
        type_frame = tk.Frame(left_panel, bg=CARD_BG)
        type_frame.pack(fill="x", padx=20, pady=5)
        self.ledger_type = tk.StringVar(value="expense")
        tk.Radiobutton(type_frame, text="支出", variable=self.ledger_type, value="expense",
                       font=FONT_BODY, bg=CARD_BG, fg=DANGER, activebackground=CARD_BG,
                       selectcolor=CARD_BG).pack(side="left", padx=(0, 30))
        tk.Radiobutton(type_frame, text="收入", variable=self.ledger_type, value="income",
                       font=FONT_BODY, bg=CARD_BG, fg=SUCCESS, activebackground=CARD_BG,
                       selectcolor=CARD_BG).pack(side="left")
        
        # 金额
        tk.Label(left_panel, text="金额", font=FONT_BODY, bg=CARD_BG, fg=TEXT_SECONDARY).pack(anchor="w", padx=20, pady=(10, 0))
        self.amount_entry = tk.Entry(left_panel, font=FONT_BODY, bd=1, relief="solid")
        self.amount_entry.pack(fill="x", padx=20, pady=2)
        
        # 分类
        tk.Label(left_panel, text="分类", font=FONT_BODY, bg=CARD_BG, fg=TEXT_SECONDARY).pack(anchor="w", padx=20, pady=(10, 0))
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        cat_menu = ttk.Combobox(left_panel, textvariable=self.category_var, values=CATEGORIES,
                                 font=FONT_BODY, state="readonly")
        cat_menu.pack(fill="x", padx=20, pady=2)
        
        # 日期
        tk.Label(left_panel, text="日期", font=FONT_BODY, bg=CARD_BG, fg=TEXT_SECONDARY).pack(anchor="w", padx=20, pady=(10, 0))
        self.date_entry = tk.Entry(left_panel, font=FONT_BODY, bd=1, relief="solid")
        self.date_entry.insert(0, now.strftime("%Y-%m-%d"))
        self.date_entry.pack(fill="x", padx=20, pady=2)
        
        # 备注
        tk.Label(left_panel, text="备注", font=FONT_BODY, bg=CARD_BG, fg=TEXT_SECONDARY).pack(anchor="w", padx=20, pady=(10, 0))
        self.note_entry = tk.Entry(left_panel, font=FONT_BODY, bd=1, relief="solid")
        self.note_entry.pack(fill="x", padx=20, pady=2)
        
        # 添加按钮
        tk.Button(
            left_panel, text="+ 添加记录", font=FONT_HEADING,
            bg=ACCENT, fg="white", activebackground="#2980b9", activeforeground="white",
            bd=0, padx=20, pady=10, cursor="hand2",
            command=self._add_ledger_record
        ).pack(pady=20)
        
        # 右侧：记录列表
        right_panel = tk.Frame(content, bg=CARD_BG)
        right_panel.pack(side="left", fill="both", expand=True)
        
        # 筛选栏
        filter_bar = tk.Frame(right_panel, bg=CARD_BG)
        filter_bar.pack(fill="x", padx=20, pady=(15, 5))
        
        self.ledger_filter_type = tk.StringVar(value="全部")
        ttk.Combobox(filter_bar, textvariable=self.ledger_filter_type,
                     values=["全部", "expense", "income"], font=FONT_SMALL,
                     state="readonly", width=8).pack(side="left", padx=(0, 5))
        
        self.ledger_filter_cat = tk.StringVar(value="全部")
        ttk.Combobox(filter_bar, textvariable=self.ledger_filter_cat,
                     values=["全部"] + CATEGORIES, font=FONT_SMALL,
                     state="readonly", width=8).pack(side="left", padx=(0, 10))
        
        tk.Button(filter_bar, text="筛选", font=FONT_SMALL, bg=ACCENT, fg="white",
                  bd=0, padx=10, cursor="hand2",
                  command=self._refresh_ledger).pack(side="left")
        
        # 汇总
        self.ledger_summary = tk.Label(filter_bar, text="", font=FONT_SMALL, bg=CARD_BG, fg=TEXT_SECONDARY)
        self.ledger_summary.pack(side="right")
        
        # 列表（Treeview）
        list_frame = tk.Frame(right_panel, bg=CARD_BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        columns = ("date", "type", "category", "amount", "note")
        self.ledger_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        self.ledger_tree.heading("date", text="日期")
        self.ledger_tree.heading("type", text="类型")
        self.ledger_tree.heading("category", text="分类")
        self.ledger_tree.heading("amount", text="金额")
        self.ledger_tree.heading("note", text="备注")
        self.ledger_tree.column("date", width=100)
        self.ledger_tree.column("type", width=60)
        self.ledger_tree.column("category", width=80)
        self.ledger_tree.column("amount", width=100)
        self.ledger_tree.column("note", width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.ledger_tree.yview)
        self.ledger_tree.configure(yscrollcommand=scrollbar.set)
        self.ledger_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 右键删除菜单
        self.ledger_tree.bind("<Button-3>", self._ledger_right_click)
        
        self._refresh_ledger()

    def _add_ledger_record(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("输入错误", "请输入有效的金额")
            return
        
        db.add_record(
            self.date_entry.get(),
            amount,
            self.category_var.get(),
            self.note_entry.get(),
            self.ledger_type.get()
        )
        self.amount_entry.delete(0, "end")
        self.note_entry.delete(0, "end")
        self._refresh_ledger()

    def _refresh_ledger(self):
        for item in self.ledger_tree.get_children():
            self.ledger_tree.delete(item)
        
        cat = self.ledger_filter_cat.get()
        tp = self.ledger_filter_type.get()
        records = db.get_records(category=cat, record_type=tp, month=self.current_month)
        
        for r in records:
            type_text = "收入" if r["type"] == "income" else "支出"
            amount_text = f"+{r['amount']:.2f}" if r["type"] == "income" else f"-{r['amount']:.2f}"
            tag = "income" if r["type"] == "income" else "expense"
            self.ledger_tree.insert("", "end", values=(
                r["date"], type_text, r["category"], amount_text, r["note"]
            ), tags=(tag,), iid=r["id"])
        
        self.ledger_tree.tag_configure("income", foreground=SUCCESS)
        self.ledger_tree.tag_configure("expense", foreground=DANGER)
        
        income, expense, balance = db.get_monthly_summary(self.current_month)
        self.ledger_summary.config(
            text=f"收入: ¥{income:.2f}  支出: ¥{expense:.2f}  结余: ¥{balance:.2f}"
        )

    def _ledger_right_click(self, event):
        item = self.ledger_tree.identify_row(event.y)
        if item:
            self.ledger_tree.selection_set(item)
            menu = tk.Menu(self.window, tearoff=0)
            menu.add_command(label="删除", command=lambda: self._delete_ledger(item))
            menu.post(event.x_root, event.y_root)

    def _delete_ledger(self, item_id):
        if messagebox.askyesno("确认", "确定要删除这条记录吗？"):
            db.delete_record(int(item_id))
            self._refresh_ledger()

    # ===== 记事本页面 =====
    def show_notes(self):
        frame = tk.Frame(self.main_frame, bg=BG)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame
        
        header = tk.Frame(frame, bg=CARD_BG, height=50)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)
        tk.Label(header, text="记事本", font=FONT_TITLE, bg=CARD_BG, fg=TEXT).pack(side="left", padx=20)
        tk.Button(header, text="+ 新建笔记", font=FONT_BODY, bg=ACCENT, fg="white",
                  bd=0, padx=15, pady=5, cursor="hand2",
                  command=self._new_note).pack(side="right", padx=20)
        
        content = tk.Frame(frame, bg=BG)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 左侧笔记列表
        list_panel = tk.Frame(content, bg=CARD_BG, width=250)
        list_panel.pack(side="left", fill="y", padx=(0, 10))
        list_panel.pack_propagate(False)
        
        # 标签筛选
        tag_frame = tk.Frame(list_panel, bg=CARD_BG)
        tag_frame.pack(fill="x", padx=10, pady=10)
        self.note_tag_filter = tk.StringVar(value="全部")
        self.tag_menu = ttk.Combobox(tag_frame, textvariable=self.note_tag_filter,
                                      font=FONT_SMALL, state="readonly")
        self.tag_menu.pack(fill="x")
        self.tag_menu.bind("<<ComboboxSelected>>", lambda e: self._refresh_notes_list())
        
        self.note_listbox = tk.Listbox(list_panel, font=FONT_BODY, bg=CARD_BG, fg=TEXT,
                                        selectbackground=ACCENT, selectforeground="white",
                                        bd=0, highlightthickness=0)
        self.note_listbox.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        self.note_listbox.bind("<<ListboxSelect>>", self._on_note_select)
        
        # 右侧编辑区
        edit_panel = tk.Frame(content, bg=CARD_BG)
        edit_panel.pack(side="left", fill="both", expand=True)
        
        # 标题
        tk.Label(edit_panel, text="标题", font=FONT_SMALL, bg=CARD_BG, fg=TEXT_SECONDARY).pack(anchor="w", padx=15, pady=(15, 0))
        self.note_title = tk.Entry(edit_panel, font=FONT_HEADING, bd=0, bg="#f8f9fa")
        self.note_title.pack(fill="x", padx=15, pady=2)
        
        # 标签
        tk.Label(edit_panel, text="标签（逗号分隔）", font=FONT_SMALL, bg=CARD_BG, fg=TEXT_SECONDARY).pack(anchor="w", padx=15, pady=(10, 0))
        self.note_tags = tk.Entry(edit_panel, font=FONT_BODY, bd=0, bg="#f8f9fa")
        self.note_tags.pack(fill="x", padx=15, pady=2)
        
        # 编辑区
        edit_bar = tk.Frame(edit_panel, bg=CARD_BG)
        edit_bar.pack(fill="x", padx=15, pady=(15, 5))
        tk.Label(edit_bar, text="支持 Markdown", font=FONT_SMALL, bg=CARD_BG, fg=TEXT_SECONDARY).pack(side="left")
        tk.Button(edit_bar, text="预览", font=FONT_SMALL, bg=ACCENT, fg="white",
                  bd=0, padx=10, command=self._preview_note).pack(side="right", padx=(5, 0))
        tk.Button(edit_bar, text="保存", font=FONT_SMALL, bg=SUCCESS, fg="white",
                  bd=0, padx=10, command=self._save_note).pack(side="right")
        
        self.note_content = tk.Text(edit_panel, font=FONT_MONO, bg="#f8f9fa", fg=TEXT,
                                     bd=0, wrap="word", undo=True)
        self.note_content.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # 删除按钮
        tk.Button(edit_panel, text="🗑 删除笔记", font=FONT_SMALL, bg="white", fg=DANGER,
                  bd=1, padx=10, pady=3, cursor="hand2",
                  command=self._delete_current_note).pack(anchor="e", padx=15, pady=(0, 15))
        
        self.current_note_id = None
        self._refresh_notes_list()

    def _refresh_notes_list(self):
        self.note_listbox.delete(0, "end")
        tag = self.note_tag_filter.get()
        notes = db.get_notes(tag_filter=None if tag == "全部" else tag)
        self._notes_data = notes
        for n in notes:
            self.note_listbox.insert("end", n["title"])
        
        # 更新标签菜单
        all_tags = ["全部"] + db.get_all_tags()
        self.tag_menu["values"] = all_tags
        if self.note_tag_filter.get() not in all_tags:
            self.note_tag_filter.set("全部")

    def _new_note(self):
        self.current_note_id = None
        self.note_title.delete(0, "end")
        self.note_tags.delete(0, "end")
        self.note_content.delete("1.0", "end")
        self.note_listbox.selection_clear(0, "end")

    def _on_note_select(self, event):
        sel = self.note_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        note = self._notes_data[idx]
        self.current_note_id = note["id"]
        self.note_title.delete(0, "end")
        self.note_title.insert(0, note["title"])
        self.note_tags.delete(0, "end")
        self.note_tags.insert(0, note["tags"])
        self.note_content.delete("1.0", "end")
        self.note_content.insert("1.0", note["content"])

    def _save_note(self):
        title = self.note_title.get().strip()
        if not title:
            messagebox.showwarning("提示", "标题不能为空")
            return
        content = self.note_content.get("1.0", "end-1c")
        tags = self.note_tags.get().strip()
        
        if self.current_note_id:
            db.update_note(self.current_note_id, title, content, tags)
        else:
            db.add_note(title, content, tags)
        
        self._refresh_notes_list()
        messagebox.showinfo("提示", "保存成功")

    def _delete_current_note(self):
        if not self.current_note_id:
            return
        if messagebox.askyesno("确认", "确定要删除这条笔记吗？"):
            db.delete_note(self.current_note_id)
            self._new_note()
            self._refresh_notes_list()

    def _preview_note(self):
        content = self.note_content.get("1.0", "end-1c")
        if not content.strip():
            return
        # 简单 Markdown 预览弹窗
        preview = tk.Toplevel(self.window)
        preview.title("Markdown 预览")
        preview.geometry("500x400")
        preview.configure(bg="white")
        
        text = tk.Text(preview, font=FONT_BODY, bg="white", fg=TEXT, wrap="word",
                       padx=20, pady=20, bd=0)
        text.pack(fill="both", expand=True)
        text.insert("1.0", content)
        text.configure(state="disabled")

    # ===== 预算页面 =====
    def show_budget(self):
        frame = tk.Frame(self.main_frame, bg=BG)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame
        
        header = tk.Frame(frame, bg=CARD_BG, height=50)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)
        tk.Label(header, text="预算管理", font=FONT_TITLE, bg=CARD_BG, fg=TEXT).pack(side="left", padx=20)
        
        content = tk.Frame(frame, bg=BG)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 预算设定区
        card = tk.Frame(content, bg=CARD_BG)
        card.pack(fill="x", pady=(0, 15))
        
        tk.Label(card, text="设定月度预算", font=FONT_HEADING, bg=CARD_BG, fg=TEXT).pack(pady=(20, 10))
        
        input_frame = tk.Frame(card, bg=CARD_BG)
        input_frame.pack(pady=(0, 15))
        
        now = datetime.now()
        self.budget_month = tk.StringVar(value=now.strftime("%Y-%m"))
        tk.Label(input_frame, text="月份", font=FONT_BODY, bg=CARD_BG).pack(side="left", padx=(0, 5))
        tk.Entry(input_frame, textvariable=self.budget_month, font=FONT_BODY,
                 width=10, bd=1, relief="solid").pack(side="left", padx=(0, 15))
        
        self.budget_amount = tk.StringVar()
        tk.Label(input_frame, text="预算金额 ¥", font=FONT_BODY, bg=CARD_BG).pack(side="left", padx=(0, 5))
        tk.Entry(input_frame, textvariable=self.budget_amount, font=FONT_BODY,
                 width=12, bd=1, relief="solid").pack(side="left", padx=(0, 10))
        
        tk.Button(input_frame, text="保存", font=FONT_BODY, bg=ACCENT, fg="white",
                  bd=0, padx=20, pady=5, command=self._save_budget).pack(side="left")
        
        # 预算进度显示
        self.budget_progress_frame = tk.Frame(content, bg=BG)
        self.budget_progress_frame.pack(fill="both", expand=True)
        
        self._refresh_budget()

    def _save_budget(self):
        try:
            amount = float(self.budget_amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("输入错误", "请输入有效的预算金额")
            return
        db.set_budget(self.budget_month.get(), amount)
        self._refresh_budget()

    def _refresh_budget(self):
        for w in self.budget_progress_frame.winfo_children():
            w.destroy()
        
        month = self.budget_month.get()
        budget = db.get_budget(month)
        income, expense, balance = db.get_monthly_summary(month)
        
        # 预算概览卡片
        card = tk.Frame(self.budget_progress_frame, bg=CARD_BG)
        card.pack(fill="x")
        
        cards_inner = tk.Frame(card, bg=CARD_BG)
        cards_inner.pack(padx=30, pady=20, fill="x")
        
        # 三个数字卡片
        stats = [
            ("本月预算", f"¥{budget:.2f}", ACCENT),
            ("已消费", f"¥{expense:.2f}", DANGER if expense > budget else SUCCESS),
            ("剩余", f"¥{budget - expense:.2f}", SUCCESS if budget > expense else DANGER),
        ]
        
        for label, value, color in stats:
            s = tk.Frame(cards_inner, bg=CARD_BG)
            s.pack(side="left", padx=(0, 40))
            tk.Label(s, text=label, font=FONT_SMALL, bg=CARD_BG, fg=TEXT_SECONDARY).pack()
            tk.Label(s, text=value, font=("Microsoft YaHei", 24, "bold"), bg=CARD_BG, fg=color).pack()
        
        # 进度条
        bar_frame = tk.Frame(card, bg=CARD_BG)
        bar_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        pct = min(expense / budget * 100, 100) if budget > 0 else 0
        bar_color = DANGER if pct > 90 else (WARNING if pct > 70 else SUCCESS)
        
        tk.Label(bar_frame, text=f"消费进度: {pct:.1f}%", font=FONT_BODY, bg=CARD_BG, fg=TEXT).pack(anchor="w")
        
        bar_outer = tk.Frame(bar_frame, bg=BORDER, height=20)
        bar_outer.pack(fill="x", pady=(5, 0))
        bar_outer.pack_propagate(False)
        
        bar_width = int(pct / 100 * 800)
        if bar_width > 0:
            tk.Frame(bar_outer, bg=bar_color, width=bar_width, height=20).pack(side="left")
        
        if pct >= 100:
            messagebox.showwarning("预算超支", f"{month} 月预算已超支！", parent=self.window)

    # ===== 进度箭头页面 =====
    def show_tracker(self):
        frame = tk.Frame(self.main_frame, bg=BG)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame
        
        header = tk.Frame(frame, bg=CARD_BG, height=50)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)
        tk.Label(header, text="进度箭头", font=FONT_TITLE, bg=CARD_BG, fg=TEXT).pack(side="left", padx=20)
        
        # 项目选择
        self.tracker_project = tk.StringVar(value="记账本开发")
        proj_frame = tk.Frame(header, bg=CARD_BG)
        proj_frame.pack(side="right", padx=20)
        tk.Label(proj_frame, text="项目: ", font=FONT_BODY, bg=CARD_BG).pack(side="left")
        ttk.Combobox(proj_frame, textvariable=self.tracker_project,
                     values=["记账本开发"], font=FONT_SMALL,
                     state="readonly", width=15).pack(side="left")
        
        # 初始化项目阶段
        db.init_tracker_phases("记账本开发", [
            "Phase 1: 环境搭建",
            "Phase 2: Python 入门",
            "Phase 3: 数据库设计",
            "Phase 4: 界面骨架",
            "Phase 5: 记账功能",
            "Phase 6: 记事本功能",
            "Phase 7: 预算管理",
            "Phase 8: 打包发布",
        ])
        
        # 可滚动的箭头画布
        canvas_frame = tk.Frame(frame, bg=BG)
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tracker_canvas = tk.Canvas(canvas_frame, bg=CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.tracker_canvas.yview)
        self.tracker_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.tracker_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tracker_inner = tk.Frame(self.tracker_canvas, bg=CARD_BG)
        self.tracker_canvas.create_window((0, 0), window=self.tracker_inner, anchor="nw", 
                                           tags="inner")
        
        self._draw_tracker()
        
        self.tracker_inner.bind("<Configure>", lambda e: self.tracker_canvas.configure(
            scrollregion=self.tracker_canvas.bbox("all")))

    def _draw_tracker(self):
        for w in self.tracker_inner.winfo_children():
            w.destroy()
        
        phases = db.get_phases(self.tracker_project.get())
        if not phases:
            tk.Label(self.tracker_inner, text="暂无阶段", font=FONT_BODY, bg=CARD_BG).pack(pady=30)
            return
        
        for phase in phases:
            self._draw_phase(phase["id"], phase["phase_name"], phase["completed"],
                             phase["phase_order"], len(phases))

    def _draw_phase(self, phase_id, name, completed, order, total):
        """绘制一个阶段（箭头形状的卡片）"""
        row = tk.Frame(self.tracker_inner, bg=CARD_BG)
        row.pack(fill="x", pady=5, padx=30)
        
        # 状态指示
        color = SUCCESS if completed else ACCENT
        symbol = "✓" if completed else str(order)
        status_bg = SUCCESS if completed else ACCENT
        
        indicator = tk.Frame(row, bg=status_bg, width=36, height=36, cursor="hand2")
        indicator.pack(side="left", padx=(0, 15))
        indicator.pack_propagate(False)
        inner_label = tk.Label(indicator, text=symbol, font=("Microsoft YaHei", 14, "bold"),
                               bg=status_bg, fg="white")
        inner_label.pack(expand=True)
        indicator.bind("<Button-1>", lambda e, pid=phase_id: self._toggle_tracker(pid))
        inner_label.bind("<Button-1>", lambda e, pid=phase_id: self._toggle_tracker(pid))
        
        # 阶段名称
        name_label = tk.Label(
            row, text=name,
            font=("Microsoft YaHei", 12, "bold" if not completed else "overstrike"),
            bg=CARD_BG, fg=SUCCESS if completed else TEXT
        )
        name_label.pack(side="left")
        name_label.bind("<Button-1>", lambda e, pid=phase_id: self._toggle_tracker(pid))
        
        # 不是最后一项时，画箭头连接线
        if order < total:
            arrow = tk.Frame(row, bg=CARD_BG)
            arrow.pack(side="right")
            tk.Label(arrow, text="→", font=("Microsoft YaHei", 16), bg=CARD_BG,
                     fg=SUCCESS if completed else BORDER).pack()
        
        # 进度条
        bar_outer = tk.Frame(self.tracker_inner, bg=BORDER, height=6)
        bar_outer.pack(fill="x", padx=80, pady=(2, 10))
        bar_outer.pack_propagate(False)
        
        bar_w = 600 if completed else 0
        if bar_w > 0:
            tk.Frame(bar_outer, bg=SUCCESS, width=bar_w, height=6).pack(side="left")
        
        # 子任务（如果有）
        subtasks = db.get_subtasks(phase_id)
        for st in subtasks:
            sub_row = tk.Frame(self.tracker_inner, bg=CARD_BG)
            sub_row.pack(fill="x", padx=100, pady=2)
            
            sub_symbol = "✓" if st["completed"] else "○"
            sub_color = SUCCESS if st["completed"] else TEXT_SECONDARY
            tk.Label(sub_row, text=f"    {sub_symbol}  {st['phase_name']}",
                     font=FONT_SMALL, bg=CARD_BG, fg=sub_color).pack(side="left")

    def _toggle_tracker(self, phase_id):
        db.toggle_phase(phase_id)
        self._draw_tracker()


if __name__ == "__main__":
    app = MoneyApp()
    app.window.mainloop()
