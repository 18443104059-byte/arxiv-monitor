# arXiv文献监控系统

一个自动化的arXiv文献监控系统，专门为凝聚态物理研究人员设计。系统每天自动搜索磁电耦合、量子自旋液体等相关领域的最新文献，并生成结构化报告。

## ✨ 功能特性

### 🔍 智能文献搜索
- **多关键词监控**：同时监控6+个研究领域
- **时间范围控制**：可设置搜索最近N天的文献
- **智能过滤**：按arXiv分类自动过滤
- **实时更新**：每天自动获取最新研究

### 📊 结构化报告
- **分类统计**：按研究领域自动分类
- **详细摘要**：包含文献摘要和关键信息
- **直接链接**：提供arXiv链接和PDF下载
- **多种格式**：支持Markdown和纯文本输出

### ⏰ 自动化运行
- **定时任务**：每天自动运行（可配置时间）
- **云端部署**：支持阿里云等云平台
- **稳定可靠**：24/7不间断监控
- **错误处理**：自动重试和错误报告

### 🔗 集成推送
- **飞书推送**：自动发送日报到飞书
- **文件保存**：自动保存历史报告
- **日志记录**：完整的运行日志
- **可扩展性**：易于添加新的推送渠道

## 🚀 快速开始

### 本地运行
```bash
# 克隆项目
git clone https://github.com/你的用户名/arxiv-monitor.git
cd arxiv-monitor

# 安装依赖
pip install feedparser

# 测试运行
python scripts/arxiv_simple.py
```

### 云端部署（阿里云）
详细部署指南请查看：[DEPLOY_TO_ALIYUN.md](DEPLOY_TO_ALIYUN.md)

## 📁 项目结构

```
arxiv-monitor/
├── README.md                    # 项目说明
├── DEPLOY_TO_ALIYUN.md         # 阿里云部署指南
├── config.yaml                  # 配置文件
├── requirements.txt             # Python依赖
├── scripts/                     # 脚本目录
│   ├── arxiv_search.py         # 核心搜索脚本
│   ├── arxiv_daily_report.py   # 日报生成器
│   ├── arxiv_simple.py         # 测试脚本
│   ├── setup_arxiv_monitor.py  # 系统设置
│   ├── test_network_simple.py  # 网络测试
│   └── arxiv_real_search.py    # 真实API搜索
├── reports/                     # 报告保存目录
└── logs/                       # 日志目录
```

## ⚙️ 配置说明

### 基本配置
编辑 `config.yaml` 文件：

```yaml
# 搜索配置
search:
  keywords:
    - "quantum spin liquid"      # 量子自旋液体
    - "magnetoelectric coupling" # 磁电耦合
    - "multiferroic"             # 多铁性
    - "topological insulator"    # 拓扑绝缘体
    - "skyrmion"                 # 斯格明子
    - "spintronics"              # 自旋电子学
  
  # 搜索参数
  days: 7           # 搜索最近7天
  max_results: 10   # 每关键词最多10篇
  
# 输出配置
output:
  format: "markdown"  # 输出格式：markdown 或 text
  save_to_file: true  # 是否保存到文件
  report_dir: "./reports"  # 报告保存目录
  
# 飞书推送配置
feishu:
  enable: false      # 是否启用飞书推送
  webhook: ""        # 飞书webhook URL
  
# 定时任务配置
cron:
  enable: true       # 是否启用定时任务
  schedule: "0 9 * * *"  # 每天9点运行
  timezone: "Asia/Shanghai"  # 时区
```

### 自定义关键词
你可以添加自己的研究关键词：

```yaml
search:
  keywords:
    - "你的研究关键词1"
    - "你的研究关键词2"
    - "你的研究关键词3"
```

## 📖 使用方法

### 1. 测试运行
```bash
# 简单测试
python scripts/arxiv_simple.py

# 网络测试
python scripts/test_network_simple.py
```

### 2. 手动搜索
```bash
# 搜索特定关键词
python scripts/arxiv_search.py --keywords "quantum spin liquid" --days 30

# 生成日报
python scripts/arxiv_daily_report.py --days 1 --save
```

### 3. 设置定时任务
```bash
# 使用系统设置脚本
python scripts/setup_arxiv_monitor.py --schedule "09:00"
```

