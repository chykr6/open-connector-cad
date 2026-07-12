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

主要输出：

- [`DA803-350-3P.FCStd`](DA_CONNECTOR/DA803-350-3P.FCStd)：FreeCAD 可编辑主模型；
- [`DA803-350-3P.step`](DA_CONNECTOR/DA803-350-3P.step)：供 ECAD、MCAD 和 PCBA 展示使用的交换模型；
- [`DA803-350-3P-preview.png`](DA_CONNECTOR/DA803-350-3P-preview.png)：当前模型预览；
- [`build_da803_3p.py`](DA_CONNECTOR/build_da803_3p.py)：参数化模型生成器；
- [`verify_da803_3p.py`](DA_CONNECTOR/verify_da803_3p.py)：尺寸、实体数量及 STEP 回读验证。

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

## 重新生成 DA803 3P

```powershell
$env:DA803_DIR='E:\.proj\3D\DA_CONNECTOR'
& 'D:\destool\FreeCAD\bin\FreeCADCmd.exe' -c "p=r'E:\.proj\3D\DA_CONNECTOR\build_da803_3p.py'; exec(compile(open(p,encoding='utf-8').read(),p,'exec'),{'__name__':'__main__','__file__':p})"
```

生成后运行验证：

```powershell
& 'D:\destool\FreeCAD\bin\FreeCADCmd.exe' -c "p=r'E:\.proj\3D\DA_CONNECTOR\verify_da803_3p.py'; exec(compile(open(p,encoding='utf-8').read(),p,'exec'),{'__name__':'__main__','__file__':p})"
```

生成预览：

```powershell
& 'D:\destool\FreeCAD\bin\freecad.exe' 'E:\.proj\3D\DA_CONNECTOR\render_da803_preview.py'
```

## 参数调整

DA803 的尺寸与默认颜色集中在 `build_da803_3p.py` 顶部的 `PARAMS` 中。修改后应同时重新生成 FCStd、STEP 和预览图，并执行验证脚本。

详细设计资料见 [`docs/README.md`](docs/README.md)。

## Git 说明

`FCStd` 可以被 Git 保存和恢复，但属于压缩二进制文件，不适合逐行比较。参数化 Python 脚本是主要追溯来源，FCStd、STEP 和预览图作为对应版本的模型快照保留。

任何 Git 暂存、提交或推送操作都必须由用户明确提出，具体规则见 [`AGENTS.md`](AGENTS.md)。

