# 计算进程隔离清单（M2.6）

盘点日期：2026-10-31。范围：`PyHydroGeophysX/qt_apps/modules/` 下所有页面中的 `TaskWorker`（进程内线程）、`WorkflowWorker`（进程内工作流线程）和 `ProcessWorkflowWorker`（子进程）调用，共 36 处。

## 分类原则

- **重计算**：反演、网格生成、大规模正演，以及调用原生网格库（Triangle、TetGen、Gmsh、pyGIMLi 网格生成）的步骤。一律走 `ProcessWorkflowWorker` 加已注册的工作流。原生库崩溃或用户点停止时只结束子进程，界面不受影响；在子进程里长时间持有 GIL 也不会卡住界面绘制。
- **轻 IO 与绘图**：读文件、取瓦片、对内存中的数组做交互式处理、从已有结果派生绘图数据。这些保留在进程内的 `TaskWorker` 中，可以逐步取消，参数改动后能复用缓存快速重算。

页面自身的重计算步骤（例如网格预览）不是 Project 的一次“运行”，经 `qt_apps/process_jobs.scratch_process_worker` 在临时目录中运行，不写入运行历史。

## 清单

### 已在子进程中运行（15 处，改造前已是如此）

| 页面 | 调用位置 | 工作流 |
|---|---|---|
| em | `_start_single` / `_start_line` | `em.inversion` / `em.line_inversion` |
| ert | `_run_inversion` / `_launch_timelapse` | `ert.single_inversion` / `ert.timelapse_inversion` |
| geo_hydrology | `_run_inverse` | `geo_hydrology.ert_to_wc` |
| gravmag | `_run_inversion` | `gravmag.invert` |
| hydro_geophysics | `_run_forward` | `hydro_geophysics.forward` |
| joint_inversion | `_run` | `joint_inversion.run` |
| mesh3d | `_generate_mesh` / `_run_ert_forward` | `mesh3d.build` / `ert3d.forward` |
| mt | `_start` | `mt.process`、`mt.invert_1d`、`mt.invert_profile` |
| seismic3d | `_run_build` | `seismic3d.build` |
| seismic | `_run_srt` | `seismic.srt_inversion` |

### 本次迁入子进程（2 处）

| 页面 | 调用位置 | 原做法 | 现做法 |
|---|---|---|---|
| ert | `_refresh_mesh_preview`（Mesh 页预览） | 线程中调用 `build_inversion_mesh`，三维可达几十万单元 | 子进程运行 `ert.mesh_build`，网格和数据作为对象交回；预览（单元轮廓、计数、PyVista 体）在线程中从网格派生（`qt_apps/modules/ert_mesh_preview.py`） |
| ert | `_mesh_from_e4d_config`（导入 E4D 配置） | 线程中调用 `build_e4d_mesh`（TetGen） | 子进程运行 `ert.e4d_mesh`，保存 `.bms` 供反演使用 |

验证：`tests/yuem/gui/test_compute_isolation.py`。预览在子进程中构建；构建中途强制杀掉子进程（模拟原生库崩溃）后，页面仍响应，并能再次构建。

### 保留在进程内（19 处）

| 页面 | 调用位置 | 内容 | 理由 |
|---|---|---|---|
| em | `_start_plan_maps` | 平面图绘制 | 绘图 |
| em | `_ensure_survey` | 读测量文件 | IO |
| ert | `_start_load` | 读 ERT 数据 | IO |
| ert | `_start_recip_read` | 读互易测量 | IO |
| ert | `_run_timelapse` / `_fit_timelapse_from_cache` | 时序数据质控、误差拟合 | 轻量统计，结果直接用于界面 |
| ert | `_derive_mesh_preview` | 从子进程交回的网格派生预览 | 数组运算 |
| gpr | `_load` | 读雷达数据 | IO |
| gpr | `_simulate_example` | 示例剖面（CRIM 换算加合成雷达图） | 小规模 NumPy |
| gpr | `_reprocess` | 雷达处理流程 | 交互式数组处理 |
| hydro_geophysics | `_update_preview` | 抽取剖面预览 | 轻量 |
| mesh3d | `_open_e4d_mesh` | 读已有网格 | IO |
| model_viewer | `_selection_changed` | 统计运行目录大小 | IO |
| mt | `_read_recording` | 读时间序列 | IO |
| project_map | `_fetch_tiles` | 下载底图瓦片 | 网络 IO |
| seismic | `_load_gather` | 读道集 | IO |
| seismic | `_auto_pick_all` | 逐炮初至拾取 | 交互式 NumPy，可逐炮取消 |
| seismic | `_run_reflection` | 反射叠加 | 交互式 NumPy，可分步取消，复用已准备的数据 |

## 后续

- 新增页面的计算步骤按上述原则归类；重计算必须注册为工作流（插件同样适用，见 `docs/yuem/plugins.md`）。
- 棘轮指标 `inprocess_worker_modules` 统计含进程内 worker 的页面数（现为 10）。轻量步骤保留在进程内属正常，该指标只防止增加，不以清零为目标。
