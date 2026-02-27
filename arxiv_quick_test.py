#!/usr/bin/env python3
"""
快速arXiv API测试
"""

import urllib.request
import urllib.error
import socket

def test_arxiv_api():
    """测试arXiv API连接"""
    
    print("测试arXiv API连接...")
    print("-" * 40)
    
    # 测试URL
    test_url = "http://export.arxiv.org/api/query?search_query=all:quantum&max_results=1"
    
    try:
        # 设置超时
        socket.setdefaulttimeout(10)
        
        # 发送请求
        req = urllib.request.Request(test_url, headers={'User-Agent': 'OpenClaw/1.0'})
        
        print(f"请求URL: {test_url}")
        print("正在连接...")
        
        response = urllib.request.urlopen(req)
        status = response.getcode()
        content_length = len(response.read())
        
        print(f"✅ 连接成功!")
        print(f"状态码: {status}")
        print(f"响应大小: {content_length} 字节")
        print(f"API可用性: 正常")
        
        return True
        
    except urllib.error.URLError as e:
        print(f"❌ URL错误: {e.reason}")
        return False
    except socket.timeout:
        print("❌ 连接超时 (10秒)")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_network():
    """测试网络连接"""
    
    print("\n测试网络连接...")
    print("-" * 40)
    
    test_sites = [
        ("Google", "https://www.google.com"),
        ("arXiv", "https://arxiv.org"),
        ("GitHub", "https://github.com")
    ]
    
    for name, url in test_sites:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw/1.0'})
            response = urllib.request.urlopen(req, timeout=5)
            print(f"✅ {name}: 可访问")
        except Exception as e:
            print(f"❌ {name}: 不可访问 ({e})")

def main():
    """主函数"""
    print("=" * 50)
    print("arXiv API连接诊断工具")
    print("=" * 50)
    
    # 测试网络
    test_network()
    
    print("\n" + "=" * 50)
    print("arXiv API测试")
    print("=" * 50)
    
    # 测试arXiv API
    api_ok = test_arxiv_api()
    
    print("\n" + "=" * 50)
    print("诊断结果")
    print("=" * 50)
    
    if api_ok:
        print("🎉 arXiv API连接正常!")
        print("下一步: 可以运行完整的文献搜索")
    else:
        print("⚠️ arXiv API连接失败")
        print("可能原因:")
        print("1. 网络连接问题")
        print("2. arXiv服务器暂时不可用")
        print("3. 防火墙或代理设置")
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 稍后再试")
        print("3. 使用测试模式继续开发")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()