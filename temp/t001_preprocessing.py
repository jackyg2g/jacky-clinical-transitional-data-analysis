#!/usr/bin/env python3
"""T-001: 双数据源预处理与结构化解析
Processes both sample.xlsx (CAR-T kinetics) and G957 central lab data.
"""

import pandas as pd
import numpy as np
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

# ============================================================
# 1. CAR-T 动力学数据预处理 (sample.xlsx)
# ============================================================
print("=" * 60)
print("1. Processing sample.xlsx (CAR-T kinetics)")
print("=" * 60)

sample = pd.read_excel('reference/raw-data-yance/sample.xlsx')
print(f"  Loaded: {sample.shape[0]} rows x {sample.shape[1]} columns")
print(f"  Subjects: {sorted(sample['受试者ID'].unique())}")
print(f"  Visits: {sorted(sample['访视'].unique())}")
print(f"  Tests: {sorted(sample['分析项'].unique())}")

# Visit → Day mapping
visit_day_map = {
    '清淋前检查': -5,
    '主要随访期 D1': 1,
    '主要随访期 D4': 4,
    '主要随访期 D7': 7,
    '主要随访期 D10': 10,
    '主要随访期 D14': 14,
    '主要随访期 D21': 21,
    '主要随访期 D28': 28,
    '主要随访期 D60': 60,
    '主要随访期 D90': 90,
    '主要随访期 D180': 180,
    '主要随访期 D270': 270,
    '主要随访期 D360': 360,
    '主要随访期 D540': 540,
    '退出主要随访访视': None,  # Special handling
}

sample['Day'] = sample['访视'].map(visit_day_map)

# Parse results - handle BLD/BLQ
def parse_result(val):
    if isinstance(val, (int, float)):
        return float(val) if not np.isnan(val) else np.nan
    s = str(val).strip()
    if s in ('BLD', 'BLQ'):
        return 0.0  # For plotting; keep original for PK flag
    try:
        return float(s)
    except ValueError:
        return np.nan

def get_original_flag(val):
    if isinstance(val, (int, float)):
        return 'numeric'
    s = str(val).strip()
    if s == 'BLD':
        return 'BLD'
    if s == 'BLQ':
        return 'BLQ'
    return 'numeric'

sample['Value'] = sample['结果'].apply(parse_result)
sample['Flag'] = sample['结果'].apply(get_original_flag)

# Standardize subject ID to 5-digit format
sample['SubjectID_5'] = sample['受试者ID'].apply(lambda x: f'0{x}')
# Keep original ID for matching with G957 (which uses integer IDs)
sample['SubjectID'] = sample['受试者ID']

# Split by analysis item
cart_pct = sample[sample['分析项'] == 'CAR-T细胞占T细胞百分比'].copy()
cart_abs = sample[sample['分析项'] == 'CAR-T细胞绝对计数'].copy()

# Remove rows where Day is None (退出主要随访访视) and NaN values
cart_pct = cart_pct.dropna(subset=['Day', 'Value'])
cart_abs = cart_abs.dropna(subset=['Day', 'Value'])
cart_pct['Day'] = cart_pct['Day'].astype(int)
cart_abs['Day'] = cart_abs['Day'].astype(int)

# Sort and deduplicate
cart_pct = cart_pct.sort_values(['SubjectID', 'Day']).drop_duplicates(subset=['SubjectID', 'Day'], keep='first')
cart_abs = cart_abs.sort_values(['SubjectID', 'Day']).drop_duplicates(subset=['SubjectID', 'Day'], keep='first')

print(f"\n  CAR-T/T-cell %: {len(cart_pct)} data points, {cart_pct['SubjectID'].nunique()} subjects")
print(f"  CAR-T absolute count: {len(cart_abs)} data points, {cart_abs['SubjectID'].nunique()} subjects")

# BLD/BLQ counts
for name, df in [('T-cell %', cart_pct), ('Absolute count', cart_abs)]:
    flags = sample[sample['分析项'] == ('CAR-T细胞占T细胞百分比' if 'T-cell' in name else 'CAR-T细胞绝对计数')]['Flag'].value_counts()
    print(f"  {name} flags: {dict(flags)}")

# Save processed
cart_pct_out = cart_pct[['SubjectID', 'Day', 'Value', 'Flag', '访视']].copy()
cart_pct_out.columns = ['SubjectID', 'Day', 'Value', 'Flag', 'Visit']
cart_pct_out.to_csv('transformed/cart_tcell_pct.csv', index=False)

