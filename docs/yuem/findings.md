# 改造过程中发现的问题

按发现顺序记录。每条写明现象、根因、影响、处理和证据。状态取值：已修复、已规避、待排查、计划中。

| 编号 | 问题 | 根因 | 影响 | 处理 | 状态 | 证据 |
|---|---|---|---|---|---|---|
| F-01 | `pip install ".[geophysics]"` 解析失败 | `pftools` 硬锁 `pyyaml==6.0.1`，1.3.2–1.3.5 元数据被 pip 拒收 | 地球物理整组依赖装不上 | 移到 `parflow-tools` extra | 已修复（P-0002，可回馈） | 2026-10-30 本机安装日志 |
| F-02 | `pip install ".[all]"`、`.[adtlert]` 在 macOS 上不可安装 | CuPy、ADTLERT 没有 macOS 轮子 | Mac 用户无法装全量 | 加 `sys_platform != 'darwin'` 标记 | 已修复（P-0002，可回馈） | `uv lock` 解析失败信息 |
| F-03 | pygimli 1.5.5 装上后无法导入 | 1.5.5 是不含 pgcore 的纯 Python 轮子；pgcore 1.6.0 的 macOS 轮子只有 cp312 且需 macOS 26 | 依赖解析可能选中不可用版本 | 锁文件约束 `pygimli>=1.6.1`，平台矩阵按轮子覆盖限定 | 已规避（ADR 0002） | PyPI 轮子清单 |
| F-04 | macOS 上 pyGIMLi 导入失败 | pgcore 轮子链接 `libblas.3.dylib` 却只带 `libopenblas.0.dylib` | pyGIMLi 全部功能不可用 | `dev_env.sh` 建链接，`phgx-doctor` 检测 | 已规避 | 2026-10-30 安装、`phgx-doctor` |
| F-05 | 可编辑安装只能在仓库根目录导入；Qt 找不到 offscreen 插件 | iCloud Drive 的“桌面与文稿”同步在数秒内给点目录（`.venv`）中的文件重新打上 macOS 隐藏标志（清除后 20 秒内复现，`/tmp` 下不出现）；Python 3.12 跳过隐藏 `.pth`，Qt 跳过隐藏插件 | 测试与 GUI 在仓库根目录之外运行失败 | 仓库位于 `~/Desktop` 或 `~/Documents` 时，`dev_env.sh` 把环境建在 `~/Library/Caches/phgx-venvs/`，`.venv` 为符号链接；`phgx-doctor` 检测隐藏文件 | 已规避 | `python -v` 输出 “Skipping hidden .pth file”；清除后复现实验 |
| F-06 | 打包时 rustsolve 校验失败，且污染 conda 包缓存 | `packaging/rustsolve/apply.py` 用 `shutil.copyfile` 原地写入被 conda 硬链接的文件 | 同一缓存创建的所有环境都通不过校验 | 写入前先删除目标文件 | 已修复（可回馈） | 两个环境与缓存中 libgimli 为同一 inode |
| F-07 | `gravmag.invert`、`FDEMInversion`、`TDEMInversion`、MT 二维反演在 SimPEG 0.26 下报错 | 使用了 0.26 已删除的 `maxIterCG`/`tolCG`/`save_txt` | 按上游声明的依赖范围新装即不可用 | `_internal/simpeg_compat` 按版本选参数名 | 已修复（P-0004，可回馈） | 冒烟测试 `gravmag.invert` |
| F-08 | 逐单元电阻率模型被映射到错误单元（ERT 正演） | `ERTForwardModeling` 未忽略 pyGIMLi 区域管理器，标记 1 区域被视为背景 | 二维两层模型误差 284%；三维正演（`ert3d.forward`，Studio 三维正演）合成数据误差达 90% | 按模型长度选择区域算子或逐单元算子，长度不符时报错 | 已修复（P-0005，可回馈） | 数值验证 V-ERT-02、V-ERT-03 |
| F-09 | 冒烟用三维网格上，100 Ωm 均匀模型的视电阻率为 184–220 Ωm | `create_3d_ert_data_container` 用 pyGIMLi 的解析几何因子，它把 z = 0 当作地表、在其上方镜像每个电极；电极在 100 m 高程的地面排列被当成埋深 100 m，k 接近全空间值，是半空间值的 2 倍。与网格无关：外扩 1.4 至 6 倍、单元 4320 至 115200，比值都约为 2 | 三维正演合成数据（`ert3d.forward`、Studio 三维正演）在电极不在 z = 0 时视电阻率约为真值 2 倍；用同一数据容器反演时 k 前后一致，模型不受影响，但导出的视电阻率、以及与按文件导入的数据（导入路径已以电极处为地表）混用时量级相差一倍 | 地面排列且电极不在 z = 0 时，改用以电极处为地表的半空间几何因子，与导入路径共用同一实现（`_internal/ert_factors.py`）；井中排列保持 pyGIMLi 的算法 | 已修复（P-0007，可回馈） | 数值验证 V-ERT-04；`tests/yuem/test_geometric_factors.py` |
| F-10 | Studio 允许把工程建在 `examples/` 等源码目录下 | 工程路径无约束 | 运行记录混入源码树 | 打开或新建工程时校验：包源码目录内拒绝，源码检出的 `examples/` 内给出警告（兼容已有工程） | 已修复（M5） | `tests/yuem/test_project_location.py` |
| F-11 | 启动和每个页面都提示缺少 “Segoe UI” 字体 | 主题写死 Windows 字体 | 每次启动多耗约 110 ms，非 Windows 平台字体替换不可控 | 字体回退链，只引用已安装字体 | 已修复（M4.2） | `tests/yuem/gui/test_pages.py::test_the_studio_starts_without_font_warnings` |
| F-12 | 一次 GUI 测试运行在进程退出时报 “QThread: Destroyed while thread is still running” | 未复现（当时 shell 残留指向旧环境的 `QT_PLUGIN_PATH`） | 退出时可能崩溃 | GUI 测试守护：运行中销毁 QThread/QProcess 即失败 | 已加守护 | `tests/yuem/gui/conftest.py` |
| F-13 | 重力+磁法联合反演在给定种子下不可复现 | SimPEG ≥ 0.23 的 `PairedBetaEstimate_ByEig` 用自身 `seed`，上游只设了全局种子 | 同一种子两次运行结果相差 2.6% | 种子直接赋给 directive，保留全局设种兼容旧版 | 已修复（P-0006，可回馈） | `tests/yuem/test_rng.py`；上游原代码对比 |
| F-14 | 三维克里金的变差函数搜索与训练/验证划分不可复现 | 使用全局 `np.random` | 结果随运行变化 | 显式 `random_seed` 与 `default_rng` | 已修复（P-0006，可回馈） | 棘轮 global_np_random 9 → 0 |
| F-15 | 带地形的三维地面排列上，均匀模型的视电阻率仍偏离真值约 ±10%（冒烟网格坡度 0.1：92–110 Ωm），且不随网格加密改变 | pyGIMLi 默认的奇异性消除按水平地表解析计算一次场；均匀模型没有二次场，地形完全未计入。解析几何因子同样假定水平地表 | 带地形三维数据的视电阻率绝对量级约有 10% 误差；用同一 k 反演时自洽 | 地形测区改用数值几何因子（同一网格加密后以 1 Ωm 正演取倒数），或关闭奇异性消除并加密网格；需评估计算量后决定 | 待排查 | 4320、25704、128464 个单元的网格上，开启奇异性消除时结果完全相同；关闭时中位数为 100.33、96.99、98.65 Ωm |
| F-16 | Windows 上工程目录含中文时，`ert3d.forward` 写不出数据文件，`seismic3d.build` 读写不了网格 | pyGIMLi C++ 的文件函数（`DataContainer.save`、`Mesh.save`/`saveBinaryV2`、`pg.load` 等）接收窄字符串，Windows 按系统代码页解释 Python 传入的 UTF-8 字节，非 ASCII 路径打不开 | 中文 Windows 用户把工程放在中文目录下时，凡经 pyGIMLi 读写文件的步骤都会失败；代码中这类调用超过 50 处 | 需要全局方案：在 Windows 构建的程序清单中启用 UTF-8 代码页，或启动时把 C 运行库 locale 设为 UTF-8，取决于 pgcore 所链接的运行库，需在 Windows 上实验；冒烟测试在 Windows 上把这两个工作流标为预期失败（strict），修好后会提示 | 待排查 | CI 首轮 Windows 快速层（run 41182178543） |
| F-17 | Linux CI 的 GUI 层 43 条全部通过后，进程退出时以 SIGABRT（134）结束 | 待查；日志无报错输出，疑为 VTK 或 Qt 在 offscreen 平台退出清理时中止 | macOS 上不出现；可能影响 Linux 用户退出程序 | GUI 层改用 `python -X faulthandler` 运行，拿到退出时的调用栈后再定 | 待排查 | CI run 41182178543 |
| F-18 | Windows CI 上 `RunContext(threads=1)` 期间仍有线程池不是 1 个线程 | 待查；测试已改为列出未受限的库 | 线程上限在 Windows 上可能不完整 | 根据下一轮 CI 列出的库处理 | 待排查 | CI run 41182178543 |
