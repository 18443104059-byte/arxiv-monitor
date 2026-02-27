@echo off
chcp 65001 >nul
echo ========================================
echo arXiv文献监控系统 - 测试工具
echo ========================================
echo.

echo 1. 测试网络连接...
python test_network_simple.py
echo.

echo 2. 运行简单测试...
python arxiv_simple.py
echo.

echo 3. 测试真实搜索（需要网络）...
echo 注意：这可能需要一些时间...
python arxiv_real_search.py
echo.

echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 如果所有测试都通过，系统可以正常使用。
echo 如果有错误，请查看上面的错误信息。
echo.
pause