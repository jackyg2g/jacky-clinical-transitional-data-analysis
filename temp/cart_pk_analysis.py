#!/usr/bin/env python3
"""CAR-T Cell PK Analysis Script for CT103AC004 Clinical Trial"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# ============================================================
# Step 1: Data Preprocessing
# ============================================================
print("=" * 60)
print("Step 1: Data Preprocessing")
print("=" * 60)

df = pd.read_excel(
    'reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx'
)

# Filter for CAR-T cell detection - WBC percentage
cart = df[df['检测项目'].str.contains('CAR-T', na=False)].copy()
wbc = cart[cart['检测分项'] == 'CAR-T细胞占白细胞百分比'].copy()

print(f"Total CAR-T WBC% rows: {len(wbc)}")
print(f"Unique patients: {wbc['受试者筛选号'].nunique()}")
print(f"Timepoints: {wbc['访视周期'].unique()}")

# Map timepoints to numeric days
timepoint_map = {
    '清淋前': 0,  # Baseline (pre-lymphodepletion)
    'D5': 5,
    'D8': 8,
    'D11': 11,
    'D15': 15,
    'D22': 22,
    'D29': 29,
}

# Map timepoint labels for chart
timepoint_labels = {
    0: 'BL',
    5: 'D5',
    8: 'D8',
    11: 'D11',
    15: 'D15',
    22: 'D22',
    29: 'D29',
}

wbc['Day'] = wbc['访视周期'].map(timepoint_map)
# Drop rows with unmapped timepoints (e.g., 计划外 = unscheduled)
wbc_mapped = wbc.dropna(subset=['Day']).copy()
wbc_mapped['Day'] = wbc_mapped['Day'].astype(int)

# Handle non-numeric results
def parse_result(val):
    """Parse result values, handling BLD and other non-numeric values."""
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

wbc_mapped['Value'] = wbc_mapped['结果'].apply(parse_result)
wbc_mapped = wbc_mapped.dropna(subset=['Value'])

# Create clean dataframe
clean = wbc_mapped[['受试者筛选号', 'Day', 'Value', '访视周期']].copy()
clean.columns = ['PatientID', 'Day', 'CAR_T_WBC_pct', 'Visit']
clean = clean.sort_values(['PatientID', 'Day'])

# Remove duplicates (keep first)
clean = clean.drop_duplicates(subset=['PatientID', 'Day'], keep='first')

print(f"\nCleaned data: {len(clean)} rows, {clean['PatientID'].nunique()} patients")
print(f"Days present: {sorted(clean['Day'].unique())}")

# Save transformed data
clean.to_csv('transformed/cart_wbc_pct_cleaned.csv', index=False)
print("\nSaved: transformed/cart_wbc_pct_cleaned.csv")

# ============================================================
# Step 2: Trend Chart Generation
# ============================================================
print("\n" + "=" * 60)
print("Step 2: Trend Chart Generation")
print("=" * 60)

# Pivot for chart
pivot = clean.pivot_table(index='Day', columns='PatientID', values='CAR_T_WBC_pct')

# Standard timepoints for x-axis
standard_days = [0, 8, 11, 15, 22, 29]

# Calculate median at each timepoint
median_values = clean.groupby('Day')['CAR_T_WBC_pct'].median()

# Get all patient IDs
patient_ids = sorted(clean['PatientID'].unique())

# Color palette - use a colormap to generate distinct colors
n_patients = len(patient_ids)
cmap = plt.cm.get_cmap('tab20', max(n_patients, 20))
colors = [cmap(i) for i in range(n_patients)]

# Marker styles
markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'd', '|']

fig, ax = plt.subplots(figsize=(10, 7))

# Plot individual patient lines
for i, pid in enumerate(patient_ids):
    pdata = clean[clean['PatientID'] == pid].sort_values('Day')
    marker = markers[i % len(markers)]
    ax.plot(pdata['Day'], pdata['CAR_T_WBC_pct'],
            marker=marker, markersize=6, linewidth=1.2,
            color=colors[i], label=str(pid), alpha=0.8)

# Plot median line
median_days = sorted(median_values.index)
median_days_filtered = [d for d in median_days if d in standard_days]
median_vals_filtered = [median_values[d] for d in median_days_filtered]
ax.plot(median_days_filtered, median_vals_filtered,
        marker='o', markersize=8, linewidth=2.5,
        color='black', linestyle='--', label='Median',
        zorder=10, markerfacecolor='white', markeredgecolor='black', markeredgewidth=2)

# Formatting
ax.set_xlabel('Time post-infusion', fontsize=12)
ax.set_ylabel('CAR-T/Live WBC (%)', fontsize=12)
ax.set_xticks(standard_days)
ax.set_xticklabels([timepoint_labels.get(d, f'D{d}') for d in standard_days])
ax.set_xlim(-2, 31)
ax.set_ylim(bottom=0)

# Legend - put Median first, then patients in columns
handles, labels = ax.get_legend_handles_labels()
# Move Median to first position
median_idx = labels.index('Median')
handles = [handles[median_idx]] + handles[:median_idx] + handles[median_idx+1:]
labels = [labels[median_idx]] + labels[:median_idx] + labels[median_idx+1:]

# Place legend outside right if many patients, or inside if few
if n_patients <= 10:
    ax.legend(handles, labels, loc='upper right', fontsize=8, ncol=2, framealpha=0.9)
else:
    ax.legend(handles, labels, loc='upper left', bbox_to_anchor=(1.02, 1),
              fontsize=7, ncol=2, framealpha=0.9, borderaxespad=0)
    fig.subplots_adjust(right=0.75)

ax.grid(True, alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('generated/chart_cart_wbc_trend.png', dpi=200, bbox_inches='tight')
plt.close()
print("Saved: generated/chart_cart_wbc_trend.png")

# ============================================================
# Step 3: PK Parameter Calculation
# ============================================================
print("\n" + "=" * 60)
print("Step 3: PK Parameter Calculation")
print("=" * 60)

pk_results = []

for pid in patient_ids:
    pdata = clean[clean['PatientID'] == pid].sort_values('Day')
    days = pdata['Day'].values
    vals = pdata['CAR_T_WBC_pct'].values

    # Cmax and Tmax
    cmax_idx = np.argmax(vals)
    cmax = vals[cmax_idx]
    tmax = days[cmax_idx]

    # Tlast: last timepoint with non-zero value
    nonzero_mask = vals > 0
    if nonzero_mask.any():
        tlast = days[nonzero_mask][-1]
    else:
        tlast = np.nan

    # AUC0-29d (trapezoidal rule) - only if data extends >= 28 days
    max_day = days.max()
    if max_day >= 28:
        # Filter data within 0-29 day range
        auc_mask = days <= 29
        auc_days = days[auc_mask]
        auc_vals = vals[auc_mask]
        if len(auc_days) >= 2:
            auc = np.trapz(auc_vals, auc_days)
        else:
            auc = np.nan
    else:
        auc = np.nan

    # Terminal half-life (t1/2)
    # Use log-linear regression on declining phase after Cmax
    t_half = np.nan
    if cmax_idx < len(days) - 2:  # Need at least 3 points after Cmax (inclusive)
        decline_days = days[cmax_idx:]
        decline_vals = vals[cmax_idx:]

        # Filter positive values only for log transform
        pos_mask = decline_vals > 0
        decline_days_pos = decline_days[pos_mask]
        decline_vals_pos = decline_vals[pos_mask]

        if len(decline_days_pos) >= 3:
            log_vals = np.log(decline_vals_pos)
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                decline_days_pos, log_vals
            )
            if slope < 0:  # Must be declining
                t_half = -np.log(2) / slope

    pk_results.append({
        'PatientID': pid,
        'Cmax (%)': round(cmax, 3),
        'Tmax (Day)': int(tmax),
        'AUC0-29d (%.day)': round(auc, 2) if not np.isnan(auc) else 'N/A',
        'Tlast (Day)': int(tlast) if not np.isnan(tlast) else 'N/A',
        't1/2 (Day)': round(t_half, 2) if not np.isnan(t_half) else 'NC',
    })

pk_df = pd.DataFrame(pk_results)
pk_df.to_csv('transformed/pk_parameters.csv', index=False)
print("Saved: transformed/pk_parameters.csv")
print(f"\nPK Parameters for {len(pk_results)} patients:")
print(pk_df.to_string(index=False))

# Summary statistics
print("\n\nSummary Statistics:")
numeric_cols = ['Cmax (%)', 'Tmax (Day)']
for col in numeric_cols:
    vals = pk_df[col].astype(float)
    print(f"  {col}: median={vals.median():.3f}, mean={vals.mean():.3f}, "
          f"range=[{vals.min():.3f}, {vals.max():.3f}]")

# AUC summary (exclude N/A)
auc_vals = pk_df['AUC0-29d (%.day)']
auc_numeric = pd.to_numeric(auc_vals, errors='coerce').dropna()
if len(auc_numeric) > 0:
    print(f"  AUC0-29d: median={auc_numeric.median():.2f}, mean={auc_numeric.mean():.2f}, "
          f"range=[{auc_numeric.min():.2f}, {auc_numeric.max():.2f}] (n={len(auc_numeric)})")

# t1/2 summary (exclude NC)
thalf_vals = pk_df['t1/2 (Day)']
thalf_numeric = pd.to_numeric(thalf_vals, errors='coerce').dropna()
if len(thalf_numeric) > 0:
    print(f"  t1/2: median={thalf_numeric.median():.2f}, mean={thalf_numeric.mean():.2f}, "
          f"range=[{thalf_numeric.min():.2f}, {thalf_numeric.max():.2f}] (n={len(thalf_numeric)})")

# ============================================================
# Step 4: Verification
# ============================================================
print("\n" + "=" * 60)
print("Step 4: Verification")
print("=" * 60)

# Verify a few patients
for pid in patient_ids[:3]:
    pdata = clean[clean['PatientID'] == pid].sort_values('Day')
    pk_row = pk_df[pk_df['PatientID'] == pid].iloc[0]
    print(f"\nPatient {pid}:")
    print(f"  Data: {list(zip(pdata['Day'].values, pdata['CAR_T_WBC_pct'].values))}")
    print(f"  Cmax={pk_row['Cmax (%)']}, Tmax=D{pk_row['Tmax (Day)']}")

print("\nAnalysis complete!")
