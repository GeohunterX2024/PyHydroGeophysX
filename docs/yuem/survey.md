# 共用测量视图：布设图（二维 / 三维）、曲线、频谱

各方法页面共用的测量布设与数据质量浏览组件。数据描述不依赖 Qt（`PyHydroGeophysX/survey/`），界面在 `PyHydroGeophysX/qt_apps/widgets/survey/`，出版图在 `PyHydroGeophysX/visualization/styles/survey.py`。目前接入的有 DCIP 插件的“炮记录”、MT 的“测站与数据质量”和 ERT 的“测量布设”。

## 1. 分层

```
方法适配            DCIP（插件 phgx_dcip/survey_adapter.py）· MT（survey/adapters/mt.py）· ERT（survey/adapters/ert.py）
                        │  把方法自己的数据翻译成通用描述，不做计算
数据描述（无 Qt）    survey/layout.py · pseudo.py · traces.py · spectra.py · scene.py · provider.py · attributes.py
                        │
界面（Qt）          widgets/survey/ 平面图 · 剖面图 · 曲线 · 频谱 · 三维（PyVista / Matplotlib）· 共享选择 · 工作台
出版图              visualization/styles/survey.py（Matplotlib，PDF / PNG / SVG）
```

- **数据描述**只说明“有什么”：布设 `SurveyLayout`（点、连线、地形、测线方向、坐标系）、拟深度点 `PseudoPoints`、曲线 `TraceSet`（含时间窗 `Window`）、频谱与噪声指标、三维场景 `Scene3D`。它属于算法层，导入约束禁止它引用 Qt，并按 `mypy --strict` 检查。
- **界面**只读数据描述。二维、三维、PyVista、Matplotlib 画的是同一份内容。
- **方法适配**只做转换，数值与页面原有的显示一致（由测试逐元素比对）。

## 2. 数据约定

- **坐标**：单位为米，`x` 为东、`y` 为北、`z` 为高程（向上）。经纬度用 `local_projection` 转成本地米制（等距圆柱投影，与 `mt.station_distances` 一致）。沿测线距离可由适配直接给出（DCIP 取北坐标，与测量表一致；ERT 取传感器第一坐标，与拟断面一致），否则按测点的主方向（`LineFrame.fit`）计算。
- **点的角色**：`A`、`B`、`M`、`N`、`electrode`、`site`、`tx`、`rx`。远离测线的点（三极装置的远端 B）标为 `remote`，视图默认画在边缘并标注距离。
- **分组**：一炮、一个注入电极对或一个测站是一个组。当前组的供电点和偶极高亮，其他组的供电点淡化；`site`、`rx` 不论分组始终显示。
- **选择键**：与质控记录（`QCLog`）的键同形，例如 `("shot", 炮号)`、`("trace", 炮号, 仪器序号, 通道码)`、`("reading", 行号)`，所以任何视图里框选的对象都能交给页面的质控栏。
- **着色值**：共用名称见 `survey/attributes.py`（视电阻率、视极化率、装置系数、是否剔除、误差、工频峰值、噪声均方根、信噪比、高程、电流、一次场电压），界面会翻译并按需取对数刻度。方法也可以用自己的名称，按原文显示。
- **拟深度**是显示约定，不是真实深度，约定随数据记录，图例中写明：
  - `pole_dipole_zond`：与 DCIP 插件相同。三极装置取 A 与较近电位电极的中点，深度为两者距离的一半；B 在测线上时取 AB、MN 中点的平均，深度为两中点距离的一半。
  - `pygimli`：与 ERT 页面相同。取四个电极的平均位置，深度为电极跨度的 0.19 倍（至少 1 cm）。
- **频谱**按时间窗计算（Welch 法，汉宁窗，线性去趋势，分段约为记录的四分之一）。工频取数据自带的值，缺省 50 Hz，可选 60 Hz。高于奈奎斯特频率的谐波按折叠后的位置标出：250 Hz 采样时，150 Hz 出现在 100 Hz，200 Hz 出现在 50 Hz。
- **噪声指标**（每个通道）：
  - 工频峰值：工频处相对宽带噪声底的 dB。
  - 噪声底：谐波以外功率谱的中位数。
  - 噪声均方根：噪声窗内线性去趋势后的均方根。
  - 信噪比：信号窗与噪声窗中位数之差，相对于噪声均方根，单位 dB。

## 3. 界面

`SurveyWorkbench` 是右侧绘图区，页面自己的列表、摘要和质控栏留在页面上。工作台按页面提供的能力（`survey_capabilities`）显示子选项卡，只绘制当前可见的一个。

- **布设图 · 二维**：上方平面图，下方剖面图。
  - 平面图按真实坐标、等比例显示，可按点的数值着色。它显示当前组的连线和其他组淡化的供电点；远端点用边缘箭头标距离，勾选“包含远端 B”则按实际位置显示，并会缩放平面图。
  - 剖面图显示地形、电极和拟深度点（画在“地表高程减拟深度”处），可着色、可选对数刻度，当前组的点有圈标。
  - 两张图都可以“框选”。“锁定范围”用于在两条测线之间统一色标。
- **布设图 · 三维**：
  - 图层：地形面（有网格用曲面，否则为沿测线的带状面）、按角色区分形状的电极、当前组的 AB 与 MN 连线、远端 B 标记与距离、拟深度点云、标签。
  - 右侧“三维选项”可收起，内含：图层开关、着色依据与色标、纵向夸大、点大小、最大拟深度、相机预设（俯视、沿测线、垂直测线、斜视）、平行投影、测距、截图、导出 VTK（`.vtm`，可用 ParaView 打开）。
  - 右键点选（简易三维中为单击）会选中对应的组和对象。
