#!/usr/bin/env python3
"""T-004: PK-PD 关联探索性分析
Links CAR-T PK parameters with disease biomarker changes for matched subjects.
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy import stats
import json
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

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

# Load data
pk_df = pd.read_csv('transformed/pk_parameters_comprehensive.csv')
lab = pd.read_pickle('transformed/lab_preprocessed.pkl')
with open('transformed/subject_matching.json') as f:
    match_info = json.load(f)

matched_ids = match_info['matched_ids']
print(f"Matched subjects for PK-PD: {len(matched_ids)} ({matched_ids})")
print(f"PK-PD eligible (≥5): {match_info['pkpd_eligible']}")

# ============================================================
# 1. Extract PD biomarker data for matched subjects
# ============================================================
print("\n=== Extracting PD biomarker data ===")

# Post-infusion visit order
post_visits = ['清淋前', 'D29', 'W8', 'W12', 'W16', 'W20', 'W24', 'W28', 'W32',
               'W36', 'W40', 'W44', 'W48', 'W52', 'W76']

pd_data = []

for sid in matched_ids:
    sub_lab = lab[lab['受试者筛选号'] == sid]

    # M-protein (SPEP M蛋白含量)
    mprotein = sub_lab[(sub_lab['检测项目'] == '血清蛋白电泳') &
                       (sub_lab['检测分项'] == 'M蛋白含量')]
    mprotein_vals = mprotein[mprotein['NumericResult'].notna()].copy()

    # Baseline M-protein (清淋前 or 筛选期)
    baseline_mp = mprotein_vals[mprotein_vals['访视周期'].isin(['清淋前', '筛选期'])]
    mp_baseline = baseline_mp['NumericResult'].iloc[0] if len(baseline_mp) > 0 else np.nan

    # Best response M-protein (minimum post-infusion)
    post_mp = mprotein_vals[mprotein_vals['访视周期'].isin(post_visits)]
    mp_best = post_mp['NumericResult'].min() if len(post_mp) > 0 else np.nan

    # Best % change
    if not np.isnan(mp_baseline) and mp_baseline > 0 and not np.isnan(mp_best):
        mp_best_pct_change = (mp_best - mp_baseline) / mp_baseline * 100
    else:
        mp_best_pct_change = np.nan

    # FLC ratio
    flc_ratio = sub_lab[(sub_lab['检测项目'] == '血清游离轻链') &
                        (sub_lab['检测分项'] == 'κ:λ比值')]
    flc_ratio_vals = flc_ratio[flc_ratio['NumericResult'].notna()].copy()

    # Baseline FLC ratio
    baseline_flc = flc_ratio_vals[flc_ratio_vals['访视周期'].isin(['清淋前', '筛选期'])]
    flc_baseline = baseline_flc['NumericResult'].iloc[0] if len(baseline_flc) > 0 else np.nan

    # Best response FLC ratio (closest to normal range 0.26-1.65)
    post_flc = flc_ratio_vals[flc_ratio_vals['访视周期'].isin(post_visits)]
    if len(post_flc) > 0:
        # Best = minimum distance from 1.0 (midpoint of normal range)
        flc_best = post_flc.loc[(post_flc['NumericResult'] - 1.0).abs().idxmin(), 'NumericResult']
        flc_change = flc_best - flc_baseline if not np.isnan(flc_baseline) else np.nan
    else:
        flc_best = np.nan
        flc_change = np.nan

    # IFE status
    ife = sub_lab[(sub_lab['检测项目'] == '血清免疫固定电泳') &
                  (sub_lab['检测分项'] == '结果解释')]
    # Baseline IFE
    bl_ife = ife[ife['访视周期'].isin(['清淋前', '筛选期'])]
    bl_ife_positive = len(bl_ife) > 0 and any('未见' not in str(v) for v in bl_ife['结果'].values)

    # Latest post-infusion IFE
    post_ife = ife[ife['访视周期'].isin(post_visits)]
    if len(post_ife) > 0:
        latest_ife = post_ife.iloc[-1]['结果']
        ife_negative = '未见' in str(latest_ife) or '阴性' in str(latest_ife).lower()
        ife_conversion = bl_ife_positive and ife_negative
    else:
        ife_negative = np.nan
        ife_conversion = np.nan

    pd_data.append({
        'SubjectID': sid,
        'MP_baseline': mp_baseline,
        'MP_best': mp_best,
        'MP_best_pct_change': mp_best_pct_change,
        'FLC_ratio_baseline': flc_baseline,
        'FLC_ratio_best': flc_best,
        'FLC_ratio_change': flc_change,
        'IFE_baseline_positive': bl_ife_positive,
        'IFE_conversion': ife_conversion,
    })

pd_df = pd.DataFrame(pd_data)
print("\nPD data summary:")
print(pd_df.to_string(index=False))

# ============================================================
# 2. Merge PK + PD
# ============================================================
pk_matched = pk_df[pk_df['SubjectID'].isin(matched_ids)].copy()
pkpd = pk_matched.merge(pd_df, on='SubjectID', how='inner')
pkpd.to_csv('transformed/pkpd_integrated.csv', index=False)

print(f"\nPK-PD integrated: {len(pkpd)} subjects")
print(pkpd[['SubjectID', 'Cmax_pct', 'AUC0_28d', 'MP_best_pct_change', 'FLC_ratio_change', 'IFE_conversion']].to_string(index=False))

# ============================================================
# 3. PK-PD Plots (if ≥5 subjects)
# ============================================================
n_eligible = len(pkpd)

if n_eligible >= 5:
    print(f"\n=== Generating PK-PD plots ({n_eligible} subjects) ===")

    # 3.1 Cmax vs M-protein best % change
    print("Generating: chart_pkpd_cmax_mprotein.png")
    fig, ax = plt.subplots(figsize=(8, 6))

    valid = pkpd.dropna(subset=['Cmax_pct', 'MP_best_pct_change'])
    valid = valid[valid['Cmax_pct'] > 0]  # Exclude non-expanders

    if len(valid) >= 3:
        ax.scatter(valid['Cmax_pct'], valid['MP_best_pct_change'],
                   c=COLORS['primary'], s=80, alpha=0.7, edgecolors='white', linewidth=1, zorder=5)

        # Label points
        for _, row in valid.iterrows():
            ax.annotate(str(int(row['SubjectID'])),
                        (row['Cmax_pct'], row['MP_best_pct_change']),
                        textcoords='offset points', xytext=(5, 5), fontsize=8, color='gray')

        # Spearman correlation
        if len(valid) >= 4:
            rho, p = stats.spearmanr(valid['Cmax_pct'], valid['MP_best_pct_change'])
            ax.text(0.05, 0.95, f'Spearman ρ = {rho:.3f}\np = {p:.3f}\nn = {len(valid)}',
                    transform=ax.transAxes, fontsize=10, va='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        ax.axhline(0, color='gray', linestyle=':', alpha=0.5)
        style_ax(ax, 'CAR-T Cmax vs M 蛋白最佳变化', 'Cmax (%)', 'M 蛋白 Best % Change from Baseline')
    else:
        ax.text(0.5, 0.5, f'数据不足（n={len(valid)}）', ha='center', va='center', fontsize=14)

    plt.tight_layout()
    plt.savefig('generated/chart_pkpd_cmax_mprotein.png', dpi=200, bbox_inches='tight')
    plt.close()

    with open('generated/chart_pkpd_cmax_mprotein.png.desc.md', 'w') as f:
        f.write(f"# Cmax vs M 蛋白最佳变化散点图\n\n展示 CAR-T Cmax (%) 与 M 蛋白最佳百分比变化的关系（n={len(valid)}）。标注 Spearman 相关系数和受试者 ID。探索性分析，样本量有限。\n")

    # 3.2 AUC vs FLC ratio change
    print("Generating: chart_pkpd_auc_flc.png")
    fig, ax = plt.subplots(figsize=(8, 6))

    valid_flc = pkpd.dropna(subset=['AUC0_28d', 'FLC_ratio_change'])
    valid_flc = valid_flc[valid_flc['AUC0_28d'] > 0]

    if len(valid_flc) >= 3:
        ax.scatter(valid_flc['AUC0_28d'], valid_flc['FLC_ratio_change'],
                   c=COLORS['secondary'], s=80, alpha=0.7, edgecolors='white', linewidth=1, zorder=5)

        for _, row in valid_flc.iterrows():
            ax.annotate(str(int(row['SubjectID'])),
                        (row['AUC0_28d'], row['FLC_ratio_change']),
                        textcoords='offset points', xytext=(5, 5), fontsize=8, color='gray')

        if len(valid_flc) >= 4:
            rho, p = stats.spearmanr(valid_flc['AUC0_28d'], valid_flc['FLC_ratio_change'])
            ax.text(0.05, 0.95, f'Spearman ρ = {rho:.3f}\np = {p:.3f}\nn = {len(valid_flc)}',
                    transform=ax.transAxes, fontsize=10, va='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        ax.axhline(0, color='gray', linestyle=':', alpha=0.5)
        style_ax(ax, 'AUC0-28d vs FLC 比值变化', 'AUC0-28d (%.day)', 'FLC κ:λ 比值变化')
    else:
        ax.text(0.5, 0.5, f'数据不足（n={len(valid_flc)}）', ha='center', va='center', fontsize=14)

    plt.tight_layout()
    plt.savefig('generated/chart_pkpd_auc_flc.png', dpi=200, bbox_inches='tight')
    plt.close()

    with open('generated/chart_pkpd_auc_flc.png.desc.md', 'w') as f:
        f.write(f"# AUC vs FLC 比值变化散点图\n\n展示 CAR-T AUC0-28d 与 FLC κ:λ 比值变化的关系。探索性分析。\n")

    # 3.3 CAR-T expansion vs IFE conversion
    print("Generating: chart_pkpd_cart_ife.png")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ife_data = pkpd.dropna(subset=['IFE_conversion'])
    if len(ife_data) >= 2 and ife_data['IFE_conversion'].nunique() > 1:
        converted = ife_data[ife_data['IFE_conversion'] == True]
        not_converted = ife_data[ife_data['IFE_conversion'] == False]

        for ax_i, (param, label) in enumerate([('Cmax_pct', 'Cmax (%)'), ('AUC0_28d', 'AUC0-28d')]):
            ax = axes[ax_i]
            data_groups = []
            labels_groups = []

            if len(converted) > 0 and converted[param].notna().any():
                data_groups.append(converted[param].dropna().values)
                labels_groups.append(f'IFE 转阴\n(n={len(converted)})')
            if len(not_converted) > 0 and not_converted[param].notna().any():
                data_groups.append(not_converted[param].dropna().values)
                labels_groups.append(f'IFE 未转阴\n(n={len(not_converted)})')

            if len(data_groups) > 0:
                bp = ax.boxplot(data_groups, labels=labels_groups, patch_artist=True, widths=0.4)
                colors_bp = [COLORS['accent'], COLORS['danger']]
                for patch, color in zip(bp['boxes'], colors_bp[:len(bp['boxes'])]):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.3)

                # Overlay points
                for gi, grp in enumerate(data_groups):
                    jitter = np.random.normal(0, 0.05, len(grp))
                    ax.scatter([gi+1]*len(grp) + jitter, grp, alpha=0.6, s=40,
                               color=colors_bp[gi], zorder=5)

            style_ax(ax, f'{label} by IFE 转阴状态', '', label)
    else:
        for ax in axes:
            ax.text(0.5, 0.5, 'IFE 转阴数据不足', ha='center', va='center', fontsize=12)
            ax.set_axis_off()

    plt.suptitle('CAR-T 扩增与 IFE 转阴', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig('generated/chart_pkpd_cart_ife.png', dpi=200, bbox_inches='tight')
    plt.close()

    with open('generated/chart_pkpd_cart_ife.png.desc.md', 'w') as f:
        f.write("# CAR-T 扩增与 IFE 转阴箱线图\n\n分组箱线图对比 IFE 转阴组 vs 未转阴组的 Cmax 和 AUC。探索性分析，样本量有限。\n")

else:
    print(f"\n样本量不足 ({n_eligible} < 5)，PK-PD 分析降级为列表展示")

# ============================================================
# 4. PK-PD Summary Table
# ============================================================
print("\nPK-PD Summary Table:")
summary_cols = ['SubjectID', 'Cmax_pct', 'Tmax_pct_day', 'AUC0_28d', 't_half_day',
                'MP_baseline', 'MP_best', 'MP_best_pct_change',
                'FLC_ratio_baseline', 'FLC_ratio_best', 'IFE_conversion']
print(pkpd[summary_cols].to_string(index=False))

print("\n=== T-004 COMPLETE ===")
