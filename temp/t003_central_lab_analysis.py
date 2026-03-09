#!/usr/bin/env python3
"""T-003: 中心实验室数据质量与生物标志物分析
Data quality assessment + biomarker trend analysis from G957 central lab data.
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

lab = pd.read_pickle('transformed/lab_preprocessed.pkl')
print(f"Loaded: {lab.shape[0]} rows, {lab['受试者筛选号'].nunique()} subjects, {lab['中心编号'].nunique()} centers")

# Key post-infusion visits for biomarker trend analysis
post_infusion_visits = ['清淋前', 'D5', 'D8', 'D11', 'D15', 'D22', 'D29',
                        'W8', 'W12', 'W16', 'W20', 'W24', 'W28', 'W32', 'W36',
                        'W40', 'W44', 'W48', 'W52', 'W56', 'W60', 'W64', 'W68', 'W72', 'W76']
# Map for x-axis position
visit_day_map = {
    '筛选期': -60, '清淋前': -5,
    'D5': 5, 'D8': 8, 'D11': 11, 'D15': 15, 'D22': 22, 'D29': 29,
    'W8': 56, 'W12': 84, 'W16': 112, 'W20': 140, 'W24': 168,
    'W28': 196, 'W32': 224, 'W36': 252, 'W40': 280, 'W44': 308,
    'W48': 336, 'W52': 364, 'W56': 392, 'W60': 420, 'W64': 448,
    'W68': 476, 'W72': 504, 'W76': 532,
}

COLORS = {
    'primary': '#2563EB', 'secondary': '#7C3AED', 'accent': '#059669',
    'warning': '#D97706', 'danger': '#DC2626', 'dark': '#1F2937',
}

def style_ax(ax, title=None, xlabel=None, ylabel=None):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3)
    if title: ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
    if xlabel: ax.set_xlabel(xlabel, fontsize=11)
    if ylabel: ax.set_ylabel(ylabel, fontsize=11)

# ============================================================
# Part A: 数据质量评估
# ============================================================
print("\n=== Part A: Data Quality Assessment ===")

# A1. Missing rate per column
print("\nA1. Column missing rates:")
missing_rates = {}
for col in lab.columns:
    rate = lab[col].isna().mean()
    missing_rates[col] = rate
    if rate > 0:
        print(f"  {col}: {rate:.4f} ({lab[col].isna().sum()} / {len(lab)})")

# A2. Abnormal sample analysis
print("\nA2. Abnormal sample analysis:")
abnormal = lab['异常样本备注'].dropna()
abnormal_count = len(abnormal)
abnormal_rate = abnormal_count / len(lab)
print(f"  Total abnormal: {abnormal_count} ({abnormal_rate:.2%})")
if abnormal_count > 0:
    # Classify abnormal types
    abnormal_types = abnormal.value_counts().head(20)
    print("  Top types:")
    for t, c in abnormal_types.items():
        print(f"    {t}: {c}")

# A3. Recheck (反审) analysis
print("\nA3. Recheck analysis:")
recheck = lab['反审时间'].notna()
recheck_count = recheck.sum()
recheck_rate = recheck_count / len(lab)
print(f"  Total rechecked: {recheck_count} ({recheck_rate:.2%})")
if recheck_count > 0:
    recheck_reasons = lab.loc[recheck, '反审备注'].dropna().value_counts().head(10)
    print("  Top reasons:")
    for r, c in recheck_reasons.items():
        print(f"    {r}: {c}")

# A4. Center data volume
center_stats = lab.groupby('中心编号').agg(
    记录数=('受试者筛选号', 'count'),
    受试者数=('受试者筛选号', 'nunique'),
    检测项目数=('检测项目', 'nunique'),
).sort_values('记录数', ascending=False)
print(f"\nA4. Center data volume (top 10):")
print(center_stats.head(10).to_string())

# --- Chart: 各中心数据量柱状图 ---
print("\nGenerating: chart_center_data_volume.png")
fig, ax = plt.subplots(figsize=(14, 6))
centers_sorted = center_stats.sort_values('记录数', ascending=True)
bars = ax.barh(range(len(centers_sorted)), centers_sorted['记录数'], color=COLORS['primary'], alpha=0.8)
ax.set_yticks(range(len(centers_sorted)))
ax.set_yticklabels([f"中心 {c}" for c in centers_sorted.index], fontsize=8)
# Annotate subject count
for i, (idx, row) in enumerate(centers_sorted.iterrows()):
    ax.text(row['记录数'] + 50, i, f"N={row['受试者数']}", va='center', fontsize=7)
style_ax(ax, '各中心数据量对比', '记录数', '')
plt.tight_layout()
plt.savefig('generated/chart_center_data_volume.png', dpi=200, bbox_inches='tight')
plt.close()

with open('generated/chart_center_data_volume.png.desc.md', 'w') as f:
    f.write(f"# 各中心数据量对比\n\n水平柱状图展示 {lab['中心编号'].nunique()} 个中心的记录数，标注各中心受试者数（N=xx）。\n")

# --- Chart: 检测项目 × 访视周期完整性热力图 ---
print("Generating: chart_missing_rate_heatmap.png")
key_tests = ['血清蛋白电泳', '血清游离轻链', '免疫球蛋白IgA定量(IgA)',
             '免疫球蛋白IgG定量(IgG)', '免疫球蛋白IgM定量(IgM)',
             '血清免疫固定电泳', '24小时尿蛋白定量', 'BCMA检测',
             '微小残留病检测（多发性骨髓瘤）', 'CAR-T 细胞检测（CT103A）']
display_visits = ['筛选期', '清淋前', 'D29', 'W8', 'W12', 'W16', 'W20', 'W24',
                  'W28', 'W32', 'W36', 'W40', 'W48', 'W52', 'W76']

coverage = pd.DataFrame(index=key_tests, columns=display_visits, dtype=float)
for test in key_tests:
    for visit in display_visits:
        sub = lab[(lab['检测项目'] == test) & (lab['访视周期'] == visit)]
        n_subjects = sub['受试者筛选号'].nunique()
        coverage.loc[test, visit] = n_subjects

fig, ax = plt.subplots(figsize=(14, 7))
im = ax.imshow(coverage.values.astype(float), aspect='auto', cmap='YlGnBu', interpolation='nearest')
ax.set_xticks(range(len(display_visits)))
ax.set_xticklabels(display_visits, fontsize=8, rotation=45, ha='right')
ax.set_yticks(range(len(key_tests)))
# Shorter names for display
short_names = [t[:15] + '...' if len(t) > 15 else t for t in key_tests]
ax.set_yticklabels(short_names, fontsize=8)
# Annotate
for i in range(len(key_tests)):
    for j in range(len(display_visits)):
        val = coverage.values[i, j]
        if not np.isnan(val) and val > 0:
            ax.text(j, i, f'{int(val)}', ha='center', va='center', fontsize=6,
                    color='white' if val > coverage.values[~np.isnan(coverage.values.astype(float))].max() * 0.6 else 'black')
plt.colorbar(im, ax=ax, shrink=0.8, label='受试者数')
ax.set_title('检测项目 × 访视周期覆盖人数热力图', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('generated/chart_missing_rate_heatmap.png', dpi=200, bbox_inches='tight')
plt.close()

with open('generated/chart_missing_rate_heatmap.png.desc.md', 'w') as f:
    f.write("# 检测项目 × 访视周期覆盖人数热力图\n\n展示关键检测项目在各访视周期的受试者覆盖人数。颜色越深表示覆盖人数越多。\n")

# --- Chart: 异常样本分布 ---
print("Generating: chart_abnormal_sample_dist.png")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Pie chart - abnormal proportion
labels_pie = ['正常样本', '异常样本']
sizes_pie = [len(lab) - abnormal_count, abnormal_count]
axes[0].pie(sizes_pie, labels=labels_pie, autopct='%1.1f%%', startangle=90,
            colors=[COLORS['primary'], COLORS['danger']])
axes[0].set_title('异常样本比例', fontsize=12, fontweight='bold')

# Bar chart - abnormal types
if abnormal_count > 0:
    top_types = abnormal.value_counts().head(8)
    axes[1].barh(range(len(top_types)), top_types.values, color=COLORS['warning'], alpha=0.8)
    axes[1].set_yticks(range(len(top_types)))
    labels = [str(t)[:25] for t in top_types.index]
    axes[1].set_yticklabels(labels, fontsize=7)
    style_ax(axes[1], '异常样本类型分布（Top 8）', '记录数', '')
else:
    axes[1].text(0.5, 0.5, '无异常样本记录', ha='center', va='center', fontsize=12)
    axes[1].set_axis_off()

plt.tight_layout()
plt.savefig('generated/chart_abnormal_sample_dist.png', dpi=200, bbox_inches='tight')
plt.close()

with open('generated/chart_abnormal_sample_dist.png.desc.md', 'w') as f:
    f.write(f"# 异常样本分布\n\n左：异常样本比例饼图（{abnormal_rate:.1%}）。右：异常样本类型分布柱状图（Top 8 类型）。\n")

# ============================================================
# Part B: 生物标志物趋势分析
# ============================================================
print("\n=== Part B: Biomarker Trend Analysis ===")

def plot_biomarker_trend(data, test_name, sub_items, title, ylabel, output_name,
                         ref_lines=None, log_scale=False):
    """Generic biomarker trend plot with median + IQR."""
    n_panels = len(sub_items)
    fig, axes = plt.subplots(1, n_panels, figsize=(6*n_panels, 5), squeeze=False)
    axes = axes[0]

    for ax_i, (sub_item, sub_label) in enumerate(sub_items):
        ax = axes[ax_i]
        sub = data[(data['检测项目'] == test_name) & (data['检测分项'] == sub_item)].copy()
        sub = sub[sub['访视周期'].isin(post_infusion_visits)]
        sub['DayNum'] = sub['访视周期'].map(visit_day_map)
        sub = sub.dropna(subset=['DayNum', 'NumericResult'])

        if len(sub) == 0:
            ax.text(0.5, 0.5, f'无数据: {sub_label}', ha='center', va='center')
            continue

        # Aggregate by visit
        agg = sub.groupby('DayNum')['NumericResult'].agg(['median', 'mean',
            lambda x: x.quantile(0.25), lambda x: x.quantile(0.75), 'count'])
        agg.columns = ['Median', 'Mean', 'Q1', 'Q3', 'N']
        agg = agg.sort_index()

        ax.fill_between(agg.index, agg['Q1'], agg['Q3'], alpha=0.2, color=COLORS['primary'])
        ax.plot(agg.index, agg['Median'], marker='o', markersize=6, linewidth=2,
                color=COLORS['primary'], markerfacecolor='white', markeredgecolor=COLORS['primary'],
                markeredgewidth=1.5, zorder=10)

        # Annotate sample size
        for day, row in agg.iterrows():
            ax.annotate(f'n={int(row["N"])}', (day, row['Median']),
                        textcoords='offset points', xytext=(0, 10),
                        fontsize=6, ha='center', color='gray')

        # Reference lines
        if ref_lines:
            for ref_val, ref_label, ref_color in ref_lines:
                ax.axhline(ref_val, color=ref_color, linestyle=':', linewidth=1, alpha=0.7)
                ax.text(agg.index[-1], ref_val, f' {ref_label}', fontsize=7, color=ref_color, va='bottom')

        if log_scale:
            ax.set_yscale('log')

        # X-axis labels
        xticks = agg.index.tolist()
        xlabels = []
        for d in xticks:
            for v, dm in visit_day_map.items():
                if dm == d:
                    xlabels.append(v)
                    break
            else:
                xlabels.append(str(d))
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels, fontsize=7, rotation=60, ha='right')
        style_ax(ax, sub_label, 'Visit', ylabel)

    plt.suptitle(title, fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'generated/{output_name}', dpi=200, bbox_inches='tight')
    plt.close()
    return True

# B1. M 蛋白 (SPEP)
print("\nB1. M-protein (SPEP) trend...")
plot_biomarker_trend(
    lab, '血清蛋白电泳',
    [('M蛋白含量', 'M 蛋白含量 (g/L)'), ('M蛋白百分比', 'M 蛋白百分比 (%)')],
    '血清蛋白电泳 — M 蛋白趋势', 'Value',
    'chart_mprotein_trend.png'
)
with open('generated/chart_mprotein_trend.png.desc.md', 'w') as f:
    f.write("# M 蛋白趋势图\n\n展示 M 蛋白含量和百分比随访视周期的变化，中位数 + IQR，标注各时间点样本量。\n")

# B2. FLC (游离轻链)
print("B2. FLC trend...")
plot_biomarker_trend(
    lab, '血清游离轻链',
    [('血清游离轻链Kappa', 'FLC Kappa (mg/L)'),
     ('血清游离轻链Lambda', 'FLC Lambda (mg/L)'),
     ('κ:λ比值', 'Kappa/Lambda 比值')],
    '血清游离轻链趋势', 'Value',
    'chart_flc_trend.png'
)
with open('generated/chart_flc_trend.png.desc.md', 'w') as f:
    f.write("# FLC 趋势图\n\n展示血清游离轻链 Kappa、Lambda 和 Kappa/Lambda 比值随访视周期变化，中位数 + IQR。\n")

# FLC ratio separately with reference range
print("B2b. FLC ratio trend with reference lines...")
fig, ax = plt.subplots(figsize=(10, 5))
sub = lab[(lab['检测项目'] == '血清游离轻链') & (lab['检测分项'] == 'κ:λ比值')].copy()
sub = sub[sub['访视周期'].isin(post_infusion_visits)]
sub['DayNum'] = sub['访视周期'].map(visit_day_map)
sub = sub.dropna(subset=['DayNum', 'NumericResult'])

agg = sub.groupby('DayNum')['NumericResult'].agg(['median', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75), 'count'])
agg.columns = ['Median', 'Q1', 'Q3', 'N']
agg = agg.sort_index()

ax.fill_between(agg.index, agg['Q1'], agg['Q3'], alpha=0.2, color=COLORS['secondary'])
ax.plot(agg.index, agg['Median'], marker='o', markersize=7, linewidth=2,
        color=COLORS['secondary'], markerfacecolor='white', markeredgecolor=COLORS['secondary'],
        markeredgewidth=1.5, zorder=10)

# Normal range reference lines
ax.axhline(0.26, color=COLORS['accent'], linestyle='--', linewidth=1.5, alpha=0.8, label='正常范围下限 (0.26)')
ax.axhline(1.65, color=COLORS['accent'], linestyle='--', linewidth=1.5, alpha=0.8, label='正常范围上限 (1.65)')
ax.fill_between(agg.index, 0.26, 1.65, alpha=0.05, color=COLORS['accent'])

for day, row in agg.iterrows():
    ax.annotate(f'n={int(row["N"])}', (day, row['Median']),
                textcoords='offset points', xytext=(0, 10), fontsize=7, ha='center', color='gray')

xticks = agg.index.tolist()
xlabels = []
for d in xticks:
    for v, dm in visit_day_map.items():
        if dm == d:
            xlabels.append(v)
            break
    else:
        xlabels.append(str(d))
ax.set_xticks(xticks)
ax.set_xticklabels(xlabels, fontsize=8, rotation=45, ha='right')
style_ax(ax, 'FLC Kappa/Lambda 比值趋势（含正常范围参考线）', 'Visit', 'κ:λ 比值')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('generated/chart_flc_ratio_trend.png', dpi=200, bbox_inches='tight')
plt.close()

with open('generated/chart_flc_ratio_trend.png.desc.md', 'w') as f:
    f.write("# FLC Kappa/Lambda 比值趋势图\n\n展示 FLC κ:λ 比值随访视周期变化（中位数 + IQR），绿色虚线标注正常范围（0.26-1.65）。\n")

# B3. 免疫球蛋白 (IgA/IgG/IgM)
print("B3. Immunoglobulin trend...")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
ig_tests = [
    ('免疫球蛋白IgA定量(IgA)', '免疫球蛋白A', 'IgA (g/L)', COLORS['primary']),
    ('免疫球蛋白IgG定量(IgG)', '免疫球蛋白G', 'IgG (g/L)', COLORS['secondary']),  # Note: need to check sub-item name
    ('免疫球蛋白IgM定量(IgM)', '免疫球蛋白M', 'IgM (g/L)', COLORS['accent']),
]

# Get actual sub-item names
for test_name, _, _, _ in ig_tests:
    subs = lab[lab['检测项目'] == test_name]['检测分项'].unique()
    print(f"  {test_name} sub-items: {subs}")

# Correct sub-item names
ig_tests_corrected = [
    ('免疫球蛋白IgA定量(IgA)', '免疫球蛋白A', 'IgA (g/L)', COLORS['primary']),
    ('免疫球蛋白IgG定量(IgG)', '免疫球蛋白G', 'IgG (g/L)', COLORS['secondary']),
    ('免疫球蛋白IgM定量(IgM)', '免疫球蛋白M', 'IgM (g/L)', COLORS['accent']),
]

for ax_i, (test_name, sub_item, ylabel, color) in enumerate(ig_tests_corrected):
    ax = axes[ax_i]
    sub = lab[(lab['检测项目'] == test_name)].copy()

    sub = sub[sub['访视周期'].isin(post_infusion_visits)]
    sub['DayNum'] = sub['访视周期'].map(visit_day_map)
    sub = sub.dropna(subset=['DayNum', 'NumericResult'])

    if len(sub) == 0:
        ax.text(0.5, 0.5, f'无数据', ha='center', va='center')
        continue

    agg = sub.groupby('DayNum')['NumericResult'].agg(['median', lambda x: x.quantile(0.25),
        lambda x: x.quantile(0.75), 'count'])
    agg.columns = ['Median', 'Q1', 'Q3', 'N']
    agg = agg.sort_index()

    ax.fill_between(agg.index, agg['Q1'], agg['Q3'], alpha=0.2, color=color)
    ax.plot(agg.index, agg['Median'], marker='o', markersize=6, linewidth=2,
            color=color, markerfacecolor='white', markeredgecolor=color, markeredgewidth=1.5)

    for day, row in agg.iterrows():
        ax.annotate(f'n={int(row["N"])}', (day, row['Median']),
                    textcoords='offset points', xytext=(0, 10), fontsize=6, ha='center', color='gray')

    xticks = agg.index.tolist()
    xlabels = []
    for d in xticks:
        for v, dm in visit_day_map.items():
            if dm == d:
                xlabels.append(v)
                break
        else:
            xlabels.append(str(d))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels, fontsize=7, rotation=60, ha='right')
    style_ax(ax, ylabel, 'Visit', 'g/L')

plt.suptitle('免疫球蛋白定量趋势（IgA / IgG / IgM）', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('generated/chart_immunoglobulin_trend.png', dpi=200, bbox_inches='tight')
plt.close()

with open('generated/chart_immunoglobulin_trend.png.desc.md', 'w') as f:
    f.write("# 免疫球蛋白定量趋势图\n\n三面板展示 IgA、IgG、IgM 随访视周期的变化趋势（中位数 + IQR），标注样本量。\n")

# B4. IFE (免疫固定电泳)
print("B4. IFE response analysis...")
ife = lab[lab['检测项目'] == '血清免疫固定电泳'].copy()
ife_result = ife[ife['检测分项'] == '结果解释'].copy()
ife_result = ife_result[ife_result['访视周期'].isin(post_infusion_visits)]

# Classify as positive/negative
def classify_ife(val):
    s = str(val).strip().lower()
    if '阴性' in s or 'negative' in s:
        return '阴性'
    elif '阳性' in s or 'positive' in s or s not in ('', 'nan', 'none'):
        return '阳性'
    return np.nan

ife_result['IFE_Status'] = ife_result['结果'].apply(classify_ife)
ife_result = ife_result.dropna(subset=['IFE_Status'])

# Check what values exist
print(f"  IFE result values sample: {ife_result['结果'].unique()[:10]}")

fig, ax = plt.subplots(figsize=(12, 5))

if len(ife_result) > 0:
    ife_result['DayNum'] = ife_result['访视周期'].map(visit_day_map)
    ife_agg = ife_result.groupby(['DayNum', 'IFE_Status']).size().unstack(fill_value=0)
    ife_agg = ife_agg.sort_index()

    # Calculate proportions
    ife_total = ife_agg.sum(axis=1)
    ife_pct = ife_agg.div(ife_total, axis=0) * 100

    if '阳性' in ife_pct.columns and '阴性' in ife_pct.columns:
        ax.bar(range(len(ife_pct)), ife_pct['阳性'], label='阳性', color=COLORS['danger'], alpha=0.8)
        ax.bar(range(len(ife_pct)), ife_pct['阴性'], bottom=ife_pct['阳性'],
               label='阴性', color=COLORS['accent'], alpha=0.8)
    elif '阳性' in ife_pct.columns:
        ax.bar(range(len(ife_pct)), ife_pct['阳性'], label='阳性', color=COLORS['danger'], alpha=0.8)
    elif '阴性' in ife_pct.columns:
        ax.bar(range(len(ife_pct)), ife_pct['阴性'], label='阴性', color=COLORS['accent'], alpha=0.8)

    # Annotate total N
    for i, (day, total) in enumerate(ife_total.items()):
        ax.text(i, 102, f'n={int(total)}', ha='center', fontsize=7, color='gray')

    xlabels = []
    for d in ife_pct.index:
        for v, dm in visit_day_map.items():
            if dm == d:
                xlabels.append(v)
                break
        else:
            xlabels.append(str(d))
    ax.set_xticks(range(len(ife_pct)))
    ax.set_xticklabels(xlabels, fontsize=8, rotation=45, ha='right')
    ax.set_ylim(0, 115)
    ax.legend(fontsize=10)
    style_ax(ax, '免疫固定电泳（IFE）阳性/阴性比例变化', 'Visit', '比例 (%)')
else:
    ax.text(0.5, 0.5, 'IFE 数据不足', ha='center', va='center', fontsize=12)

plt.tight_layout()
plt.savefig('generated/chart_ife_response.png', dpi=200, bbox_inches='tight')
plt.close()

with open('generated/chart_ife_response.png.desc.md', 'w') as f:
    f.write("# IFE 阳性/阴性比例变化图\n\n堆叠柱状图展示各访视周期免疫固定电泳阳性/阴性比例变化，标注样本量。\n")

# B5. Daratumumab interference removal
print("B5. Daratumumab interference removal...")
dara = lab[lab['检测项目'] == '达雷妥尤(Dara)药物干扰移除检测'].copy()
print(f"  Dara records: {len(dara)}, subjects: {dara['受试者筛选号'].nunique()}")
if len(dara) > 0:
    print(f"  检测分项: {dara['检测分项'].unique()}")
    dara_sub = dara[dara['访视周期'].isin(post_infusion_visits)]
    dara_sub['DayNum'] = dara_sub['访视周期'].map(visit_day_map)
    dara_sub = dara_sub.dropna(subset=['DayNum', 'NumericResult'])

    if len(dara_sub) > 0:
        fig, ax = plt.subplots(figsize=(10, 5))
        agg = dara_sub.groupby('DayNum')['NumericResult'].agg(['median', lambda x: x.quantile(0.25),
            lambda x: x.quantile(0.75), 'count'])
        agg.columns = ['Median', 'Q1', 'Q3', 'N']
        agg = agg.sort_index()

        ax.fill_between(agg.index, agg['Q1'], agg['Q3'], alpha=0.2, color=COLORS['warning'])
        ax.plot(agg.index, agg['Median'], marker='o', markersize=7, linewidth=2,
                color=COLORS['warning'], markerfacecolor='white', markeredgecolor=COLORS['warning'])

        for day, row in agg.iterrows():
            ax.annotate(f'n={int(row["N"])}', (day, row['Median']),
                        textcoords='offset points', xytext=(0, 10), fontsize=7, ha='center', color='gray')

        xticks = agg.index.tolist()
        xlabels = []
        for d in xticks:
            for v, dm in visit_day_map.items():
                if dm == d:
                    xlabels.append(v)
                    break
            else:
                xlabels.append(str(d))
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels, fontsize=8, rotation=45, ha='right')
        style_ax(ax, 'Daratumumab 干扰去除检测结果趋势', 'Visit', 'Value')
        plt.tight_layout()
        plt.savefig('generated/chart_dara_interference.png', dpi=200, bbox_inches='tight')
        plt.close()

        with open('generated/chart_dara_interference.png.desc.md', 'w') as f:
            f.write(f"# Daratumumab 干扰去除检测趋势\n\n展示 Daratumumab 药物干扰去除后的检测结果趋势（{dara_sub['受试者筛选号'].nunique()} 例受试者）。\n")
    else:
        print("  No post-infusion Dara data with numeric results")
else:
    print("  No Dara interference data available")

# B6. Test coverage heatmap
print("B6. Test coverage heatmap...")
all_tests = lab['检测项目'].unique()
display_visits_b6 = ['筛选期', '清淋前', 'D5', 'D8', 'D11', 'D15', 'D22', 'D29',
                      'W8', 'W12', 'W24', 'W36', 'W48', 'W76']

coverage_b6 = pd.DataFrame(0, index=all_tests, columns=display_visits_b6, dtype=float)
for test in all_tests:
    for visit in display_visits_b6:
        sub = lab[(lab['检测项目'] == test) & (lab['访视周期'] == visit)]
        coverage_b6.loc[test, visit] = sub['受试者筛选号'].nunique()

# Remove all-zero rows
coverage_b6 = coverage_b6[(coverage_b6 > 0).any(axis=1)]
coverage_b6 = coverage_b6.sort_values(coverage_b6.columns.tolist(), ascending=False)

fig, ax = plt.subplots(figsize=(14, 10))
im = ax.imshow(coverage_b6.values.astype(float), aspect='auto', cmap='YlOrRd', interpolation='nearest')
ax.set_xticks(range(len(display_visits_b6)))
ax.set_xticklabels(display_visits_b6, fontsize=8, rotation=45, ha='right')
ax.set_yticks(range(len(coverage_b6)))
ax.set_yticklabels([t[:20] for t in coverage_b6.index], fontsize=7)
for i in range(len(coverage_b6)):
    for j in range(len(display_visits_b6)):
        val = coverage_b6.values[i, j]
        if val > 0:
            ax.text(j, i, f'{int(val)}', ha='center', va='center', fontsize=5,
                    color='white' if val > 50 else 'black')
plt.colorbar(im, ax=ax, shrink=0.7, label='受试者数')
ax.set_title('全部检测项目 × 访视周期覆盖热力图', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('generated/chart_test_coverage_heatmap.png', dpi=200, bbox_inches='tight')
plt.close()

with open('generated/chart_test_coverage_heatmap.png.desc.md', 'w') as f:
    f.write(f"# 全部检测项目覆盖热力图\n\n展示 {len(all_tests)} 个检测项目在各访视周期的受试者覆盖数，颜色深浅反映覆盖程度。\n")

print("\n=== T-003 COMPLETE ===")
print("Generated files:")
for f in ['chart_center_data_volume.png', 'chart_missing_rate_heatmap.png',
          'chart_abnormal_sample_dist.png', 'chart_mprotein_trend.png',
          'chart_flc_trend.png', 'chart_flc_ratio_trend.png',
          'chart_immunoglobulin_trend.png', 'chart_ife_response.png',
          'chart_test_coverage_heatmap.png']:
    print(f"  - generated/{f} + .desc.md")
