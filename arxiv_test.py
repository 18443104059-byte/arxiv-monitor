#!/usr/bin/env python3
"""
arXiv测试脚本 - 模拟数据用于演示
"""

import json
from datetime import datetime, timedelta
import random

def generate_test_papers():
    """生成测试文献数据"""
    
    test_keywords = [
        "magnetoelectric coupling",
        "quantum spin liquid", 
        "multiferroic",
        "topological insulator",
        "skyrmion"
    ]
    
    papers = []
    
    # 生成5篇测试文献
    for i in range(5):
        keyword = random.choice(test_keywords)
        paper_id = f"cond-mat/{random.randint(2000, 3000)}.{random.randint(1000, 9999)}v{i+1}"
        
        paper = {
            'id': paper_id,
            'title': f"Experimental study of {keyword} in novel materials",
            'summary': f"This paper presents experimental results on {keyword} in newly synthesized materials. The findings show significant advances in understanding the underlying physics.",
            'authors': [f"Author {j+1}" for j in range(random.randint(1, 5))],
            'published': (datetime.now() - timedelta(days=random.randint(0, 3))).isoformat(),
            'updated': (datetime.now() - timedelta(days=random.randint(0, 1))).isoformat(),
            'pdf_url': f"https://arxiv.org/pdf/{paper_id}.pdf",
            'arxiv_url': f"https://arxiv.org/abs/{paper_id}",
            'categories': [f"cond-mat.{random.choice(['mes-hall', 'str-el', 'mtrl-sci'])}"],
            'primary_category': f"cond-mat.{random.choice(['mes-hall', 'str-el'])}",
            'matched_keyword': keyword
        }
        
        papers.append(paper)
    
    return papers

def main():
    """主函数"""
    print("📚 arXiv文献监控系统 - 测试模式")
    print("=" * 50)
    
    # 生成测试数据
    papers = generate_test_papers()
    
    print(f"✅ 生成 {len(papers)} 篇测试文献")
    print()
    
    # 显示文献信息
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   关键词: {paper['matched_keyword']}")
        print(f"   作者: {', '.join(paper['authors'][:2])}" + 
              ("等" if len(paper['authors']) > 2 else ""))
        print(f"   发布时间: {paper['published'][:10]}")
        print(f"   arXiv: {paper['arxiv_url']}")
        print()
    
    # 统计信息
    print("📊 统计信息:")
    keyword_count = {}
    for paper in papers:
        keyword = paper['matched_keyword']
        keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
    
    for keyword, count in keyword_count.items():
        print(f"   {keyword}: {count}篇")
    
    print()
    print("💡 提示: 这是测试数据。实际使用时将连接arXiv API获取真实文献。")
    print("🔧 要使用真实数据，请确保网络连接正常且arXiv API可用。")

if __name__ == "__main__":
    main()