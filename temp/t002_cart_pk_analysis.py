#!/usr/bin/env python3
"""T-002: CAR-T 细胞 PK 分析
Generates kinetics curves and calculates PK parameters from sample.xlsx data.
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

# Load preprocessed data
cart_pct = pd.read_csv('transformed/cart_tcell_pct.csv')
cart_abs = pd.read_csv('transformed/cart_abs_count.csv')

subject_ids = sorted(cart_pct['SubjectID'].unique())
print(f"Subjects: {len(subject_ids)} — {subject_ids}")

# Time points for plotting
all_days = sorted(cart_pct['Day'].unique())
print(f"Time points: {all_days}")

# Day → label mapping
day_label = {
    -5: 'BL', 1: 'D1', 4: 'D4', 7: 'D7', 10: 'D10', 14: 'D14',
    21: 'D21', 28: 'D28', 60: 'D60', 90: 'D90', 180: 'D180',
    270: 'D270', 360: 'D360', 540: 'D540'
}

# ============================================================
# 1. PK 参数计算 (NCA)
# ============================================================
print("\n=== PK Parameter Calculation ===")

pk_results = []
for sid in subject_ids:
    pdata_pct = cart_pct[cart_pct['SubjectID'] == sid].sort_values('Day')
    pdata_abs = cart_abs[cart_abs['SubjectID'] == sid].sort_values('Day')

    days_pct = pdata_pct['Day'].values
    vals_pct = pdata_pct['Value'].values
    flags_pct = pdata_pct['Flag'].values

    days_abs = pdata_abs['Day'].values
    vals_abs = pdata_abs['Value'].values

    # --- Cmax and Tmax (percentage) ---
    cmax_pct = vals_pct.max()
    tmax_pct = days_pct[np.argmax(vals_pct)]

    # --- Cmax and Tmax (absolute count) ---
    cmax_abs = vals_abs.max() if len(vals_abs) > 0 else np.nan
    tmax_abs = days_abs[np.argmax(vals_abs)] if len(vals_abs) > 0 else np.nan

    # --- Tlast (last quantifiable time point, non-BLD/BLQ) ---
    numeric_mask = flags_pct == 'numeric'
    if numeric_mask.any():
        tlast = days_pct[numeric_mask][-1]
    else:
        tlast = np.nan

    # --- AUC0-28d (linear trapezoidal, BLQ=0) ---
    auc_28_mask = days_pct <= 28
    if auc_28_mask.sum() >= 2:
        auc_days = days_pct[auc_28_mask]
        auc_vals = vals_pct[auc_28_mask]
        auc_28 = np.trapz(auc_vals, auc_days)
    else:
        auc_28 = np.nan

    # --- AUC0-last ---
    if not np.isnan(tlast):
        last_mask = days_pct <= tlast
        if last_mask.sum() >= 2:
            auc_last = np.trapz(vals_pct[last_mask], days_pct[last_mask])
        else:
            auc_last = np.nan
    else:
        auc_last = np.nan

    # --- t1/2 and lambda_z ---
    t_half = np.nan
    lambda_z = np.nan

    # Find peak index
    peak_idx = np.argmax(vals_pct)
    if peak_idx < len(days_pct) - 1:
        # Terminal phase: points after Cmax that are positive
        term_days = days_pct[peak_idx:]
        term_vals = vals_pct[peak_idx:]
        pos_mask = term_vals > 0
        t_pos = term_days[pos_mask]
        v_pos = term_vals[pos_mask]

        if len(t_pos) >= 3:
            # Log-linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                t_pos, np.log(v_pos)
            )
            if slope < 0 and r_value**2 > 0.7:  # Reasonable fit
                lambda_z = -slope
                t_half = np.log(2) / lambda_z

    pk_results.append({
        'SubjectID': int(sid),
        'Cmax_pct': round(cmax_pct, 3),
        'Tmax_pct_day': int(tmax_pct),
        'Cmax_abs': round(cmax_abs, 1) if not np.isnan(cmax_abs) else np.nan,
        'Tmax_abs_day': int(tmax_abs) if not np.isnan(tmax_abs) else np.nan,
        'AUC0_28d': round(auc_28, 1) if not np.isnan(auc_28) else np.nan,
        'AUC0_last': round(auc_last, 1) if not np.isnan(auc_last) else np.nan,
        'Tlast_day': int(tlast) if not np.isnan(tlast) else np.nan,
        't_half_day': round(t_half, 1) if not np.isnan(t_half) else np.nan,
        'Lambda_z': round(lambda_z, 5) if not np.isnan(lambda_z) else np.nan,
    })

pk_df = pd.DataFrame(pk_results)
pk_df.to_csv('transformed/pk_parameters_comprehensive.csv', index=False)

print("\nPer-subject PK parameters:")
print(pk_df.to_string(index=False))

# Descriptive statistics
print("\n\nDescriptive Statistics:")
desc_cols = ['Cmax_pct', 'Tmax_pct_day', 'Cmax_abs', 'AUC0_28d', 'AUC0_last', 'Tlast_day', 't_half_day']
desc_stats = []
for col in desc_cols:
    vals = pk_df[col].dropna()
    if len(vals) == 0:
        continue
    row = {
        'Parameter': col,
        'N': len(vals),
        'Mean': round(vals.mean(), 2),
        'SD': round(vals.std(), 2),
        'Median': round(vals.median(), 2),
        'Min': round(vals.min(), 2),
        'Max': round(vals.max(), 2),
    }
    # Geometric mean (only for positive values)
    pos = vals[vals > 0]
    if len(pos) > 0:
        row['GeoMean'] = round(np.exp(np.log(pos).mean()), 2)
    else:
        row['GeoMean'] = np.nan
    desc_stats.append(row)

desc_df = pd.DataFrame(desc_stats)
print(desc_df.to_string(index=False))
desc_df.to_csv('transformed/pk_descriptive_stats.csv', index=False)

# t1/2 calculability
n_thalf = pk_df['t_half_day'].notna().sum()
print(f"\nt1/2 calculable: {n_thalf}/{len(pk_df)} subjects")

# ============================================================
# 2. Chart Generation
# ============================================================

# Color palette for 18 subjects
colors_18 = plt.cm.tab20(np.linspace(0, 1, 20))[:18]
markers_list = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'X', 'd', 'P', '8', 'H', '+', 'x', '1']

# --- Chart: CAR-T 细胞百分比动力学图 (reference style) ---
print("\nGenerating chart: CAR-T kinetics (percentage)...")
fig, ax = plt.subplots(figsize=(14, 8))

for i, sid in enumerate(subject_ids):
    pdata = cart_pct[cart_pct['SubjectID'] == sid].sort_values('Day')
    ax.plot(pdata['Day'], pdata['Value'],
            marker=markers_list[i], markersize=5, linewidth=1.2,
            color=colors_18[i], alpha=0.7, label=str(sid))

# Median line
median_by_day = cart_pct.groupby('Day')['Value'].median()
ax.plot(median_by_day.index, median_by_day.values,
        marker='o', markersize=9, linewidth=2.5,
        color='black', linestyle='--',
        markerfacecolor='white', markeredgecolor='black', markeredgewidth=2,
        label='Median', zorder=100)

ax.set_xlabel('Time post-infusion', fontsize=12)
ax.set_ylabel('CAR-T/T Cell (%)', fontsize=12)
ax.set_title('CAR-T/T Cell (%) 随回输后时间变化 — 全部受试者 (N=18)', fontsize=14, fontweight='bold')

# X-axis: actual days but show labels
xtick_days = [d for d in all_days if d in day_label]
ax.set_xticks(xtick_days)
ax.set_xticklabels([day_label[d] for d in xtick_days], fontsize=9, rotation=45)

ax.set_ylim(bottom=-0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.3)
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8, ncol=1, framealpha=0.9)

# Bottom annotation
fig.text(0.05, -0.02,
    '注：1) 图中展示 CAR-T 细胞占 T 细胞百分比随时间的变化趋势（上图）；'
    '2) 计算 PK 参数：Cmax、Tmax (day)、AUC0-28d (%.day)、AUC0-last、'
    'Tlast (末次可定量浓度时间)、terminal half-life (t1/2)',
    fontsize=8, color='gray', ha='left', va='top', wrap=True)

plt.tight_layout()
plt.savefig('generated/chart_cart_kinetics_pct.png', dpi=200, bbox_inches='tight')
plt.close()

# Description file
with open('generated/chart_cart_kinetics_pct.png.desc.md', 'w') as f:
    f.write("""# CAR-T/T Cell (%) 动力学曲线图

