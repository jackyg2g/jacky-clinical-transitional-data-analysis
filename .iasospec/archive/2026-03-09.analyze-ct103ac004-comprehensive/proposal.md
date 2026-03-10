# Proposal: CT103AC004 临床试验综合数据分析

## Requirement Summary

基于 CT103AC004 CAR-T 临床试验的两组核心数据（CAR-T 细胞动力学数据 + 中心实验室检测结果），执行药代动力学（PK）分析、疾病生物标志物趋势分析、PK-PD 关联探索性分析，并生成综合分析报告。

## Background and Motivation

- CT103AC004 是驯鹿生物（Legend Biotech）cilta-cel CAR-T 细胞疗法针对多发性骨髓瘤的多中心临床试验
- 现有两组关键数据源：
  - **CAR-T 细胞检测数据**（`sample.xlsx`）：18 例受试者的 CAR-T 细胞扩增与持续性数据，覆盖清淋前至 D540
  - **中心实验室检测结果**（`G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx`）：28 个中心、109,237 条记录，覆盖 M 蛋白、游离轻链、免疫球蛋白、免疫固定电泳等多发性骨髓瘤核心监测指标
- 世界级临床转化数据分析应将 PK（CAR-T 扩增动力学）与 PD（疾病应答生物标志物）关联分析，揭示 CAR-T 扩增与肿瘤负荷变化之间的关系
- 参考图表（`requirement & template/1st_requirement.png`）展示了 CAR-T/Live WBC (%) 随时间的动力学曲线，需复现并扩展

## Goals and Success Criteria

- 完成 CAR-T 细胞 PK 分析：生成动力学曲线，计算 Cmax、Tmax、AUC、t1/2 等关键 PK 参数
- 完成中心实验室数据质量评估与关键生物标志物趋势分析
- 完成 PK-PD 关联探索性分析：CAR-T 扩增参数与 M 蛋白/FLC 变化的关联
- 输出包含图表和统计表格的中文综合分析报告

**Success Criteria**:
- CAR-T 动力学图表风格匹配参考图（`1st_requirement.png`）
- PK 参数表覆盖所有可计算的受试者
- 生物标志物趋势图覆盖 M 蛋白、FLC、免疫球蛋白、IFE 等核心指标
- PK-PD 散点图展示扩增参数与应答标志物的关系
- 所有数据可溯源至原始文件

## Scope and Boundaries

### In Scope (Included This Time)

- **CAR-T PK 分析**
  - CAR-T 细胞百分比和绝对计数动力学曲线（个体线 + 中位数线）
  - Per-subject PK 参数计算（Cmax、Tmax、AUC0-28d、Tlast、t1/2）
  - PK 参数汇总统计表
- **中心实验室数据分析**
  - 数据质量评估（缺失率、异常样本、反审记录、中心级完整性）
  - 关键生物标志物趋势：M 蛋白（SPEP）、FLC kappa/lambda/比值、IgA/IgG/IgM、IFE 阳性率
  - 各中心数据量和检测覆盖率
- **PK-PD 关联探索性分析**
  - 对 sample.xlsx 中 18 例受试者，匹配中心实验室数据中的疾病标志物
  - CAR-T Cmax vs M 蛋白最佳变化（Best % change）
  - CAR-T AUC vs FLC 比值变化
- **综合报告输出至 `output/report.md`**

### Out of Scope (Not Included This Time)

- 临床应答分类（CR、VGPR 等）— 需独立的临床裁定数据
- 统计学建模（生存分析、多变量回归）— 本次为描述性与探索性分析
- 安全性数据分析（不良事件、实验室安全指标）— 当前数据不含
- 与其他试验数据的交叉比较 — 单一试验分析

## User/System Scenarios

### Scenario 1: 生成 CAR-T 动力学图表与 PK 参数

