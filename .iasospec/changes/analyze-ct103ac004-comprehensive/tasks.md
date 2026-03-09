# T-001 双数据源预处理与结构化解析

## Requirement Description

将两组数据源（CAR-T 动力学 + 中心实验室检测结果）预处理为可分析的结构化格式，建立统一时间轴映射，验证受试者 ID 匹配关系。此任务为后续全部分析任务的基础。

**Requirement Type**: Infrastructure

**Involved Domain**: Full-stack

### 1. CAR-T 动力学数据预处理（sample.xlsx）

- 读取 338 行 × 4 列数据
- 访视名称映射为回输后天数（清淋前检查 → -5, D1 → 1, D4 → 4, ..., D540 → 540）
- BLD/BLQ 标记识别，转为数值（绘图设 0，保留原始标记供 PK 计算判断）
- 按分析项分组：CAR-T 细胞百分比 / 绝对计数
- 受试者 ID 标准化：1003 → 01003（5 位格式）
- 输出数据描述至 `transformed/sample.xlsx.md`

### 2. 中心实验室数据预处理（G957 xlsx）

- 读取 109,237 行 × 18 列数据
- 时间字段（采集时间、检测时间、报告时间、反审时间）转 datetime
- "结果" 列按检测项目分组，区分数值型和定性型
- 建立访视周期排序映射（筛选期 → 桥接治疗-DPd → 清淋前 → W8 → W12 → ... → 长期随访）
- 访视周期转换为回输后天数（W8 → 56, W12 → 84, ...），与 CAR-T 数据时间轴对齐
- 输出数据描述至 `transformed/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx.md`

### 3. 受试者匹配验证

- 验证 sample.xlsx 中 18 例受试者在中心实验室数据中的存在性
- 输出匹配结果：匹配成功的受试者列表、匹配失败的受试者及原因
- 确定 PK-PD 分析可用的受试者集合

## Relevant Guidelines

**Others:**
- `reference/raw-data-yance/sample.xlsx` — 338 行, 18 例受试者, 15 个时间点, 2 个检测项
- `reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx` — 109,237 行, 28 个中心
- `requirement & template/requirement planning.md` — 需求规划文档，含时间点映射说明
- `CLAUDE.md` — transformed 目录规范

## Notes

- sample.xlsx 中受试者 ID 为 4 位数（1003-1028），中心实验室为 5 位数（01001-28003），需验证映射规则
- "退出主要随访访视" 这一访视在动力学分析中需特殊处理（可能对应不同天数）
- 中心实验室数据中 "桥接治疗-DPd" 等周期发生在回输前，天数因人而异

## Scenario

### Scenario 1: 执行双数据源预处理

**Scenario Description:**
- **Precondition**: reference 目录下存在两个 Excel 文件
- **Operation Steps**:
  1. 运行预处理脚本读取两个 Excel
  2. 执行数据类型转换、时间映射、ID 标准化
  3. 验证受试者匹配
  4. 输出数据描述至 transformed 目录
- **Expected Result**:
  - 两份数据结构描述文件生成
  - 受试者匹配报告明确可分析集合
  - 时间轴映射覆盖所有访视周期

## Checklist

- [x] C-001 sample.xlsx 数据成功读取，338 行完整加载
- [x] C-002 G957 xlsx 数据成功读取，109,237 行完整加载
- [x] C-003 访视名称 → 回输后天数映射正确（两组数据）
- [x] C-004 BLD/BLQ 值正确识别和标记
- [x] C-005 受试者 ID 匹配验证完成，输出匹配报告
- [x] C-006 `transformed/` 目录生成两份数据描述 Markdown 文件
- [x] C-007 中心实验室 "结果" 列按检测项目正确区分数值型和定性型

---

# T-002 CAR-T 细胞 PK 分析 (deps: T-001)

## Requirement Description

基于预处理后的 CAR-T 动力学数据，生成动力学曲线图，计算每例受试者的 PK 参数（Cmax、Tmax、AUC0-28d、Tlast、t1/2），并汇总统计。

**Requirement Type**: Feature

**Involved Domain**: Full-stack

### 1. CAR-T 动力学曲线图

**1.1 CAR-T 细胞百分比动力学图**（主要图表，复现参考图风格）

