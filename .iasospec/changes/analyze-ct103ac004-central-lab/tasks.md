# T-001 数据预处理与结构化解析

## Requirement Description

将 Excel 原始数据预处理为可分析的结构化格式，包括数据类型转换、缺失值标记、访视周期排序映射等。此任务为后续所有分析任务的基础。

**Requirement Type**: Infrastructure

**Involved Domain**: Full-stack

### 具体要求

1. 读取 Excel 文件，解析所有列
2. 时间字段（采集时间、检测时间、报告时间、反审时间）转换为 datetime
3. "结果" 列按检测项目分组，区分数值型和定性型结果
4. 建立访视周期排序映射（按临床方案时间线：筛选期 → 桥接治疗-DPd → 清淋前 → W8 → W12 → ... → 长期随访）
5. 统计基本数据维度：受试者数、样本数、各中心数据量
6. 将预处理结果描述输出至 `transformed/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx.md`

## Relevant Guidelines

**Others:**
- 数据文件: `reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx`
- 项目结构: `CLAUDE.md` — transformed 目录用于存放解析后的 Markdown 描述

## Notes

- "结果" 列混合数值和文本，需按检测项目分别处理
- 访视周期编码不能按字母序排列，需自定义排序
- 预处理脚本放置于 `temp/` 目录

## Scenario

### Scenario 1: 执行数据预处理

**Scenario Description:**
- **Precondition**: `reference/raw-data-yance/` 下存在目标 Excel 文件
- **Operation Steps**:
  1. 运行预处理脚本读取 Excel 数据
  2. 执行数据类型转换和清洗
  3. 输出数据结构描述至 transformed 目录
- **Expected Result**:
  - 数据成功加载，时间字段转换正确
  - 数值型结果正确提取，定性结果保留文本
  - transformed 目录生成数据描述文件

## Checklist

- [ ] C-001 Excel 数据成功读取，109,237 行 × 18 列完整加载
- [ ] C-002 时间字段正确转换为 datetime 格式
- [ ] C-003 "结果" 列按检测项目正确区分数值型和定性型
- [ ] C-004 访视周期排序映射建立，符合临床方案时间线
- [ ] C-005 `transformed/` 目录生成数据描述 Markdown 文件

---

# T-002 数据质量评估分析 (deps: T-001)

## Requirement Description

基于预处理后的数据，进行全面的数据质量评估，包括缺失率分析、异常样本统计、反审记录分析、各中心数据完整性对比。生成相关图表至 `generated/` 目录。

**Requirement Type**: Feature

**Involved Domain**: Full-stack

### 具体分析维度

1. **整体缺失率统计**
   - 各列缺失率（特别关注"结果"列）
   - 按检测项目统计结果缺失率
   - 按访视周期统计数据完整性

2. **异常样本分析**
   - "异常样本备注" 分类统计（溶血、脂血、乳糜等）
   - 异常样本在各中心的分布
   - 异常样本对结果的潜在影响说明

3. **反审记录分析**
   - 反审率（有反审记录的行数/总行数）
   - 反审原因分类统计
   - 反审时间分布

4. **各中心数据量对比**
   - 各中心检测记录数
   - 各中心受试者数
   - 各中心访视覆盖率

### 需生成图表

- `chart_center_data_volume.png` — 各中心数据量柱状图
- `chart_missing_rate_by_test.png` — 各检测项目缺失率热力图
- `chart_abnormal_sample_dist.png` — 异常样本分类分布图

## Relevant Guidelines

**Others:**
- `CLAUDE.md` — generated 目录规范：非文本文件需配 `.desc.md` 描述文件

## Notes

- 缺失率需区分"未采集"和"结果为空"两种情况
- 异常样本备注仅约 1% 的行有值，需关注分布是否集中于特定中心
- 反审记录约 3%，需分析是否存在系统性问题

## Scenario

### Scenario 1: 生成数据质量评估章节

**Scenario Description:**
- **Precondition**: T-001 预处理完成
- **Operation Steps**:
  1. 运行数据质量分析脚本
  2. 计算各维度质量指标
  3. 生成图表至 `generated/` 并配套描述文件
- **Expected Result**:
  - 质量指标计算准确
  - 图表清晰可读，中文标注
  - 每张图表有配套 `.desc.md` 文件

## Checklist

- [ ] C-001 各列缺失率统计完成，结果准确
- [ ] C-002 异常样本分类统计完成，覆盖所有异常类型
- [ ] C-003 反审记录分析完成，包含反审率和原因分类
- [ ] C-004 各中心数据量对比完成
- [ ] C-005 生成 3 张图表至 `generated/`，每张配 `.desc.md`
- [ ] C-006 所有统计数据可溯源至原始数据

---

# T-003 临床检测趋势分析 (deps: T-001)

## Requirement Description

对关键临床指标进行描述性统计和趋势可视化分析，展示各指标随访视周期的变化模式。聚焦多发性骨髓瘤核心监测指标。

**Requirement Type**: Feature

**Involved Domain**: Full-stack

### 关键分析指标

1. **血清蛋白电泳（SPEP）**
   - M 蛋白定量随访视周期变化（中位数 + IQR）
   - 各访视有数据的受试者数

2. **血清游离轻链（FLC）**
   - Kappa 和 Lambda 定量趋势
   - Kappa/Lambda 比值变化趋势
   - 受累/非受累轻链差异

