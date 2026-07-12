# DA803 Modular Connector

DA803 是可组合的直插式弹簧端子。本目录包含 3.50、5.00、7.50 mm 三种间距的规格书和产品渲染图，以及 3.50 mm 型号的尺寸 profile 和已验证模型。

## 当前支持

- Profile：`DA803-350`
- 极数：由命令参数决定
- 总宽：`N × 3.5 + 1.5 mm`
- 本体深度：`12.5 mm`
- 本体高度：`10.6 mm`
- 侧盖宽度：`1.5 mm`
- 每极两根 PCB 焊脚

5.00 mm 和 7.50 mm 型号已有参考资料，但尚未建立尺寸 profile；后续需要分别增加 `DA803-500.json` 和 `DA803-750.json`，不得按比例缩放 3.50 mm 模型。

## 参考资料

每个型号的正式规格书和产品渲染图独立归档：

- [DA803-350 规格书](references/DA803-350/datasheet.pdf) / [渲染图](references/DA803-350/render.png)
- [DA803-500 规格书](references/DA803-500/datasheet.pdf) / [渲染图](references/DA803-500/render.png)
- [DA803-750 规格书](references/DA803-750/datasheet.pdf) / [渲染图](references/DA803-750/render.png)

规格书是尺寸和推荐 PCB 布局的主要依据，渲染图只用于核对外观，不作为精确尺寸来源。

## 装配结构

每个电气极包含：

- 一个 3.5 mm 塑胶模块；
- 一个后端铰接压杆；
- 两根金属焊脚。

整组端子另外包含一个 1.5 mm 独立侧盖。

## 坐标系与 PCB layout

- X：沿极数增加方向；
- Y：从进线正面指向背面；
- Z：PCB 顶面为 `Z=0`，本体向上，焊脚向下。

推荐焊脚中心：

```text
X = 2.25 + pole_index × 3.5 mm
Y = 4.60 mm 和 9.60 mm
```

其中 `pole_index` 从 0 开始。PCB 推荐孔径为 1.3 mm。

## 压杆轮廓

- 闭合总长约 9.8 mm，厚主体为 2.0 mm；
- 上表面保持水平，并与主体顶部对应平面平齐；
- 压杆厚主体留在顶部通道内，只有前端约 1.6 mm 的底面向上收敛成侧视尖端；
- 尖端越过主体正面约 0.35 mm，形成便于手掰的轻微伸出；
- 压杆下方的主体通道采用斜坡底面，不是简单的平底方槽。

最终轮廓参数已经固化在生成器和 DA803-350 profile 中；历史讨论图不作为正式产品资料保留。

## 外观简化

- 正面进线口采用宽 U 形下腔、窄圆拱顶部和浅入口倒角；
- 外壳和 1.5 mm 侧盖使用相同的前上缘斜面及 0.3 mm 外轮廓圆角；
- 暴露侧面保留六个浅注塑凹点，不建模认证文字和不可见内部弹片；
- 外观尺寸以规格书为准，渲染图仅用于轮廓和比例校核。

## 当前发布模型

- `generated/DA803-350/DA803-350-3P-black-blue-green.FCStd`
- `generated/DA803-350/DA803-350-3P-black-blue-green.step`

配色：黑色主体、从左到右黑/蓝/绿压杆、银色焊脚。

## 生成命令

从仓库根目录执行：

```powershell
& '.\DA_CONNECTOR\tools\generate_connector.ps1' `
  -Series DA803 `
  -Pitch 3.5 `
  -Poles '3' `
  -BodyColor black `
  -ActuatorColors 'black,blue,green' `
  -TerminalPinColor silver `
  -Variant black-blue-green
```
