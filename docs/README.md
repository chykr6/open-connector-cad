# 项目文档索引

## 设计说明

- [`design/DA803-3P-design.md`](design/DA803-3P-design.md)：DA803 3P 的尺寸基准、装配结构、颜色和验收标准。

## 实施计划

- [`plans/DA803-3P-implementation.md`](plans/DA803-3P-implementation.md)：参数化生成器、装配树、导出和验证步骤。
- [`plans/connector-generator-implementation.md`](plans/connector-generator-implementation.md)：通用系列、间距、极数和逐极颜色生成器方案。

## 参考资料

- [`../references/DA803/dimension-drawing.png`](../references/DA803/dimension-drawing.png)：DA803 三视图尺寸图。
- [`../references/DA803/product-photo.png`](../references/DA803/product-photo.png)：DA803 产品外观参考。

## 文档维护约定

- 图纸尺寸或装配理解变化时，先更新设计说明，再修改生成器。
- 实施方式或验证命令变化时，同步更新实施计划和根目录 README。
- 文档中不记录 FreeCAD 自动备份文件；可复现信息应写入脚本、设计说明或验证程序。
