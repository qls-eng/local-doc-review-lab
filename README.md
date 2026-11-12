# 本地文档智能审查与摘要（Vibe Coding 实验）

Python 实现的本地文档批量分析原型：读取文件夹内的 txt/md 文档 → jieba 分词 → 停用词与单字过滤 → 词频统计 Top50 → 词云可视化 + CSV 汇总报告。

本仓库同时保留完整的 **Vibe Coding 协作痕迹**（`vibe_coding_log.md`），记录每一轮的 Prompt、AI 产出、实际报错与修复方案，而非只保留最终代码。

## 功能

- 批量遍历目录，支持 `.txt` / `.md`
- 加载自定义专业词典（`user_dict.txt`），提升领域词切分准确率
- 加载停用词表（`stopwords.txt`），过滤无意义词与单字
- 词频统计输出 Top50
- 生成词云图片（白底 1000×800）与高频词 CSV 报告
- 单个文件读取失败不影响整体流程；目录不存在提前返回提示
- 中文字体多级回退（msyh → simhei → simsun）

## 目录结构

```
.
├── analyze_docs.py            # 主程序
├── stopwords.txt              # 停用词表（每行一词，UTF-8）
├── user_dict.txt              # 自定义词典（每行一词，UTF-8）
├── docs/                      # 待分析文档样本
│   ├── 实验说明.txt
│   ├── 智能体笔记.txt
│   └── 工程实践记录.txt
├── report.csv                 # 运行产出：Top50 高频词报告
├── document_wordcloud.png     # 运行产出：词云
├── pycharm运行截图.png          # PyCharm 内运行成功留档
└── vibe_coding_log.md         # Vibe Coding 全流程痕迹记录
```

## 环境与运行

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple jieba wordcloud matplotlib
.venv\Scripts\python.exe analyze_docs.py
```

PyCharm 中：绑定项目 `.venv` 解释器 → 右键 `analyze_docs.py` → 运行。

## 关键坑（实验重点）

| 现象 | 根因 | 解法 |
|---|---|---|
| 词云中文全是方框 | `font_path` 未指定或路径错 | 显式传 `C:\Windows\Fonts\msyh.ttc` |
| 图表标题中文方框 | matplotlib 未设 `rcParams` 字体 | `plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']` |
| 专业词被切碎 | 未加载自定义词典 | `jieba.load_userdict()` |
| IDE 报 ModuleNotFound | 库装到系统 Python，非项目 venv | 一律用 `.venv\Scripts\python.exe -m pip` |
| 换机路径全错 | 硬编码绝对路径 | 基于 `os.path.dirname(os.path.abspath(__file__))` |

> 要点：`wordcloud` 的 `font_path` 只管词云内部文字，matplotlib 的标题/坐标轴走自己的字体配置——**两处都要设**。

## 后续可扩展（Agent 化）

- 对接大模型 API，把关键词与词频交给模型生成审查意见与摘要
- 引入 watchdog 监控文件夹，新增文档自动分析（无人值守）
- 增加蒙特卡洛模拟，对不确定指标做概率预测
