# FreeCAD 3D 零件项目

本仓库用于维护参数化 FreeCAD 零件、PCBA 展示模型以及对应的 STEP 交换文件。

## 当前模型

### DA803 3.5 mm 3P 端子

模型位于 [`DA_CONNECTOR/`](DA_CONNECTOR/)，采用以下装配结构：

- 3 个独立的 3.5 mm 电气模块；
- 1 个独立的 1.5 mm 右侧盖；
- 3 个后端铰接压杆，默认闭合；
- 每极 2 根焊脚，共 6 根；
- 主体默认灰色，压杆默认黑色。

当前实际配色输出：

- [`DA803-350-3P-black-blue-green.FCStd`](DA_CONNECTOR/generated/DA803-350/DA803-350-3P-black-blue-green.FCStd)：黑色主体、黑/蓝/绿压杆的 FreeCAD 模型；
- [`DA803-350-3P-black-blue-green.step`](DA_CONNECTOR/generated/DA803-350/DA803-350-3P-black-blue-green.step)：保留部件颜色的 STEP；
- [`connector_generator.py`](DA_CONNECTOR/connector_generator.py)：通用参数化几何生成器；
- [`generate_connector.ps1`](DA_CONNECTOR/generate_connector.ps1)：推荐的 Windows 命令入口；
- [`connector_verify.py`](DA_CONNECTOR/connector_verify.py)：任意极数的动态验证程序；
- [`profiles/DA803-350.json`](DA_CONNECTOR/profiles/DA803-350.json)：DA803 3.5 mm 图纸尺寸 profile。

## 目录结构

```text
3D/
├─ AGENTS.md                 协作规则和 Git 授权边界
├─ README.md                 项目入口
├─ DA_CONNECTOR/             DA 系列端子工程
├─ docs/
│  ├─ design/                模型设计说明
│  └─ plans/                 实施计划
├─ references/               图纸和产品照片
├─ exports/                  独立或历史导出件
└─ .agents/skills/           项目本地技能
```

`DA_CONNECTOR/legacy/` 保存通用生成器启用前的 3P 专用脚本和模型快照，仅供对照，不作为当前生成入口。

## 生成任意极数和配色

```powershell
& '.\DA_CONNECTOR\generate_connector.ps1' `
  -Series DA803 `
  -Pitch 3.5 `
  -Poles '3' `
  -BodyColor black `
  -ActuatorColors 'black,blue,green' `
  -TerminalPinColor silver `
  -Variant black-blue-green
```

批量生成 1P、2P、4P、8P，统一使用黑色压杆：

```powershell
& '.\DA_CONNECTOR\generate_connector.ps1' `
  -Series DA803 `
  -Pitch 3.5 `
  -Poles '1,2,4,8' `
  -BodyColor black `
  -ActuatorColors black `
  -TerminalPinColor silver
```

颜色参数支持英文颜色名或 `#RRGGBB`。压杆颜色只给一个值时应用到全部极；给多个值时必须与极数一致，并按从左到右的顺序应用。

生成后运行验证：

```powershell
& 'D:\destool\FreeCAD\bin\python.exe' `
  '.\DA_CONNECTOR\connector_verify.py' `
  '.\DA_CONNECTOR\generated\DA803-350\DA803-350-3P-black-blue-green.FCStd'
```

## 间距 profile

DA803-350、DA803-500、DA803-750 使用不同尺寸 profile。当前只有完成图纸确认的 `DA803-350.json`；取得 5.0 mm、7.5 mm 图纸后分别增加 profile，不修改或复制通用 Python 几何入口。

详细设计资料见 [`docs/README.md`](docs/README.md)。

## Git 说明

`FCStd` 可以被 Git 保存和恢复，但属于压缩二进制文件，不适合逐行比较。参数化 Python 脚本是主要追溯来源，FCStd、STEP 和预览图作为对应版本的模型快照保留。

任何 Git 暂存、提交或推送操作都必须由用户明确提出，具体规则见 [`AGENTS.md`](AGENTS.md)。
