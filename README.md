# Parametric FreeCAD Connector Models

使用 FreeCAD Python API 生成参数化端子模型，并导出可编辑的 FCStd 与带颜色的 STEP 文件。

当前已实现：

- DA803，3.50 mm 和 5.00 mm 独立尺寸 profile；
- 任意极数，例如 1P、2P、3P、4P、8P、12P；
- 侧盖、逐极塑料主体、逐极压杆和金属焊脚独立配色；
- 已发布 DA803-350 8P 黑/蓝交替压杆模型；
- 动态装配树和推荐 PCB 焊脚布局验证；
- Windows PowerShell 命令入口。

## 仓库结构

```text
DA_CONNECTOR/
├─ tools/                         通用生成与验证工具
├─ tests/                         参数和 FreeCAD 几何测试
└─ products/
   └─ DA803/
      ├─ README.md                产品说明
      ├─ profiles/                不同间距的真实尺寸配置
      ├─ references/              按型号归档的规格书和产品渲染图
      └─ generated/               FCStd 与 STEP 输出
docs/                             设计说明和实施记录
```

通用代码不保存产品尺寸。DA803-350、DA803-500、DA803-750 必须使用各自图纸对应的 profile，禁止整体缩放替代。

## 环境要求

- FreeCAD 1.0，或兼容的 FreeCAD 0.21；
- Windows PowerShell 5.1 或 PowerShell 7；
- 不需要额外安装 Python 包，脚本使用 FreeCAD 自带 Python。

## 快速开始

设置 FreeCAD 路径：

```powershell
$env:FREECAD_EXE = 'C:\Program Files\FreeCAD 1.0\bin\FreeCAD.exe'
$env:FREECAD_PYTHON = 'C:\Program Files\FreeCAD 1.0\bin\python.exe'
```

如果 FreeCAD 已加入 `PATH`，可以省略 `FREECAD_EXE`。也可以每次通过 `-FreeCADExe` 显式指定。

生成黑色主体、黑/蓝/绿压杆、银色焊脚的 DA803-350 3P：

```powershell
& '.\DA_CONNECTOR\tools\generate_connector.ps1' `
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

批量生成多个极数：

```powershell
& '.\DA_CONNECTOR\tools\generate_connector.ps1' `
  -Series DA803 `
  -Pitch 3.5 `
  -Poles '1,2,4,8' `
  -BodyColor black `
  -ActuatorColors black `
  -TerminalPinColor silver
```

验证模型：

```powershell
& '.\DA_CONNECTOR\tools\verify_connector.ps1' `
  -Model '.\DA_CONNECTOR\products\DA803\generated\DA803-350\DA803-350-3P-black-blue-green.FCStd'
```

运行测试：

```powershell
& $env:FREECAD_PYTHON -m unittest discover -s '.\DA_CONNECTOR\tests' -v
```

## 颜色参数

颜色接受内置英文名称或 `#RRGGBB`：

- `-BodyColor`：兼容旧命令，作为主体和侧盖的默认颜色；
- `-CoverColor`：独立侧盖颜色，省略时回退到 `BodyColor`；
- `-HousingColors`：一个颜色应用全部极，或提供与极数相同的列表；
- `-ActuatorColors`：一个颜色应用全部极，或提供与极数相同的列表；
- `-TerminalPinColor`：PCB 金属焊脚。

主体和压杆颜色列表均按 Pin 1 → Pin N 输入。侧盖位于高 X 侧，因此 Pin 1 是最靠近侧盖、X 坐标最大的一极；列表数量不是 1 或极数时，生成器会终止并报告错误。编号变化不会移动侧盖或 PCB 焊脚坐标。

生成轴测预览：

```powershell
& '.\DA_CONNECTOR\tools\render_connector.ps1' `
  -Model '.\DA_CONNECTOR\products\DA803\generated\DA803-500\DA803-500-2P-black-red.FCStd'
```

## 添加新间距或产品

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。产品尺寸配置和参考资料必须放在对应产品目录，通用工具目录不得包含产品专属尺寸。

DA803 的尺寸、坐标系和现有输出见 [DA803 产品说明](DA_CONNECTOR/products/DA803/README.md)。

## Git 与二进制模型

FCStd 是压缩二进制文件，Git 可以保存和恢复版本，但无法提供有意义的逐行 diff。JSON profile 与 Python 生成器是主要可追溯来源，FCStd 和 STEP 作为已验证的发布快照保存。

## 许可证

本项目采用 [MIT License](LICENSE)。