展示 18 例受试者 CAR-T 细胞占 T 细胞百分比随回输后时间的变化趋势。每例受试者一条彩色实线，黑色虚线为各时间点中位数。X 轴为回输后时间（BL 至 D540），Y 轴为 CAR-T/T Cell (%)。图例标识各受试者 ID。底部注释说明 PK 参数定义。
""")

# --- Chart: CAR-T 绝对计数动力学图 ---
print("Generating chart: CAR-T kinetics (absolute count)...")
fig, ax = plt.subplots(figsize=(14, 8))

for i, sid in enumerate(subject_ids):
    pdata = cart_abs[cart_abs['SubjectID'] == sid].sort_values('Day')
    ax.plot(pdata['Day'], pdata['Value'],
            marker=markers_list[i], markersize=5, linewidth=1.2,
            color=colors_18[i], alpha=0.7, label=str(sid))

median_abs = cart_abs.groupby('Day')['Value'].median()
ax.plot(median_abs.index, median_abs.values,
        marker='o', markersize=9, linewidth=2.5,
        color='black', linestyle='--',
        markerfacecolor='white', markeredgecolor='black', markeredgewidth=2,
        label='Median', zorder=100)

ax.set_xlabel('Time post-infusion', fontsize=12)
ax.set_ylabel('CAR-T 细胞绝对计数 (cells/µL)', fontsize=12)
ax.set_title('CAR-T 细胞绝对计数随回输后时间变化 — 全部受试者 (N=18)', fontsize=14, fontweight='bold')

xtick_days_abs = sorted(cart_abs['Day'].unique())
xtick_days_abs = [d for d in xtick_days_abs if d in day_label]
ax.set_xticks(xtick_days_abs)
ax.set_xticklabels([day_label[d] for d in xtick_days_abs], fontsize=9, rotation=45)

ax.set_ylim(bottom=-10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.3)
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8, ncol=1, framealpha=0.9)

plt.tight_layout()
plt.savefig('generated/chart_cart_kinetics_abs.png', dpi=200, bbox_inches='tight')
plt.close()

with open('generated/chart_cart_kinetics_abs.png.desc.md', 'w') as f:
    f.write("""# CAR-T 细胞绝对计数动力学曲线图

