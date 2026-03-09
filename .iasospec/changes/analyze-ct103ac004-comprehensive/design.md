## Context

CT103AC004 临床试验产生两组核心数据：CAR-T 细胞动力学数据（sample.xlsx，338 行 × 4 列，18 例受试者）和中心实验室检测结果（G957 xlsx，109,237 行 × 18 列，28 个中心）。需要将两组数据整合分析，产出世界级的临床转化数据分析报告。

参考图表（`1st_requirement.png`）展示了 5 例受试者的 CAR-T/Live WBC (%) 动力学曲线及中位数线，需以此为基线复现并扩展至全部 18 例受试者。

## Goals / Non-Goals

### Goals

- 建立双数据源预处理与整合流程
- 实现标准 PK 参数计算（Cmax、Tmax、AUC、t1/2）
- 生成临床级质量的可视化图表
- 探索 PK-PD 关联，揭示 CAR-T 扩增与疾病应答关系
- 输出结构化综合报告

### Non-Goals

- 不做确证性统计分析（如假设检验、回归建模）
- 不构建交互式仪表板
- 不做安全性或不良事件分析
- 不做正式群体 PK 建模（如 NONMEM）

## Decisions

### 1. PK 参数计算方法

**Decision**: 使用非房室分析（NCA）方法计算 PK 参数

**Rationale**: NCA 是 CAR-T 细胞 PK 分析的标准方法，不依赖房室模型假设，适合个体化描述性分析。FDA/EMA 指南均认可 NCA 用于细胞治疗 PK 评估。

**具体方法**:
- Cmax/Tmax: 直接从观测数据中取最大值及其对应时间
- AUC0-28d: 线性梯形法（Linear Trapezoidal Rule），BLQ 值按 0 处理
- t1/2: 终末消除相 ≥3 个连续下降点，对数线性回归（ln(C) vs t），t1/2 = ln(2)/λz
- Tlast: 最后一个高于检测限的时间点

**Alternatives Considered**:
- 房室模型: 数据点数量有限（每例最多 15 个时间点），不适合复杂模型拟合
- Phoenix WinNonlin: 需要商业软件许可，Python scipy 实现同等计算足够

### 2. 受试者 ID 匹配策略

**Decision**: sample.xlsx 中 ID（如 1003）映射为中心实验室中的 01003（中心 01 + 受试者 003），即补齐 5 位格式

**Rationale**: 参考图中显示 10020、27002 等 5 位 ID，前 2 位为中心编号。sample.xlsx 中 18 例均在 1003-1028 范围，对应中心 01 的受试者。

**Alternatives Considered**:
- 模糊匹配: 风险高，可能错配

### 3. 时间轴对齐方案

**Decision**: 以 CAR-T 回输日（D1）为 Day 0 建立统一时间轴

**Rationale**:
- sample.xlsx 时间点已按回输后天数编码（D1, D4, D7...）
- 中心实验室访视周期（W8=Day 56, W12=Day 84...）可转换为回输后天数
- 统一时间轴是 PK-PD 关联分析的前提

### 4. 图表风格设计

**Decision**:
- CAR-T 动力学图复现参考图风格：个体彩色线 + 空心圆标记 + 虚线中位数线
- 临床标志物图使用中位数 + IQR 箱线图/带状图
- PK-PD 散点图使用对数坐标 + 回归趋势线
- 统一使用 matplotlib + seaborn，中文字体（SimHei/STHeiti），150 DPI PNG

**Rationale**: 参考图风格清晰专业，保持一致性；中文标注满足报告需求

### 5. BLD/BLQ 数据处理

**Decision**:
- 动力学曲线绘图: BLD/BLQ 设为 0
- PK 参数计算: 首个 BLQ 之前的 BLQ 设为 0；末尾连续 BLQ 视为低于检测限，Tlast 取最后可定量点
- AUC 计算: BLQ 设为 0 纳入梯形计算

**Rationale**: 符合 FDA Guidance for Industry: Pharmacokinetic Data Analysis 的 BLQ 处理建议

## Data Model

### 数据源 1: CAR-T 动力学数据 (sample.xlsx)

