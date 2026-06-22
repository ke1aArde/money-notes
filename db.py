"""
数据库模块 - 管理所有 SQLite 操作
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")


def get_conn():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 让查询结果可以用列名访问
    return conn


def init_db():
    """初始化所有表"""
    conn = get_conn()
    c = conn.cursor()
    
    # 记账表
    c.execute("""
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,           -- 日期 YYYY-MM-DD
            amount REAL NOT NULL,          -- 金额
            category TEXT NOT NULL,        -- 分类：餐饮/交通/购物/娱乐/住房/医疗/教育/其他
            note TEXT DEFAULT '',          -- 备注
            type TEXT NOT NULL,            -- income 或 expense
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    
    # 笔记表
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            tags TEXT DEFAULT '',          -- 逗号分隔的标签
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    
    # 预算表
    c.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year_month TEXT NOT NULL UNIQUE, -- 2026-06
            amount REAL NOT NULL
        )
    """)
    
    # 进度箭头系统表
    c.execute("""
        CREATE TABLE IF NOT EXISTS tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            phase_name TEXT NOT NULL,
            phase_order INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            parent_id INTEGER DEFAULT 0,   -- 0=主阶段，>0=属于哪个主阶段的子任务
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    
    conn.commit()
    conn.close()


# ===== 记账操作 =====

def add_record(date, amount, category, note, record_type):
    """添加一条收支记录"""
    conn = get_conn()
    conn.execute(
        "INSERT INTO ledger (date, amount, category, note, type) VALUES (?, ?, ?, ?, ?)",
        (date, amount, category, note, record_type)
    )
    conn.commit()
    conn.close()


def get_records(category=None, record_type=None, month=None):
    """查询记录，支持按分类、类型、月份筛选"""
    conn = get_conn()
    sql = "SELECT * FROM ledger WHERE 1=1"
    params = []
    
    if category and category != "全部":
        sql += " AND category = ?"
        params.append(category)
    if record_type and record_type != "全部":
        sql += " AND type = ?"
        params.append(record_type)
    if month:
        sql += " AND strftime('%Y-%m', date) = ?"
        params.append(month)
    
    sql += " ORDER BY date DESC, id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def delete_record(record_id):
    """删除一条记录"""
    conn = get_conn()
    conn.execute("DELETE FROM ledger WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def get_monthly_summary(month):
    """获取月度汇总：总收入、总支出、结余"""
    conn = get_conn()
    income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM ledger WHERE type='income' AND strftime('%Y-%m', date) = ?",
        (month,)
    ).fetchone()[0]
    expense = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM ledger WHERE type='expense' AND strftime('%Y-%m', date) = ?",
        (month,)
    ).fetchone()[0]
    conn.close()
    return income, expense, income - expense


# ===== 笔记操作 =====

def add_note(title, content="", tags=""):
    """新建笔记"""
    conn = get_conn()
    conn.execute(
        "INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)",
        (title, content, tags)
    )
    conn.commit()
    conn.close()


def get_notes(tag_filter=None):
    """获取所有笔记，可按标签筛选"""
    conn = get_conn()
    if tag_filter:
        rows = conn.execute(
            "SELECT * FROM notes WHERE tags LIKE ? ORDER BY updated_at DESC",
            (f"%{tag_filter}%",)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM notes ORDER BY updated_at DESC"
        ).fetchall()
    conn.close()
    return rows


def update_note(note_id, title, content, tags):
    """更新笔记"""
    conn = get_conn()
    conn.execute(
        "UPDATE notes SET title=?, content=?, tags=?, updated_at=datetime('now','localtime') WHERE id=?",
        (title, content, tags, note_id)
    )
    conn.commit()
    conn.close()


def delete_note(note_id):
    """删除笔记"""
    conn = get_conn()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


def get_all_tags():
    """获取所有标签"""
    conn = get_conn()
    rows = conn.execute("SELECT tags FROM notes WHERE tags != ''").fetchall()
    conn.close()
    tags = set()
    for row in rows:
        for t in row["tags"].split(","):
            t = t.strip()
            if t:
                tags.add(t)
    return sorted(tags)


# ===== 预算操作 =====

def set_budget(year_month, amount):
    """设定或更新预算"""
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO budget (year_month, amount) VALUES (?, ?)",
        (year_month, amount)
    )
    conn.commit()
    conn.close()


def get_budget(year_month):
    """获取某月的预算"""
    conn = get_conn()
    row = conn.execute(
        "SELECT amount FROM budget WHERE year_month = ?", (year_month,)
    ).fetchone()
    conn.close()
    return row["amount"] if row else 0


# ===== 进度跟踪操作 =====

def init_tracker_phases(project_name, phases):
    """初始化项目阶段"""
    conn = get_conn()
    for order, name in enumerate(phases, 1):
        conn.execute(
            "INSERT OR IGNORE INTO tracker (project_name, phase_name, phase_order) VALUES (?, ?, ?)",
            (project_name, name, order)
        )
    conn.commit()
    conn.close()


def get_phases(project_name):
    """获取某项目的所有阶段"""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM tracker WHERE project_name=? AND parent_id=0 ORDER BY phase_order",
        (project_name,)
    ).fetchall()
    conn.close()
    return rows


def toggle_phase(phase_id):
    """切换阶段的完成状态"""
    conn = get_conn()
    row = conn.execute("SELECT completed FROM tracker WHERE id=?", (phase_id,)).fetchone()
    if row:
        new_status = 0 if row["completed"] else 1
        conn.execute("UPDATE tracker SET completed=? WHERE id=?", (new_status, phase_id))
        conn.commit()
    conn.close()


def add_subtask(phase_id, name):
    """给阶段添加子任务"""
    conn = get_conn()
    parent = conn.execute("SELECT phase_order, project_name FROM tracker WHERE id=?", (phase_id,)).fetchone()
    if parent:
        count = conn.execute(
            "SELECT COUNT(*) FROM tracker WHERE parent_id=?", (phase_id,)
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO tracker (project_name, phase_name, phase_order, parent_id) VALUES (?, ?, ?, ?)",
            (parent["project_name"], name, count + 1, phase_id)
        )
        conn.commit()
    conn.close()


def get_subtasks(phase_id):
    """获取某阶段的子任务"""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM tracker WHERE parent_id=? ORDER BY phase_order", (phase_id,)
    ).fetchall()
    conn.close()
    return rows


def toggle_subtask(task_id):
    """切换子任务完成状态"""
    toggle_phase(task_id)  # 共用同一逻辑
