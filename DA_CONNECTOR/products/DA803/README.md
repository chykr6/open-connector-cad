# DA803 Modular Connector

DA803 是可组合的直插式弹簧端子。本目录包含 3.50 mm 间距型号的尺寸 profile、参考资料和已验证模型。

## 当前支持

- Profile：`DA803-350`
- 极数：由命令参数决定
- 总宽：`N × 3.5 + 1.5 mm`
- 本体深度：`12.5 mm`
- 本体高度：`10.6 mm`
- 侧盖宽度：`1.5 mm`
- 每极两根 PCB 焊脚

5.00 mm 和 7.50 mm 型号需要各自图纸，后续分别增加 `DA803-500.json` 和 `DA803-750.json`。

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

- 长条主体厚度：2.0 mm；
- 上表面保持水平；
- 前端绿色区域从矩形毛坯切除；
- 底面通过直线斜边收敛到上方尖点；
- 尖点位于主体最前缘内约 0.10 mm。

最终轮廓参考位于 `references/actuator-tip-profile.png` 和 `references/actuator-thickness-profile.png`。

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

