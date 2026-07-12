# 通用端子生成器设计

## 设计目标

同一套命令和 Python 几何逻辑生成不同系列、间距、极数和配色的端子模型。不同间距的真实图纸尺寸由独立 profile 提供，不通过整体缩放推导。

## 输入模型

- `series`：产品系列，例如 `DA803`。
- `pitch`：极间距，例如 `3.5`、`5.0`、`7.5`。
- `poles`：单个极数或逗号分隔的批量极数，例如 `1,2,4,8`。
- `body_color`：全部电气模块和侧盖的颜色。
- `actuator_colors`：顶部塑料压杆颜色；一个值表示全部相同，多个值按从左到右逐极对应。
- `terminal_pin_color`：底部金属焊脚颜色。
- `variant`：可选配色名称，用于防止不同配色文件互相覆盖。

## Profile 边界

`profiles/<series>-<pitch-code>.json` 保存深度、高度、侧盖宽度、孔位、焊脚尺寸、压杆尺寸和默认颜色。DA803-500 与 DA803-750 在取得各自图纸后添加独立 profile；通用生成器不假定它们与 DA803-350 成比例。

## 输出命名

标准格式：

```text
<series>-<pitch-code>-<poles>P[-<variant>].FCStd
<series>-<pitch-code>-<poles>P[-<variant>].step
```

示例：

```text
DA803-350-3P-black-blue-green.FCStd
DA803-350-3P-black-blue-green.step
```

## 颜色规则

颜色接受内置英文名称或 `#RRGGBB`。每个部件同时保存 `ConfiguredColor` 元数据；FCStd 保存实际视图颜色，STEP 使用 FreeCAD GUI 导出并包含颜色记录。颜色数量错误时终止生成，不静默截断或循环填充。

