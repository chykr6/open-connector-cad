# DA803 系列参数化生成设计

本文是 DA803 系列当前有效的建模说明。历史 3P 专用实现、逐极配色扩展和早期实施计划不再作为当前设计依据；需要追溯过程时查看 Git 历史。

## 产品命名

DA803 是地安的可组合直插式扳手端子系列。官方型号按间距命名：

- `DA803-3.5`
- `DA803-5.0`
- `DA803-7.5`

仓库内部文件名、profile 名、资料目录和输出目录使用无小数点 pitch code：

- `DA803-350` 对应官方 `DA803-3.5`
- `DA803-500` 对应官方 `DA803-5.0`
- `DA803-750` 对应官方 `DA803-7.5`

内部命名保持稳定，避免小数点进入脚本路径、STEP 产品名和发布文件名。

## 目录边界

```text
DA803/
├─ README.md           DA803 系列产品说明
├─ DESIGN.md           DA803 系列建模规范
├─ profiles/           DA803-350/500/750 参数 profile
├─ references/         规格书和产品渲染图
├─ generated/          FCStd、STEP 和预览 PNG
├─ tools/              DA803 生成、渲染、验证工具
└─ tests/              DA803 参数与 FreeCAD 几何测试
```

DA803 的尺寸、外观假设和默认颜色由对应 JSON profile 提供。后续其他系列使用独立顶层目录，只有在多个系列验证为同一套流程后才提取共享工具。

## 生成输入

- `series`：产品系列，例如 `DA803`。
- `pitch`：官方间距数值，例如 `3.5`、`5.0`、`7.5`。
- `poles`：单个极数或逗号分隔的批量极数。
- `body_color`：兼容旧命令的主体默认颜色。
- `cover_color`：独立侧盖颜色。
- `spacer_color`：`DA803-7.5` 极间绝缘垫片颜色；未指定时回退到 profile 默认值或侧盖颜色。
- `housing_colors`：Pin 1 到 Pin N 的功能主体颜色。
- `actuator_colors`：Pin 1 到 Pin N 的压杆颜色。
- `terminal_pin_color`：金属焊脚颜色。
- `variant`：输出文件名中的配色/版本描述。

颜色接受内置英文名称或 `#RRGGBB`。逐极颜色列表数量必须为 1 或等于极数；其他数量直接报错。

## Pin 编号

侧盖位于高 X 侧。Pin 1 是最靠近侧盖的一极，Pin N 是远离侧盖的一极。

几何坐标仍从低 X 到高 X 排列；逻辑 Pin `p` 映射到几何索引 `N - p`。这个规则只改变对象命名和颜色映射，不移动侧盖或 PCB 焊脚坐标。

## 几何结构

`DA803-3.5` 和 `DA803-5.0`：

- 每极一个对应 pitch 宽度的功能主体。
- 每极一个后端铰接压杆。
- 每极两根 PCB 焊脚。
- 整体高 X 侧一个 1.5 mm 独立侧盖。
- 总宽为 `N × pitch + 1.5 mm`。

`DA803-7.5`：

- 每极一个 5.0 mm 功能主体，局部结构复用 `DA803-5.0` 的开口、压杆、焊脚和 PCB Y 布局。
- 相邻极之间一个 2.5 mm 极间绝缘垫片，作为独立实体保存。
- 整体高 X 侧一个 1.5 mm 独立侧盖。
- 总宽为 `5.0 × N + 2.5 × (N - 1) + 1.5 = 7.5 × N - 1.0 mm`。

所有间距都不允许用缩放其他间距模型替代真实 profile。

## PCB 坐标

`DA803-3.5`：

```text
X = 2.25 + pole_index × 3.5 mm
Y = 4.60 mm 和 9.60 mm
```

`DA803-5.0`：

```text
X = 3.00 + pole_index × 5.00 mm
Y = 4.60 mm 和 9.60 mm
```

`DA803-7.5`：

```text
X = 3.00 + pole_index × 7.50 mm
Y = 4.60 mm 和 9.60 mm
```

`pole_index` 是低 X 到高 X 的几何索引。逻辑 Pin 编号通过映射函数转换，不改变这些 PCB 坐标。

## 输出命名

标准格式：

```text
<series>-<pitch-code>-<poles>P[-<variant>].FCStd
<series>-<pitch-code>-<poles>P[-<variant>].step
```

示例：

```text
DA803-350-3P-black-blue-green.FCStd
DA803-750-8P-black-gray-gray.step
```

`FCStd` 是可编辑主模型，`STEP` 是交换文件，PNG 只用于外观预览。

## 验证要求

修改生成器、profile 或发布模型后，应使用 FreeCAD 自带 Python 运行测试和验证：

```powershell
& 'D:\destool\FreeCAD\bin\python.exe' -m unittest discover -s '.\DA803\tests' -v
```

单模型验证示例：

```powershell
& '.\DA803\tools\verify_connector.ps1' `
  -Model '.\DA803\generated\DA803-750\DA803-750-8P-black-gray-gray.FCStd' `
  -FreeCADPython 'D:\destool\FreeCAD\bin\python.exe'
```

只有命令退出码为 0 且输出 `VERIFY_OK`，才能声称模型通过验证。