```
Sheet1: 338 rows × 4 columns
├── 受试者ID (int) - 18 unique (1003-1028)
├── 访视 (str) - 15 timepoints: 清淋前检查, 主要随访期 D1-D540, 退出主要随访访视
├── 分析项 (str) - 2 items: CAR-T细胞占T细胞百分比, CAR-T细胞绝对计数
└── 结果 (str/mixed) - numeric values + BLD/BLQ
```

### 数据源 2: 中心实验室数据 (G957 xlsx)

```
项目管理导出: 109,237 rows × 18 columns
├── 方案编号, 中心编号, 观合样本编号, 受试者筛选号
├── 访视周期, 样本类型, 采集时间
├── 检测项目, 检测分项, 结果, 单位
├── 检验备注, 异常样本备注, 申请单备注
└── 反审时间, 反审备注, 检测时间, 报告时间
```

### 时间轴映射

| sample.xlsx 访视 | Day (相对回输) | 中心实验室访视 | Day |
|----------------|------------|------------|-----|
| 清淋前检查 | -5 (approx) | 清淋前 | -5 |
| D1 | 1 | — | — |
| D4 | 4 | — | — |
| D7 | 7 | — | — |
| D14 | 14 | — | — |
| D28 | 28 | — | — |
| D60 | 60 | W8 | 56 |
| D90 | 90 | W12 | 84 |
| D180 | 180 | W24 | 168 |
| D270 | 270 | W36 | 252 |
| D360 | 360 | W48 | 336 |
| D540 | 540 | W76 | 532 |

### PK 参数输出

```
Per-subject PK table:
├── Subject ID
├── Cmax (%) / Cmax (cells/µL)
├── Tmax (day)
├── AUC0-28d (%.day / cells.day/µL)
├── Tlast (day)
├── t1/2 (day) — or NC
└── Lambda_z (1/day) — terminal rate constant
```

## Architecture Patterns

- **多阶段流水线**: T-001 预处理 → T-002 PK 分析 / T-003 中心实验室分析（并行） → T-004 PK-PD 关联 → T-005 报告撰写
- **独立脚本**: 每个任务的分析脚本独立存放于 `temp/`，可单独运行
- **图表-描述文件对**: 每个 `generated/*.png` 配 `generated/*.png.desc.md`

## Risks / Trade-offs

### Risk: 受试者匹配不完整

**Risk**: sample.xlsx 的 18 例受试者可能仅部分存在于中心实验室数据中（中心实验室数据覆盖 28 个中心，但 sample.xlsx 受试者可能均来自中心 01）

**Mitigation**:
- 预处理阶段即验证匹配情况
- PK-PD 分析仅针对可匹配受试者，报告中注明样本量
- 即使匹配有限，PK 分析和中心实验室分析各自独立仍有完整价值

### Risk: t1/2 不可计算

**Risk**: 部分受试者终末期下降数据点不足 3 个，无法计算 t1/2

**Mitigation**:
- 标记为 NC（Not Calculable）
- 报告中说明可计算比例及原因

### Trade-off: 分析深度 vs 范围

**Decision**: 优先覆盖所有核心指标的描述性分析，PK-PD 关联作为探索性分析呈现

**Impact**: PK-PD 部分可能因样本量限制无法得出统计显著结论，但仍能展示趋势和模式

## Open Questions

1. **sample.xlsx 受试者 ID 与中心实验室受试者筛选号的精确映射规则**
   - 假设 1003 → 01003，需在预处理阶段验证

2. **中心实验室访视周期中 "桥接治疗-DPd" 等非标准访视的时间定位**
   - 桥接治疗发生在清淋前，具体天数因患者而异
   - 可能需排除或单独处理

3. **Daratumumab 干扰去除检测结果与常规结果的优先级**
   - 对于接受 Daratumumab 治疗的患者，去除干扰后的结果更准确
   - 需确认是否优先使用去除干扰后的结果

## References

- CAR-T 动力学数据: `reference/raw-data-yance/sample.xlsx`
- 中心实验室数据: `reference/raw-data-yance/G957_驯鹿CT103AC004-中心实验室检测结果周汇总-20260206.xlsx`
- 参考图表: `requirement & template/1st_requirement.png`
- 需求规划: `requirement & template/requirement planning.md`
- FDA Guidance: Pharmacokinetic Data Analysis — BLQ handling
