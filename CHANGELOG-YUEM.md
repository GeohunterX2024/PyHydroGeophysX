# YUEM 分叉变更记录

本文件只记录 YUEM 软分叉相对上游 PyHydroGeophysX 的改动；上游自身的变更见 `CHANGELOG.md`。
格式参照 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号形如 `0.5.0+yuem.N`。

## [Unreleased]

### 治理

- 建立软分叉：基点 `16930bb`，`upstream` 与 `yuem/main` 双分支，上游推送地址禁用。基点核对记录 `.yuem/baseline_diff.md`。
- 新增代码归属清单 `.yuem/ownership.toml`、补丁台账 `.yuem/PATCHES.md`、同步日志 `.yuem/SYNC_LOG.md`。
- 新增架构决策记录 ADR 0001（软分叉）、0002（uv 与 conda-lock 工具链）、0003（质量门禁与棘轮）。
- 新增中文开发指南 `docs/yuem/README.md`。
- `.gitignore` 放行分叉的 Markdown 治理文档（台账 P-0001）。

### 工具链与环境

- 版本号改为 `0.5.0+yuem.1`（台账 P-0002、P-0003）。
- 新增 ruff、pytest、mypy、coverage 配置；全仓库沿用现有代码零告警的规则 `E9,F63,F7,W6`，严格路径（`.yuem/ownership.toml` 的 `[quality]`）使用完整规则、ruff format 与 `mypy --strict`。
- 新增 `tools/yuem/gates.sh`（统一门禁）、`metrics.py`（棘轮指标与基线 `.yuem/metrics/baseline-0.5.0.json`）、`patch_ledger.py`（台账核对与 CHANGELOG 检查）、`quality_paths.py`，以及 `.pre-commit-config.yaml`。
- `dev` extra 换成 ruff、mypy、import-linter、pytest-qt、pytest-benchmark、hypothesis、empymod，新增同内容的 `[dependency-groups] dev`。
- 新增 `uv.lock` 与 `tools/yuem/dev_env.sh`：显式使用 PyPI；锁定平台按 pgcore 轮子实际覆盖限定；自动修复 macOS 上三个问题：pgcore 缺 `libblas.3.dylib`、解释器缺 CA 证书、`.pth` 文件带隐藏标志被 Python 3.12 跳过（可编辑安装只能在仓库根目录导入）。

- 新增 Full 打包环境 `packaging/conda/environment-full.yml` 与三平台锁文件 `conda-lock.yml`（osx-arm64、win-64、linux-64），与上游 Full CI 的包和 rustsolve 校验过的 pgcore 构建一致。
- 新增 CI `.github/workflows/yuem-ci.yml`：静态门禁；快速测试（Linux 3.11/3.12、macOS 26 arm64 3.12、Windows 3.12）；GUI 测试（Linux、macOS）；`yuem/main` 推送与手动触发时运行 slow、numerical、golden 三层。
- 新增 `tools/yuem/build_macos_dmg.sh`：在锁定的 Full 环境中构建、拷出源码树后签名、自检、生成 DMG、挂载复检、输出 SHA-256。

### 质量护栏（M1）

- 工作流冒烟测试 `tests/yuem/smoke/`：注册表中全部 17 个工作流各有最小 recipe（`recipes.py`，依赖其他工作流输出的先在进程内跑前置），经 `python -m PyHydroGeophysX.workflows.cli run` 子进程执行；断言状态、产物存在且校验和一致、结果可 JSON 序列化、带完整溯源；工程目录名含中文与空格。另有测试保证每个注册的工作流都有 recipe。
- Studio 页面冒烟测试 `tests/yuem/gui/`：15 个页面 offscreen 构建，不得退化为占位页，`agent_describe()` 可用，`stop_workers()` 5 秒内返回；主窗口帮助菜单有环境自检入口；测试期间 Qt 报告 QThread/QProcess 在运行中被销毁即判失败。
- `phgx-doctor` 增加 macOS 隐藏文件检测（`.pth` 与 Qt 平台插件）；`dev_env.sh` 对整个 `.venv` 递归清除隐藏标志（Qt 也会跳过隐藏的平台插件）。