cart_abs_out = cart_abs[['SubjectID', 'Day', 'Value', 'Flag', '访视']].copy()
cart_abs_out.columns = ['SubjectID', 'Day', 'Value', 'Flag', 'Visit']
cart_abs_out.to_csv('transformed/cart_abs_count.csv', index=False)

# ============================================================
# 2. 中心实验室数据预处理 (G957 xlsx)
# ============================================================
print("\n" + "=" * 60)
print("2. Processing G957 central lab data")
print("=" * 60)

lab = pd.read_excel('reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx')
print(f"  Loaded: {lab.shape[0]} rows x {lab.shape[1]} columns")
print(f"  Centers: {lab['中心编号'].nunique()}")
print(f"  Subjects: {lab['受试者筛选号'].nunique()}")
print(f"  Tests: {lab['检测项目'].nunique()}")

# Time fields to datetime
for col in ['采集时间', '检测时间', '报告时间', '反审时间']:
    if col in lab.columns:
        lab[col] = pd.to_datetime(lab[col], errors='coerce')

# Visit cycle ordering and day mapping
lab_visit_day_map = {
    '筛选期': -60,
    '桥接治疗-DPd（D28）': -35,
    '桥接治疗-PVd（D21）': -28,
    'C1D28（桥接治疗 DPd）': -35,
    'C1D21（桥接治疗 PVd）': -28,
    'C2D28（桥接治疗 DPd）': -7,
    'C2D1': -42,
    'C3D1': -14,
    'C3D28（桥接治疗 DPd）': -7,
    'C4D1': -14,
    'C4D28（桥接治疗 DPd）': -7,
    '清淋前': -5,
    'D5': 5,
    'D8': 8,
    'D11': 11,
    'D15': 15,
    'D22': 22,
    'D29': 29,
    'W8': 56,
    'W12': 84,
    'W16': 112,
    'W20': 140,
    'W24': 168,
    'W28': 196,
    'W32': 224,
    'W36': 252,
    'W40': 280,
    'W44': 308,
    'W48': 336,
    'W52': 364,
    'W56': 392,
    'W60': 420,
    'W64': 448,
    'W68': 476,
    'W72': 504,
    'W76': 532,
    'EOT': None,
    '计划外': None,
    'PFS随访终止': None,
}

# Also map cycle visits like C5D1, C6D1 etc.
for i in range(5, 20):
    lab_visit_day_map[f'C{i}D1'] = None  # Pre-infusion bridging cycles, variable

lab['Day'] = lab['访视周期'].map(lab_visit_day_map)

# Visit ordering for display
visit_order = ['筛选期', '桥接治疗-DPd（D28）', '桥接治疗-PVd（D21）',
               'C1D28（桥接治疗 DPd）', 'C1D21（桥接治疗 PVd）',
               'C2D1', 'C2D28（桥接治疗 DPd）', 'C3D1', 'C3D28（桥接治疗 DPd）',
               'C4D1', 'C4D28（桥接治疗 DPd）',
               '清淋前', 'D5', 'D8', 'D11', 'D15', 'D22', 'D29',
               'W8', 'W12', 'W16', 'W20', 'W24', 'W28', 'W32', 'W36',
               'W40', 'W44', 'W48', 'W52', 'W56', 'W60', 'W64', 'W68',
               'W72', 'W76', 'EOT', '计划外', 'PFS随访终止']
visit_order_map = {v: i for i, v in enumerate(visit_order)}
lab['VisitOrder'] = lab['访视周期'].map(visit_order_map).fillna(999)

# Parse numeric results
def parse_lab_result(val):
    """Parse lab result, return numeric value or NaN for non-numeric."""
    if isinstance(val, (int, float)):
        return float(val) if not np.isnan(val) else np.nan
    s = str(val).strip()
    if s in ('', '/', 'nan', 'None'):
        return np.nan
    # Handle results like "<0.01", ">100"
    if s.startswith('<'):
        try:
            return float(s[1:]) / 2  # Use half of detection limit
        except:
            return np.nan
    if s.startswith('>'):
        try:
            return float(s[1:])
        except:
            return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan

def is_qualitative(val):
    """Check if result is qualitative (non-numeric text)."""
    if isinstance(val, (int, float)):
        return False
    s = str(val).strip()
    if s in ('', '/', 'nan', 'None'):
        return False
    try:
        float(s.lstrip('<>'))
        return False
    except ValueError:
        return True

