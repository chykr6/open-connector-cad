# Contributing

感谢参与参数化 FreeCAD 端子模型维护。

## 基本原则

- 图纸尺寸优先于照片比例和经验估算；
- 不同间距使用独立 profile，不按比例缩放其他型号；
- 通用生成器不得包含某个产品专属的固定尺寸；
- FCStd、STEP 和 profile 必须来自同一次生成；
- 修改几何后必须增加或更新自动测试。

## 新增产品或间距

以 DA803-500 为例：

1. 创建 `DA_CONNECTOR/products/DA803/profiles/DA803-500.json`；
2. 将规格书和渲染图放入 `DA_CONNECTOR/products/DA803/references/DA803-500/`；
3. 记录图纸未标尺寸的工程假设；
4. 使用通用命令生成至少一个代表性极数；
5. 使用 `verify_connector.ps1` 验证 FCStd 和 STEP；
6. 更新产品 README，说明坐标系、尺寸来源和已知限制。

新增完全不同的产品系列时，创建 `DA_CONNECTOR/products/<series>/`，不要把资料混入 DA803。

## 测试

```powershell
& $env:FREECAD_PYTHON -m unittest discover -s '.\DA_CONNECTOR\tests' -v
```

测试至少应覆盖：

- profile 解析和输出命名；
- 极数与逐极颜色；
- 本体、侧盖、压杆和焊脚实体有效性；
- 推荐 PCB 焊脚坐标；
- STEP 回读后的实体数量。

## 文件约定

- 不提交 `__pycache__`、`.FCBak`、日志和临时配置；
- 调试截图在问题关闭后删除；
- 只保留最终图纸、最终轮廓参考和可复现的生成产物；
- 旧实现依靠 Git 历史恢复，不在当前目录维护 `legacy` 副本。

## 提交建议

使用 Conventional Commits，例如：

```text
feat(cad): add DA803-500 profile
fix(cad): align DA803 pin layout with footprint
docs: clarify FreeCAD setup
```