- 数值验证集 `tests/yuem/verification/`（标记 `numerical`）14 例：ERT 均匀半空间、两层 Wenner（镜像级数）、三维逐单元模型；SRT 两层折射；TDEM 中心回线（Ward & Hohmann）；FDEM 半空间与三层（empymod，Anderson 801 点滤波器）；MT 半空间与三层（Wait 递推）；重力棱柱（Bouguer 板）与球体/立方体（点质量）；磁性球体（极点偶极子）；Waxman-Smits 正反变换往返。`tools/yuem/verification_report.py` 生成 `docs/yuem/verification.md`。
- 回归金标准 `tests/yuem/golden/`（标记 `golden`）10 例：ERT 单次与时移反演、SRT、FDEM 单点、TEM LCI 剖面、MT Occam 1D、MT 处理、重力反演、FDEM+TDEM 联合、重力处理；提取产物、指标与内存模型中的全部数值数组比对；容差按实测的运行间可重复性设定（SRT 因 pyGIMLi 射线追踪约 1e-4 波动取 1e-3，其余 1e-6 至 1e-10）。`tools/yuem/golden.py --update --reason` 更新并记入 `tests/yuem/golden/CHANGES.md`。
- 随机数确定性：全局 `np.random` 调用由 9 处降为 0（保留的一处为兼容旧版 SimPEG 的设种并保存/恢复全局状态，入白名单）；`kriging_3d` 的变差函数搜索与训练/验证划分接受 `random_seed`。
- 覆盖率基线 `tools/yuem/coverage.py --record` → `.yuem/metrics/coverage-baseline.json`：全部测试层，含子进程中的工作流运行；全包 37.0%，核心算法路径（data_processing、forward、inversion）49.1%。
- 新增 `docs/yuem/findings.md`：改造过程中发现的问题、根因、影响与处理状态。
- 溯源的 BLAS 识别在 threadpoolctl 看不到 Apple Accelerate 时回退到 NumPy 构建配置。
- 棘轮白名单 `.yuem/metrics_allowlist.toml`：只收边界代码（CLI 前端、诊断边界），逐文件写明理由，命中数单独报告。

- 运行溯源 `PyHydroGeophysX/_internal/provenance.py`：每个工作流结果的 `provenance` 记录分叉版本、`git describe`、Python 与平台、关键库版本（取自安装元数据，不读模块 `__version__`，因为 pyGIMLi 的 `__version__` 反映的是当前目录的 git 状态）、BLAS 实现与线程数、种子、输入校验和、参数摘要；Studio 页面在进程内计算的运行由 `ResultsStore.finish_run` 补记环境。
- `pyhydrogeophysx-workflow env-diff <run.json>` 比较记录环境与当前环境；`run` 重跑时若 recipe 旁有 `run.json`，自动提示环境差异。
- 环境自检 `phgx-doctor`（`PyHydroGeophysX/doctor.py`）：Python、包、核心库、pyGIMLi 核心（含 macOS libblas 缺失检测）、证书、Qt 平台插件、VTK/OpenGL、中文字体、工程目录空间与写权限、可选引擎；退出码 0/1/2。Studio“Help > Environment Check…”运行同一套检查。

### 架构（M2）

