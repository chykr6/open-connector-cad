# Open Connector CAD

本仓库用于维护参数化连接器和端子 3D 模型。模型以 FreeCAD 脚本生成，输出可编辑的 `FCStd` 和通用交换用 `STEP` 文件。

仓库按产品系列组织。每个系列目录自包含 profile、参考资料、生成产物、工具和测试，避免把不同品牌或结构的端子过早揉成一套通用工具。

## Product Families

- [DA803](DA803/README.md)：地安 DA803 扳手端子系列，支持 `DA803-3.5`、`DA803-5.0`、`DA803-7.5`。

## Repository Layout

```text
<series>/
├─ README.md        系列说明和使用命令
├─ DESIGN.md        建模规范、尺寸假设和验证要求
├─ profiles/        参数化尺寸配置
├─ references/      规格书、渲染图和其他资料
├─ generated/       FCStd、STEP 和预览 PNG
├─ tools/           该系列的生成、渲染、验证工具
└─ tests/           该系列的参数和几何测试
```

新增 DA806、凤凰端子或其他系列时，在仓库根目录创建新的系列目录。只有当多个系列已经验证为同一套流程时，再提取共享工具。

## Environment

- FreeCAD 1.0，或兼容的 FreeCAD 0.21；
- Windows PowerShell 5.1 或 PowerShell 7；
- 不安装全局 Python 依赖；
- 不使用 uv 管理的 Python 执行 FreeCAD 脚本；
- 生成模型使用 FreeCAD 安装目录下的 `bin\FreeCAD.exe`；
- 测试和验证使用 FreeCAD 安装目录下的 `bin\python.exe`。

可以通过环境变量设置 FreeCAD 路径：

```powershell
$env:FREECAD_EXE = 'D:\destool\FreeCAD\bin\FreeCAD.exe'
$env:FREECAD_PYTHON = 'D:\destool\FreeCAD\bin\python.exe'
```

也可以在各系列脚本中通过 `-FreeCADExe` 和 `-FreeCADPython` 显式指定。

## Working With Models

DA803 的生成、验证、颜色参数、Pin 编号和已发布模型见 [DA803 README](DA803/README.md)。

新增系列或维护规范见 [CONTRIBUTING.md](CONTRIBUTING.md)。协作规则见 [AGENTS.md](AGENTS.md)。

## Git And Binary Models

`FCStd` 是可编辑主模型，`STEP` 是交换文件，JSON profile 和生成脚本是主要可追溯来源。FreeCAD 自动生成的 `.FCBak`、Python `__pycache__`、日志和临时文件不进入版本库。

## License

本项目采用 [MIT License](LICENSE)。
