#!/usr/bin/env python3
"""
真实arXiv API测试脚本
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import time

def search_arxiv_real(query, max_results=5):
    """使用真实arXiv API搜索"""
    
    # arXiv API基础URL
    base_url = "http://export.arxiv.org/api/query"
    
    # 构建查询参数
    params = {
        'search_query': f'all:{query}',
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    # 编码URL
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"
    
    print(f"正在搜索: {query}")
    print(f"API URL: {url}")
    print("-" * 60)
    
    try:
        # 发送请求
        req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw/1.0'})
        response = urllib.request.urlopen(req, timeout=30)
        xml_data = response.read().decode('utf-8')
        
        # 解析XML
        root = ET.fromstring(xml_data)
        
        # Atom命名空间
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # 获取总结果数
        total_results = root.find('atom:opensearch:totalResults', ns)
        if total_results is not None:
            print(f"找到文献: {total_results.text} 篇")
        
        # 解析条目
        entries = root.findall('atom:entry', ns)
        results = []
        
        for i, entry in enumerate(entries[:max_results]):
            # 提取标题
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip() if title_elem is not None else "无标题"
            
            # 提取作者
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text)
            
            # 提取摘要
            summary_elem = entry.find('atom:summary', ns)
            summary = summary_elem.text.strip() if summary_elem is not None else "无摘要"
            
            # 提取发布时间
            published_elem = entry.find('atom:published', ns)
            published = published_elem.text[:10] if published_elem is not None else "未知"
            
            # 提取arXiv ID和链接
            id_elem = entry.find('atom:id', ns)
            arxiv_id = id_elem.text if id_elem is not None else ""
            
            # 提取PDF链接
            pdf_link = ""
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_link = link.get('href')
                    break
            
            # 构建结果
            result = {
                'index': i + 1,
                'title': title,
                'authors': authors[:3],  # 只显示前3位作者
                'published': published,
                'arxiv_id': arxiv_id,
                'pdf_link': pdf_link,
                'summary_preview': summary[:200] + "..." if len(summary) > 200 else summary
            }
            results.append(result)
            
            # 打印结果
            print(f"\n{i+1}. {title}")
            print(f"   作者: {', '.join(authors[:3])}{'等' if len(authors) > 3 else ''}")
            print(f"   发布时间: {published}")
            print(f"   arXiv: {arxiv_id}")
            if pdf_link:
                print(f"   PDF: {pdf_link}")
            print(f"   摘要预览: {result['summary_preview']}")
        
        return results
        
    except Exception as e:
        print(f"❌ API请求失败: {e}")
        print("可能的原因:")
        print("1. 网络连接问题")
        print("2. arXiv API暂时不可用")
        print("3. 请求超时")
        return []

def main():
    """主函数"""
    print("=" * 60)
    print("arXiv真实API测试")
    print("=" * 60)
    
    # 测试关键词
    test_queries = [
        "quantum spin liquid",
        "magnetoelectric coupling",
        "multiferroic",
        "topological insulator"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"搜索关键词: {query}")
        print(f"{'='*60}")
        
        results = search_arxiv_real(query, max_results=3)
        
        if not results:
            print("⚠️ 未找到结果或API请求失败")
        
        # 添加延迟，避免请求过快
        time.sleep(2)
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")
    
    # 生成测试报告
    print("\n📋 测试总结:")
    print("-" * 40)
    print("✅ 如果看到文献列表: API连接成功")
    print("❌ 如果看到错误信息: 需要检查网络或API状态")
    print("💡 建议: 可以稍后再试，arXiv API有时不稳定")

if __name__ == "__main__":
    main()