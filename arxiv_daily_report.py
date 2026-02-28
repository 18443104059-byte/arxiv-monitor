#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多源论文监控系统：arXiv + IOP Science (via nsearch)
✅ arXiv 预印本（每日更新）
✅ IOP 正式论文（Japanese Journal of Applied Physics 等）
✅ 支持 QSL / 阻挫磁体 / 磁电耦合 / 单晶生长
✅ DeepSeek 中文摘要 + 飞书推送（支持签名）
"""

import os
import sys
import requests
import json
import time
import hashlib
import base64
import hmac
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re

# ==================== 配置区 ====================
# 从环境变量读取（GitHub Secrets 注入）
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")
FEISHU_SECRET = os.getenv("FEISHU_SECRET")          # 可选，如果开启了签名则必须提供
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not FEISHU_WEBHOOK_URL:
    print("❌ 未设置 FEISHU_WEBHOOK_URL，无法发送飞书消息")
    sys.exit(1)
if not DEEPSEEK_API_KEY:
    print("❌ 未设置 DEEPSEEK_API_KEY，无法翻译摘要")
    sys.exit(1)

# === arXiv 检索策略（使用 abs: 字段，避免语法错误）===
ARXIV_TOPICS = [
    {
        "name": "【arXiv-QSL】",
        "queries": [
            'abs:"quantum spin liquid"',
            'abs:"quantum spin liquid" abs:pyrochlore',
            'abs:QSL abs:"frustrated magnet"',
            'abs:"spin liquid" abs:"geometric frustration"',
            'abs:"kagome" abs:"geometric frustration"'
        ],
        "target_count": 5
    },
    {
        "name": "【arXiv-生长/磁电】",
        "queries": [
            'abs:"single crystal growth" abs:magnet',
            'abs:"flux growth" abs:"quantum magnet"',
            'abs:"magnetoelectric" abs:kagome',
            'abs:multiferroic abs:"frustrated"'
        ],
        "target_count": 3
    }
]

# === IOP nsearch 搜索词 ===
IOP_SEARCH_TERMS = [
    "quantum spin liquid frustrated magnet",
    "single crystal growth kagome pyrochlore",
    "magnetoelectric frustrated quantum magnet",
    "flux growth RuCl3 Herbertsmithite"
]

TIME_WINDOW_HOURS = 168  # 查最近7天
SENT_IDS_FILE = Path(__file__).parent / "sent_papers.json"

# ==================== 工具函数 ====================
def load_sent_ids():
    if SENT_IDS_FILE.exists():
        try:
            return set(json.loads(SENT_IDS_FILE.read_text(encoding="utf-8")))
        except:
            return set()
    return set()

def save_sent_ids(ids):
    SENT_IDS_FILE.write_text(json.dumps(list(ids), indent=2), encoding="utf-8")

# --- arXiv 相关 ---
def query_arxiv_raw(query_str, max_results=30, timeout=30):
    base_url = "https://export.arxiv.org/api/query"
    url = f"{base_url}?search_query={quote_plus(query_str)}&sortBy=submittedDate&sortOrder=descending&start=0&max_results={max_results}"
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text

def parse_arxiv_xml(xml_text, since_dt):
    entries = []
    for entry in xml_text.split("<entry>")[1:]:
        try:
            title = entry.split("<title>")[1].split("</title>")[0].strip()
            summary = entry.split("<summary>")[1].split("</summary>")[0].strip()
            link = entry.split('<link href="')[1].split('"')[0]
            paper_id = "arxiv:" + link.split("/abs/")[-1]
            published = entry.split("<published>")[1].split("</published>")[0]
            pub_dt = datetime.strptime(published[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
            if pub_dt >= since_dt:
                entries.append({"id": paper_id, "title": title, "summary": summary, "link": link})
        except:
            continue
    return entries

# --- IOP nsearch 抓取 ---
def fetch_iop_nsearch_papers(keywords, since_dt):
    base_url = "https://iopscience.iop.org/nsearch"
    params = {"terms": keywords, "sort": "publishDate"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        papers = []
        for item in soup.select('div.list-item'):
            try:
                title_tag = item.select_one('h3 a')
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                link = "https://iopscience.iop.org" + title_tag['href']
                abs_tag = item.select_one('.abstract')
                abstract = abs_tag.get_text(strip=True) if abs_tag else ""
                date_tag = item.select_one('.pub-date')
                if not date_tag:
                    continue
                date_str = date_tag.get_text()
                match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', date_str)
                if not match:
                    continue
                day, month, year = match.groups()
                pub_date = datetime.strptime(f"{day} {month} {year}", "%d %b %Y").replace(tzinfo=timezone.utc)
                if pub_date >= since_dt:
                    paper_id = f"iop:{link.split('/')[-1]}"
                    papers.append({
                        "id": paper_id,
                        "title": title,
                        "summary": abstract,
                        "link": link
                    })
            except Exception:
                continue
        return papers
    except Exception as e:
        print(f"⚠️ IOP nsearch 抓取失败 ({keywords}): {e}")
        return []

# --- 摘要翻译 ---
def summarize_with_deepseek(text):
    if not text.strip():
        return "【摘要】无摘要。"
    prompt = (
        "你是一位顶尖凝聚态物理学家。请将以下英文论文摘要翻译成专业、简洁的中文，并提炼出核心创新点（100字以内）。"
        f"\n\n{text}\n\n"
        "输出格式：【中文摘要】... 【核心创新】..."
    )
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "deepseek-coder", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=20)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"【摘要】{text[:200]}..."
    except:
        return f"【摘要】{text[:200]}..."

# --- 飞书推送（支持签名）---
def send_to_feishu(title, deep_summary, link, tag):
    # 构造飞书富文本消息
    content = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": f"{tag} {title}",
                    "content": [
                        [{"tag": "text", "text": deep_summary}],
                        [{"tag": "a", "text": "查看全文", "href": link}]
                    ]
                }
            }
        }
    }
    # 如果设置了签名密钥，添加签名
    if FEISHU_SECRET:
        timestamp = str(int(time.time()))
        string_to_sign = timestamp + "\n" + FEISHU_SECRET
        sign = base64.b64encode(
            hmac.new(string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
        ).decode('utf-8')
        content["timestamp"] = timestamp
        content["sign"] = sign
    try:
        resp = requests.post(FEISHU_WEBHOOK_URL, json=content, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 0:
                print(f"✅ 已发送到飞书: {title[:30]}...")
            else:
                print(f"❌ 飞书返回错误: {result}")
        else:
            print(f"❌ 发送失败 HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ 发送异常: {e}")

# ==================== 主程序 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 启动多源论文监控系统")
    print("📚 来源：arXiv + IOP Science (nsearch)")
    print("=" * 60)
    
    sent_ids = load_sent_ids()
    all_new_papers = []
    since_dt = datetime.now(timezone.utc) - timedelta(hours=TIME_WINDOW_HOURS)
    
    # 1. 抓取 arXiv
    for topic in ARXIV_TOPICS:
        print(f"\n🔍 检索 arXiv: {topic['name']}")
        collected = 0
        for q in topic["queries"]:
            if collected >= topic["target_count"]:
                break
            try:
                xml = query_arxiv_raw(q, max_results=25)
                papers = parse_arxiv_xml(xml, since_dt)
                for p in papers:
                    if p["id"] not in sent_ids and p["id"] not in [x["id"] for x in all_new_papers]:
                        print(f"  🧠 arXiv: {p['title'][:50]}...")
                        p["deep_summary"] = summarize_with_deepseek(p["summary"])
                        p["tag"] = topic["name"]
                        all_new_papers.append(p)
                        sent_ids.add(p["id"])
                        collected += 1
                        if collected >= topic["target_count"]:
                            break
            except Exception as e:
                print(f"  ⚠️ arXiv 查询失败: {e}")
        print(f"  ✅ 获取 {collected} 篇")

    # 2. 抓取 IOP
    print("\n📡 搜索 IOP Science (nsearch) ...")
    iop_count = 0
    for terms in IOP_SEARCH_TERMS:
        iop_papers = fetch_iop_nsearch_papers(terms, since_dt)
        for p in iop_papers:
            if p["id"] not in sent_ids:
                print(f"  🧠 IOP: {p['title'][:50]}...")
                p["deep_summary"] = summarize_with_deepseek(p["summary"])
                p["tag"] = "【IOP】"
                all_new_papers.append(p)
                sent_ids.add(p["id"])
                iop_count += 1
    print(f"  ✅ IOP 共获取 {iop_count} 篇")
    
    total = len(all_new_papers)
    print(f"\n📬 总共找到新论文: {total} 篇")
    
    # 3. 推送
    for p in all_new_papers:
        send_to_feishu(p["title"], p["deep_summary"], p["link"], p["tag"])
    
    save_sent_ids(sent_ids)
    print(f"\n✅ 任务完成！已记录 {len(sent_ids)} 篇论文。")