- **Who**: 数据分析人员
- **When/Condition**: reference 目录包含 sample.xlsx
- **What**: 处理 CAR-T 检测数据，生成动力学曲线和 PK 参数表
- **Result**: 获得匹配参考图风格的动力学曲线，以及每例受试者的 PK 参数汇总

### Scenario 2: 生成疾病标志物趋势分析

- **Who**: 数据分析人员
- **When/Condition**: reference 目录包含中心实验室 Excel 数据
- **What**: 分析关键生物标志物随访视周期的变化
- **Result**: 获得 M 蛋白、FLC、免疫球蛋白等指标的趋势图和统计表

### Scenario 3: 查看 PK-PD 关联分析

- **Who**: 临床/医学团队
- **When/Condition**: 阅读报告中的 PK-PD 章节
- **What**: 查看 CAR-T 扩增参数与疾病标志物变化的关联图
- **Result**: 了解 CAR-T 扩增程度与治疗应答之间的初步关系

### Scenario 4: 评估数据质量

- **Who**: 临床运营团队
- **When/Condition**: 阅读报告中的数据质量章节
- **What**: 查看各中心数据完整性、异常样本分布
- **Result**: 识别数据质量问题，为后续数据管理提供参考

## Constraints and Assumptions

### Constraints

- 分析以描述性统计和探索性分析为主，不做确证性统计推断
- 报告语言为中文，图表标注为中文
- BLD/BLQ 处理：绘图时设为 0，PK 参数计算时排除或设为 LOQ/2
- t1/2 计算需至少 3 个终末期下降数据点，不足时标记为 NC（Not Calculable）
- 图表生成至 `generated/`，每张配 `.desc.md` 描述文件

### Assumptions

- sample.xlsx 中受试者 ID（1003-1028）对应中心实验室数据中受试者筛选号的后 4 位（如 01003）
- sample.xlsx 的 D1 对应 CAR-T 回输日（Day 1）
- 中心实验室访视周期（W8、W12 等）可映射为回输后天数，用于 PK-PD 时间轴对齐
- 两组数据的重叠受试者可能有限（sample.xlsx 18 例 vs 中心实验室 28 个中心），PK-PD 分析仅针对可匹配的受试者

## Terms and Terminology

| Term/Abbreviation | Meaning | Notes |
|----------|------|------|
| CT103AC004 | 临床试验方案编号 | 驯鹿生物 cilta-cel CAR-T |
| PK | 药代动力学（Pharmacokinetics） | 本试验中指 CAR-T 细胞扩增动力学 |
| PD | 药效动力学（Pharmacodynamics） | 本试验中指疾病生物标志物应答 |
| Cmax | 最大浓度/最大百分比 | CAR-T 细胞扩增峰值 |
| Tmax | 达峰时间 | 达到 Cmax 的天数 |
| AUC0-28d | 0-28 天曲线下面积 | 线性梯形法计算 |
| t1/2 | 终末半衰期 | 对数线性回归估算 |
| Tlast | 末次可定量浓度时间 | 最后一个高于检测限的时间点 |
| BLD | 低于检测限（Below Limit of Detection） | |
| BLQ | 低于定量限（Below Limit of Quantification） | |
| M 蛋白 | 单克隆免疫球蛋白（M-protein） | 多发性骨髓瘤核心标志物 |
| FLC | 血清游离轻链 | kappa/lambda 比值为关键指标 |
| SPEP | 血清蛋白电泳 | M 蛋白定量检测 |
| IFE | 免疫固定电泳 | M 蛋白定性检测 |
| DPd | Daratumumab + Pomalidomide + Dex | 桥接治疗方案 |

## References and Links

- CAR-T 动力学数据: `reference/raw-data-yance/sample.xlsx`
- 中心实验室数据: `reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx`
- 参考图表: `requirement & template/1st_requirement.png`
- 需求规划文档: `requirement & template/requirement planning.md`
- 项目结构: `CLAUDE.md`