- **曲线**：多通道叠加，参考曲线（如供电电流）在右纵轴；时间窗浅色标出，“窗口”可缩放到指定时间窗。长记录按峰值抽稀并只绘制可见部分。
- **频谱**：功率谱用对数纵轴，标出工频及谐波（虚线为折叠位置），可叠加参考曲线的频谱；下方噪声指标表可按列排序。
- **导出图件**：工作台右上角可导出平面图、剖面图、曲线图、频谱图，格式为 PDF、PNG 或 SVG，使用 `visualization/styles` 的出版图式。
- **记住的设置**：各视图的选择按方法分别存在 Studio 设置的 `survey/<方法>/…` 下。

### 三维后端与备用方案

- 优先用 PyVista。遇到下列任一情况时自动改用 Matplotlib 三维（“简易三维”），图下方会写明原因：
  - 没有安装 PyVista；
  - 运行在无显示的 offscreen 环境（测试即如此）；
  - 三维窗口创建失败；
  - 设置了环境变量 `PHGX_SURVEY_3D=simple`；
  - 在选项中勾选了“使用简易三维（不需要显卡）”。
- 简易三维画同样的图层，但没有测距和 VTK 导出，这两个按钮会置灰并说明原因。
- 没有显卡驱动时 VTK 可能直接让程序退出，Python 无法拦截。遇到这种情况，设置 `PHGX_SURVEY_3D=simple` 再启动即可。`phgx-doctor` 的 “Survey 3D view” 一项会报告当前用的是哪种三维。
- VTK 自带字体没有中文，三维中的色标标题和坐标轴改用 Matplotlib 找到的中文字体文件。

## 4. 方法接入

适配实现 `SurveyProvider` 协议（`survey/provider.py`）：

```python
class MySurvey:
    def survey_capabilities(self) -> frozenset[str]: ...   # {"layout", "pseudo", "traces", "spectrum"} 的子集
    def survey_layout(self) -> SurveyLayout | None: ...
    def survey_pseudo(self) -> PseudoPoints | None: ...
    def survey_traces(self, group: str, channels: Sequence[str]) -> TraceSet | None: ...
```

页面这样用：

```python
from PyHydroGeophysX.qt_apps.widgets import colormaps as cmaps
from PyHydroGeophysX.qt_apps.widgets.survey import SurveyWorkbench

bench = SurveyWorkbench(colormaps=cmaps.colormap_settings(page.state), settings_key="mymethod")
bench.set_provider(MySurvey(...))
bench.selection.set_group(group)          # 页面列表选中一组
bench.set_channels(names)                 # 选中的通道
bench.selection.keysChanged.connect(...)  # 视图中框选或点选的对象
```

### 已接入的方法

- **DCIP**（插件“炮记录”）：
  - A、B、M、N 取自 LAS 表头，`x` 为东、`y` 为北，沿测线距离为北坐标。远端 B 来自 `geometry["remote_b"]`。LAS 中的高程为 0，因此按测线地形插值。
  - 拟深度点直接取 `viewdata.measurements` 的位置。
  - 曲线为所选测道加供电电流，时间窗为全段、供电段（平稳）、供电段末、断电段、断电段后段和门。
  - 平面图或三维中点选的炮会同步选中炮表；框选的测量交给质控栏。
  - 原“测点地图”选项卡已并入；助手的 `show_tab map` 改为打开布设图。
- **MT**（“测站与数据质量”选项卡）：
  - 测站来自传递函数和记录的经纬度；记录的 Ex、Ey 偶极由通道的方位和长度画出，以测站为中心。
  - 曲线为所选记录的各通道，可切换到场值单位（mV/km、nT）。时间窗为全段、第一分钟和最后一分钟；工频按记录自动识别。
  - 原有“时间序列”页不变。
- **ERT**（“测量布设”选项卡）：
  - 电极取自 pyGIMLi 数据容器的传感器坐标。二维测线的第二坐标是高程。
  - 每个 A-B 注入电极对是一组，可在左侧列表中选择。
  - 拟深度点与 ERT 拟断面相同（`pygimli` 约定），可按视电阻率、误差、装置系数和有效性着色。
  - 剔除读数仍在“数据”选项卡中进行。

### 以后可以接入

- 反演结果幕帘：`scene.py` 已定义 `CurtainLayer`，尚未绘制。
- 多测线的工程级三维总览、三维地形贴底图。
- EM、地震、GPR 的适配。

## 5. 测试

- `tests/yuem/survey/`：
  - 数据描述与适配：拟深度与 DCIP、`ert_io` 逐元素一致；投影与 `station_distances` 一致；谐波折叠与 Welch 峰值；噪声指标；三维场景图层。
  - 出版图：中文与英文、PDF 与 PNG。
- `tests/yuem/gui/test_survey_views.py`：工作台的能力与选项卡、框选与点选、曲线与频谱、简易三维的回退与点选、选项保存、导出图件、中文界面构建。测试中的设置只存在内存里，不写入用户的 Studio 设置。
- `tests/yuem/gui/test_survey_pyvista.py`：场景转为 PyVista 数据集与 VTK 导出，不需要窗口。
- 插件：`tests/unit/test_survey_adapter.py`，以及 `tests/gui/test_page.py`、`test_page_flow.py`。
