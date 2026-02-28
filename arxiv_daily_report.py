#!/usr/bin/env python3
"""
arXiv每日文献报告生成
"""

import argparse
import json
from datetime import datetime, timedelta
import os
import sys

def setup_encoding():
    """设置编码以支持中文"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    
    # 默认配置
    default_config = {
        'keywords': [
            'magnetoelectric coupling',
            'quantum spin liquid',
            'multiferroic',
            'topological insulator',
            'skyrmion',
            'spintronics',
            'condensed matter physics'
        ],
        'categories': ['cond-mat', 'physics'],
        'max_results': 15,
        'output_dir': './reports',
        'timezone': 'Asia/Shanghai'
    }
    
    # 如果配置文件存在则加载
    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        except:
            pass
    
    return default_config

def generate_daily_report(config, days_back=1):
    """生成每日报告"""
    from arxiv_search import search_arxiv, filter_by_keywords, format_output
    
    print(f"📊 生成arXiv每日文献报告")
    print(f"📅 日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🔑 关键词: {', '.join(config['keywords'][:5])}...")
    
    # 搜索文献
    papers = search_arxiv(
        keywords=config['keywords'],
        max_results=config['max_results'],
        days_back=days_back
    )
    
    if not papers:
        return "❌ 今日未找到相关文献"
    
    # 关键词过滤
    filtered_papers = filter_by_keywords(papers, config['keywords'])
    
    # 按关键词分类
    categorized = {}
    for paper in filtered_papers:
        keyword = paper.get('matched_keyword', '其他')
        if keyword not in categorized:
            categorized[keyword] = []
        categorized[keyword].append(paper)
    
    # 生成报告
    report = []
    report.append(f"# 📚 arXiv每日文献监控报告")
    report.append(f"**报告日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**搜索范围**: 最近{days_back}天")
    report.append(f"**找到文献**: {len(filtered_papers)}篇 (共搜索到{len(papers)}篇)")
    report.append("")
    
    # 按关键词分类展示
    for keyword, papers_in_category in categorized.items():
        report.append(f"## 🔍 {keyword} ({len(papers_in_category)}篇)")
        report.append("")
        
        for i, paper in enumerate(papers_in_category, 1):
            report.append(f"### {i}. {paper['title']}")
            report.append("")
            report.append(f"**ID**: `{paper['id']}`  ")
            report.append(f"**作者**: {', '.join(paper['authors'][:2])}" + 
                         ("等" if len(paper['authors']) > 2 else ""))
            report.append(f"**发布时间**: {paper['published']}  ")
            report.append(f"**分类**: {', '.join(paper['categories'][:2])}  ")
            report.append(f"**PDF**: [下载链接]({paper['pdf_url']})  ")
            report.append(f"**arXiv**: [查看页面]({paper['arxiv_url']})  ")
            report.append("")
            report.append(f"**摘要**:")
            report.append(f"> {paper['summary']}")
            report.append("")
    
    # 统计信息
    report.append("## 📊 统计信息")
    report.append("")
    report.append(f"- **总文献数**: {len(filtered_papers)}篇")
    report.append(f"- **关键词分布**:")
    for keyword, papers_in_category in categorized.items():
        report.append(f"  - {keyword}: {len(papers_in_category)}篇")
    
    report.append(f"- **时间范围**: {datetime.now().strftime('%Y-%m-%d')}")
    if days_back > 1:
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        report.append(f"- **搜索区间**: {start_date} 至 {datetime.now().strftime('%Y-%m-%d')}")
    
    report.append("")
    report.append("---")
    report.append("*自动生成于 OpenClaw arXiv监控系统*")
    
    return '\n'.join(report)

def save_report(report, output_format='markdown'):
    """保存报告到文件"""
    # 创建输出目录
    output_dir = './reports'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"arxiv_daily_report_{date_str}.md"
    filepath = os.path.join(output_dir, filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return filepath

def send_to_feishu(report, webhook_url, secret=None):
    """
    发送报告到飞书（支持签名验证）
    :param report: 报告内容（字符串）
    :param webhook_url: 飞书机器人 webhook 地址
    :param secret: 飞书签名密钥（如果开启了签名验证）
    """
    try:
        import requests
    except ImportError:
        print("❌ 未安装 requests 库，无法发送飞书消息")
        return

    # 简化报告内容（飞书消息有长度限制）
    lines = report.split('\n')
    summary = '\n'.join(lines[:50])  # 取前 50 行
    if len(lines) > 50:
        summary += "\n\n... (报告过长，请查看完整文件)"

    payload = {
        "msg_type": "text",
        "content": {
            "text": summary
        }
    }

    # 如果提供了 secret，则添加签名
    if secret:
        import hashlib
        import base64
        import hmac
        import time
        timestamp = str(int(time.time()))
        string_to_sign = timestamp + "\n" + secret
        sign = base64.b64encode(
            hmac.new(string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
        ).decode('utf-8')
        payload["timestamp"] = timestamp
        payload["sign"] = sign

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("✅ 已发送到飞书")
            else:
                print(f"❌ 飞书返回错误: {result}")
        else:
            print(f"❌ 发送失败 HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ 发送异常: {e}")

def main():
    """主函数"""
    setup_encoding()
    
    parser = argparse.ArgumentParser(description='arXiv每日文献报告')
    parser.add_argument('--days', type=int, default=1,
                       help='搜索过去多少天的文献 (默认: 1)')
    parser.add_argument('--output', choices=['markdown', 'text'],
                       default='markdown', help='输出格式')
    parser.add_argument('--save', action='store_true',
                       help='保存报告到文件')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config()
    
    # 生成报告
    report = generate_daily_report(config, args.days)
    
    # 输出报告
    if args.output == 'text':
        # 简化文本格式
        import re
        text_report = re.sub(r'#+\s*', '', report)
        text_report = re.sub(r'\*\*(.*?)\*\*', r'\1', text_report)
        text_report = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text_report)
        print(text_report)
    else:
        print(report)
    
    # 保存报告
    if args.save:
        filepath = save_report(report)
        print(f"\n💾 报告已保存到: {filepath}")

    # 发送到飞书
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    secret = os.getenv("FEISHU_SECRET")   # 获取签名密钥
    if webhook_url:
        send_to_feishu(report, webhook_url, secret)
    else:
        print("⚠️ 未设置 FEISHU_WEBHOOK_URL，跳过发送")

if __name__ == "__main__":
    main()
