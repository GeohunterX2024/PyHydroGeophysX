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
| F-09 | 冒烟用三维网格上，100 Ωm 均匀模型的视电阻率为 184–220 Ωm | 待查：网格外扩只有 1.4 倍且较粗，或三维数据容器的几何因子与带地形网格不一致 | 可能影响三维正演数据的绝对量级 | 用生产级网格参数复核；若几何因子有误，改为数值几何因子 | 待排查 | `/tmp/proto_ert3d.py` 复现 |
| F-10 | Studio 允许把工程建在 `examples/` 等源码目录下 | 工程路径无约束 | 运行记录混入源码树 | 显式工程上下文中校验 | 计划中（M2.5） | `.yuem/baseline_diff.md` |
| F-11 | 启动和每个页面都提示缺少 “Segoe UI” 字体 | 主题写死 Windows 字体 | 每次启动多耗约 110 ms，非 Windows 平台字体替换不可控 | 字体回退链 | 计划中（M4.2） | Studio 自检输出 |
| F-12 | 一次 GUI 测试运行在进程退出时报 “QThread: Destroyed while thread is still running” | 未复现（当时 shell 残留指向旧环境的 `QT_PLUGIN_PATH`） | 退出时可能崩溃 | GUI 测试守护：运行中销毁 QThread/QProcess 即失败 | 已加守护 | `tests/yuem/gui/conftest.py` |
| F-13 | 重力+磁法联合反演在给定种子下不可复现 | SimPEG ≥ 0.23 的 `PairedBetaEstimate_ByEig` 用自身 `seed`，上游只设了全局种子 | 同一种子两次运行结果相差 2.6% | 种子直接赋给 directive，保留全局设种兼容旧版 | 已修复（P-0006，可回馈） | `tests/yuem/test_rng.py`；上游原代码对比 |
| F-14 | 三维克里金的变差函数搜索与训练/验证划分不可复现 | 使用全局 `np.random` | 结果随运行变化 | 显式 `random_seed` 与 `default_rng` | 已修复（P-0006，可回馈） | 棘轮 global_np_random 9 → 0 |
