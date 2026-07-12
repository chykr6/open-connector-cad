# DA803 引脚编号、逐极配色与 5.00 mm 型号实施计划

**目标：** 在保持现有几何与 PCB 坐标的前提下统一逻辑 Pin 方向，扩展逐极主体配色，建立 DA803-500 独立 profile，并交付六套已验证模型和三张预览。

**架构：** 通用生成器增加逻辑 Pin 到几何索引的单一映射函数，颜色参数先解析为规范化列表，再传入装配创建和 Parameters。不同间距的尺寸全部由独立 JSON profile 驱动，验证器从 FCStd/STEP 回读结构、坐标和颜色。

**技术栈：** FreeCAD Python API、Python `unittest`、PowerShell、JSON、STEP。

## 全局约束

- 不改变侧盖位置或现有 DA803-350 PCB 焊脚坐标。
- 颜色列表顺序始终为 Pin 1（靠近侧盖）到 Pin N（远离侧盖）。
- 不执行 `git add`、`git commit`、`git push` 或其他 Git 写操作。
- 生产代码修改前必须存在对应失败测试并确认失败原因正确。

### 任务 1：编号与颜色解析

- [x] 在 `DA_CONNECTOR/tests/test_connector_generator.py` 添加逻辑 Pin 反向映射、主体/压杆单色展开、错误数量拒绝和旧 BodyColor 回退测试。
- [x] 单独运行新增测试，确认因接口或行为缺失而失败。
- [x] 在 `DA_CONNECTOR/tools/connector_generator.py` 实现通用颜色展开、颜色默认值解析和 `pin_to_geometry_index(poles, pin_number)`。
- [x] 运行参数测试并确认通过。

### 任务 2：FCStd 装配与命令接口

- [x] 添加每极主体/压杆颜色、独立侧盖颜色、Pole_1 位于高 X、350 PCB 坐标不变和动态零件数测试。
- [x] 运行测试并确认预期失败。
- [x] 修改 Python CLI、环境请求转换和 `generate_connector.ps1` 参数；更新装配循环和 Parameters 属性。
- [x] 运行集成测试并确认通过。

### 任务 3：DA803-500 profile

- [x] 将规格书页面渲染为临时 PNG，并结合文本/视觉读取主体、侧盖、焊脚和 PCB layout 尺寸。
- [x] 添加 500 profile 加载、总宽、Pin 1 坐标及 PCB layout 测试并确认失败。
- [x] 创建 `DA_CONNECTOR/products/DA803/profiles/DA803-500.json`，明确图纸尺寸和外观工程假设。
- [x] 运行 profile 与几何测试并确认通过。

### 任务 4：验证器

- [x] 添加或扩展验证测试，覆盖 Parameters、装配树逻辑编号、每极颜色、实体数量、宽度、PCB 坐标、STEP 实体/颜色回读和行尾空白。
- [x] 确认新增验证在旧行为或不合格样本上失败。
- [x] 修改 `DA_CONNECTOR/tools/connector_verify.py` 和 PowerShell 入口所需参数。
- [x] 运行验证器相关测试并确认通过。

### 任务 5：生成、渲染与文档

- [x] 生成两个彩色 4P、全黑 4P/8P/12P 和黑红 500-2P 的 FCStd/STEP，确保输出名不重叠。
- [x] 对六个 FCStd/STEP 分别运行 `verify_connector.ps1`，要求退出码 0 且输出 `VERIFY_OK`。
- [x] 渲染两个彩色 350-4P 和 500-2P 轴测 PNG，人工检查颜色方向和外观。
- [x] 更新根 README、DA803 README、CONTRIBUTING 和必要设计说明。
- [x] 删除 `tmp/`、`.FCBak`、`__pycache__` 等临时文件。
- [x] 运行全量单元测试、逐模型验证、STEP 行尾检查和 `git status --short --branch`，逐项审计需求。