```
布局参考 requirement & template/1st_requirement.png:
- X 轴: Time post-infusion（BL, D1, D4, D7, D10, D14, D21, D28, D60, D90...）
- Y 轴: CAR-T/T Cell (%)
- 每例受试者一条彩色实线 + 圆形标记
- 中位数虚线（空心圆标记）
- 图例显示受试者 ID
- 底部注释说明 PK 参数定义
```

**图表要求**:
- 配色方案：每例受试者不同颜色，使用 seaborn 调色板确保区分度
- 中位数线为黑色虚线 + 空心圆标记
- X 轴使用实际天数但标签显示访视名称
- Y 轴范围自适应，必要时使用对数刻度
- 输出: `generated/chart_cart_kinetics_pct.png` + `.desc.md`

**1.2 CAR-T 细胞绝对计数动力学图**

- 相同布局，Y 轴改为绝对计数（cells/µL）
- 输出: `generated/chart_cart_kinetics_abs.png` + `.desc.md`

### 2. PK 参数计算（NCA 方法）

对每例受试者分别计算以下参数：

| 参数 | 计算方法 | 备注 |
|------|--------|------|
| Cmax | 观测最大值 | 分别计算百分比和绝对计数 |
| Tmax | Cmax 对应天数 | |
| AUC0-28d | 线性梯形法 (0 到 Day 28) | BLQ 设为 0 |
| AUC0-last | 线性梯形法 (0 到 Tlast) | |
| Tlast | 末次可定量时间点 | 最后一个非 BLD/BLQ 值 |
| t1/2 | ln(2)/λz | 终末期 ≥3 个下降点，否则 NC |
| λz | 终末消除速率常数 | 对数线性回归斜率 |

### 3. PK 参数汇总表

- Per-subject 完整参数表
- 描述性统计汇总：N、Mean、SD、Median、Min、Max、Geometric Mean（如适用）
- 输出: `generated/chart_pk_summary.png`（表格图）+ `.desc.md`

## Relevant Guidelines

**Others:**
- 参考图: `requirement & template/1st_requirement.png`
- 需求规划: `requirement & template/requirement planning.md` — PK 参数计算详细说明
- Python 库: numpy, scipy.stats（对数线性回归）, matplotlib

## Notes

- 参考图中使用 5 例受试者（10020, 27002, 10021, 23010, 12012），实际 sample.xlsx 有 18 例，图表需适应更多线条
- t1/2 可能对许多受试者不可计算（数据点不足或 CAR-T 细胞持续存在未进入消除期）
- AUC 计算中 D60, D90 等时间间隔较大，梯形法可能低估或高估实际面积
- "退出主要随访访视" 对应的天数不确定，PK 计算中可能需排除

## Scenario

### Scenario 1: 生成 CAR-T 动力学曲线

**Scenario Description:**
- **Precondition**: T-001 预处理完成，CAR-T 数据已结构化
- **Operation Steps**:
  1. 筛选 CAR-T 细胞百分比数据
  2. 按受试者分组绘制个体线
  3. 计算各时间点中位数绘制中位数线
  4. 添加图例、标注、注释
- **Expected Result**:
  - 动力学图与参考图风格一致
  - 所有 18 例受试者均在图中
  - 中位数线正确反映群体趋势

### Scenario 2: 计算 PK 参数

**Scenario Description:**
- **Precondition**: 动力学数据已处理
- **Operation Steps**:
  1. 对每例受试者执行 NCA 计算
  2. 生成 per-subject 参数表
  3. 计算描述性统计
- **Expected Result**:
  - 所有可计算参数均有值
  - 不可计算的参数标记为 NC
  - 汇总统计格式规范

## Checklist

- [x] C-001 CAR-T 细胞百分比动力学图生成，风格匹配参考图
- [x] C-002 CAR-T 细胞绝对计数动力学图生成
- [x] C-003 Cmax 和 Tmax 计算正确（百分比 + 绝对计数）
- [x] C-004 AUC0-28d 使用线性梯形法计算正确
- [x] C-005 AUC0-last 计算正确
- [x] C-006 t1/2 计算正确，不足 3 点的标记为 NC
- [x] C-007 Per-subject PK 参数表完整
- [x] C-008 描述性统计汇总表格式规范
- [x] C-009 所有图表配 `.desc.md` 文件
- [x] C-010 BLD/BLQ 处理符合设计文档规定

