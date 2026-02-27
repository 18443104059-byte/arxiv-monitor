# arXiv文献监控系统 - 阿里云部署指南

## 📋 系统概述

这是一个自动化的arXiv文献监控系统，专门为凝聚态物理研究人员设计。系统每天自动搜索磁电耦合、量子自旋液体等相关领域的最新文献，并生成结构化报告。

## 🚀 一键部署到阿里云Coding Plan

### 第一步：准备工作

#### 1.1 登录阿里云
- 访问：https://aliyun.com
- 进入「Coding Plan」服务

#### 1.2 创建新项目
```
项目名称：arxiv-monitor
描述：arXiv文献自动监控系统
编程语言：Python 3.x
```

### 第二步：上传代码

#### 方法A：通过Git（推荐）
```bash
# 在阿里云终端中执行
git clone https://github.com/你的用户名/arxiv-monitor.git
cd arxiv-monitor
```

#### 方法B：通过文件上传
1. 下载本项目的ZIP文件
2. 在阿里云控制台上传ZIP
3. 解压到项目目录

### 第三步：安装依赖

```bash
# 在阿里云终端执行
pip install feedparser
```

### 第四步：测试运行

```bash
# 测试网络连接
python scripts/test_network_simple.py

# 测试搜索功能
python scripts/arxiv_simple.py
```

### 第五步：配置定时任务

在阿里云Cron配置页面：

```yaml
# 每天上午9点运行（北京时间）
名称：arXiv每日监控
时间：0 9 * * *
命令：cd /path/to/arxiv-monitor/scripts && python arxiv_daily_report.py --save
```

### 第六步：配置飞书推送（可选）

#### 6.1 获取飞书webhook
1. 打开飞书，进入「群设置」
2. 选择「群机器人」→「添加机器人」
3. 选择「自定义机器人」
4. 复制webhook URL

#### 6.2 配置系统
编辑 `config.yaml`：
```yaml
feishu:
  webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/你的token"
  enable: true
```

## 📁 项目文件结构

```
arxiv-monitor/
├── README.md                    # 项目说明
├── DEPLOY_TO_ALIYUN.md         # 本部署指南
├── config.yaml                  # 配置文件
├── requirements.txt             # Python依赖
├── scripts/                     # 脚本目录
│   ├── arxiv_search.py         # 核心搜索脚本
│   ├── arxiv_daily_report.py   # 日报生成器
│   ├── arxiv_simple.py         # 测试脚本
│   ├── setup_arxiv_monitor.py  # 系统设置
│   └── test_network_simple.py  # 网络测试
├── reports/                     # 报告保存目录
└── logs/                       # 日志目录
```

## ⚙️ 配置文件说明

编辑 `config.yaml` 自定义设置：

```yaml
# 搜索配置
search:
  keywords:
    - "quantum spin liquid"
    - "magnetoelectric coupling"
    - "multiferroic"
    - "topological insulator"
    - "skyrmion"
    - "spintronics"
  
  # 搜索参数
  days: 7           # 搜索最近几天
  max_results: 10   # 每关键词最多结果数
  
# 输出配置
output:
  format: "markdown"  # markdown 或 text
  save_to_file: true
  report_dir: "./reports"
  
# 飞书推送配置
feishu:
  enable: false
  webhook: ""
  
# 定时任务配置
cron:
  enable: true
  schedule: "0 9 * * *"  # 每天9点
  timezone: "Asia/Shanghai"
```

## 🔧 常用命令

### 手动运行搜索
```bash
# 搜索特定关键词
python scripts/arxiv_search.py --keywords "quantum spin liquid"

# 生成日报
python scripts/arxiv_daily_report.py --days 1 --save

# 测试所有功能
python scripts/arxiv_simple.py
```

### 查看报告
```bash
# 查看最新报告
ls -la reports/
cat reports/arxiv_report_最新日期.md
```

### 查看日志
```bash
# 查看运行日志
cat logs/arxiv_monitor.log
```

## 🐛 故障排除

### 问题1：网络连接失败
```bash
# 测试网络
python scripts/test_network_simple.py

# 如果失败，检查：
# 1. 阿里云网络配置
# 2. 防火墙设置
# 3. arXiv API状态
```

### 问题2：Python依赖问题
```bash
# 重新安装依赖
pip uninstall feedparser
pip install feedparser==6.0.10
```

### 问题3：定时任务不执行
1. 检查阿里云Cron配置
2. 查看系统日志：`cat /var/log/cron`
3. 手动测试命令是否正常

### 问题4：飞书推送失败
1. 检查webhook URL是否正确
2. 检查网络是否能访问飞书
3. 查看错误日志

## 📞 技术支持

### 快速检查清单
- [ ] 阿里云项目创建成功
- [ ] 代码上传完成
- [ ] 依赖安装成功
- [ ] 测试运行通过
- [ ] 定时任务配置
- [ ] 飞书推送配置（可选）

### 获取帮助
1. 查看本指南
2. 检查 `README.md`
3. 查看脚本中的注释
4. 联系开发者

## 🔄 更新维护

### 更新代码
```bash
# 从GitHub拉取最新代码
git pull origin main

# 重新安装依赖
pip install -r requirements.txt
```

### 备份数据
```bash
# 备份报告
tar -czf reports_backup_$(date +%Y%m%d).tar.gz reports/

# 备份配置
cp config.yaml config_backup_$(date +%Y%m%d).yaml
```

## 🎯 成功标志

当看到以下输出时，表示系统部署成功：

```bash
# 测试运行输出
arXiv API Connection Test
==================================================
Testing network connection...
----------------------------------------
Testing arXiv API...
SUCCESS: arXiv API is accessible
Response size: 2377 bytes
Status code: 200
VALID: Response contains arXiv data
```

## 💡 使用建议

### 最佳实践
1. **定期检查**：每周查看一次运行状态
2. **关键词优化**：根据研究进展调整搜索关键词
3. **报告整理**：每月整理一次重要文献
4. **系统更新**：每季度更新一次依赖

### 扩展功能
1. 添加更多研究领域关键词
2. 集成文献管理工具（如Zotero）
3. 添加机器学习文献推荐
4. 生成研究趋势分析报告

---

*最后更新：2026-02-27*
*部署指南版本：v1.0*