# 3D 零件项目协作规则

本文件适用于仓库根目录及其全部子目录。

## 最高优先级：Git 操作授权

- 未经用户在当前对话中明确要求，不得执行任何会改变 Git 状态或历史的操作。
- 禁止自行执行 `git add`、`git commit`、`git push`、`git tag`、`git merge`、`git rebase`、`git cherry-pick`、创建或删除分支，以及其他 Git 写操作。
- 可以执行只读检查，例如 `git status`、`git diff`、`git log`、`git show` 和 `git ls-files`。
- 完成文件修改后，仅报告工作区状态和建议的提交说明；等待用户明确说“提交”“commit”或给出等价指令后，才能暂存或提交。

## 项目目标

- 本仓库用于 FreeCAD 参数化零件设计、PCBA 展示模型和通用 STEP 交换文件管理。
- 当前主要零件为 DA803 3.5 mm 间距模块化端子。
- 模型侧重外观、安装尺寸和 PCBA 展示，不要求不可见的内部弹片结构。

## 目录约定

- `DA_CONNECTOR/`：DA 系列端子模型、生成脚本、验证脚本和对应导出文件。
- `references/`：尺寸图、产品照片及其他建模参考资料。
- `exports/`：不属于具体零件工程目录的独立导出件和历史交换文件。
- `docs/design/`：确认过的模型设计说明和尺寸假设。
- `docs/plans/`：实施计划和建模步骤记录。
- `.agents/skills/`：项目本地技能；依赖必须安装在仓库内，不得全局安装。

## FreeCAD 建模规则

- 优先维护参数化生成脚本；不要只修改二进制 `FCStd` 而不保留可追溯的参数来源。
- `FCStd` 是可编辑主模型，`STEP` 是交换文件，预览 PNG 用于快速外观检查。
- 图纸明确标注的尺寸优先于照片比例；估算尺寸必须记录在设计文档或脚本参数中。
- 模块化端子应将电气模块、侧盖、压杆和焊脚作为独立装配实体保存。
- 修改生成器后，应重新生成 FCStd、STEP 和预览图，并运行验证脚本。

## 验证要求

DA803 3P 模型的标准验证命令：

```powershell
$env:DA803_DIR='E:\.proj\3D\DA_CONNECTOR'
& 'D:\destool\FreeCAD\bin\FreeCADCmd.exe' -c "p=r'E:\.proj\3D\DA_CONNECTOR\verify_da803_3p.py'; exec(compile(open(p,encoding='utf-8').read(),p,'exec'),{'__name__':'__main__','__file__':p})"
```

只有在命令退出码为 0，并输出 `VERIFY_OK` 后，才能声称模型通过验证。

## 文件保护

- 保留用户已有模型和不相关修改，不得擅自覆盖或删除。
- FreeCAD 自动生成的 `.FCBak` 和 Python `__pycache__` 不进入版本库。
- 移动或重命名文件时同步更新 README、设计文档和脚本中的路径引用。

