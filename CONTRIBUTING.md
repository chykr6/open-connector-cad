# Contributing

感谢参与参数化 FreeCAD 端子模型维护。

## 基本原则

- 图纸尺寸优先于照片比例和经验估算；
- 不同间距使用独立 profile，不按比例缩放其他型号；
- 系列工具不得包含其他系列的固定尺寸；确认多个系列确实共用前，不提前抽根目录通用工具；
- FCStd、STEP 和 profile 必须来自同一次生成；
- 修改几何后必须增加或更新自动测试。
- 逐极主体和压杆颜色列表统一按 Pin 1 → Pin N 输入；Pin 1 位于高 X 侧盖旁，不能通过移动侧盖或 PCB 焊脚来改变编号。

## 新增产品或间距

以官方型号 `DA803-5.0` 为例，仓库内部 profile 和资料目录使用 pitch code `DA803-500`：

1. 创建 `DA803/profiles/DA803-500.json`；
2. 将规格书和渲染图放入 `DA803/references/DA803-500/`；
3. 记录图纸未标尺寸的工程假设；
4. 使用该系列目录下的命令生成至少一个代表性极数；
5. 使用该系列目录下的 `verify_connector.ps1` 验证 FCStd 和 STEP；
6. 更新产品 README 和 DESIGN，说明坐标系、尺寸来源和已知限制。

新增完全不同的产品系列时，在仓库根目录创建 `<series>/`，目录内至少包含 `README.md`、`DESIGN.md`、`profiles/`、`references/`、`generated/`、`tools/` 和 `tests/`。不同品牌或结构明显不同的端子不要混入 DA803，也不要强行复用 DA803 工具。

## 测试

```powershell
& $env:FREECAD_PYTHON -m unittest discover -s '.\DA803\tests' -v
```

测试至少应覆盖：

- profile 解析和输出命名；
- 极数与逐极颜色；
- 本体、侧盖、压杆和焊脚实体有效性；
- 推荐 PCB 焊脚坐标；
- STEP 回读后的实体数量。
- FCStd 装配树的 Pin 方向、Parameters 颜色配置、STEP 配置颜色和行尾空白。

## 文件约定

- 不提交 `__pycache__`、`.FCBak`、日志和临时配置；
- 调试截图在问题关闭后删除；
- 只保留最终图纸、最终轮廓参考和可复现的生成产物；
- 旧实现依靠 Git 历史恢复，不在当前目录维护 `legacy` 副本。

## 提交建议

使用 Conventional Commits，例如：

```text
feat(cad): add DA803-5.0 profile
fix(cad): align DA803 pin layout with footprint
docs: clarify FreeCAD setup
```
