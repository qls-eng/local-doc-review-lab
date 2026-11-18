# -*- coding: utf-8 -*-
"""
本地文档智能审查与摘要 - 基础版
功能：批量读取文件夹内 txt 文档 -> jieba 分词 -> 过滤停用词/单字 -> 词频统计 Top50 -> 词云可视化
"""
import os
import sys
from collections import Counter

import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def load_stopwords(stopwords_file):
    """加载停用词表，每行一个词，UTF-8 编码"""
    stopwords = set()
    if stopwords_file and os.path.exists(stopwords_file):
        try:
            with open(stopwords_file, 'r', encoding='utf-8') as f:
                stopwords = {line.strip() for line in f if line.strip()}
            print(f"[OK] 已加载停用词 {len(stopwords)} 个：{stopwords_file}")
        except Exception as e:
            print(f"[WARN] 停用词表读取失败：{e}，改用内置基础停用词")
    if not stopwords:
        stopwords = {"的", "了", "和", "在", "是", "我", "你", "他", "我们",
                     "他们", "为", "以", "等", "并", "对", "与", "也", "就"}
    return stopwords


def load_user_dict(user_dict):
    """加载自定义专业词典，提升领域词分词准确率"""
    if user_dict and os.path.exists(user_dict):
        try:
            jieba.load_userdict(user_dict)
            print(f"[OK] 已加载自定义词典：{user_dict}")
        except Exception as e:
            print(f"[WARN] 自定义词典加载失败：{e}")


def read_folder(folder_path, stopwords):
    """遍历文件夹，读取所有 txt 文件并分词"""
    if not os.path.isdir(folder_path):
        print(f"[ERROR] 文件夹不存在：{folder_path}")
        return []

    all_words = []
    file_count = 0
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith((".txt", ".md")):
            continue
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            file_count += 1
        except Exception as e:
            print(f"[ERROR] 读取文件 {filename} 失败：{e}")
            continue

        words = jieba.lcut(text)
        # 过滤：长度 > 1、非停用词、非纯数字/符号
        filtered = [w.strip() for w in words
                    if len(w.strip()) > 1 and w not in stopwords and w.strip().isalnum()]
        all_words.extend(filtered)

    print(f"[OK] 共读取 {file_count} 个文件，有效词条 {len(all_words)} 个")
    return all_words


def make_wordcloud(top_words, font_path, out_image):
    """根据 Top N 词频生成词云"""
    wc = WordCloud(
        font_path=font_path,
        width=1000,
        height=800,
        background_color='white',
        max_words=50,
        collocations=False,
    )
    wc.generate_from_frequencies(dict(top_words))
    wc.to_file(out_image)
    print(f"[OK] 词云已保存：{out_image}")


def save_report(top_words, out_csv):
    """输出高频词汇总报告（utf-8-sig：Excel 直接双击打开中文不乱码）"""
    with open(out_csv, 'w', encoding='utf-8-sig') as f:
        f.write("排名,关键词,出现次数\n")
        for i, (word, count) in enumerate(top_words, 1):
            f.write(f"{i},{word},{count}\n")
    print(f"[OK] 汇总报告已保存：{out_csv}")


def analyze(folder_path, font_path, stopwords_file=None, user_dict=None, top_n=50):
    load_user_dict(user_dict)
    stopwords = load_stopwords(stopwords_file)
    all_words = read_folder(folder_path, stopwords)

    if not all_words:
        print("[ERROR] 未提取到有效词汇，请检查文件夹内容或编码")
        return

    counter = Counter(all_words)
    top_words = counter.most_common(top_n)

    print(f"\n===== Top {top_n} 高频词 =====")
    for i, (word, count) in enumerate(top_words, 1):
        print(f"{i:>2}. {word:<10} {count}")

    base = os.path.dirname(os.path.abspath(__file__))
    make_wordcloud(top_words, font_path, os.path.join(base, "document_wordcloud.png"))
    save_report(top_words, os.path.join(base, "report.csv"))


if __name__ == "__main__":
    BASE = os.path.dirname(os.path.abspath(__file__))

    # 中文字体：Windows 用 msyh.ttc；如不存在则自动回退
    FONT_CANDIDATES = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
    ]
    font = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
    if font is None:
        print("[ERROR] 未找到中文字体，词云中文会显示方框")
        sys.exit(1)
    print(f"[OK] 使用字体：{font}")

    analyze(
        folder_path=os.path.join(BASE, "docs"),
        font_path=font,
        stopwords_file=os.path.join(BASE, "stopwords.txt"),
        user_dict=os.path.join(BASE, "user_dict.txt"),
        top_n=50,
    )

    # 展示词云（若在无界面环境运行可注释掉）
    # 【迭代修复】matplotlib 绘图区中文需单独设置字体，否则标题显示为方框
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    if os.path.exists(os.path.join(BASE, "document_wordcloud.png")):
        img = plt.imread(os.path.join(BASE, "document_wordcloud.png"))
        plt.figure(figsize=(10, 8))
        plt.imshow(img)
        plt.axis('off')
        plt.title("本地文档高频词云")
        plt.tight_layout()
        plt.show()
