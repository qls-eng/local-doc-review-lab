# Vibe Coding 全流程痕迹记录

> 实验：本地文档智能审查与摘要
> 记录时间：2026-11-12
> 执行环境：Windows / Python 3.13.16 / PyCharm 2026.2.3（D:\PyCharm 2026.2.3）
> 项目目录：`C:\Users\Lenovo\Doubao\chats\2026-11-12\new-chat-1\doc_agent_demo`

本文件保留完整的人机协作轨迹：**人定边界 → 写结构化 Prompt → AI 产代码 → 本地运行报错 → 报错回灌修复 → 分模块迭代**。所有代码、报错原文均为实际运行结果，非示意。

---

## 痕迹总览（5 轮）

| 轮次 | 触发方式 | 输入（人） | 输出（AI/程序） | 结果 |
|---|---|---|---|---|
| R1 | 结构化 Prompt | 需求边界 + 技术约束 | `analyze_docs.py` 完整代码 | 代码落地 |
| R2 | 环境事实 | Python 3.13.16，无 jieba/wordcloud | pip 安装清单 | 依赖就绪 |
| R3 | 实跑报错 | 直接执行脚本 | Top50 词频 + 词云 PNG | 主链路跑通 |
| R4 | 报错回灌 | `Glyph missing from font` 警告 | 补 `plt.rcParams` 中文字体 | 中文标题修复 |
| R5 | 迭代指令 | 分模块增强（报告输出/异常兜底） | `report.csv` + 分层异常处理 | 交付完整 |
| R6 | 换到 PyCharm | 用本人 IDE 打开项目、配解释器 | `.venv` + 镜像装依赖 | IDE 内跑通，退出码 0 |

---

## R1：需求边界与结构化 Prompt（人的工作）

**必须先由人确定的四件事**（不交给 AI 猜）：

- 输入：`docs/` 下的 `.txt`/`.md`；`stopwords.txt`；`user_dict.txt`
- 处理：目录遍历 → 文本清洗 → 加载词典 → jieba 分词 → 过滤停用词与单字 → 词频统计
- 输出：Top50 词云 `document_wordcloud.png`；高频词报告 `report.csv`
- 约束：中文字体必须显式指定；文件读取异常不得中断整体流程

**实际下发给 AI 的 Prompt 原文：**

```
需求背景：开发一个本地文档分析工具，批量处理文件夹中的 txt 文档，提取高频词并生成词云。
明确约束：
1. 使用 os 遍历指定目录下所有 .txt / .md 文件。
2. 使用 jieba 分词，支持加载自定义词典 user_dict.txt 与停用词表 stopwords.txt。
3. 使用 wordcloud 生成词云，显式指定中文字体路径，白底，尺寸 1000x800。
4. 代码需含详细注释，并处理文件读取异常（单个文件失败不影响整体）。
输出要求：完整 Python 代码 + 停用词表/自定义词典的配置说明。
```

> 关键点：Prompt 里没有出现"帮我做个文档分析"这种模糊表述，而是把**输入路径、库选型、参数、异常策略、输出物**全部固化。这是 Vibe Coding 不返工的前提。

**AI 产出**：`analyze_docs.py`（函数化拆分：`load_stopwords` / `load_user_dict` / `read_folder` / `make_wordcloud` / `save_report` / `analyze`）。

---

## R2：环境事实核查（AI 产出前先验证，不假设）

实际执行的探测命令与返回：

```powershell
$PSVersionTable.PSVersion   # 7.6.4
python --version            # Python 3.13.16
python -c "import jieba, wordcloud, matplotlib"
```

**报错原文：**

```
ModuleNotFoundError: No module named 'jieba'
```

**处置：**

```powershell
python -m pip install jieba wordcloud matplotlib
# 实际安装结果：matplotlib-3.11.2  wordcloud-1.9.6  contourpy-1.4.0  cycler-0.12.1  python-dateutil-4.0.0
```

> 痕迹要点：AI 生成的代码能不能跑，取决于本机依赖。**先探测、再安装，不凭空假设环境已就绪。**

---

## R3：首次实跑（主链路验证）

```powershell
$env:MPLBACKEND='Agg'; python analyze_docs.py
```

**实际输出（节选）：**

```
[OK] 使用字体：C:\Windows\Fonts\msyh.ttc
[OK] 已加载自定义词典：...\user_dict.txt
[OK] 已加载停用词 46 个：...\stopwords.txt
[OK] 共读取 3 个文件，有效词条 345 个

===== Top 50 高频词 =====
 1. 文档         7
 2. 能力         7
 3. 词频统计       5
 4. 文本         4
 5. 分词         4
 6. 词云         4
 7. 可视化        4
 ...
[OK] 词云已保存：...\document_wordcloud.png
[OK] 汇总报告已保存：...\report.csv
```

**产物核对：**

| 文件 | 大小 | 说明 |
|---|---|---|
| `document_wordcloud.png` | 187,652 B | 词云图，白底 1000×800 |
| `report.csv` | 711 B | 排名/关键词/出现次数字段 |
| `docs/` | — | 3 篇样本 txt |

> 痕迹要点：**跑通 ≠ 没问题**。同一轮输出里已经埋了下一个待修的坑（见 R4）。

---

## R4：报错回灌修复（中文字体坑）

**实际报错（Warning 原文，重复多行）：**

```
UserWarning: Glyph 26412 (\N{CJK UNIFIED IDEOGRAPH-672C}) missing from font(s) DejaVu Sans.
  plt.tight_layout()
UserWarning: Glyph 25991 (\N{CJK UNIFIED IDEOGRAPH-6587}) missing from font(s) DejaVu Sans.
  plt.title("本地文档高频词云") → 渲染为方框
```