---

# T-003 中心实验室数据质量与生物标志物分析 (deps: T-001)

## Requirement Description

基于预处理后的中心实验室数据，完成数据质量评估和关键生物标志物趋势分析。数据质量部分评估完整性和异常情况；趋势分析部分聚焦多发性骨髓瘤核心监测指标随访视周期的变化。

**Requirement Type**: Feature

**Involved Domain**: Full-stack

### Part A: 数据质量评估

#### A1. 数据完整性

- 各列缺失率统计（特别关注 "结果" 列）
- 按检测项目 × 访视周期的完整性矩阵
- 各中心数据量对比（记录数、受试者数、访视覆盖率）

#### A2. 异常样本分析

- "异常样本备注" 分类统计（溶血、脂血、乳糜等）
- 异常样本在各中心的分布
- 异常比例及影响说明

#### A3. 反审记录分析

- 反审率（有反审记录的行数 / 总行数）
- 反审原因分类
- 反审时间分布

#### A4. 数据质量图表

- `generated/chart_center_data_volume.png` — 各中心数据量柱状图
- `generated/chart_missing_rate_heatmap.png` — 检测项目 × 访视周期完整性热力图
- `generated/chart_abnormal_sample_dist.png` — 异常样本分类分布饼图/柱状图

### Part B: 生物标志物趋势分析

#### B1. 血清蛋白电泳（SPEP）— M 蛋白

- M 蛋白定量随访视周期变化：中位数 + IQR
- 各访视有数据的受试者数（n=xxx）
- 输出: `generated/chart_mprotein_trend.png` + `.desc.md`

#### B2. 血清游离轻链（FLC）

- Kappa 和 Lambda 定量趋势
- Kappa/Lambda 比值趋势（关键：正常范围 0.26-1.65 参考线）
- 输出: `generated/chart_flc_trend.png`, `generated/chart_flc_ratio_trend.png` + `.desc.md`

#### B3. 免疫球蛋白定量（IgA/IgG/IgM）

- 各亚型随访视周期变化
- 标注正常范围参考线
- 输出: `generated/chart_immunoglobulin_trend.png` + `.desc.md`

#### B4. 免疫固定电泳（IFE）

- 各访视阳性/阴性比例变化（堆叠柱状图或面积图）
- M 蛋白类型分布
- 输出: `generated/chart_ife_response.png` + `.desc.md`

#### B5. Daratumumab 干扰去除检测

- 去除前后结果对比（如有配对数据）
- 输出: `generated/chart_dara_interference.png` + `.desc.md`（如数据支持）

#### B6. 检测项目覆盖

- 各检测项目 × 时间的覆盖热力图
- 输出: `generated/chart_test_coverage_heatmap.png` + `.desc.md`

## Relevant Guidelines

**Others:**
- `CLAUDE.md` — generated 目录规范：非文本文件需配 `.desc.md`
- 数据结构参考: `temp/inspect_data.py` 输出

## Notes

- 中心实验室数据的 "结果" 列混合数值和文本，趋势分析仅用数值型结果
- IFE 为定性检测（阳性/阴性 + M 蛋白类型），做分类统计而非趋势线
- FLC 比值需处理除零情况（Lambda=0 时）
- 免疫球蛋白可能因 CAR-T 治疗后免疫重建而呈现特征性变化模式（先降后升）
- 图表中标注各访视点的样本量
- M 蛋白可能存在 "<检测限" 结果，替换为检测限值的一半

## Scenario

### Scenario 1: 数据质量评估

**Scenario Description:**
- **Precondition**: T-001 预处理完成
- **Operation Steps**:
  1. 计算各维度质量指标
  2. 生成质量评估图表
- **Expected Result**: 质量指标准确，图表清晰，各中心可对比

### Scenario 2: 生物标志物趋势分析

**Scenario Description:**
- **Precondition**: T-001 预处理完成
- **Operation Steps**:
  1. 按指标分组提取数值型结果
  2. 按访视周期聚合计算统计量
  3. 生成趋势图
- **Expected Result**: 趋势图展示中位数和 IQR，标注样本量和参考范围