- 插件注册中心 `PyHydroGeophysX/plugins.py`：`register_module`（页面、导航顺序与分组、模块描述）、`register_workflow`、`register_reader`（后缀与嗅探）、`register_short_code`；入口分组 `phgx.plugins`、`phgx.modules`、`phgx.workflows`、`phgx.readers`。原有硬编码表保持数据形态、原地更新。页面注册不依赖 Qt，无界面工作进程加载同一插件时工作流照常注册；损坏的插件被记录、不影响其他插件。工作流注册表与 Studio 页面表首次使用时自动加载插件。开发指南 `docs/yuem/plugins.md`。`phgx-doctor` 列出插件与加载失败。
- 分层契约 `.importlinter`（门禁运行 `lint-imports`）：界面与助手 > 工作流 > 算法 > 核心 > 内部；算法层不得引用 PySide6。上游 4 处跨层依赖列入 `ignore_imports`，由棘轮指标 `layer_exceptions` 保证只减不增。插件加载核心下沉到 `_internal/plugin_loader.py`，使工作流注册表只向下依赖；溯源模块不再导入整个包。
- 异常体系 `PyHydroGeophysX/errors.py`：`PHGXError` 及 `DataValidationError`（消息带文件、行号、字段）、`ConvergenceError`、`Cancelled`、`ResourceLimitError`，并转出 `BackendUnavailable`；各类继承调用方已在捕获的内置异常（`ValueError`/`RuntimeError`），替换旧的 raise 不破坏现有 `except`。边界统一处理：`pyhydrogeophysx-workflow run` 遇领域异常输出一行“类型: 消息 (hint: 建议)”并以退出码 2 结束（未知异常仍输出堆栈、退出码 1）；Studio 子进程失败消息与进程内工作线程给出通俗说明。工作流层（`workflows/domain.py`）输入缺失、长度不一致等 12 处校验改抛 `DataValidationError`。`workflows/cli.py` 中 3 处 psutil 宽泛捕获收窄为具体异常。
- 日志体系 `PyHydroGeophysX/_internal/logging_setup.py`：Studio 应用日志 `phgx.log` 写在 platformdirs 给出的目录（macOS 为 `~/Library/Logs/PHGX`，`PHGX_LOG_DIR` 可覆盖），按 5 MB × 5 轮转；同一位置的重复堆栈只保留前 3 条；上游代码的 `print` 与写到 stderr 的堆栈经旁路捕获进入应用日志（不改上游源码）。每次工作流运行在结果目录写 `run.log.jsonl`（每行一条 JSON 记录：时间、级别、记录器、消息、线程、堆栈），包括运行打印的每一行和失败堆栈；父进程读到的输出不变。页面日志 `BaseModule.log` 同时写入 logging。启动器的 faulthandler 原生崩溃记录移到应用日志目录下的 `diagnostics/`。
- own 代码中 144 处静默吞掉异常的 `except Exception` 改为带堆栈写入应用日志（DEBUG 级），新增只降不升的棘轮指标 `own_silent_broad_except`（现为 0）。ADR 0003 补充：存量超长文件因横切的可靠性改造增加几行时，在白名单 `[file_length]` 登记只降不升的行数上限。
- 显式运行上下文：`RunContext` 新增 `threads`（BLAS/OpenMP 与 pyGIMLi 线程数，运行期间生效、结束后恢复，记入溯源 `provenance.threads`）与 `cache_dir`（默认每用户缓存目录 `~/Library/Caches/PHGX`，`PHGX_CACHE_DIR` 可覆盖；`cache_path()` 按类别建子目录）。`pyhydrogeophysx-workflow run --threads N`，缺省读 `PHGX_THREADS`。own 之外的环境变量读取冻结在 `.yuem/environ_reads.toml`（19 个文件 42 处，均为外部程序路径与本地库开关），测试保证只减不增。
- 计算进程隔离（`docs/yuem/compute_isolation.md`）：盘点 10 个页面共 36 处后台计算调用，15 处已在子进程中运行，19 处轻量 IO 与绘图保留在进程内。ERT 页面的两处网格生成迁入子进程：Mesh 页预览走新工作流 `ert.mesh_build`（网格交回后在线程中派生预览），导入 E4D 配置走 `ert.e4d_mesh`。原生网格库崩溃或点停止只结束子进程。`qt_apps/process_jobs.scratch_process_worker` 供页面在临时目录运行工作流，不写入运行历史。GUI 测试覆盖“构建中途强制杀掉子进程后页面存活并可再次构建”。
- Streamlit 桥接解耦：上下文读取与结果文件写出移到 `qt_apps/bridge_compat.py`（`BridgeLink` 持有上下文文件、内容与结果文件路径）；`StudioState` 只保留工程状态，原有 `context`、`context_path`、`result_path`、`load_context`、`build_result`、`save_result` 作为转发保留，调用方不变。行为由 `tests/yuem/test_bridge_compat.py` 锁定（改动前先在原代码上通过）。
- `dev_env.sh`：仓库位于 iCloud 同步的 `~/Desktop` 或 `~/Documents` 时，环境建在 `~/Library/Caches/phgx-venvs/`，`.venv` 为符号链接（iCloud 会持续给点目录中的文件打隐藏标志）。