展示 18 例受试者 CAR-T 细胞绝对计数（cells/µL）随回输后时间的变化趋势。每例受试者一条彩色实线，黑色虚线为中位数。X 轴为回输后时间，Y 轴为绝对计数。
""")

# --- Chart: PK 参数汇总表 (as figure) ---
print("Generating chart: PK summary table...")
fig, ax = plt.subplots(figsize=(16, 10))
ax.axis('off')

# Build table data
table_cols = ['SubjectID', 'Cmax_pct', 'Tmax_pct_day', 'Cmax_abs', 'Tmax_abs_day',
              'AUC0_28d', 'AUC0_last', 'Tlast_day', 't_half_day']
col_labels = ['受试者 ID', 'Cmax\n(%)', 'Tmax\n(day)', 'Cmax\n(cells/µL)', 'Tmax_abs\n(day)',
              'AUC0-28d\n(%.day)', 'AUC0-last\n(%.day)', 'Tlast\n(day)', 't1/2\n(day)']

table_data = []
for _, row in pk_df.iterrows():
    r = []
    for col in table_cols:
        val = row[col]
        if pd.isna(val):
            r.append('NC')
        elif col == 'SubjectID':
            r.append(str(int(val)))
        elif 'day' in col.lower() and col != 't_half_day':
            r.append(str(int(val)))
        else:
            r.append(f'{val:.2f}' if isinstance(val, float) else str(val))
    table_data.append(r)

# Add summary row
summary = ['汇总 (N, Mean±SD, Median)']
for col in table_cols[1:]:
    vals = pk_df[col].dropna()
    if len(vals) > 0:
        summary.append(f'N={len(vals)}\n{vals.mean():.1f}±{vals.std():.1f}\nMed={vals.median():.1f}')
    else:
        summary.append('—')
table_data.append(summary)

table = ax.table(cellText=table_data, colLabels=col_labels,
                 cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(7)
table.scale(1.0, 1.6)

# Style header
for j in range(len(col_labels)):
    table[0, j].set_facecolor('#2563EB')
    table[0, j].set_text_props(color='white', fontweight='bold')

# Style summary row
for j in range(len(col_labels)):
    table[len(table_data), j].set_facecolor('#E5E7EB')

ax.set_title('CAR-T 细胞 PK 参数汇总表', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('generated/chart_pk_summary.png', dpi=200, bbox_inches='tight')
plt.close()

with open('generated/chart_pk_summary.png.desc.md', 'w') as f:
    f.write(f"""# CAR-T 细胞 PK 参数汇总表

展示 {len(subject_ids)} 例受试者的个体 PK 参数，包括 Cmax (%)、Tmax (day)、Cmax (cells/µL)、AUC0-28d (%.day)、AUC0-last (%.day)、Tlast (day)、t1/2 (day)。末行为汇总统计（N、Mean±SD、Median）。NC 表示不可计算。
""")

print("\n=== T-002 COMPLETE ===")
print(f"Generated files:")
print(f"  - transformed/pk_parameters_comprehensive.csv")
print(f"  - transformed/pk_descriptive_stats.csv")
print(f"  - generated/chart_cart_kinetics_pct.png + .desc.md")
print(f"  - generated/chart_cart_kinetics_abs.png + .desc.md")
print(f"  - generated/chart_pk_summary.png + .desc.md")
