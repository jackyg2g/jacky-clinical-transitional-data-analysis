# Proposal: CT103AC004 中心实验室检测结果综合分析

## Requirement Summary

基于 CT103AC004 临床试验中心实验室检测结果周汇总数据，生成综合分析报告，涵盖数据质量评估和临床检测趋势分析。

## Background and Motivation

- CT103AC004 是驯鹿生物 CAR-T 细胞治疗产品（cilta-cel）针对多发性骨髓瘤的多中心临床试验
- 中心实验室数据包含 109,237 条检测记录，覆盖 28 个中心、78 个检测分项、54 个访视周期
- 需要对数据进行系统性分析，为临床运营和医学团队提供数据质量和检测趋势的全面视图
- 当前项目中尚无任何分析产出，transformed/generated/output 目录均为空

## Goals and Success Criteria

- 完成数据预处理，将 Excel 数据解析为可分析的结构化格式
- 生成数据质量评估：缺失率、异常样本、反审记录、各中心完整性
- 生成临床检测趋势分析：关键指标（M 蛋白、游离轻链、免疫球蛋白等）随访视周期的变化趋势
- 输出包含图表引用的中文综合分析报告

**Success Criteria**:
- 报告涵盖所有 28 个检测项目的基本统计
- 数据质量部分包含缺失率、异常样本率、反审率等量化指标
- 趋势分析部分包含关键指标的可视化图表
- 报告中所有数据均可溯源至原始数据

## Scope and Boundaries

### In Scope (Included This Time)

- Excel 数据预处理与结构化解析
- 数据质量评估（缺失率、异常样本、反审记录、中心级完整性）
- 关键临床指标描述性统计与趋势可视化（M 蛋白、FLC kappa/lambda、免疫球蛋白 IgA/IgG/IgM、血清蛋白电泳、免疫固定电泳）
- 各中心数据量与检测覆盖率对比
- 中文综合分析报告输出至 `output/report.md`

### Out of Scope (Not Included This Time)

- 患者临床应答分类（CR、VGPR、PR 等）— 需要临床裁定，非纯实验室数据可判定
- 统计学假设检验或建模 — 本次为描述性分析
- 与其他数据源（如疗效评估、不良事件）的交叉分析 — 当前仅有中心实验室数据
- 英文版报告 — 后续按需扩展

## User/System Scenarios

### Scenario 1: 生成综合分析报告

- **Who**: 数据分析人员
- **When/Condition**: reference 目录中已有中心实验室数据文件
- **What**: 执行预处理、分析、图表生成、报告输出的完整流程
- **Result**: 在 `output/report.md` 获得包含图表和数据表格的中文综合分析报告

### Scenario 2: 查看数据质量概况

- **Who**: 临床运营/医学团队
- **When/Condition**: 阅读生成的报告
- **What**: 查看数据质量评估章节
- **Result**: 了解各中心数据完整性、异常样本分布、反审情况

### Scenario 3: 查看检测趋势

- **Who**: 临床运营/医学团队
- **When/Condition**: 阅读生成的报告
- **What**: 查看趋势分析章节中的图表和统计
- **Result**: 了解关键生物标志物随访视周期的变化模式

## Constraints and Assumptions

### Constraints

- 分析基于描述性统计，不做临床应答判定
- 报告语言为中文
- 图表生成至 `generated/` 目录，每张图需配 `.desc.md` 描述文件
- 报告中数据引用需可溯源

### Assumptions

- Excel 数据为最新版本的完整数据导出
- 访视周期编码遵循方案规定的时间点
- "结果" 列中混合数值和文本结果（如免疫固定电泳的定性结果），需分别处理
- 数据中的 "检验备注"、"异常样本备注" 等字段反映实际质量问题

## Terms and Terminology

| Term/Abbreviation | Meaning | Notes |
|----------|------|------|
| CT103AC004 | 临床试验方案编号 | 驯鹿生物 cilta-cel CAR-T 疗法 |
| M 蛋白 | 单克隆免疫球蛋白（M-protein） | 多发性骨髓瘤关键监测指标 |
| FLC | 血清游离轻链（Free Light Chain） | kappa/lambda 比值为关键指标 |
| SPEP | 血清蛋白电泳（Serum Protein Electrophoresis） | 检测 M 蛋白定量 |
| IFE | 免疫固定电泳（Immunofixation Electrophoresis） | 定性检测 M 蛋白类型 |
| DPd | Daratumumab + Pomalidomide + Dexamethasone | 桥接治疗方案 |
| 反审 | Re-audit / Data Correction | 检测结果的修正记录 |

## References and Links

- 数据文件: `reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx`
- 项目结构说明: `CLAUDE.md`