lab['NumericResult'] = lab['结果'].apply(parse_lab_result)
lab['IsQualitative'] = lab['结果'].apply(is_qualitative)

# Classify tests
test_type_map = {}
for test in lab['检测项目'].unique():
    sub = lab[lab['检测项目'] == test]
    qual_rate = sub['IsQualitative'].mean()
    test_type_map[test] = 'qualitative' if qual_rate > 0.5 else 'quantitative'

print("\n  Test classification:")
for test, ttype in sorted(test_type_map.items()):
    count = len(lab[lab['检测项目'] == test])
    print(f"    {test}: {ttype} ({count} records)")

# ============================================================
# 3. 受试者匹配验证
# ============================================================
print("\n" + "=" * 60)
print("3. Subject ID matching verification")
print("=" * 60)

sample_ids = sorted(sample['受试者ID'].unique())
lab_ids = sorted(lab['受试者筛选号'].unique())

matched = [sid for sid in sample_ids if sid in lab_ids]
unmatched = [sid for sid in sample_ids if sid not in lab_ids]

print(f"  sample.xlsx subjects: {len(sample_ids)} ({sample_ids})")
print(f"  Central lab subjects: {len(lab_ids)}")
print(f"  Matched: {len(matched)} ({matched})")
print(f"  Unmatched: {len(unmatched)} ({unmatched})")
print(f"  PK-PD analysis available subjects: {len(matched)}")

# Check what tests matched subjects have
print("\n  Matched subjects - key biomarker availability:")
key_tests = ['血清蛋白电泳', '血清游离轻链', '免疫球蛋白IgA定量(IgA)',
             '免疫球蛋白IgG定量(IgG)', '免疫球蛋白IgM定量(IgM)',
             '血清免疫固定电泳', '达雷妥尤(Dara)药物干扰移除检测']

for sid in matched:
    sub = lab[lab['受试者筛选号'] == sid]
    tests = sub['检测项目'].unique()
    available = [t.split('(')[0][:6] for t in key_tests if t in tests]
    print(f"    {sid}: {len(sub)} records, key tests: {len([t for t in key_tests if t in tests])}/{len(key_tests)}")

# Save matching result
match_result = {
    'sample_ids': [int(x) for x in sample_ids],
    'matched_ids': [int(x) for x in matched],
    'unmatched_ids': [int(x) for x in unmatched],
    'match_rate': len(matched) / len(sample_ids),
    'pkpd_eligible': len(matched) >= 5,
}
with open('transformed/subject_matching.json', 'w') as f:
    json.dump(match_result, f, indent=2)

# ============================================================
# 4. Generate transformed data description files
# ============================================================
print("\n" + "=" * 60)
print("4. Generating data description files")
print("=" * 60)

# sample.xlsx description
sample_desc = f"""# sample.xlsx 数据描述

## 基本信息

- **文件**: reference/raw-data-yance/sample.xlsx
- **数据量**: {sample.shape[0]} 行 × {sample.shape[1]} 列
- **受试者数**: {sample['受试者ID'].nunique()} 例
- **受试者 ID**: {sorted(sample['受试者ID'].unique())}

## 数据结构

| 列名 | 数据类型 | 说明 |
|------|---------|------|
| 受试者ID | int | 受试者编号（1003-1028） |
| 访视 | str | 访视名称（15 个时间点） |
| 分析项 | str | 检测项目（2 项） |
| 结果 | mixed | 检测结果（数值 + BLD/BLQ） |

## 访视时间点

| 访视名称 | 回输后天数（Day） |
|----------|---------------|
| 清淋前检查 | -5 |
| 主要随访期 D1 | 1 |
| 主要随访期 D4 | 4 |
| 主要随访期 D7 | 7 |
| 主要随访期 D10 | 10 |
| 主要随访期 D14 | 14 |
| 主要随访期 D21 | 21 |
| 主要随访期 D28 | 28 |
| 主要随访期 D60 | 60 |
| 主要随访期 D90 | 90 |
| 主要随访期 D180 | 180 |
| 主要随访期 D270 | 270 |
| 主要随访期 D360 | 360 |
| 主要随访期 D540 | 540 |
| 退出主要随访访视 | 不确定 |

## 分析项

| 分析项 | 数据点数 | 受试者数 |
|--------|---------|---------|
| CAR-T 细胞占 T 细胞百分比 | {len(cart_pct)} | {cart_pct['SubjectID'].nunique()} |
| CAR-T 细胞绝对计数 | {len(cart_abs)} | {cart_abs['SubjectID'].nunique()} |

## BLD/BLQ 分布

| 标记 | CAR-T/T-cell % | CAR-T 绝对计数 |
|------|---------------|---------------|
| BLD | {len(sample[(sample['分析项']=='CAR-T细胞占T细胞百分比') & (sample['Flag']=='BLD')])} | {len(sample[(sample['分析项']=='CAR-T细胞绝对计数') & (sample['Flag']=='BLD')])} |
| BLQ | {len(sample[(sample['分析项']=='CAR-T细胞占T细胞百分比') & (sample['Flag']=='BLQ')])} | {len(sample[(sample['分析项']=='CAR-T细胞绝对计数') & (sample['Flag']=='BLQ')])} |
| 数值 | {len(sample[(sample['分析项']=='CAR-T细胞占T细胞百分比') & (sample['Flag']=='numeric')])} | {len(sample[(sample['分析项']=='CAR-T细胞绝对计数') & (sample['Flag']=='numeric')])} |
"""

