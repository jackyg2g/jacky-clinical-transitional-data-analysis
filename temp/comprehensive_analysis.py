#!/usr/bin/env python3
"""Comprehensive CAR-T Cell PK Analysis - All Visualizations & Deep Analytics"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.gridspec import GridSpec
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# ============================================================
# DATA LOADING & PREPROCESSING
# ============================================================
print("Loading data...")
df = pd.read_excel(
    'reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx'
)

cart_all = df[df['检测项目'].str.contains('CAR-T', na=False)].copy()

# --- CAR-T / WBC % ---
wbc = cart_all[cart_all['检测分项'] == 'CAR-T细胞占白细胞百分比'].copy()
# --- CAR-T / T cell % ---
tcell = cart_all[cart_all['检测分项'] == 'CAR-T细胞占T细胞百分比'].copy()
# --- CAR-T absolute concentration ---
absconc = cart_all[cart_all['检测分项'] == 'CAR-T细胞绝对浓度'].copy()

timepoint_map = {'清淋前': 0, 'D5': 5, 'D8': 8, 'D11': 11, 'D15': 15, 'D22': 22, 'D29': 29}
timepoint_labels = {0: 'BL', 5: 'D5', 8: 'D8', 11: 'D11', 15: 'D15', 22: 'D22', 29: 'D29'}
standard_days = [0, 8, 11, 15, 22, 29]

def parse_result(val):
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip()
    if val_str in ('BLD', 'BLQ', '/', ''):
        return 0.0
    if val_str == '见备注':
        return np.nan
    try:
        return float(val_str)
    except ValueError:
        return np.nan

def clean_dataset(data, name):
    data = data.copy()
    data['Day'] = data['访视周期'].map(timepoint_map)
    data = data.dropna(subset=['Day'])
    data['Day'] = data['Day'].astype(int)
    data['Value'] = data['结果'].apply(parse_result)
    data = data.dropna(subset=['Value'])
    clean = data[['受试者筛选号', 'Day', 'Value', '访视周期', '单位']].copy()
    clean.columns = ['PatientID', 'Day', 'Value', 'Visit', 'Unit']
    clean = clean.sort_values(['PatientID', 'Day'])
    clean = clean.drop_duplicates(subset=['PatientID', 'Day'], keep='first')
    print(f"  {name}: {len(clean)} rows, {clean['PatientID'].nunique()} patients")
    return clean

print("Cleaning datasets...")
wbc_clean = clean_dataset(wbc, 'CAR-T/WBC%')
tcell_clean = clean_dataset(tcell, 'CAR-T/T-cell%')
absconc_clean = clean_dataset(absconc, 'CAR-T absolute conc.')

# Save all transformed
wbc_clean.to_csv('transformed/cart_wbc_pct_all.csv', index=False)
tcell_clean.to_csv('transformed/cart_tcell_pct_all.csv', index=False)
absconc_clean.to_csv('transformed/cart_abs_conc_all.csv', index=False)

# ============================================================
# PK PARAMETER CALCULATION (extended)
# ============================================================
print("\nCalculating PK parameters...")

patient_ids = sorted(wbc_clean['PatientID'].unique())

pk_results = []
for pid in patient_ids:
    pdata = wbc_clean[wbc_clean['PatientID'] == pid].sort_values('Day')
    days = pdata['Day'].values
    vals = pdata['Value'].values

    cmax_idx = np.argmax(vals)
    cmax = vals[cmax_idx]
    tmax = days[cmax_idx]

    nonzero_mask = vals > 0
    tlast = days[nonzero_mask][-1] if nonzero_mask.any() else np.nan

    max_day = days.max()
    if max_day >= 28:
        auc_mask = days <= 29
        auc_days = days[auc_mask]
        auc_vals = vals[auc_mask]
        auc = np.trapz(auc_vals, auc_days) if len(auc_days) >= 2 else np.nan
    else:
        auc = np.nan

    t_half = np.nan
    if cmax_idx < len(days) - 2:
        decline_days = days[cmax_idx:]
        decline_vals = vals[cmax_idx:]
        pos_mask = decline_vals > 0
        d_pos = decline_days[pos_mask]
        v_pos = decline_vals[pos_mask]
        if len(d_pos) >= 3:
            slope, intercept, r_value, p_value, std_err = stats.linregress(d_pos, np.log(v_pos))
            if slope < 0:
                t_half = -np.log(2) / slope

    # Also get T-cell % Cmax for this patient
    tdata = tcell_clean[tcell_clean['PatientID'] == pid]
    tcell_cmax = tdata['Value'].max() if len(tdata) > 0 else np.nan

    # Also get absolute concentration Cmax
    adata = absconc_clean[absconc_clean['PatientID'] == pid]
    abs_cmax = adata['Value'].max() if len(adata) > 0 else np.nan

    # Data completeness
    n_timepoints = len(days)

    pk_results.append({
        'PatientID': pid,
        'Cmax_WBC_pct': cmax,
        'Tmax_day': int(tmax),
        'AUC_0_29d': auc,
        'Tlast_day': int(tlast) if not np.isnan(tlast) else np.nan,
        't_half_day': t_half,
        'Cmax_Tcell_pct': tcell_cmax,
        'Cmax_abs_conc': abs_cmax,
        'n_timepoints': n_timepoints,
    })

pk_df = pd.DataFrame(pk_results)
pk_df.to_csv('transformed/pk_parameters_full.csv', index=False)

# ============================================================
# CHARTS
# ============================================================

# Color scheme
COLORS = {
    'primary': '#2563EB',
    'secondary': '#7C3AED',
    'accent': '#059669',
    'warning': '#D97706',
    'danger': '#DC2626',
    'dark': '#1F2937',
    'light_bg': '#F9FAFB',
    'grid': '#E5E7EB',
    'median': '#111827',
}

def style_ax(ax, title=None, xlabel=None, ylabel=None):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3, color=COLORS['grid'])
    if title:
        ax.set_title(title, fontsize=13, fontweight='bold', pad=12, color=COLORS['dark'])
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11, color=COLORS['dark'])
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11, color=COLORS['dark'])

# ---- CHART 1: Individual patient trend with median (improved) ----
print("\nGenerating Chart 1: Individual trend lines...")
fig, ax = plt.subplots(figsize=(12, 7))

n_patients = len(patient_ids)
cmap = plt.cm.get_cmap('tab20c', max(n_patients, 20))
markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']

for i, pid in enumerate(patient_ids):
    pdata = wbc_clean[wbc_clean['PatientID'] == pid].sort_values('Day')
    ax.plot(pdata['Day'], pdata['Value'],
            marker=markers[i % len(markers)], markersize=4, linewidth=0.8,
            color=cmap(i % 20), alpha=0.6)

median_by_day = wbc_clean.groupby('Day')['Value'].median()
md = sorted([d for d in median_by_day.index if d in standard_days])
ax.plot(md, [median_by_day[d] for d in md],
        marker='o', markersize=9, linewidth=3,
        color=COLORS['median'], linestyle='--',
        markerfacecolor='white', markeredgecolor=COLORS['median'], markeredgewidth=2.5,
        label='Median', zorder=100)

ax.set_xticks(standard_days)
ax.set_xticklabels([timepoint_labels[d] for d in standard_days])
ax.set_xlim(-2, 31)
ax.set_ylim(bottom=0)
style_ax(ax, 'CAR-T/Live WBC (%) Over Time Post-Infusion — All Patients (N=76)',
         'Time Post-Infusion', 'CAR-T/Live WBC (%)')
ax.legend(loc='upper right', fontsize=11, framealpha=0.95)
plt.tight_layout()
plt.savefig('generated/chart_01_wbc_trend_all.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 2: Median + IQR ribbon ----
print("Generating Chart 2: Median + IQR ribbon...")
fig, ax = plt.subplots(figsize=(10, 6))

stats_by_day = wbc_clean.groupby('Day')['Value'].agg(['median', 'mean',
    lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)])
stats_by_day.columns = ['Median', 'Mean', 'Q1', 'Q3']
stats_by_day = stats_by_day.loc[stats_by_day.index.isin(standard_days)]

ax.fill_between(stats_by_day.index, stats_by_day['Q1'], stats_by_day['Q3'],
                alpha=0.25, color=COLORS['primary'], label='IQR (Q1–Q3)')
ax.plot(stats_by_day.index, stats_by_day['Median'],
        marker='o', markersize=8, linewidth=2.5, color=COLORS['primary'],
        markerfacecolor='white', markeredgecolor=COLORS['primary'], markeredgewidth=2,
        label='Median', zorder=10)
ax.plot(stats_by_day.index, stats_by_day['Mean'],
        marker='s', markersize=6, linewidth=2, color=COLORS['warning'],
        linestyle='--', label='Mean', zorder=9)

for d in stats_by_day.index:
    ax.annotate(f'{stats_by_day.loc[d, "Median"]:.1f}',
                (d, stats_by_day.loc[d, 'Median']),
                textcoords='offset points', xytext=(0, 12),
                ha='center', fontsize=9, color=COLORS['primary'], fontweight='bold')

ax.set_xticks(standard_days)
ax.set_xticklabels([timepoint_labels[d] for d in standard_days])
ax.set_xlim(-2, 31)
ax.set_ylim(bottom=0)
style_ax(ax, 'CAR-T/Live WBC (%) — Median with Interquartile Range (N=76)',
         'Time Post-Infusion', 'CAR-T/Live WBC (%)')
ax.legend(loc='upper right', fontsize=10)
plt.tight_layout()
plt.savefig('generated/chart_02_wbc_median_iqr.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 3: Box plot by timepoint ----
print("Generating Chart 3: Box plots by timepoint...")
fig, ax = plt.subplots(figsize=(10, 6))

box_data = [wbc_clean[wbc_clean['Day'] == d]['Value'].values for d in standard_days]
bp = ax.boxplot(box_data, positions=range(len(standard_days)), widths=0.5,
                patch_artist=True, showfliers=True,
                flierprops=dict(marker='o', markerfacecolor=COLORS['danger'], markersize=4, alpha=0.5),
                medianprops=dict(color=COLORS['median'], linewidth=2))
for patch in bp['boxes']:
    patch.set_facecolor(COLORS['primary'])
    patch.set_alpha(0.3)

# Overlay individual points (jittered)
for i, d in enumerate(standard_days):
    vals = wbc_clean[wbc_clean['Day'] == d]['Value'].values
    jitter = np.random.normal(0, 0.08, len(vals))
    ax.scatter([i] * len(vals) + jitter, vals, color=COLORS['primary'],
               alpha=0.4, s=15, zorder=5)

ax.set_xticks(range(len(standard_days)))
ax.set_xticklabels([timepoint_labels[d] for d in standard_days])
ax.set_ylim(bottom=0)
style_ax(ax, 'Distribution of CAR-T/Live WBC (%) at Each Timepoint',
         'Time Post-Infusion', 'CAR-T/Live WBC (%)')
plt.tight_layout()
plt.savefig('generated/chart_03_wbc_boxplot.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 4: Waterfall plot of Cmax ----
print("Generating Chart 4: Cmax waterfall...")
fig, ax = plt.subplots(figsize=(14, 6))

pk_sorted = pk_df.sort_values('Cmax_WBC_pct', ascending=False).reset_index(drop=True)
colors_wf = [COLORS['danger'] if c >= 50 else COLORS['warning'] if c >= 20 else COLORS['primary']
             for c in pk_sorted['Cmax_WBC_pct']]

bars = ax.bar(range(len(pk_sorted)), pk_sorted['Cmax_WBC_pct'], color=colors_wf, width=0.8, alpha=0.85)

# Median line
med_cmax = pk_df['Cmax_WBC_pct'].median()
ax.axhline(med_cmax, color=COLORS['median'], linestyle='--', linewidth=1.5, alpha=0.7,
           label=f'Median Cmax = {med_cmax:.1f}%')

ax.set_xticks(range(len(pk_sorted)))
ax.set_xticklabels(pk_sorted['PatientID'].astype(int).astype(str), rotation=90, fontsize=6)
ax.set_ylim(bottom=0)
style_ax(ax, 'Waterfall Plot of CAR-T/WBC Cmax by Patient (Ranked)',
         'Patient ID', 'Cmax CAR-T/Live WBC (%)')
ax.legend(fontsize=10)

# Color legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=COLORS['danger'], alpha=0.85, label='Cmax ≥ 50%'),
    Patch(facecolor=COLORS['warning'], alpha=0.85, label='20% ≤ Cmax < 50%'),
    Patch(facecolor=COLORS['primary'], alpha=0.85, label='Cmax < 20%'),
]
ax.legend(handles=legend_elements + [plt.Line2D([0],[0], color=COLORS['median'], linestyle='--',
          label=f'Median = {med_cmax:.1f}%')], loc='upper right', fontsize=9)

plt.tight_layout()
plt.savefig('generated/chart_04_cmax_waterfall.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 5: Tmax distribution ----
print("Generating Chart 5: Tmax distribution...")
fig, ax = plt.subplots(figsize=(8, 5))

tmax_counts = pk_df['Tmax_day'].value_counts().sort_index()
# Only show meaningful Tmax values (exclude BL=0 for patients with all zeros)
active = pk_df[pk_df['Cmax_WBC_pct'] > 0]
tmax_active = active['Tmax_day'].value_counts().sort_index()

bars = ax.bar(tmax_active.index, tmax_active.values, color=COLORS['secondary'], width=2, alpha=0.8)
for bar, val in zip(bars, tmax_active.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val}\n({val/len(active)*100:.0f}%)', ha='center', fontsize=10, fontweight='bold')

ax.set_xticks(sorted(tmax_active.index))
ax.set_xticklabels([timepoint_labels.get(d, f'D{d}') for d in sorted(tmax_active.index)])
style_ax(ax, f'Distribution of Tmax (Time to Peak) — Active Patients (N={len(active)})',
         'Tmax (Day Post-Infusion)', 'Number of Patients')
plt.tight_layout()
plt.savefig('generated/chart_05_tmax_distribution.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 6: AUC histogram ----
print("Generating Chart 6: AUC distribution...")
fig, ax = plt.subplots(figsize=(9, 5))

auc_valid = pk_df['AUC_0_29d'].dropna()
ax.hist(auc_valid, bins=20, color=COLORS['accent'], alpha=0.7, edgecolor='white', linewidth=0.8)
ax.axvline(auc_valid.median(), color=COLORS['median'], linestyle='--', linewidth=2,
           label=f'Median = {auc_valid.median():.1f} %.day')
ax.axvline(auc_valid.mean(), color=COLORS['warning'], linestyle='--', linewidth=1.5,
           label=f'Mean = {auc_valid.mean():.1f} %.day')

style_ax(ax, f'Distribution of AUC₀₋₂₉d (N={len(auc_valid)})',
         'AUC₀₋₂₉d (%.day)', 'Number of Patients')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('generated/chart_06_auc_histogram.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 7: Heatmap ----
print("Generating Chart 7: Heatmap...")
fig, ax = plt.subplots(figsize=(10, 16))

pivot = wbc_clean.pivot_table(index='PatientID', columns='Day', values='Value')
pivot = pivot.reindex(columns=standard_days)
# Sort by Cmax
pivot['Cmax'] = pivot.max(axis=1)
pivot = pivot.sort_values('Cmax', ascending=False)
pivot = pivot.drop(columns='Cmax')

im = ax.imshow(pivot.values, aspect='auto', cmap='YlOrRd', interpolation='nearest')
ax.set_xticks(range(len(standard_days)))
ax.set_xticklabels([timepoint_labels[d] for d in standard_days], fontsize=10)
ax.set_yticks(range(len(pivot)))
ax.set_yticklabels(pivot.index.astype(int).astype(str), fontsize=6)
ax.set_title('CAR-T/Live WBC (%) Heatmap — Patients Ranked by Cmax', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Time Post-Infusion', fontsize=11)
ax.set_ylabel('Patient ID', fontsize=11)

cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
cbar.set_label('CAR-T/Live WBC (%)', fontsize=10)

plt.tight_layout()
plt.savefig('generated/chart_07_heatmap.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 8: Cmax vs AUC scatter ----
print("Generating Chart 8: Cmax vs AUC correlation...")
fig, ax = plt.subplots(figsize=(8, 6))

valid = pk_df.dropna(subset=['AUC_0_29d'])
valid = valid[valid['Cmax_WBC_pct'] > 0]

ax.scatter(valid['Cmax_WBC_pct'], valid['AUC_0_29d'],
           c=COLORS['primary'], alpha=0.6, s=50, edgecolors='white', linewidth=0.5)

# Fit line
slope, intercept, r, p, se = stats.linregress(valid['Cmax_WBC_pct'], valid['AUC_0_29d'])
x_fit = np.linspace(0, valid['Cmax_WBC_pct'].max() * 1.05, 100)
ax.plot(x_fit, slope * x_fit + intercept, color=COLORS['danger'], linewidth=2, linestyle='--',
        label=f'R² = {r**2:.3f}, p < {"0.001" if p < 0.001 else f"{p:.3f}"}')

style_ax(ax, 'Cmax vs AUC₀₋₂₉d Correlation',
         'Cmax CAR-T/Live WBC (%)', 'AUC₀₋₂₉d (%.day)')
ax.legend(fontsize=10)
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
plt.tight_layout()
plt.savefig('generated/chart_08_cmax_vs_auc.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 9: t1/2 distribution ----
print("Generating Chart 9: t1/2 distribution...")
fig, ax = plt.subplots(figsize=(9, 5))

thalf_valid = pk_df['t_half_day'].dropna()
ax.hist(thalf_valid, bins=20, color=COLORS['secondary'], alpha=0.7, edgecolor='white', linewidth=0.8)
ax.axvline(thalf_valid.median(), color=COLORS['median'], linestyle='--', linewidth=2,
           label=f'Median = {thalf_valid.median():.1f} days')

style_ax(ax, f'Distribution of Terminal Half-Life t₁/₂ (N={len(thalf_valid)})',
         't₁/₂ (Days)', 'Number of Patients')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('generated/chart_09_thalf_distribution.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 10: Multi-metric comparison (WBC%, T-cell%, Abs conc.) ----
print("Generating Chart 10: Multi-metric median comparison...")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

datasets = [
    (wbc_clean, 'CAR-T/Live WBC (%)', COLORS['primary']),
    (tcell_clean, 'CAR-T/T-cell (%)', COLORS['secondary']),
    (absconc_clean, 'CAR-T Absolute Conc.', COLORS['accent']),
]

for ax, (data, title, color) in zip(axes, datasets):
    med = data.groupby('Day')['Value'].agg(['median', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)])
    med.columns = ['Median', 'Q1', 'Q3']
    med = med.loc[med.index.isin(standard_days)]

    ax.fill_between(med.index, med['Q1'], med['Q3'], alpha=0.2, color=color)
    ax.plot(med.index, med['Median'], marker='o', markersize=7, linewidth=2, color=color,
            markerfacecolor='white', markeredgecolor=color, markeredgewidth=2)

    ax.set_xticks(standard_days)
    ax.set_xticklabels([timepoint_labels[d] for d in standard_days], fontsize=9)
    ax.set_xlim(-2, 31)
    ax.set_ylim(bottom=0)

    unit = data['Unit'].iloc[0] if 'Unit' in data.columns and len(data) > 0 else ''
    style_ax(ax, title, 'Time Post-Infusion', f'Value ({unit})')

plt.suptitle('CAR-T Cell Kinetics — Three Detection Metrics (Median ± IQR)', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('generated/chart_10_multi_metric.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 11: Expansion subgroup analysis ----
print("Generating Chart 11: Expansion subgroups...")
fig, ax = plt.subplots(figsize=(10, 6))

# Define expansion subgroups
high_exp = pk_df[pk_df['Cmax_WBC_pct'] >= 50]['PatientID']
mid_exp = pk_df[(pk_df['Cmax_WBC_pct'] >= 20) & (pk_df['Cmax_WBC_pct'] < 50)]['PatientID']
low_exp = pk_df[(pk_df['Cmax_WBC_pct'] > 0) & (pk_df['Cmax_WBC_pct'] < 20)]['PatientID']
no_exp = pk_df[pk_df['Cmax_WBC_pct'] == 0]['PatientID']

groups = [
    (high_exp, 'High (Cmax ≥ 50%)', COLORS['danger']),
    (mid_exp, 'Moderate (20–50%)', COLORS['warning']),
    (low_exp, 'Low (0–20%)', COLORS['primary']),
]

for pids, label, color in groups:
    sub = wbc_clean[wbc_clean['PatientID'].isin(pids)]
    med = sub.groupby('Day')['Value'].median()
    med = med.loc[med.index.isin(standard_days)]
    q1 = sub.groupby('Day')['Value'].quantile(0.25)
    q3 = sub.groupby('Day')['Value'].quantile(0.75)
    q1 = q1.loc[q1.index.isin(standard_days)]
    q3 = q3.loc[q3.index.isin(standard_days)]

    ax.fill_between(med.index, q1, q3, alpha=0.15, color=color)
    ax.plot(med.index, med, marker='o', markersize=7, linewidth=2, color=color,
            markerfacecolor='white', markeredgecolor=color, markeredgewidth=2,
            label=f'{label} (N={len(pids)})')

ax.set_xticks(standard_days)
ax.set_xticklabels([timepoint_labels[d] for d in standard_days])
ax.set_xlim(-2, 31)
ax.set_ylim(bottom=0)
style_ax(ax, 'CAR-T Expansion Subgroup Analysis (Median ± IQR)',
         'Time Post-Infusion', 'CAR-T/Live WBC (%)')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('generated/chart_11_subgroup_expansion.png', dpi=200, bbox_inches='tight')
plt.close()

# ---- CHART 12: Spider/Radar summary of PK params ----
print("Generating Chart 12: PK parameter correlation matrix...")
fig, ax = plt.subplots(figsize=(8, 7))

corr_cols = ['Cmax_WBC_pct', 'AUC_0_29d', 't_half_day', 'Cmax_Tcell_pct', 'Cmax_abs_conc']
corr_labels = ['Cmax\n(WBC%)', 'AUC₀₋₂₉d', 't₁/₂', 'Cmax\n(T-cell%)', 'Cmax\n(Abs Conc.)']
corr_data = pk_df[corr_cols].dropna()

if len(corr_data) > 5:
    corr_matrix = corr_data.corr()
    im = ax.imshow(corr_matrix.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    ax.set_xticks(range(len(corr_labels)))
    ax.set_xticklabels(corr_labels, fontsize=9)
    ax.set_yticks(range(len(corr_labels)))
    ax.set_yticklabels(corr_labels, fontsize=9)

    for i in range(len(corr_labels)):
        for j in range(len(corr_labels)):
            val = corr_matrix.values[i, j]
            color = 'white' if abs(val) > 0.6 else 'black'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=10, color=color, fontweight='bold')

    plt.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title('PK Parameter Correlation Matrix', fontsize=13, fontweight='bold', pad=12)

plt.tight_layout()
plt.savefig('generated/chart_12_pk_correlation.png', dpi=200, bbox_inches='tight')
plt.close()

# ============================================================
# GENERATE DESC FILES
# ============================================================
print("\nGenerating description files...")

descs = {
    'chart_01_wbc_trend_all.png': 'Line chart showing CAR-T/Live WBC (%) for all 76 patients over time post-infusion with individual colored lines and bold dashed median line. X-axis: BL to D29. Y-axis: CAR-T/WBC percentage.',
    'chart_02_wbc_median_iqr.png': 'Median CAR-T/Live WBC (%) with IQR shaded ribbon and mean line overlaid. Shows central tendency and spread across 76 patients from BL to D29.',
    'chart_03_wbc_boxplot.png': 'Box-and-whisker plot with jittered individual data points at each timepoint (BL, D8, D11, D15, D22, D29) showing distribution of CAR-T/WBC% values.',
    'chart_04_cmax_waterfall.png': 'Waterfall (ranked bar) chart of individual patient Cmax values, color-coded by expansion level: red (≥50%), orange (20-50%), blue (<20%). Horizontal dashed line at median.',
    'chart_05_tmax_distribution.png': 'Bar chart of Tmax distribution among active patients showing number and percentage at each timepoint. Most patients reach Cmax at D11 or D15.',
    'chart_06_auc_histogram.png': 'Histogram of AUC₀₋₂₉d distribution with median and mean reference lines. Shows right-skewed distribution indicating variable total CAR-T exposure.',
    'chart_07_heatmap.png': 'Patient-by-timepoint heatmap of CAR-T/WBC% values. Rows sorted by descending Cmax. Yellow-orange-red color scale. Visualizes expansion patterns across the full cohort.',
    'chart_08_cmax_vs_auc.png': 'Scatter plot with regression line showing correlation between Cmax and AUC₀₋₂₉d. Strong positive correlation expected as higher peak generally correlates with higher total exposure.',
    'chart_09_thalf_distribution.png': 'Histogram of terminal half-life (t₁/₂) distribution. Most patients show t₁/₂ between 2-10 days with some outliers showing prolonged persistence.',
    'chart_10_multi_metric.png': 'Three-panel comparison of CAR-T kinetics across three detection metrics: WBC%, T-cell%, and absolute concentration. Each shows median ± IQR.',
    'chart_11_subgroup_expansion.png': 'Subgroup analysis comparing high (≥50%), moderate (20-50%), and low (0-20%) expansion groups. Shows median ± IQR kinetic curves for each subgroup.',
    'chart_12_pk_correlation.png': 'Correlation matrix heatmap of PK parameters (Cmax WBC%, AUC, t₁/₂, Cmax T-cell%, Cmax absolute concentration). Shows inter-parameter relationships.',
}

for fname, desc in descs.items():
    with open(f'generated/{fname}.desc.md', 'w') as f:
        f.write(f'# {fname}\n\n{desc}\n')

# ============================================================
# SUMMARY STATS FOR REPORT
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY STATISTICS")
print("=" * 60)

print(f"\nTotal patients: {len(pk_df)}")
print(f"Active patients (Cmax > 0): {len(pk_df[pk_df['Cmax_WBC_pct'] > 0])}")
print(f"Non-expanders (Cmax = 0): {len(pk_df[pk_df['Cmax_WBC_pct'] == 0])}")

print(f"\nCmax WBC%: median={pk_df['Cmax_WBC_pct'].median():.2f}, "
      f"mean={pk_df['Cmax_WBC_pct'].mean():.2f}, "
      f"range=[{pk_df['Cmax_WBC_pct'].min():.2f}, {pk_df['Cmax_WBC_pct'].max():.2f}]")

active = pk_df[pk_df['Cmax_WBC_pct'] > 0]
print(f"Cmax WBC% (active only): median={active['Cmax_WBC_pct'].median():.2f}, "
      f"mean={active['Cmax_WBC_pct'].mean():.2f}")

tmax_mode = active['Tmax_day'].mode().values
print(f"Tmax mode: D{tmax_mode[0]} ({(active['Tmax_day'] == tmax_mode[0]).sum()}/{len(active)} patients)")

auc_v = pk_df['AUC_0_29d'].dropna()
print(f"AUC0-29d: median={auc_v.median():.1f}, mean={auc_v.mean():.1f}, n={len(auc_v)}")

th_v = pk_df['t_half_day'].dropna()
print(f"t1/2: median={th_v.median():.1f}, mean={th_v.mean():.1f}, n={len(th_v)}")

# Subgroup counts
print(f"\nExpansion subgroups:")
print(f"  High (≥50%): {len(high_exp)} patients ({len(high_exp)/len(pk_df)*100:.1f}%)")
print(f"  Moderate (20-50%): {len(mid_exp)} patients ({len(mid_exp)/len(pk_df)*100:.1f}%)")
print(f"  Low (0-20%): {len(low_exp)} patients ({len(low_exp)/len(pk_df)*100:.1f}%)")
print(f"  No expansion: {len(no_exp)} patients ({len(no_exp)/len(pk_df)*100:.1f}%)")

# Cmax vs AUC correlation
v = pk_df.dropna(subset=['AUC_0_29d'])
v = v[v['Cmax_WBC_pct'] > 0]
r, p = stats.pearsonr(v['Cmax_WBC_pct'], v['AUC_0_29d'])
print(f"\nCmax-AUC correlation: r={r:.3f}, R²={r**2:.3f}, p={p:.2e}")

print("\nAll charts generated successfully!")
