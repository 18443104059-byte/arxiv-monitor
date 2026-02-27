#!/usr/bin/env python3
"""
arXiv监控系统设置脚本
创建定时任务和配置文件
"""

import argparse
import os
import sys
import json
import yaml
from datetime import datetime

def setup_encoding():
    """设置编码以支持中文"""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def create_config_file(config_path):
    """创建配置文件"""
    config = {
        'arxiv_monitor': {
            'keywords': [
                'magnetoelectric coupling',
                'quantum spin liquid',
                'multiferroic',
                'topological insulator',
                'skyrmion',
                'spintronics',
                'condensed matter physics',
                'magnetic materials',
                'electronic structure',
                'strongly correlated systems'
            ],
            'categories': [
                'cond-mat.mes-hall',  # 介观系统和霍尔效应
                'cond-mat.str-el',    # 强关联电子系统
                'cond-mat.mtrl-sci',  # 材料科学
                'cond-mat.supr-con',  # 超导
                'physics.app-ph',     # 应用物理
                'physics.chem-ph'     # 化学物理
            ],
            'search_settings': {
                'max_results': 20,
                'days_back': 1,
                'filter_strict': True,
                'include_abstract': True
            },
            'report_settings': {
                'format': 'markdown',
                'include_stats': True,
                'categorize_by_keyword': True,
                'max_authors_display': 3
            },
            'notification_settings': {
                'enabled': True,
                'channel': 'feishu',
                'schedule': '09:00',
                'only_new_papers': True,
                'min_papers_to_notify': 1
            },
            'storage_settings': {
                'output_dir': './reports',
                'keep_days': 30,
                'backup_enabled': True
            }
        },
        'user_preferences': {
            'name': '科研工作者',
            'research_field': '凝聚态物理/磁电耦合/量子自旋液体',
            'timezone': 'Asia/Shanghai',
            'language': 'zh-CN'
        }
    }
    
    # 确保目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # 写入配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"✅ 配置文件已创建: {config_path}")
    return config

def create_cron_job(schedule_time="09:00"):
    """创建定时任务"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, 'arxiv_daily_report.py')
    
    # 创建批处理文件
    batch_content = f"""@echo off
REM arXiv每日文献监控任务
REM 自动运行时间: 每天 {schedule_time}

echo ========================================
echo   📚 arXiv文献监控系统
echo   运行时间: %DATE% %TIME%
echo ========================================

cd /d "{script_dir}"
python "{main_script}" --days 1 --save

echo.
echo 任务完成! 按任意键退出...
pause >nul
"""
    
    batch_path = os.path.join(script_dir, 'run_arxiv_monitor.bat')
    with open(batch_path, 'w', encoding='gbk') as f:
        f.write(batch_content)
    
    print(f"✅ 批处理文件已创建: {batch_path}")
    
    # 创建Windows任务计划命令
    task_name = "OpenClaw_arXiv_Monitor"
    task_command = f'schtasks /create /tn "{task_name}" /tr "{batch_path}" /sc daily /st {schedule_time} /ru SYSTEM'
    
    print("\n📅 要创建Windows定时任务，请以管理员身份运行以下命令:")
    print("=" * 60)
    print(task_command)
    print("=" * 60)
    print("\n或者手动创建任务计划:")
    print("1. 打开'任务计划程序'")
    print(f"2. 创建基本任务，名称: {task_name}")
    print(f"3. 触发器: 每天 {schedule_time}")
    print(f"4. 操作: 启动程序 -> {batch_path}")
    print("5. 完成")
    
    return batch_path

def create_quick_start_guide():
    """创建快速开始指南"""
    guide = """# arXiv文献监控系统 - 快速开始指南

## 🚀 立即开始

### 1. 测试搜索功能
```cmd
cd scripts
python arxiv_search.py --keywords "magnetoelectric coupling quantum spin liquid" --days 1
```

### 2. 生成今日报告
```cmd
python arxiv_daily_report.py --days 1 --save
```

