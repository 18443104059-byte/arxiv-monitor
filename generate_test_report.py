#!/usr/bin/env python3
"""
arXiv文献监控系统 - 物理实验与材料发现定向版
核心关注：多铁/磁电耦合、量子自旋液体、交错磁体
功能：生成针对材料生长与性质预测的测试报告
"""

from datetime import datetime
import os
import json

def generate_test_report():
    """生成针对材料制备与物理特性的精细化测试报告"""
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""# 🔬 arXiv 凝聚态物理文献追踪 (定向科研版)

**报告生成时间**: {current_time}
**重点领域**: 多铁性与磁电耦合 | 量子自旋液体 | 交错磁体 (Altermagnetism)
**筛选逻辑**: 侧重 **"新材料合成"、"单晶生长"、"DFT预测可生长"**

---

## 🌟 今日高价值文献 (模拟/测试数据)

### 1. 【交错磁体 - 新材料预测】
**标题**: Prediction of large spin-splitting in a new class of altermagnetic ternary compounds
**作者**: Phys. Material Team
**发布时间**: 2026-02-28
**关键词**: Altermagnetism, DFT, Spin-splitting, Materials Discovery
**arXiv**: https://arxiv.org/abs/cond-mat/2602.12345
**[摘要预览]**: 本文通过第一性原理计算预测了一类新型三元化合物，具有显著的交错磁序（Altermagnetism）。对称性分析表明其具有巨大的自旋分裂效应，**文中给出了合成该类材料的固相反应温度曲线，极具实验制备参考价值。**

---

### 2. 【量子自旋液体 - 实验生长】
**标题**: Single crystal growth and exchange anisotropy of the Kitaev candidate Na2Co2TeO6
**作者**: Crystal Growth Lab
**发布时间**: 2026-03-01
**关键词**: Quantum Spin Liquid, Flux Method, Single Crystal, Honeycomb Lattice
**arXiv**: https://arxiv.org/abs/cond-mat/2603.54321
**[摘要预览]**: 报告了利用**自熔剂法（Self-flux method）**生长高质量蜂窝状钴基氧化物单晶的详细过程。通过中子散射观测到了Kitaev相互作用的证据，为量子自旋液体候选材料提供了新的实验平台。

---

### 3. 【多铁/磁电耦合 - 本征机制】
**标题**: Enhanced magnetoelectric coupling in a new type-II multiferroic oxide
**作者**: Magnetics Group
**发布时间**: 2026-03-02
**关键词**: Multiferroic, Magnetoelectric Effect, Floating Zone Method, Helical Order
**arXiv**: https://arxiv.org/abs/cond-mat/2603.99887
**[摘要预览]**: 利用**光学浮区炉（Optical Floating Zone）**生长了新型多铁氧化物单晶。观察到非共线螺旋磁序诱导的强磁电耦合效应，电场对磁化强度的调控率达到了新高。

---

## 📊 文献分布统计 (基于关键词匹配)

| 核心领域 | 匹配关键词 (部分) | 关注度 |
| :--- | :--- | :--- |
| **交错磁体** | Altermagnet, Spin-splitting, $RuO_2$, $MnTe$ | 🔥🔥🔥 (前沿) |
| **量子自旋液体** | Kitaev, Kagome, Frustrated, Single crystal | ⭐⭐⭐⭐ (持续) |
| **磁电耦合** | Multiferroic, Magnetoelectric, Helical, Ferroelectric | 💎💎 (经典/稳定) |
| **制备工艺** | Flux method, Floating zone, CVT, Synthesis | 🛠️ (实验核心) |

---

## 🛠️ 建议更新的搜索算法 (关键词配置)

为了让你找到“能长出来”的材料，建议在 `arxiv_search.py` 中使用以下组合逻辑：

1.  **交错磁体 (Altermagnetism):**
    *   `"altermagnet*" AND (material OR crystal OR synthesis OR discovery)`
    *   *(注：Altermagnetism是近年新词，必须加星号模糊匹配)*

2.  **量子自旋液体 (QSL):**
    *   `"quantum spin liquid" AND (candidate OR synthesis OR "single crystal")`
    *   `"Kitaev" AND (material OR growth)`

3.  **多铁性/磁电耦合:**
    *   `multiferroic AND ("magnetoelectric coupling" OR "type-II")`
    *   `"magnetoelectric effect" AND (bulk OR crystal)`

4.  **材料预测筛选 (针对“理论预测我可以去长”):**
    *   `("DFT prediction" OR "theoretically predicted") AND ("new material" OR "synthesis")`

---

## 🚀 后续实验计划建议

1.  **文献1跟踪**: 评估预测材料的稳定性，检查文中提到的合成原料 (Precursors) 库房是否有现货。
2.  **制备参考**: 对比文献2中的 Flux 比例（1:10），尝试在 1100℃ 环境下进行初步烧结。
3.  **系统优化**: 下一步将自动抓取摘要中的 **"Chemical Formula" (化学式)** 并高亮显示。

---
*自动生成于 OpenClaw arXiv监控系统 (科研定制版)*
"""
    return report

def save_report(report):
    """保存报告到文件"""
    os.makedirs('./reports', exist_ok=True)
    filename = f"arxiv_physics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join('./reports', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 针对性测试报告已保存: {filepath}")
    return filepath

def main():
    """主函数"""
    print("正在根据您的研究方向（多铁、自旋液体、交错磁体）生成定制报告...")
    
    # 1. 生成针对性报告
    report = generate_test_report()
    
    # 2. 保存报告
    filepath = save_report(report)
    
    # 3. 控制台打印预览 (前40行)
    print("\n" + "="*70)
    print("📋 报告内容预览 (核心关键词已优化):")
    print("="*70)
    
    lines = report.split('\n')
    for i, line in enumerate(lines[:40]):
        print(line)
    
    print("\n" + "="*70)
    print(f"📄 完整报告保存路径: {os.path.abspath(filepath)}")
    print("📤 状态: 等待飞书 Webhook 接入推送...")
    print("💡 提示: 请确保在 arxiv_search.py 中更新上述建议的关键词组合以获得真实数据。")

if __name__ == "__main__":
    main()