## Checklist

- [x] C-001 各列缺失率统计准确
- [x] C-002 检测项目 × 访视周期完整性矩阵生成
- [x] C-003 异常样本分类统计完成
- [x] C-004 反审记录分析完成
- [x] C-005 各中心数据量对比图生成
- [x] C-006 M 蛋白趋势图生成，标注样本量
- [x] C-007 FLC 趋势图（含比值）生成，标注正常范围参考线
- [x] C-008 免疫球蛋白趋势图生成
- [x] C-009 IFE 阳性率变化图生成
- [x] C-010 检测覆盖热力图生成
- [x] C-011 所有图表（约 9-10 张）配 `.desc.md`

---

# T-004 PK-PD 关联探索性分析 (deps: T-002, T-003)

## Requirement Description

将 CAR-T 扩增 PK 参数与中心实验室疾病生物标志物变化进行关联分析。此为探索性分析，旨在初步揭示 CAR-T 扩增程度与治疗应答之间的关系。

**Requirement Type**: Feature

**Involved Domain**: Full-stack

### 前提条件

- T-001 中已完成受试者匹配验证
- 仅对 sample.xlsx 与中心实验室数据中可匹配的受试者进行分析
- 样本量可能有限，结果为探索性质

### 1. PK-PD 数据整合

- 从 T-002 获取每例受试者的 PK 参数（Cmax、AUC0-28d 等）
- 从 T-003 获取匹配受试者的关键生物标志物数据：
  - M 蛋白基线值和最佳应答值（最低值）
  - M 蛋白最佳变化百分比（Best % change from baseline）
  - FLC 受累轻链基线值和最佳应答值
  - FLC 比值变化

### 2. 关联分析图表

**2.1 Cmax vs M 蛋白最佳变化**
- 散点图：X 轴 = Cmax (%)，Y 轴 = M 蛋白 Best % change
- 如数据量允许，添加 Spearman 相关系数
- 输出: `generated/chart_pkpd_cmax_mprotein.png` + `.desc.md`

**2.2 AUC0-28d vs FLC 比值变化**
- 散点图：X 轴 = AUC0-28d，Y 轴 = FLC 比值变化
- 输出: `generated/chart_pkpd_auc_flc.png` + `.desc.md`

**2.3 CAR-T 扩增与 IFE 转阴**
- 分组箱线图：IFE 转阴组 vs 未转阴组的 Cmax 和 AUC 对比
- 输出: `generated/chart_pkpd_cart_ife.png` + `.desc.md`（如数据支持）

### 3. 综合 PK-PD 汇总表

- 每例匹配受试者的 PK 参数 + 关键 PD 指标一览表

## Relevant Guidelines

**Others:**
- T-002 PK 参数输出
- T-003 生物标志物分析输出
- design.md — 受试者匹配策略

## Notes

- 样本量可能很小（<18 例），统计检验意义有限，重点展示趋势和模式
- 若匹配受试者 <5 例，PK-PD 分析降级为列表展示，不做图表
- M 蛋白/FLC 的基线值取回输前最近一次检测值
- 时间轴对齐误差在 ±7 天内可接受（如 D60 ≈ W8）

## Scenario

### Scenario 1: PK-PD 关联图生成

**Scenario Description:**
- **Precondition**: T-002 PK 参数和 T-003 生物标志物数据均已完成
- **Operation Steps**:
  1. 匹配受试者的 PK 和 PD 数据
  2. 计算 M 蛋白/FLC 的变化值
  3. 生成散点图和分组图
- **Expected Result**:
  - 散点图展示 PK-PD 关系
  - 如有趋势，标注相关系数
  - 图表注明样本量限制

### Scenario 2: 匹配受试者不足

**Scenario Description:**
- **Precondition**: 受试者匹配结果显示 <5 例可用
- **Operation Steps**:
  1. 不生成散点图
  2. 以表格形式列出每例受试者的 PK+PD 数据
- **Expected Result**:
  - 报告说明样本量不足
  - 以列表形式呈现可用数据

## Checklist