### 3. 查看报告
报告保存在 `reports/` 目录，文件名如 `arxiv_daily_report_20250227.md`

## ⏰ 设置定时任务

### 方法A: 使用OpenClaw cron功能（推荐）
```bash
# 每天9点运行
openclaw cron create --schedule "0 9 * * *" --command "cd /path/to/arxiv-monitor/scripts && python arxiv_daily_report.py --days 1 --save"
```

### 方法B: Windows任务计划
1. 打开"任务计划程序"
2. 创建基本任务
3. 名称: `OpenClaw_arXiv_Monitor`
4. 触发器: 每天 09:00
5. 操作: 启动程序 -> `run_arxiv_monitor.bat`

### 方法C: 手动运行
双击 `run_arxiv_monitor.bat`

## 🔧 自定义配置

编辑 `config.yaml` 文件:
- 修改搜索关键词
- 调整推送时间
- 设置输出格式
- 配置文献分类

## 📊 监控的关键领域

1. **磁电耦合 (Magnetoelectric Coupling)**
   - 多铁性材料
   - 磁电效应
   - 磁控电/电控磁

2. **量子自旋液体 (Quantum Spin Liquid)**
   - 阻挫磁体
   - 拓扑序
   - 任意子激发

3. **相关领域**
   - 拓扑绝缘体
   - 斯格明子
   - 自旋电子学
   - 强关联系统

## 🔔 通知设置

系统支持通过飞书发送每日文献报告。
编辑 `config.yaml` 中的 `notification_settings` 部分。

## 📁 文件结构

```
arxiv-monitor/
├── SKILL.md              # 技能说明
├── config.yaml           # 配置文件
├── scripts/              # Python脚本
│   ├── arxiv_search.py      # 搜索脚本
│   ├── arxiv_daily_report.py # 日报生成
│   └── setup_arxiv_monitor.py # 设置脚本
├── run_arxiv_monitor.bat # 批处理文件
└── reports/              # 生成的报告
```

## 🆘 常见问题

### Q: 搜索不到文献？
A: 检查网络连接，或调整关键词

### Q: 定时任务不运行？
A: 检查任务计划程序，确保路径正确

### Q: 编码问题？
A: 所有脚本已使用UTF-8编码

## 📞 支持

如有问题，请联系OpenClaw助手。
"""
    
    guide_path = os.path.join(os.path.dirname(__file__), '..', 'QUICK_START.md')
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"✅ 快速开始指南已创建: {guide_path}")
    return guide_path

def main():
    """主函数"""
    setup_encoding()
    
    parser = argparse.ArgumentParser(description='arXiv监控系统设置')
    parser.add_argument('--schedule', default='09:00',
                       help='定时任务时间 (格式: HH:MM)')
    parser.add_argument('--config-only', action='store_true',
                       help='仅创建配置文件')
    parser.add_argument('--cron-only', action='store_true',
                       help='仅创建定时任务')
    
    args = parser.parse_args()
    
    print("🚀 arXiv文献监控系统设置")
    print("=" * 50)
    
    # 配置文件路径
    config_dir = os.path.join(os.path.dirname(__file__), '..')
    config_path = os.path.join(config_dir, 'config.yaml')
    
    # 创建配置文件
    if not args.cron_only:
        config = create_config_file(config_path)
        print(f"📋 配置关键词: {', '.join(config['arxiv_monitor']['keywords'][:5])}...")
    
    # 创建定时任务
    if not args.config_only:
        batch_path = create_cron_job(args.schedule)
        print(f"⏰ 定时任务设置: 每天 {args.schedule}")
    
    # 创建快速开始指南
    guide_path = create_quick_start_guide()
    
    print("\n" + "=" * 50)
    print("✅ 设置完成!")
    print(f"📁 技能目录: {os.path.abspath(config_dir)}")
    print(f"⚡ 立即测试: cd scripts && python arxiv_search.py")
    print(f"📅 定时任务: 每天 {args.schedule} 自动运行")
    print("=" * 50)

if __name__ == "__main__":
    main()