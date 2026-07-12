# DA803 引脚编号、逐极配色与 5.00 mm 型号设计

日期：2026-07-12

## 目标

统一 DA803 的逻辑引脚方向，扩展通用生成器以独立保存侧盖、每极主体、每极压杆和金属焊脚颜色，并从 DA803-500 规格书建立独立 5.00 mm profile。生成器继续支持任意极数，不能复制极数专用脚本，也不能通过缩放 DA803-350 获得 DA803-500。

## 编号与坐标

- 现有侧盖位于高 X 侧，所有实体位置和 PCB 焊脚坐标保持不变。
- Pin 1 是最靠近侧盖、X 最大的电气模块；Pin N 是远离侧盖、X 最小的模块。
- 逻辑 Pin `p` 映射到现有几何索引 `poles - p`。几何索引仍按低 X 到高 X 定位。
- 装配树以逻辑编号命名：`Pole_1`、`Housing_P1`、`Actuator_P1`、`Pin_P1_A` 和 `Pin_P1_B` 都位于最高 X 的电气模块。
- PCB 坐标公式不变；仅改变逻辑编号到几何索引的映射。

## 颜色接口和兼容性

- `CoverColor`：侧盖颜色。
- `HousingColors`：Pin 1 到 Pin N 的塑料主体颜色列表。
- `ActuatorColors`：Pin 1 到 Pin N 的压杆颜色列表。
- `TerminalPinColor`：所有金属 PCB 焊脚颜色，目标模型使用银色。
- `HousingColors` 和 `ActuatorColors` 接受单色或恰好 N 个颜色；单色扩展到全部极，其他数量报错。
- 旧 `BodyColor` 保留。未提供 `CoverColor` 或 `HousingColors` 时分别回退到 `BodyColor`；若 `BodyColor` 也未提供，则使用 profile 默认颜色。
- Parameters 保存兼容字段 `BodyColor`，以及 `CoverColor`、`HousingColors`、`ActuatorColors`、`TerminalPinColor` 和编号方向字段。
- 每个 FCStd 实体通过 `ConfiguredColor` 保存实际颜色；STEP 按独立实体导出以保留颜色。

## DA803-500

- 从 `references/DA803-500/datasheet.pdf` 的尺寸图和推荐 PCB layout 提取明确标注尺寸。
- PCB 图中的 2.90 mm 从后边缘量到后排孔中心；换算到模型由进线正面起算的 Y 坐标后，两排为 4.60 mm 和 9.60 mm。
- 新建 `profiles/DA803-500.json`，不得复用或缩放 3.50 mm profile。
- 未在图纸标注的入口、压杆尖端、斜面、圆角和侧面浅凹点以产品渲染图校核，并在 profile 或产品文档中记录为外观工程假设。
- 目标 2P 配色按 Pin 1 到 Pin 2 为黑/红主体、黑/红压杆，黑色侧盖、银色焊脚。

## 测试与验证

所有行为先写测试并确认预期失败。测试覆盖逻辑编号、PCB 坐标不变、颜色展开和拒绝规则、动态零件数、profile 总宽、350/500 PCB layout、FCStd 参数和装配树、STEP 回读颜色与行尾空白。生成后每个模型使用通用验证命令验证；预览至少包含两种 350-4P 彩色排列和 500-2P。
