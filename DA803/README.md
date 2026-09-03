# DA803 地安扳手端子系列

DA803 是地安的可组合直插式扳手端子系列。官方型号按间距标为 `DA803-3.5`、`DA803-5.0`、`DA803-7.5`；仓库内部文件和目录使用无小数点的 pitch code：`DA803-350`、`DA803-500`、`DA803-750`。

本目录包含 3.50、5.00、7.50 mm 三种间距的规格书和产品渲染图，以及独立尺寸 profile 和已验证模型。

详细建模规则、Pin 编号、内部命名和验证要求见 [DESIGN.md](DESIGN.md)。

## 当前支持

- 官方型号：`DA803-3.5`、`DA803-5.0`、`DA803-7.5`
- 内部 profile：`DA803-350`、`DA803-500`、`DA803-750`
- 极数：由命令参数决定
- `DA803-3.5` / `DA803-5.0` 总宽：`N × pitch + 1.5 mm`
- `DA803-7.5` 总宽：`7.50 × N - 1.00 mm`
- 本体深度：`12.5 mm`
- 本体高度：`10.6 mm`
- 侧盖宽度：`1.5 mm`
- 每极两根 PCB 焊脚

`DA803-5.0` 图纸尺寸：间距 5.00 mm，总宽 `N × 5.00 + 1.50 mm`，本体深度 12.50 mm，本体高度 10.60 mm，侧盖宽度 1.50 mm，焊脚长 3.00 mm、截面 0.80 × 0.50 mm，推荐孔径 Ø1.30 mm。

`DA803-7.5` 图纸尺寸：间距 7.50 mm，总宽 `7.50 × N - 1.00 mm`，本体深度 12.50 mm，本体高度 10.60 mm，侧盖宽度 1.50 mm，焊脚长 3.00 mm、截面 0.80 × 0.50 mm，推荐孔径 Ø1.30 mm。建模时按 `5.00 mm` 功能主体、`2.50 mm` 极间绝缘垫片和 `1.50 mm` 侧盖组合，得到 `5.00 × N + 2.50 × (N - 1) + 1.50 = 7.50 × N - 1.00`。

## 参考资料

每个型号的正式规格书和产品渲染图独立归档：

- [`DA803-3.5` 规格书](references/DA803-350/datasheet.pdf) / [渲染图](references/DA803-350/render.png)
- [`DA803-5.0` 规格书](references/DA803-500/datasheet.pdf) / [渲染图](references/DA803-500/render.png)
- [`DA803-7.5` 规格书](references/DA803-750/datasheet.pdf) / [渲染图](references/DA803-750/render.png)

规格书是尺寸和推荐 PCB 布局的主要依据，渲染图只用于核对外观，不作为精确尺寸来源。

## 装配结构

`DA803-3.5` / `DA803-5.0` 每个电气极包含：

- 一个对应间距宽度的塑胶电气模块；
- 一个后端铰接压杆；
- 两根金属焊脚。

`DA803-7.5` 每个电气极包含一个 5.0 mm 功能主体、一个后端铰接压杆和两根金属焊脚；相邻极之间增加 2.5 mm 灰色绝缘垫片并作为独立实体保存。整组端子另外包含一个 1.5 mm 独立侧盖。

## 坐标系与 PCB layout

- X：从无侧盖的低 X 侧指向高 X 侧盖；
- Y：从进线正面指向背面；
- Z：PCB 顶面为 `Z=0`，本体向上，焊脚向下。

逻辑编号从侧盖向外：Pin 1 是高 X 侧最靠近 1.5 mm 侧盖的一极，然后依次为 Pin 2 到 Pin N。装配树中的 `Pole_1`、`Housing_P1`、`Actuator_P1`、`Pin_P1_A` 和 `Pin_P1_B` 均遵循此方向。颜色列表也始终按 Pin 1 → Pin N 输入。

`DA803-3.5` 推荐焊脚几何列中心（低 X 到高 X）：

```text
X = 2.25 + pole_index × 3.5 mm
Y = 4.60 mm 和 9.60 mm
```

其中 `pole_index` 是几何索引，从低 X 的 0 开始。逻辑 Pin `p` 对应几何索引 `N-p`；PCB 推荐孔径为 1.3 mm。原 `DA803-3.5` PCB 坐标没有因逻辑编号调整而移动。

`DA803-5.0` 推荐焊脚几何列中心：

```text
X = 3.00 + pole_index × 5.00 mm
Y = 4.60 mm 和 9.60 mm
```

图纸中的 2.90 mm 是后排孔中心到后边缘的距离，因此模型坐标为 `12.50 - 2.90 = 9.60 mm`；前排再减去 5.00 mm 排距，得到 4.60 mm。推荐孔径为 1.30 mm。上述尺寸来自 `DA803-5.0` 规格书；未标注的开口圆弧、压杆宽度、顶部通道和浅凹点参数为结合对应渲染图确定的独立外观假设，并记录在 `profiles/DA803-500.json` 中。

`DA803-7.5` 推荐焊脚几何列中心：

```text
X = 3.00 + pole_index × 7.50 mm
Y = 4.60 mm 和 9.60 mm
```

`DA803-7.5` 的 5.0 mm 功能主体沿用 `DA803-5.0` 的开口、压杆和焊脚局部结构；2.5 mm 极间垫片只用于拉开绝缘距离，不移动焊脚在功能主体内的局部位置。

## 压杆轮廓