3. **免疫球蛋白定量（IgA/IgG/IgM）**
   - 各亚型随访视周期变化趋势
   - 正常范围参考线标注

4. **免疫固定电泳（IFE）**
   - 各访视阳性/阴性比例变化
   - M 蛋白类型分布

5. **Daratumumab 干扰去除检测**
   - 去除前后结果对比（如有配对数据）

6. **检测项目整体分布**
   - 各检测项目的数据量和时间覆盖

### 需生成图表

- `chart_mprotein_trend.png` — M 蛋白定量趋势图（中位数 + IQR）
- `chart_flc_trend.png` — 游离轻链趋势图
- `chart_flc_ratio_trend.png` — FLC Kappa/Lambda 比值趋势图
- `chart_immunoglobulin_trend.png` — 免疫球蛋白（IgA/IgG/IgM）趋势图
- `chart_ife_response.png` — 免疫固定电泳阳性率变化图
- `chart_test_coverage.png` — 各检测项目时间覆盖热力图

## Relevant Guidelines

**Others:**
- `CLAUDE.md` — generated 目录规范
- 数据处理参考: `temp/inspect_data.py`

## Notes

- 数值型结果才能做趋势分析，定性结果做分类统计
- 访视周期需使用 T-001 建立的排序映射
- 图表中标注各访视点的样本量（n=xxx）
- M 蛋白等关键指标可能存在 "<检测限" 的结果，需合理处理（如替换为检测限值的一半）

## Scenario

### Scenario 1: 生成关键指标趋势图

**Scenario Description:**
- **Precondition**: T-001 预处理完成
- **Operation Steps**:
  1. 筛选关键检测指标数据
  2. 按访视周期聚合计算描述性统计量
  3. 生成趋势图至 `generated/`
- **Expected Result**:
  - 趋势图展示中位数和四分位数范围
  - X 轴按方案时间线排序
  - 图表标注各点样本量
  - 配套 `.desc.md` 描述文件

## Checklist

- [ ] C-001 M 蛋白定量趋势分析完成，图表生成
- [ ] C-002 游离轻链（Kappa/Lambda/比值）趋势分析完成
- [ ] C-003 免疫球蛋白（IgA/IgG/IgM）趋势分析完成
- [ ] C-004 免疫固定电泳阳性率统计完成
- [ ] C-005 Daratumumab 干扰去除检测对比分析完成（如数据支持）
- [ ] C-006 各检测项目时间覆盖热力图生成
- [ ] C-007 生成 6 张图表至 `generated/`，每张配 `.desc.md`
- [ ] C-008 所有图表中文标注，访视周期排序正确

---

# T-004 综合分析报告撰写 (deps: T-002, T-003)

## Requirement Description

整合数据质量评估和临床检测趋势分析结果，撰写中文综合分析报告，输出至 `output/report.md`。报告需引用 `generated/` 中的图表，数据均需可溯源。

**Requirement Type**: Feature

**Involved Domain**: Full-stack

### 报告结构

```
1. 概述
   1.1 分析目的
   1.2 数据来源
   1.3 分析方法

2. 数据概览
   2.1 数据规模（记录数、受试者数、中心数）
   2.2 检测项目汇总表
   2.3 访视周期分布
   2.4 样本类型分布

3. 数据质量评估
   3.1 数据完整性
   3.2 异常样本分析
   3.3 反审记录分析
   3.4 各中心数据质量对比

4. 临床检测趋势分析
   4.1 血清蛋白电泳（M 蛋白）
   4.2 血清游离轻链
   4.3 免疫球蛋白定量
   4.4 免疫固定电泳
   4.5 Daratumumab 干扰去除检测
   4.6 检测项目覆盖率

5. 总结与发现
   5.1 主要发现
   5.2 数据质量建议
   5.3 局限性说明
```

### 格式要求

- 中英文之间加半角空格
- 数字与文字之间加半角空格
- 表格和报告内容不得用省略号省略数据
- 图表引用格式: `![图表标题](../generated/chart_xxx.png)`
- 关键数据标注引用来源

## Relevant Guidelines

**Others:**
- `CLAUDE.md` — 格式要求和 output 目录规范

## Notes

- 报告为描述性分析，不做临床应答判定
- 所有图表引用路径需正确指向 `generated/` 目录
- 总结部分需客观陈述发现，避免过度解读

## Scenario

### Scenario 1: 生成完整分析报告

**Scenario Description:**
- **Precondition**: T-002 和 T-003 均已完成，图表已生成
- **Operation Steps**:
  1. 按报告结构组织内容
  2. 嵌入图表引用和数据表格
  3. 撰写分析文本和总结
  4. 输出至 `output/report.md`
- **Expected Result**:
  - 报告结构完整，章节齐全
  - 图表正确引用并显示
  - 数据准确，格式规范
  - 中文表述流畅，术语使用准确

## Checklist

- [ ] C-001 报告包含全部 5 个大章节
- [ ] C-002 数据概览章节含完整统计表格（检测项目、访视周期、样本类型）
- [ ] C-003 数据质量章节引用 T-002 生成的图表和统计数据
- [ ] C-004 趋势分析章节引用 T-003 生成的图表并配文字说明
- [ ] C-005 总结章节包含主要发现、建议和局限性
- [ ] C-006 格式符合要求（中英文空格、无省略号、图表引用正确）
- [ ] C-007 报告输出至 `output/report.md`
