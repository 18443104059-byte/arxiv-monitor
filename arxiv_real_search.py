#!/usr/bin/env python3
"""
真实arXiv搜索脚本
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time

def search_arxiv(keywords, days=7, max_results=10):
    """搜索arXiv文献"""
    
    # arXiv API基础URL
    base_url = "http://export.arxiv.org/api/query"
    
    # 构建查询 - 最近N天的文献
    date_cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    search_query = f'({keywords}) AND submittedDate:[{date_cutoff}000000 TO *]'
    
    # 构建查询参数
    params = {
        'search_query': search_query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    # 编码URL
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"
    
    print(f"搜索关键词: {keywords}")
    print(f"时间范围: 最近{days}天")
    print(f"API请求: {url}")
    print("-" * 80)
    
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
        total = int(total_results.text) if total_results is not None else 0
        
        print(f"找到文献: {total} 篇")
        
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
            
            # 提取arXiv ID
            id_elem = entry.find('atom:id', ns)
            arxiv_id = id_elem.text if id_elem is not None else ""
            
            # 提取PDF链接
            pdf_link = ""
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_link = link.get('href')
                    break
            
            # 提取分类
            categories = []
            for category in entry.findall('atom:category', ns):
                cat_term = category.get('term', '')
                if cat_term:
                    categories.append(cat_term)
            
            # 构建结果
            result = {
                'index': i + 1,
                'title': title,
                'authors': authors,
                'published': published,
                'arxiv_id': arxiv_id,
                'pdf_link': pdf_link,
                'summary': summary,
                'categories': categories[:3]  # 只显示前3个分类
            }
            results.append(result)
        
        return results, total
        
    except Exception as e:
        print(f"API请求失败: {e}")
        return [], 0

def format_results(results, keyword):
    """格式化结果"""
    
    if not results:
        return "未找到相关文献。"
    
    output = []
    output.append(f"## 🔍 关键词: {keyword}")
    output.append("")
    
    for result in results:
        output.append(f"### {result['index']}. {result['title']}")
        output.append("")
        
        # 作者信息
        authors_display = ', '.join(result['authors'][:3])
        if len(result['authors']) > 3:
            authors_display += f" 等 ({len(result['authors'])}位作者)"
        output.append(f"**作者**: {authors_display}")
        
        # 发布时间和分类
        output.append(f"**发布时间**: {result['published']}")
        if result['categories']:
            output.append(f"**分类**: {', '.join(result['categories'])}")
        
        # 链接
        if result['arxiv_id']:
            output.append(f"**arXiv链接**: {result['arxiv_id']}")
        if result['pdf_link']:
            output.append(f"**PDF下载**: {result['pdf_link']}")
        
        # 摘要
        summary_preview = result['summary'][:300] + "..." if len(result['summary']) > 300 else result['summary']
        output.append(f"**摘要**: {summary_preview}")
        
        output.append("")
        output.append("---")
        output.append("")
    
    return '\n'.join(output)

def main():
    """主函数"""
    print("=" * 80)
    print("arXiv真实文献搜索")
    print("=" * 80)
    
    # 搜索关键词
    keywords_list = [
        "quantum spin liquid",
        "magnetoelectric coupling", 
        "multiferroic",
        "topological insulator",
        "skyrmion",
        "spintronics"
    ]
    
    all_results = []
    
    for keyword in keywords_list:
        print(f"\n搜索: {keyword}")
        print("-" * 40)
        
        results, total = search_arxiv(keyword, days=30, max_results=3)
        
        if results:
            formatted = format_results(results, keyword)
            all_results.append(formatted)
            
            # 显示简要信息
            print(f"找到 {len(results)} 篇文献:")
            for result in results:
                print(f"  {result['index']}. {result['title'][:60]}...")
        
        # 添加延迟，避免请求过快
        time.sleep(2)
    
    # 生成完整报告
    if all_results:
        print("\n" + "=" * 80)
        print("生成完整报告...")
        print("=" * 80)
        
        report = f"""# 📚 arXiv文献搜索报告

**报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**搜索范围**: 最近30天
**搜索平台**: arXiv.org

---

{'\n\n'.join(all_results)}

---

## 📊 搜索总结

**搜索完成时间**: {datetime.now().strftime('%H:%M:%S')}
**数据来源**: arXiv官方API (http://export.arxiv.org/api/query)
**状态**: ✅ 真实数据获取成功

---

*报告自动生成于 OpenClaw arXiv监控系统*
*数据来源: arXiv.org - 康奈尔大学*
"""
        
        # 保存报告
        import os
        os.makedirs('./reports', exist_ok=True)
        filename = f"arxiv_real_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join('./reports', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 报告已保存: {filepath}")
        print(f"📄 报告大小: {len(report)} 字符")
        
        # 显示报告摘要
        print("\n📋 报告摘要:")
        print("-" * 40)
        lines = report.split('\n')
        for i in range(min(20, len(lines))):
            print(lines[i])
        
        return report, filepath
    else:
        print("\n⚠️ 未找到任何文献")
        return None, None

if __name__ == "__main__":
    report, filepath = main()