### 数据与结果协议（M3）

- 工程数据库 `PyHydroGeophysX/datastore/`（模式 `phgx-dataset-v1`，说明见 `docs/yuem/datastore.md`）：HDF5 六分组（meta、geometry、observations、errors、masks、provenance），每组为可无损往返的树；版本不可变，与上一版本相同的数组以相对路径外链共享，工程目录整体移动后可读；原始文件只读引用并记录 sha256，可校验；JSON 索引可从文件重建。适配器覆盖 pyGIMLi `DataContainerERT`、EM 测深字典、MT `TransferFunction`、`SeismicDataset`。
- 多参数结果协议 `PyHydroGeophysX/results/protocol.py`（`ModelResultV2`，可存为 HDF5）：几何（非结构网格、规则网格、层状测深）、带单位的命名参数（预留 rho0、m、tau、c、static_shift 等并校验量纲）、数据拟合（观测、预测、误差、残差、总体与分组 χ²）、覆盖度、DOI、分辨率与遮罩、不确定度、迭代历史、溯源。`display_mask()` 合并可用遮罩并给出图例说明（覆盖度阈值与 Model Viewer 的 log10 灵敏度 -2.0 一致；射线覆盖按“是否有射线穿过”）。适配器 `results/adapters.py` 覆盖 `ModelResult`、pyGIMLi 管理器、`InversionResult`、`TDEMInversionResult`、`FDEMInversionResult`、`LCIResult`、MT `Occam1DResult` 与 `ProfileInversionResult`、重磁结果，以及 7 个产出模型的工作流（`from_workflow_result`）。
- 行业格式导出 `PyHydroGeophysX/results/exports.py`：Res2DInv 通用阵列（type 11，含 IP 块）、Surfer ASCII GRD（空白值 1.70141e38）、Geosoft XYZ（按 Line 分块，`*` 为空值）、单元 CSV（表头带单位与显示遮罩）；`grid_section` 把网格、规则网格或层状结果插值到 GRD 所需的规则网格并应用遮罩。每种格式都有“写出后读回”的往返测试。分层契约纳入 `datastore`、`results`（算法层）与 `errors`（核心层），并禁止它们引用 Qt。
- Model Viewer 消费 `ModelResultV2`：8 个产出模型的工作流（ERT 单次与时移、SRT、EM 单点与测线、MT 一维与二维、重磁）运行结束时在输出目录写 `model_result.phgx.h5` 并登记为产物（转换失败只记日志，不影响运行）；Model Viewer 优先列出并用新组件 `widgets/model_result_view.py` 显示（网格、规则网格切片、层状剖面与单点曲线，多参数切换，单位入色标），覆盖度、DOI、分辨率遮罩默认开启，图下注明遮罩依据。ERT 剖面视图的“Hide below”覆盖度遮罩改为默认开启。Model Viewer 的数组、曲线、表格渲染移到 `model_viewer_render.py`，页面由 2094 行降到 1968 行。
- 单位与坐标系 `PyHydroGeophysX/results/units.py`：轻量单位字符串注册表（不引入 pint），`require_unit`/`check_units` 校验、同量纲换算；坐标系以 WKT 加 EPSG 代码保存（如 CGCS2000 的 EPSG:4544）。