- [x] C-001 PK-PD 数据成功整合，匹配受试者数量确认
- [x] C-002 M 蛋白最佳变化百分比计算正确
- [x] C-003 Cmax vs M 蛋白变化散点图生成（如 ≥5 例）
- [x] C-004 AUC vs FLC 变化散点图生成（如 ≥5 例）
- [x] C-005 PK-PD 汇总表完成
- [x] C-006 所有图表配 `.desc.md`
- [x] C-007 分析结果标注探索性质和样本量限制

---

# T-005 综合分析报告撰写 (deps: T-002, T-003, T-004)

## Requirement Description

整合所有分析结果，撰写中文综合分析报告，输出至 `output/report.md`。报告需引用全部生成图表，数据均需可溯源，格式符合项目规范。

**Requirement Type**: Feature

**Involved Domain**: Full-stack

### 报告结构

```
1. 概述
   1.1 分析目的
   1.2 数据来源
   1.3 分析方法摘要

2. 数据概览
   2.1 CAR-T 动力学数据概况（受试者数、时间点、检测项）
   2.2 中心实验室数据概况（记录数、中心数、检测项目汇总表）
   2.3 受试者匹配情况

3. CAR-T 细胞药代动力学分析
   3.1 CAR-T 细胞扩增动力学曲线
   3.2 CAR-T 细胞绝对计数动力学曲线
   3.3 PK 参数汇总
       - Per-subject 参数表
       - 描述性统计表
   3.4 PK 特征总结

4. 中心实验室数据质量评估
   4.1 数据完整性分析
   4.2 异常样本分析
   4.3 反审记录分析
   4.4 各中心数据质量对比

5. 疾病生物标志物趋势分析
   5.1 血清蛋白电泳（M 蛋白）
   5.2 血清游离轻链（FLC）
   5.3 免疫球蛋白定量（IgA/IgG/IgM）
   5.4 免疫固定电泳（IFE）
   5.5 Daratumumab 干扰去除检测
   5.6 检测项目覆盖率

6. PK-PD 关联探索性分析
   6.1 分析方法说明
   6.2 CAR-T 扩增与 M 蛋白应答
   6.3 CAR-T 扩增与 FLC 变化
   6.4 CAR-T 扩增与 IFE 转阴
   6.5 初步发现

7. 总结与讨论
   7.1 主要发现
   7.2 数据质量建议
   7.3 局限性说明
   7.4 后续分析建议
```

### 格式要求

- 中英文之间加半角空格
- 数字与文字之间加半角空格
- 表格和报告内容不得用省略号省略数据
- 图表引用格式: `![图表标题](../generated/chart_xxx.png)`
- 关键数据标注引用来源（数据文件名 + 筛选条件）
- PK 参数表保留适当有效数字（百分比 2 位小数，天数整数，AUC 1 位小数）

## Relevant Guidelines

**Others:**
- `CLAUDE.md` — 格式要求和 output 目录规范
- T-002, T-003, T-004 的图表和分析输出

## Notes

- 报告为描述性和探索性分析，措辞需审慎，避免因果性表述
- PK-PD 章节需强调探索性质和样本量限制
- 所有图表引用路径需正确
- 总结部分建议后续分析方向（如群体 PK 建模、与疗效数据整合等）

## Scenario

### Scenario 1: 生成完整综合报告

**Scenario Description:**
- **Precondition**: T-002, T-003, T-004 均已完成
- **Operation Steps**:
  1. 按报告结构组织内容
  2. 嵌入全部图表引用和统计表格
  3. 撰写分析文本、解读和总结
  4. 检查格式规范
  5. 输出至 `output/report.md`
- **Expected Result**:
  - 报告 7 个大章节齐全
  - 引用约 15-18 张图表
  - 数据准确可溯源
  - 中文表述流畅专业

## Checklist

- [x] C-001 报告包含全部 7 个大章节
- [x] C-002 CAR-T PK 章节引用动力学图和 PK 参数表
- [x] C-003 数据质量章节引用质量评估图表
- [x] C-004 生物标志物章节引用趋势分析图表
- [x] C-005 PK-PD 章节引用关联分析图表（或说明样本量不足）
- [x] C-006 总结包含主要发现、建议和局限性
- [x] C-007 格式符合要求（中英文空格、无省略号、有效数字、图表路径）
- [x] C-008 所有数据标注引用来源
- [x] C-009 报告输出至 `output/report.md`