- 闭合总长约 9.8 mm，厚主体为 2.0 mm；
- 上表面保持水平，并与主体顶部对应平面平齐；
- 压杆厚主体留在顶部通道内，只有前端约 1.6 mm 的底面向上收敛成侧视尖端；
- 尖端越过主体正面约 0.35 mm，形成便于手掰的轻微伸出；
- 压杆下方的主体通道采用斜坡底面，不是简单的平底方槽。

最终轮廓参数已经固化在生成器和 `DA803-3.5` profile 中；历史讨论图不作为正式产品资料保留。

## 外观简化

- 正面进线口采用宽 U 形下腔、窄圆拱顶部和浅入口倒角；
- 外壳和 1.5 mm 侧盖使用相同的前上缘斜面及 0.3 mm 外轮廓圆角；
- 暴露侧面保留六个浅注塑凹点，不建模认证文字和不可见内部弹片；
- 外观尺寸以规格书为准，渲染图仅用于轮廓和比例校核。

## 当前发布模型

- `generated/DA803-350/DA803-350-3P-black-blue-green.FCStd`
- `generated/DA803-350/DA803-350-3P-black-blue-green.step`
- `generated/DA803-350/DA803-350-4P-red-green-blue-black.FCStd/.step/.png`
- `generated/DA803-350/DA803-350-4P-black-blue-green-red.FCStd/.step/.png`（4P；主体全黑，压杆 Pin 1 → Pin 4 为黑/蓝/绿/红）
- `generated/DA803-350/DA803-350-4P-all-black.FCStd/.step`
- `generated/DA803-350/DA803-350-8P-all-black.FCStd/.step`
- `generated/DA803-350/DA803-350-8P-black-blue-black-blue-black-blue-black-blue.FCStd/.step`
- `generated/DA803-350/DA803-350-12P-all-black.FCStd/.step`
- `generated/DA803-500/DA803-500-2P-black-red.FCStd/.step/.png`
- `generated/DA803-750/DA803-750-8P-black-gray-gray.FCStd/.step`
- `generated/DA803-750/DA803-750-8P-black-gray-gray-gray-gray-gray-black-black-black-red.FCStd/.step`

所有新模型均使用银色金属焊脚；文件名中的多色顺序按 Pin 1（靠近侧盖）→ Pin N（远离侧盖）。

## 生成命令

从仓库根目录执行：

```powershell
& '.\DA803\tools\generate_connector.ps1' `
  -Series DA803 `
  -Pitch 3.5 `
  -Poles '3' `
  -BodyColor black `
  -CoverColor black `
  -HousingColors black `
  -ActuatorColors 'black,blue,green' `
  -TerminalPinColor silver `
  -Variant black-blue-green
```

生成 `DA803-3.5` 主体全黑、压杆按 Pin 1 → Pin 4 为黑/蓝/绿/红的 4P：

```powershell
& '.\DA803\tools\generate_connector.ps1' `
  -Series DA803 `
  -Pitch 3.5 `
  -Poles '4' `
  -BodyColor black `
  -CoverColor black `
  -HousingColors black `
  -ActuatorColors 'black,blue,green,red' `
  -TerminalPinColor silver `
  -Variant black-blue-green-red `
  -FreeCADExe 'D:\destool\FreeCAD\bin\FreeCAD.exe'
```

生成 `DA803-5.0` 黑/红 2P：

```powershell
& '.\DA803\tools\generate_connector.ps1' `
  -Series DA803 `
  -Pitch 5.0 `
  -Poles '2' `
  -BodyColor black `
  -CoverColor black `
  -HousingColors 'black,red' `
  -ActuatorColors 'black,red' `
  -TerminalPinColor silver `
  -Variant black-red
```

生成 `DA803-3.5` 8P 黑/蓝交替：

```powershell
& '.\DA803\tools\generate_connector.ps1' `
  -Series DA803 `
  -Pitch 3.5 `
  -Poles '8' `
  -BodyColor black `
  -CoverColor black `
  -HousingColors black `
  -ActuatorColors 'black,blue,black,blue,black,blue,black,blue' `
  -TerminalPinColor silver `
  -Variant black-blue-black-blue-black-blue-black-blue `
  -FreeCADExe 'D:\destool\FreeCAD\bin\FreeCAD.exe'
```

生成 `DA803-7.5` 黑色主体、偏白灰间隔、黑色侧盖、偏白灰压杆 8P：

```powershell
& '.\DA803\tools\generate_connector.ps1' `
  -Series DA803 `
  -Pitch 7.5 `
  -Poles '8' `
  -BodyColor black `
  -CoverColor black `
  -SpacerColor '#D9D9D9' `
  -HousingColors black `
  -ActuatorColors '#D9D9D9' `
  -TerminalPinColor silver `
  -Variant black-gray-gray `
  -FreeCADExe 'D:\destool\FreeCAD\bin\FreeCAD.exe'
```

生成 `DA803-7.5` 黑色主体、偏白灰间隔、黑色侧盖、Pin 1 → Pin 8 压杆为偏白灰/偏白灰/偏白灰/偏白灰/黑/黑/黑/红的 8P：

```powershell
& '.\DA803\tools\generate_connector.ps1' `
  -Series DA803 `
  -Pitch 7.5 `
  -Poles '8' `
  -BodyColor black `
  -CoverColor black `
  -SpacerColor '#D9D9D9' `
  -HousingColors black `
  -ActuatorColors '#D9D9D9,#D9D9D9,#D9D9D9,#D9D9D9,black,black,black,red' `
  -TerminalPinColor silver `
  -Variant black-gray-gray-gray-gray-gray-black-black-black-red `
  -FreeCADExe 'D:\destool\FreeCAD\bin\FreeCAD.exe'
```