### 专业化与体验（M4）

- 界面中文化（`docs/yuem/i18n.md`）：own 目录 54 个界面文件中 2078 处界面文字改为 `QCoreApplication.translate`（字面量与 f-string）、455 处改为 `i18n.tr`（变量），由 `tools/yuem/i18n.py wrap` 自动改写，保留原有换行与注释；`pyside6-lupdate` 生成 `qt_apps/translations/phgx_zh_CN.ts`（2399 条，全部译出，占位符与 HTML 标签经校验），`lrelease` 编译 `.qm` 并纳入 PyInstaller spec 与 wheel。默认跟随系统语言，“视图 > 语言”可切换（下次启动生效）。日志、作为取值读回的下拉框条目、无 Qt 的报告模块保持英文。门禁新增 `i18n.py check`；GUI 测试在中文翻译下逐页构建。
- 图件与报告模板 `PyHydroGeophysX/visualization/styles/`：行业图式（中文字体且 PDF 内嵌 TrueType、刻度朝内、坐标轴与色标带单位、对数色标标注数值）、自动取整比例尺、指北针、图签（图名、工程、测线、方法、日期、比例、坐标系、制图、软件）；`section_figure` 绘制任一 `ModelResultV2`（网格、规则网格、层状测线与单点），默认遮罩并以图件语言注明依据；`pseudosection_figure` 按 ERT 页面与工作流同一算法定位拟断面；`save_publication` 输出矢量 PDF 或 300 dpi PNG。Model Viewer 的结果视图新增“导出图件…”。
- 质控面板标准化（`docs/yuem/qc.md`）：ERT 拟断面框选、EM 时窗表格、MT 曲线周期选择统一提供“剔除所选 / 恢复所选 / 撤销 / 记录…”（`qt_apps/widgets/qc_actions.py`），决定（对象、原因、判据、时间）由无 Qt 的 `datastore/qc.py` `QCLog` 保存，遮罩由决定重放得出，可写入数据集的 masks 与 provenance。剔除真正进入处理：ERT 在自动检查前去掉剔除的读数并写入运行的质控文件，ERT 可把记录与数据一起保存为工程数据集新版本；EM 单点反演参数 `rejected_gates`、MT 一维反演参数 `rejected_frequencies` 由 `workflows/qc_masks.py` 应用到数据副本。为腾出空间，`em_processing.py`（3419 -> 3375 行）的时窗视图辅助函数移到 `em_gate_view.py`，`mt_processing.py`（2206 -> 2155 行）的 `FigurePane` 移到 `widgets/figure_pane.py`。
- 规范对标（`docs/yuem/standards.md`）：列出各方法参数对应的行业规程（DZ/T 0073-2016、DZ/T 0072-2020、DZ/T 0070-2016、DZ/T 0187-2016、SY/T 6589-2024、SY/T 7073-2016、DZ/T 0173-2022、DZ/T 0170-2020、DZ/T 0082-2021、DZ/T 0071-2025、DZ/T 0361-2020、CJJ/T 7-2017，编号、名称与现行状态已在国家标准馆与全国标准信息公共服务平台核对），明确软件默认值不代表规程限差。`qt_apps/standards.py` 在页面构建时把规程编号、名称与主题追加到 ERT、TEM、MT、重磁相关参数的提示文字中。
- 拆分 ERT 页面（样板工程）：7676 行的 `qt_apps/modules/ert_processing.py` 拆为 `qt_apps/modules/ert/` 包：`page.py`（控件与初始化）、`import_panel.py`、`qc_panel.py`、`mesh_panel.py`、`inversion_panel.py`、`timelapse_panel.py`、`results_panel.py`、`presenter.py`（助手接口与电极编辑）与 `common.py`（共用导入、常量与辅助函数），最长 1190 行。方法原样按功能区移入各部分（mixin），`ERTProcessingModule` 组合这些部分，覆盖关系与方法解析顺序不变；`ert_processing.py` 保留为转发入口（`MODULE_SPECS` 键、旧导入名与 0.3.0 兼容名照常可用）。行为由页面构建（中英文）、计算隔离、ERT 金标准与冒烟测试锁定。棘轮指标 `inprocess_worker_modules` 改为按页面计数。
- 中文字体回退（`qt_apps/theme.py`）：PingFang SC、Hiragino Sans GB、Microsoft YaHei、Noto Sans CJK SC、Segoe UI 依次回退，只引用已安装字体，消除自检的 “missing font family” 警告；Matplotlib 同步中文字体并关闭 unicode 负号。

