#!/usr/bin/env python3
"""
arXiv文献搜索脚本
自动搜索磁电耦合和量子自旋液体相关文献
"""

import argparse
import requests
import feedparser
from datetime import datetime, timedelta
import json
import time
import sys
import os

def setup_encoding():
    """设置编码以支持中文"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def search_arxiv(keywords, max_results=10, days_back=1):
    """
    搜索arXiv文献
    
    Args:
        keywords: 搜索关键词列表
        max_results: 最大返回结果数
        days_back: 搜索过去多少天的文献
    
    Returns:
        文献列表
    """
    # arXiv API URL
    base_url = "http://export.arxiv.org/api/query"
    
    # 构建搜索查询
    query_parts = []
    for keyword in keywords:
        query_parts.append(f'all:"{keyword}"')
    
    query = " OR ".join(query_parts)
    
    # 日期过滤
    if days_back > 0:
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
        query += f" AND submittedDate:[{start_date}000000 TO *]"
    
    # 请求参数
    params = {
        'search_query': query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    try:
        print(f"🔍 搜索arXiv: {query}")
        print(f"📅 时间范围: 最近{days_back}天")
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        # 解析Atom feed
        feed = feedparser.parse(response.content)
        
        papers = []
        for entry in feed.entries:
            paper = {
                'id': entry.id.split('/')[-1],
                'title': entry.title.replace('\n', ' ').strip(),
                'summary': entry.summary.replace('\n', ' ').strip()[:500] + "...",
                'authors': [author.name for author in entry.authors],
                'published': entry.published,
                'updated': entry.updated,
                'pdf_url': None,
                'arxiv_url': None,
                'categories': [tag.term for tag in entry.tags],
                'primary_category': entry.arxiv_primary_category['term'] if hasattr(entry, 'arxiv_primary_category') else None
            }
            
            # 查找PDF链接
            for link in entry.links:
                if link.rel == 'alternate' and link.type == 'text/html':
                    paper['arxiv_url'] = link.href
                elif link.title == 'pdf':
                    paper['pdf_url'] = link.href
            
            papers.append(paper)
        
        return papers
    
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return []

def filter_by_keywords(papers, keywords):
    """根据关键词过滤文献"""
    filtered = []
    for paper in papers:
        # 检查标题和摘要中是否包含关键词
        text = (paper['title'] + ' ' + paper['summary']).lower()
        for keyword in keywords:
            if keyword.lower() in text:
                paper['matched_keyword'] = keyword
                filtered.append(paper)
                break
    
    return filtered

def format_output(papers, output_format='text'):
    """格式化输出"""
    if output_format == 'json':
        return json.dumps(papers, ensure_ascii=False, indent=2)
    
    elif output_format == 'text':
        output = []
        output.append(f"📚 arXiv文献搜索结果 ({len(papers)}篇)")
        output.append("=" * 60)
        
        for i, paper in enumerate(papers, 1):
            output.append(f"\n{i}. {paper['title']}")
            output.append(f"   📍 ID: {paper['id']}")
            output.append(f"   👥 作者: {', '.join(paper['authors'][:3])}" + 
                         ("等" if len(paper['authors']) > 3 else ""))
            output.append(f"   📅 发布时间: {paper['published']}")
            output.append(f"   🏷️ 分类: {', '.join(paper['categories'][:3])}")
            if 'matched_keyword' in paper:
                output.append(f"   🔍 匹配关键词: {paper['matched_keyword']}")
            output.append(f"   📄 PDF: {paper['pdf_url']}")
            output.append(f"   🌐 arXiv: {paper['arxiv_url']}")
            output.append(f"   📝 摘要: {paper['summary'][:300]}...")
        
        return '\n'.join(output)
    
    elif output_format == 'markdown':
        output = []
        output.append(f"# 📚 arXiv文献监控报告")
        output.append(f"**搜索时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**找到文献**: {len(papers)}篇")
        output.append("")
        
        for i, paper in enumerate(papers, 1):
            output.append(f"## {i}. {paper['title']}")
            output.append("")
            output.append(f"**ID**: `{paper['id']}`  ")
            output.append(f"**作者**: {', '.join(paper['authors'][:3])}" + 
                         ("等" if len(paper['authors']) > 3 else ""))
            output.append(f"**发布时间**: {paper['published']}  ")
            output.append(f"**分类**: {', '.join(paper['categories'][:3])}  ")
            if 'matched_keyword' in paper:
                output.append(f"**匹配关键词**: `{paper['matched_keyword']}`  ")
            output.append(f"**PDF**: [下载链接]({paper['pdf_url']})  ")
            output.append(f"**arXiv**: [查看页面]({paper['arxiv_url']})  ")
            output.append("")
            output.append(f"**摘要**:")
            output.append(f"> {paper['summary']}")
            output.append("")
            output.append("---")
            output.append("")
        
        return '\n'.join(output)

def main():
    """主函数"""
    setup_encoding()
    
    parser = argparse.ArgumentParser(description='arXiv文献搜索')
    parser.add_argument('--keywords', nargs='+', 
                       default=['magnetoelectric coupling', 'quantum spin liquid', 'multiferroic', 'topological'],
                       help='搜索关键词')
    parser.add_argument('--max-results', type=int, default=10,
                       help='最大结果数 (默认: 10)')
    parser.add_argument('--days', type=int, default=1,
                       help='搜索过去多少天的文献 (默认: 1)')
    parser.add_argument('--output', choices=['json', 'text', 'markdown'],
                       default='text', help='输出格式')
    parser.add_argument('--filter', action='store_true',
                       help='使用关键词过滤（严格模式）')
    
    args = parser.parse_args()
    
    print(f"🚀 开始搜索arXiv文献...")
    print(f"🔑 关键词: {', '.join(args.keywords)}")
    
    # 搜索文献
    papers = search_arxiv(
        keywords=args.keywords,
        max_results=args.max_results,
        days_back=args.days
    )
    
    if not papers:
        print("❌ 未找到相关文献")
        return
    
    print(f"✅ 找到 {len(papers)} 篇文献")
    
    # 关键词过滤（可选）
    if args.filter:
        filtered_papers = filter_by_keywords(papers, args.keywords)
        print(f"🔍 关键词过滤后: {len(filtered_papers)} 篇")
        papers = filtered_papers
    
    # 输出结果
    output = format_output(papers, args.output)
    print(output)
    
    # 保存到文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"arxiv_results_{timestamp}.{args.output if args.output != 'markdown' else 'md'}"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"\n💾 结果已保存到: {filename}")

if __name__ == "__main__":
    main()