with open('transformed/sample.xlsx.md', 'w') as f:
    f.write(sample_desc)
print("  Written: transformed/sample.xlsx.md")

# G957 description
center_counts = lab.groupby('中心编号')['受试者筛选号'].nunique()
test_counts = lab['检测项目'].value_counts()

g957_desc = f"""# G957 中心实验室检测结果数据描述

## 基本信息

- **文件**: reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx
- **数据量**: {lab.shape[0]} 行 × {lab.shape[1]} 列
- **中心数**: {lab['中心编号'].nunique()}
- **受试者数**: {lab['受试者筛选号'].nunique()}
- **检测项目数**: {lab['检测项目'].nunique()}

## 数据结构

| 列名 | 数据类型 | 说明 |
|------|---------|------|
| 方案编号 | str | 试验方案编号 |
| 中心编号 | int | 参与中心编号 |
| 观合样本编号 | str | 样本编号 |
| 受试者筛选号 | int | 受试者编号 |
| 访视周期 | str | 访视时间点名称 |
| 样本类型 | str | 样本类型 |
| 采集时间 | datetime | 样本采集时间 |
| 检测项目 | str | 大类检测项目 |
| 检测分项 | str | 检测分项指标 |
| 结果 | mixed | 检测结果（数值或文本） |
| 单位 | str | 结果单位 |
| 检验备注 | str | 检验备注信息 |
| 异常样本备注 | str | 异常样本说明 |
| 申请单备注 | str | 申请单备注 |
| 反审时间 | datetime | 反审时间 |
| 反审备注 | str | 反审原因 |
| 检测时间 | datetime | 检测完成时间 |
| 报告时间 | datetime | 报告出具时间 |

## 各中心数据量

| 中心编号 | 受试者数 | 记录数 |
|---------|---------|--------|
"""

for center in sorted(lab['中心编号'].unique()):
    sub = lab[lab['中心编号'] == center]
    g957_desc += f"| {center} | {sub['受试者筛选号'].nunique()} | {len(sub)} |\n"

g957_desc += f"""
## 检测项目汇总

| 检测项目 | 记录数 | 类型 |
|---------|--------|------|
"""
for test in sorted(test_counts.index):
    g957_desc += f"| {test} | {test_counts[test]} | {test_type_map.get(test, '?')} |\n"

g957_desc += f"""
## 受试者匹配

- sample.xlsx 受试者: {len(sample_ids)} 例
- 中心实验室受试者: {len(lab_ids)} 例
- 匹配成功: {len(matched)} 例 ({matched})
- 匹配失败: {len(unmatched)} 例 ({unmatched})
- PK-PD 分析可用: {'是' if len(matched) >= 5 else '否'}（{len(matched)} 例 ≥ 5 例阈值）
"""

with open('transformed/G957_central_lab.xlsx.md', 'w') as f:
    f.write(g957_desc)
print("  Written: transformed/G957_central_lab.xlsx.md")

# Save preprocessed lab data for downstream tasks
lab.to_pickle('transformed/lab_preprocessed.pkl')
print("  Written: transformed/lab_preprocessed.pkl")

print("\n" + "=" * 60)
print("T-001 COMPLETE")
print("=" * 60)