### 发行与持续（M5）

- CI 首轮实跑暴露的问题：Linux 各测试层补装 Qt 运行库（pytest-qt 启动即导入 Qt）与 Gmsh；E4D 网格冒烟在没有 TetGen/Gmsh 的机器上跳过并说明原因；数据库原始文件校验的提示统一用记录中的 POSIX 路径（Windows 上曾显示反斜杠）；Windows 上 pyGIMLi 无法打开中文路径记为 F-16，相关两个冒烟用例在 Windows 上标为预期失败；Linux GUI 层退出时中止（F-17）的原因是助手面板在测试中联网下载 Codex CLI、退出时下载线程仍在运行，GUI 测试会话改为指向不存在的 CLI 路径，不再联网；Windows 上 pgcore 自带的 OpenBLAS 不受 threadpoolctl 控制（F-18），`--threads` 改为同时在导入前设置 `OMP_NUM_THREADS`、`OPENBLAS_NUM_THREADS`、`MKL_NUM_THREADS`。
- 性能基线：`tests/yuem/perf/`（ERT 单次反演、TEM LCI 测线、MT Occam 1D，各跑 3 轮取中位数）与 `tools/yuem/perf.py record/check`；基线按机器记录在 `.yuem/metrics/perf-baseline.json`（本机 darwin-arm64：ERT 5.18 s、TEM LCI 1.24 s、MT 0.35 s），慢 20% 以上告警；CI 每周定时与手动触发 `perf` 任务（告警不阻断，首次在 CI 上记录基线并作为产物上传）。pytest-benchmark 5.3 与 pytest 9 的私有属性不兼容，在性能测试的 conftest 中补齐。
- 签名与公证（M5.1）：`build_macos_dmg.sh` 设 `PHGX_SIGN_IDENTITY` 时由内到外以 Developer ID 签名（hardened runtime、时间戳、`packaging/macos/entitlements.plist`），再设 `PHGX_NOTARY_PROFILE` 时签名镜像、`notarytool` 公证、`stapler` 装订并以 `spctl` 核验；未设时保持 ad-hoc 签名，镜像内安装说明随之切换。当前无 Apple Developer 账号与 Windows 证书，按 ad-hoc 发布并在说明中注明。
- 发布流程（M5.2）：`docs/yuem/release_checklist.md` 与 `tools/yuem/release.sh`（核对版本号与变更记录、全部门禁层、翻译与验证报告、带审计的 DMG 构建、sha256 与发布说明；默认只打印 `gh release create --draft` 命令，`--publish` 须经负责人确认）。`build_macos_dmg.sh` 可选 `PHGX_RELEASE_AUDIT=1`：复用 `packaging/release_audit.py stage` 在镜像根目录写入 `BUILD_INFO.txt`、`SOURCE_CODE.md` 与 `LICENSES/`。
- 回馈上游候选（M5.5）：`docs/yuem/upstream_prs.md` 列出 9 项（ERT 正演区域映射、SimPEG 0.26 兼容、随机数可复现、依赖修复、rustsolve 缓存、插件注册中心、macOS 测试矩阵、中文路径与中文界面、环境自检），逐项写明文件、证据与依赖；每项提交前单独征得同意。前三项已提交：[#20](https://github.com/geohang/PyHydroGeophysX/pull/20)（ERT 正演区域映射）、[#21](https://github.com/geohang/PyHydroGeophysX/pull/21)（SimPEG 0.25/0.26 兼容）、[#22](https://github.com/geohang/PyHydroGeophysX/pull/22)（随机数可复现）。
- `PyHydroGeophysX/results/` 包此前被上游 `.gitignore` 的运行输出规则 `results/` 排除，没有入库，干净检出（CI、发布构建）缺这个包；`.gitignore` 的 YUEM 段放行该目录（台账 P-0001）。门禁新增“源码目录中没有被 `.gitignore` 隐藏的文件”一步，覆盖 `PyHydroGeophysX/`、`tests/`、`tools/`。
- 工程位置校验（F-10）：工程目录在包源码内时拒绝打开，在源码检出的 `examples/` 内时给出警告（兼容已有工程）。
- 月度上游同步：`tools/yuem/sync_upstream.sh`（拉取、快进 `upstream`、按 follow 路径列出候选提交、可选创建 `yuem/sync-YYYYMM`；不推送、不自动挑拣）；2026-10-31 检查上游无新提交，记入 `.yuem/SYNC_LOG.md`。

### 修复（可回馈上游）

- 三维 ERT 几何因子（F-09）：`create_3d_ert_data_container` 用的 pyGIMLi 解析几何因子以 z = 0 为地表，电极在 100 m 高程的地面排列被当成埋深 100 m，k 与三维正演合成数据（`ert3d.forward`、Studio 三维正演）的视电阻率约为真值 2 倍；地面排列且电极不在 z = 0 时改用以电极处为地表的半空间公式，与按文件导入的数据共用 `_internal/ert_factors.py`，井中排列不变（台账 P-0007）。数值验证新增 V-ERT-04。带地形时仍有约 ±10% 的残差，来自 pyGIMLi 奇异性消除按水平地表计算一次场，记为 F-15。
- 重力+磁法联合反演可复现性：SimPEG ≥ 0.23 的 `PairedBetaEstimate_ByEig` 不读全局随机数状态，上游的全局设种对它无效，同一种子两次运行相差 2.6%；种子改为直接赋给该 directive（台账 P-0006）。

- ERT 正演区域映射：`ERTForwardModeling` 在网格含标记 1 区域时把逐单元模型映射到错误单元，二维两层误差 284%，三维正演（`ert3d.forward`）合成数据误差达 90%；改为按模型长度选用区域算子或逐单元算子，长度不符时报错（台账 P-0005）。数值验证发现。

- SimPEG 0.26 兼容：`gravmag.invert`、`FDEMInversion`、`TDEMInversion`、MT 二维反演使用了 SimPEG 0.26 已删除的 `maxIterCG`/`tolCG`，在上游声明的依赖范围内新装即报错；改由 `_internal/simpeg_compat.cg_keywords` 按版本选择参数名（台账 P-0004）。冒烟测试发现。
- `packaging/rustsolve/apply.py`：替换 libgimli 前先删除目标文件。conda 以硬链接把包缓存中的文件装进环境，原地写入会改坏缓存中的 pgcore，之后从同一缓存创建的环境都通不过校验（本机复现）。

- `pftools` 移到独立的 `parflow-tools` extra：它硬锁 `pyyaml==6.0.1`，且部分版本元数据被 pip 拒收，导致 `geophysics` 整组无法安装。
- `gpu`、`all` 中的 CuPy 与 `adtlert` extra 中的 ADTLERT 加 `sys_platform != 'darwin'` 标记，`pip install ".[all]"` 在 macOS 上可以安装。