**归因**：`wordcloud` 的 `font_path` 只作用于**词云内部文字**；`matplotlib` 的**标题/坐标轴**走自己的 `rcParams` 字体，默认 DejaVu Sans 无中文字形。

**修复（R4 迭代指令 → AI 给出的最小改动）：**

```python
# 【迭代修复】matplotlib 绘图区中文需单独设置字体，否则标题显示为方框
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
```

**修复后重跑：** Glyph 警告全部消失，仅剩 `FigureCanvasAgg is non-interactive`（这是无界面模式的正常提示，非错误）。

> 痕迹要点：这是**两个独立字体通道**，只设一个必踩坑。实验指导书说"必须指定中文字体"其实是**两处**都要设。

---

## R5：分模块迭代增强

按模块追加，不推翻已有逻辑：

| 迭代项 | 指令内容 | 落地位置 |
|---|---|---|
| 高频词报告 | 增加 Top50 输出为 CSV | `save_report()` |
| 单文件异常隔离 | 单文件读失败不中断整体 | `read_folder()` 的 `try/except + continue` |
| 路径不存在前置校验 | 文件夹缺失直接返回提示 | `read_folder()` 开头 `os.path.isdir` |
| 字体多级回退 | msyh → simhei → simsun 自动探测 | `FONT_CANDIDATES` |
| 词性/符号过滤 | 去掉纯符号与单字 | `w.strip().isalnum()` 与 `len > 1` |

---

## 复现步骤（PyCharm 内）

1. 打开项目目录 `doc_agent_demo`
2. 解释器选择装有 jieba/wordcloud 的 Python 3.13
3. 右键 `analyze_docs.py` → Run
4. 控制台输出 Top50；弹出的 Matplotlib 窗口显示词云；同目录生成 PNG 与 CSV

---

## 踩坑清单（可复用到同类实验）

| 现象 | 根因 | 解法 |
|---|---|---|
| 词云中文全是方框 | `font_path` 未指定或路径错 | 显式传 `msyh.ttc` 绝对路径 |
| 标题/坐标轴中文方框 | 未设 `plt.rcParams` | 单独设 `font.sans-serif` |
| 分词把专业词切碎 | 未加载自定义词典 | `jieba.load_userdict()`，每行一词 UTF-8 |
| 单文件损坏导致整体崩 | 无 per-file 异常隔离 | `try/except` + `continue` |
| 无界面环境 `plt.show()` 卡住 | 后端非交互 | `MPLBACKEND=Agg`，改为读回图片显示 |
| 换电脑路径全错 | 硬编码绝对路径 | 一律基于 `os.path.dirname(os.path.abspath(__file__))` |

---

## R6：PyCharm 内实操（同一份代码，换到本人 IDE）

**环境事实：**

- PyCharm 2026.2.3，安装在 `D:\PyCharm 2026.2.3`
- 打开项目时提示 `无解释器`，需先配解释器
- 交付时选择"生成新的 Virtualenv"，基础解释器 Python 3.14，落盘 `.venv`

**依赖安装（用户提示改走镜像，实测有效）：**

```powershell
& .\.venv\Scripts\python.exe -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple `
    jieba wordcloud matplotlib
# 结果：jieba-0.42.1 wordcloud-1.9.6 matplotlib-3.11.2 numpy-2.5.4 pillow-13.0.0
```

**运行方式：** 项目树右键 `analyze_docs.py` → 运行 'analyze_docs' → 使用 `.venv` 解释器

**实际运行结果（PyCharm Run 窗口）：**

```
[OK] 使用字体：C:\Windows\Fonts\msyh.ttc
[OK] 已加载停用词 46 个
[OK] 共读取 3 个文件，有效词条 345 个
...
[OK] 词云已保存：...\document_wordcloud.png
[OK] 汇总报告已保存：...\report.csv
进程已结束，退出代码为 0
```

词云在 PyCharm 的"绘图"标签页正常显示，标题「本地文档高频词云」中文未变方框（R4 修复生效）。

**界面留档：** `pycharm运行截图.png`

**踩坑补充（IDE 侧）：**

| 现象 | 根因 | 解法 |
|---|---|---|
| 底栏显示"无解释器" | 新打开的项目未绑定 SDK | 右下角解释器 → 添加本地解释器 → 生成 venv |
| 命令行装了库，IDE 里仍报 ModuleNotFound | 装到了系统 Python，而非项目 venv | 一律用 `.venv\Scripts\python.exe -m pip` |
| 打开项目弹出"信任项目"对话框 | 非信任目录限制执行 | 信任项目；顺带**取消**"添加到 Defender 排除列表"（不改动系统安全配置） |

---

## 产物清单

```
doc_agent_demo/
├── analyze_docs.py            # 主程序（含 R4 修复与 R5 增强）
├── stopwords.txt              # 停用词表，46 条，UTF-8
├── user_dict.txt              # 自定义词典，20 个专业词，UTF-8
├── docs/
│   ├── 实验说明.txt
│   ├── 智能体笔记.txt
│   └── 工程实践记录.txt
├── report.csv                 # Top50 高频词报告
├── document_wordcloud.png     # 词云可视化
├── pycharm运行截图.png          # PyCharm 内运行成功留档
├── .venv/                     # 项目虚拟环境（Python 3.14 + 三个依赖）
└── vibe_coding_log.md         # 本文件：完整协作痕迹
```
