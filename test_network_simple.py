#!/usr/bin/env python3
"""
简单网络测试
"""

import urllib.request
import socket

def test_connection():
    print("Testing network connection...")
    print("-" * 40)
    
    # 测试arXiv API
    try:
        print("Testing arXiv API...")
        req = urllib.request.Request(
            "http://export.arxiv.org/api/query?search_query=all:quantum&max_results=1",
            headers={'User-Agent': 'OpenClaw/1.0'}
        )
        
        # 设置超时
        socket.setdefaulttimeout(15)
        
        response = urllib.request.urlopen(req)
        data = response.read()
        
        print("SUCCESS: arXiv API is accessible")
        print(f"Response size: {len(data)} bytes")
        print(f"Status code: {response.getcode()}")
        
        # 检查是否包含有效数据
        if b'<entry>' in data:
            print("VALID: Response contains arXiv data")
            return True
        else:
            print("WARNING: Response format may be incorrect")
            return False
            
    except socket.timeout:
        print("ERROR: Connection timeout (15 seconds)")
        print("Possible causes:")
        print("1. Network connectivity issues")
        print("2. arXiv server is down")
        print("3. Firewall blocking the connection")
        return False
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False

def main():
    print("=" * 50)
    print("arXiv API Connection Test")
    print("=" * 50)
    
    success = test_connection()
    
    print("\n" + "=" * 50)
    print("Test Result")
    print("=" * 50)
    
    if success:
        print("PASS: arXiv API is working correctly")
        print("Next step: Run full arXiv search")
    else:
        print("FAIL: Cannot connect to arXiv API")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Try again later (arXiv may be temporarily down)")
        print("3. Use test mode for development")
        print("4. Check firewall/proxy settings")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()