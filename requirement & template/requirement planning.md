# Requirement Planning: CAR-T Cell PK Analysis

## Objective

Based on CT103A C004 clinical trial data, perform CAR-T cell pharmacokinetics (PK) analysis, generate kinetics charts, and calculate key PK parameters.

---

## Data Sources

| File | Description | Key Fields |
|------|-------------|------------|
| `reference/raw-data-yance/sample.xlsx` | CAR-T cell detection results | 受试者 ID, 访视 (timepoint), 分析项 (CAR-T 细胞占 T 细胞百分比 / CAR-T 细胞绝对计数), 结果 |
| `reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx` | Central lab results (immunoglobulin, serum protein, etc.) | 受试者筛选号, 访视周期, 检测项目, 检测分项, 结果, 单位 |

### Data Characteristics

- **sample.xlsx**: 19 subjects (01003–01028), timepoints from 清淋前检查 (pre-lymphodepletion) through D1, D4, D7, D10, D14, D21, D28, D60, D90, D180, D270, D360, D540. Contains "BLD"/"BLQ" for below-detection-limit values. ~1M rows.
- **G957 central lab data**: 14+ subjects (01001–01014), 109K rows. Contains immunoglobulin (IgA/IgG/IgM), serum protein electrophoresis, free light chains, etc. Visits include bridging therapy cycles and post-infusion weeks (W12–W40+).

---

## Task Breakdown

### Phase 1: Data Preprocessing

1. **Extract CAR-T cell kinetics data from `sample.xlsx`**
   - Filter for "CAR-T 细胞占 T 细胞百分比" (CAR-T/T cell %)
   - Map visit names to numeric days (清淋前检查 → BL, 主要随访期 D1 → D1, etc.)
   - Handle BLD/BLQ values (treat as 0 or below quantification limit)
   - Output cleaned data to `transformed/`

2. **Extract relevant central lab data from G957 xlsx** (if needed for supplementary analysis)
   - Immunoglobulin levels (IgA, IgG, IgM)
   - Serum protein electrophoresis / M protein
   - Map visit cycles to post-infusion timeline

### Phase 2: Chart Generation

3. **Generate CAR-T cell kinetics line chart** (primary deliverable)
   - X-axis: Time post-infusion (BL, D8, D11, D15, D22, D29 — or available timepoints)
   - Y-axis: CAR-T/Live WBC (%)
   - One colored line per subject with markers
   - Dashed median line across all subjects
   - Legend with subject IDs
   - Style matching the reference chart in `requirement & template/1st_requirement.png`
   - Save to `generated/chart_cart_kinetics.png` + description file

4. **Generate CAR-T absolute count chart** (if needed)
   - Similar layout using CAR-T 细胞绝对计数 data
   - Save to `generated/chart_cart_absolute_count.png`

### Phase 3: PK Parameter Calculation

5. **Calculate per-subject PK parameters**
   - **Cmax**: Maximum CAR-T cell percentage observed
   - **Tmax**: Day at which Cmax occurs
   - **AUC0-29d**: Area under the curve from Day 0 to Day 29 (linear trapezoidal method)
   - **Tlast**: Time of last quantifiable concentration (last timepoint with value above detection limit)
   - **Terminal half-life (t1/2)**: Estimated from the terminal elimination phase using log-linear regression

6. **Generate summary statistics**
   - Per-subject PK parameter table
   - Descriptive statistics (median, mean, range) across all subjects

### Phase 4: Report Generation

7. **Compile analysis report to `output/report.md`**
   - Introduction and study background
   - Data processing methodology
   - CAR-T kinetics chart with interpretation
   - PK parameter summary table
   - Key findings and observations
   - Citation markers referencing source data

---

## Key Considerations

- **BLD/BLQ handling**: "BLD" (Below Limit of Detection) and "BLQ" (Below Limit of Quantification) values need consistent handling — typically set to 0 for charting, and excluded or set to LOQ/2 for PK calculations
- **Timepoint mapping**: The reference chart uses D8, D11, D15, D22, D29, but `sample.xlsx` has D1, D4, D7, D10, D14, D21, D28 — need to verify and use actual available timepoints
- **Subject ID mapping**: The reference chart shows 5-digit IDs (10020, 27002, etc.) which differ from `sample.xlsx` IDs (01003, 01006, etc.) — may be center+subject combined IDs
- **Terminal half-life**: Requires at least 3 data points in the terminal decline phase; may not be calculable for all subjects
- **Large file handling**: `sample.xlsx` has ~1M rows — use chunked/efficient reading (pandas with openpyxl engine)

---

## Technical Approach

- **Language**: Python 3
- **Libraries**: pandas, openpyxl, matplotlib, numpy, scipy (for log-linear regression)
- **Scripts**: Store in `temp/` directory
- **Charts**: Save to `generated/` with accompanying `.desc.md` files
- **Report**: Output to `output/report.md`
