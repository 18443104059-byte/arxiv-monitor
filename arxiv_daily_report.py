#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv每日文献报告生成（简化配置版）
只需要在 KEYWORDS 列表里填写关键词，自动生成 abs 字段查询
"""

import os
import sys
import re
import time
import argparse
import hashlib
import base64
import hmac
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus
from pathlib import Path

import requests

# ==================== 简化配置区 ====================
# 在这里填写您感兴趣的关键词，每行一个
KEYWORDS = [
    "quantum spin liquid",
    "frustrated magnet",
    "pyrochlore",
    "kagome",
    "single crystal growth",
    "magnetoelectric",
    "multiferroic",
    "QSL",
    "geometric frustration"
]

# 组合词最大数量（自动生成两两组合，增加覆盖）
MAX_COMBINE = 2

# 每个主题的目标论文数量
TARGET_COUNT = 5

# 输出目录
OUTPUT_DIR = Path("./reports")
OUTPUT_DIR.mkdir(exist_ok=True)

# 已发送ID记录
SENT_IDS_FILE = Path("./sent_papers.json")
# ===================================================

def load_sent_ids():
    if SENT_IDS_FILE.exists():
        try:
            return set(json.loads(SENT_IDS_FILE.read_text(encoding='utf-8')))
        except:
            return set()
    return set()

def save_sent_ids(ids):
    SENT_IDS_FILE.write_text(json.dumps(list(ids), indent=2), encoding='utf-8')

def generate_queries(keywords, max_combine=2):
    """
    从关键词列表生成查询语句列表
    生成策略：
    - 每个关键词单独作为 abs:"关键词"
    - 每两个关键词组合为 abs:"词1" abs:"词2"
    """
    queries = []
    # 单关键词
    for k in keywords:
        if k.strip():
            queries.append(f'abs:"{k.strip()}"')
    # 两词组合
    if max_combine >= 2:
        for i in range(len(keywords)):
            for j in range(i+1, len(keywords)):
                if keywords[i].strip() and keywords[j].strip():
                    queries.append(f'abs:"{keywords[i].strip()}" abs:"{keywords[j].strip()}"')
    # 去重
    return list(set(queries))

def query_arxiv_raw(query_str, max_results=30):
    base_url = "https://export.arxiv.org/api/query"
    url = f"{base_url}?search_query={quote_plus(query_str)}&sortBy=submittedDate&sortOrder=descending&start=0&max_results={max_results}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text

def parse_arxiv_entry(entry_xml):
    ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
    entry = ET.fromstring(entry_xml)
    title = entry.find('arxiv:title', ns).text.strip()
    summary = entry.find('arxiv:summary', ns).text.strip()
    link = entry.find('arxiv:id', ns).text
    paper_id = link.replace('http://arxiv.org/abs/', 'arxiv:')
    published = entry.find('arxiv:published', ns).text
    pub_dt = datetime.strptime(published[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    authors = [author.find('arxiv:name', ns).text for author in entry.findall('arxiv:author', ns)]
    categories = [cat.get('term') for cat in entry.findall('arxiv:category', ns)]
    return {
        'id': paper_id,
        'title': title,
        'summary': summary,
        'link': link,
        'published': published,
        'authors': authors,
        'categories': categories,
        'pub_dt': pub_dt
    }

def fetch_arxiv_papers(queries, since_dt, target_count):
    collected = []
    seen_ids = set()
    for q in queries:
        if len(collected) >= target_count:
            break
        try:
            xml = query_arxiv_raw(q, max_results=25)
            for entry_xml in xml.split('<entry>')[1:]:
                entry_xml = '<entry>' + entry_xml.split('</entry>')[0] + '</entry>'
                try:
                    paper = parse_arxiv_entry(entry_xml)
                    if paper['pub_dt'] >= since_dt and paper['id'] not in seen_ids:
                        seen_ids.add(paper['id'])
                        collected.append(paper)
                        if len(collected) >= target_count:
                            break
                except Exception as e:
                    continue
        except Exception as e:
            print(f"⚠️ 查询失败: {q[:60]}... {e}")
            continue
    return collected

def generate_report(days_back=1):
    since_dt = datetime.now(timezone.utc) - timedelta(days=days_back)
    queries = generate_queries(KEYWORDS, max_combine=MAX_COMBINE)
    print(f"📅 搜索过去 {days_back} 天")
    print(f"🔍 生成 {len(queries)} 条查询语句")
    all_papers = fetch_arxiv_papers(queries, since_dt, TARGET_COUNT * len(KEYWORDS))  # 粗略设总数

    if not all_papers:
        return "❌ 今日未找到相关文献"

    # 按ID去重（已由fetch内部去重）
    lines = []
    lines.append(f"# 📚 arXiv每日文献监控报告")
    lines.append(f"**报告日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**搜索范围**: 最近 {days_back} 天")
    lines.append(f"**新论文数**: {len(all_papers)} 篇")
    lines.append("")

    for i, p in enumerate(all_papers, 1):
        authors = p['authors'][:2]
        author_str = ', '.join(authors) + ('等' if len(p['authors']) > 2 else '')
        categories = ', '.join(p['categories'][:2])
        lines.append(f"### {i}. {p['title']}")
        lines.append("")
        lines.append(f"**ID**: `{p['id']}`  ")
        lines.append(f"**作者**: {author_str}  ")
        lines.append(f"**发布时间**: {p['published']}  ")
        lines.append(f"**分类**: {categories}  ")
        lines.append(f"**PDF**: [下载链接]({p['link']})  ")
        lines.append(f"**arXiv**: [查看页面]({p['link']})  ")
        lines.append("")
        lines.append(f"**摘要**:")
        summary = p['summary'].replace('\n', ' ')
        lines.append(f"> {summary}")
        lines.append("")

    lines.append("---")
    lines.append("*自动生成于 arXiv 监控系统*")
    return "\n".join(lines)

def save_report(content):
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"arxiv_daily_report_{date_str}.md"
    filepath = OUTPUT_DIR / filename
    filepath.write_text(content, encoding='utf-8')
    return filepath

def send_to_feishu(text, webhook_url, secret=None):
    lines = text.split('\n')
    summary = '\n'.join(lines[:50])
    if len(lines) > 50:
        summary += "\n\n... (报告过长，请查看完整文件)"
    payload = {"msg_type": "text", "content": {"text": summary}}
    if secret:
        timestamp = str(int(time.time()))
        string_to_sign = timestamp + "\n" + secret
        sign = base64.b64encode(hmac.new(string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()).decode('utf-8')
        payload["timestamp"] = timestamp
        payload["sign"] = sign
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 0:
                print("✅ 已发送到飞书")
            else:
                print(f"❌ 飞书返回错误: {result}")
        else:
            print(f"❌ 发送失败 HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ 发送异常: {e}")

def main():
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', buffering=1)
        sys.stderr = open(sys.stderr.fileno(), 'w', encoding='utf-8', buffering=1)

    parser = argparse.ArgumentParser(description='arXiv每日文献报告')
    parser.add_argument('--days', type=int, default=1, help='搜索过去多少天的文献 (默认: 1)')
    parser.add_argument('--output', choices=['markdown', 'text'], default='markdown', help='输出格式')
    parser.add_argument('--save', action='store_true', help='保存报告到文件')
    args = parser.parse_args()

    report = generate_report(days_back=args.days)

    if args.output == 'text':
        text_report = re.sub(r'#+\s*', '', report)
        text_report = re.sub(r'\*\*(.*?)\*\*', r'\1', text_report)
        text_report = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text_report)
        print(text_report)
    else:
        print(report)

    if args.save:
        filepath = save_report(report)
        print(f"\n💾 报告已保存到: {filepath}")

    webhook = os.getenv("FEISHU_WEBHOOK_URL")
    secret = os.getenv("FEISHU_SECRET")
    if webhook:
        send_to_feishu(report, webhook, secret)
    else:
        print("⚠️ 未设置 FEISHU_WEBHOOK_URL，跳过发送")

if __name__ == "__main__":
    main()
