# MoneyNotes — PWA 方案

## 架构

```
单 HTML 文件（index.html）
    ├── CSS (嵌入式，~100行)
    ├── JS (嵌入式，~250行)
    │   ├── 全局 Store（localStorage 持久化）
    │   ├── 记账模块（收支 + 分类 + 月度汇总）
    │   ├── 记事本模块（Markdown + 标签筛选）
    │   ├── 预算模块（进度环 + 设定）
    │   └── 待办模块（横向箭头链 + 子任务）
    └── Service Worker（离线可用）
```

## 数据存储

| 键 | 内容 | 示例 |
|---|---|---|
| `l` | 记账记录 JSON | `[{id,date,amount,type,category,note}]` |
| `n` | 笔记 JSON | `[{id,title,content,tags,createdAt,updatedAt}]` |
| `b` | 预算 JSON | `{"2026-06":5000}` |
| `td` | 待办 JSON | `[{id,name,nodes:[{name,done}],subs:[{name,done}]}]` |

全部存 `localStorage`，不清浏览器缓存就不会丢。零后端、零数据库。

## 部署方式

1. **CloudStudio**（当前）：`https://0239717d3ea449ba9df6cf01e2cbdcd6.app.codebuddy.work`
2. **任意静态托管**：扔到 GitHub Pages / Vercel / Netlify 直接用
3. **本地运行**：双击 `index.html` 就能在浏览器打开

## 安装到手机

| 平台 | 步骤 |
|------|------|
| iPhone | Safari 打开 → 分享 → "添加到主屏幕" |
| Android | Chrome 打开 → 三点 → "添加到主屏幕" |

安装后全屏运行，无地址栏，和原生 App 一致。

## 设计规范

- 背景 `#1a1a1a` · 卡片 `#242424` · 分割线 `#333`
- 文字 `#f5f5f5` · 次要 `#999`
- 强调 `#f5f5f5` · 红 `#ff453a` · 绿 `#30d158`
- 圆角 10px · 无 emoji · 纯文字导航
- 底部 4 Tab：记账 / 记事本 / 预算 / 待办

## 待办事项（箭头链）

- 横向滚动箭头链：① → ② → ③ → ④
- 支持多条链（点击"+ 新建待办链"）
- 每条链可无限加节点（点击链尾的 +）
- 每个节点可展开子任务
- 点击节点/子任务切换完成状态

## 优点 vs Flutter

| | PWA | Flutter |
|---|---|---|
| 安装大小 | 28KB | ~100MB SDK |
| 上手时间 | 即开即用 | 半天以上 |
| 更新 | 刷新即更新 | 重新打包 APK |
| 跨平台 | iOS + Android + 桌面 | iOS + Android |