### 4. 查看报告
报告会自动保存到 `reports/` 目录，文件名格式为：
```
arxiv_report_YYYYMMDD_HHMMSS.md
```

## 🔧 脚本说明

### `arxiv_search.py`
核心搜索脚本，使用arXiv官方API搜索文献。

**参数：**
- `--keywords`: 搜索关键词（多个用逗号分隔）
- `--days`: 搜索最近几天（默认7）
- `--max_results`: 每关键词最多结果数（默认10）
- `--save`: 保存结果到文件

### `arxiv_daily_report.py`
日报生成器，生成每日文献监控报告。

**参数：**
- `--days`: 搜索最近几天（默认1）
- `--save`: 保存报告到文件
- `--send`: 发送报告到飞书（需配置webhook）

### `arxiv_simple.py`
测试脚本，使用示例数据快速测试系统功能。

### `setup_arxiv_monitor.py`
系统设置脚本，帮助配置定时任务和其他设置。

### `test_network_simple.py`
网络测试脚本，检查arXiv API连接状态。

## 🌐 部署到云端

### 为什么选择云端部署？
1. **稳定性**：24/7不间断运行
2. **可靠性**：不受本地电脑影响
3. **自动化**：定时任务更可靠
4. **可扩展**：易于添加新功能

### 支持的云平台
- **阿里云Coding Plan**（推荐）
- 腾讯云CloudBase
- 华为云FunctionGraph
- 其他支持Python的云函数服务

详细部署指南请查看：[DEPLOY_TO_ALIYUN.md](DEPLOY_TO_ALIYUN.md)

## 🐛 故障排除

### 常见问题

#### Q1: 网络连接失败
**症状**：`Connection timeout` 或 `URLError`
**解决**：
```bash
# 测试网络连接
python scripts/test_network_simple.py

# 如果失败，检查：
# 1. 网络连接是否正常
# 2. 防火墙是否阻止访问
# 3. arXiv API是否正常
```

#### Q2: 依赖安装失败
**症状**：`ModuleNotFoundError: No module named 'feedparser'`
**解决**：
```bash
# 重新安装依赖
pip install --upgrade pip
pip install feedparser==6.0.10
```

#### Q3: 定时任务不执行
**症状**：报告没有按时生成
**解决**：
1. 检查定时任务配置是否正确
2. 查看系统日志
3. 手动运行测试是否正常

#### Q4: 飞书推送失败
**症状**：报告没有发送到飞书
**解决**：
1. 检查webhook URL是否正确
2. 检查网络是否能访问飞书
3. 查看错误日志

### 日志查看
```bash
# 查看运行日志
cat logs/arxiv_monitor.log

# 查看错误日志
cat logs/error.log
```

## 🔄 更新维护

### 更新代码
```bash
# 从GitHub拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt
```

### 备份数据
```bash
# 备份报告
tar -czf reports_backup_$(date +%Y%m%d).tar.gz reports/

# 备份配置
cp config.yaml config_backup_$(date +%Y%m%d).yaml
```

## 📈 扩展功能

### 计划中的功能
1. **文献评分系统**：基于引用和影响力的自动评分
2. **研究趋势分析**：可视化研究热点变化
3. **个性化推荐**：基于阅读历史的智能推荐
4. **多平台推送**：支持微信、钉钉、邮件等

### 自定义开发
如果你需要定制功能：
1. 修改 `config.yaml` 配置文件
2. 扩展 `arxiv_search.py` 搜索逻辑
3. 添加新的输出格式
4. 集成其他文献数据库

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- **arXiv.org**：提供开放的文献数据库
- **康奈尔大学**：维护arXiv平台
- **feedparser库**：简化RSS/Atom解析
- **所有贡献者**：感谢你们的支持和贡献

## 📞 联系支持

如有问题或建议，请：
1. 查看 [DEPLOY_TO_ALIYUN.md](DEPLOY_TO_ALIYUN.md) 部署指南
2. 检查常见问题解答
3. 提交 Issue
4. 联系开发者

---

**让文献监控变得简单高效！** 🎯

*最后更新：2026-02-27*
*版本：v1.0*