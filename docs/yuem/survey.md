# 共用测量视图：布设图（二维 / 三维）、曲线、频谱

各方法页面共用的测量布设与数据质量浏览组件。数据描述不依赖 Qt（`PyHydroGeophysX/survey/`），界面在 `PyHydroGeophysX/qt_apps/widgets/survey/`，出版图在 `PyHydroGeophysX/visualization/styles/survey.py`。

## 1. 分层

- **数据描述**（`survey/`）：布设 `SurveyLayout`、拟深度点 `PseudoPoints`、曲线 `TraceSet`、频谱与噪声指标（`spectra.py`）、三维场景 `Scene3D`、页面接口 `SurveyProvider`。只描述“有什么”，可以直接写单元测试。
- **渲染与界面**（`qt_apps/widgets/survey/`）：二维用 pyqtgraph，三维以 PyVista 为主、Matplotlib 为备用；共享选择、选项面板和多选项卡工作台。
- **方法适配**：把方法自己的数据翻译成上述描述，不做计算。DCIP 的适配在插件内（`phgx_dcip/survey_adapter.py`），MT、ERT 的在 `survey/adapters/`。

## 2. 数据约定

- 坐标单位为米，`x` 为东、`y` 为北、`z` 为高程（向上）。经纬度用 `local_projection` 转成本地米制（等距圆柱，与 `mt.station_distances` 一致）。
- 远离测线的点（三极装置的远端 B）标为 `remote`，视图默认把它画在边缘并标注距离。
- 选择键与质控记录（`QCLog`）的键同形，例如 `("shot", 炮号)`、`("trace", 炮号, 仪器序号, 通道码)`，所以任何视图里的选择都能直接剔除。
- 拟深度是显示约定，不是真实深度，约定随数据记录：
  - `pole_dipole_zond`：与 DCIP 插件相同，三极装置取 A 与较近电位电极的中点、深度为两者距离的一半；B 在测线上时取 AB、MN 中点的平均、深度为两中点距离的一半。
  - `pygimli`：与 ERT 页面相同，四个电极的平均位置，深度为电极跨度的 0.19 倍（至少 1 cm）。
- 频谱按时间窗计算（Welch 法，汉宁窗，线性去趋势）。工频取数据自带的值，缺省 50 Hz；高于奈奎斯特频率的谐波按折叠后的位置标出（250 Hz 采样时 150 Hz 出现在 100 Hz）。

## 3. 界面

（随第 2、3 阶段补充：工作台、二维视图、三维视图与备用方案、选项。）

## 4. 方法接入

（随第 4–6 阶段补充：DCIP、MT、ERT。）
