# 回馈上游的候选 PR（M5.5）

每个 PR 必须先征得负责人同意，再向 `geohang/PyHydroGeophysX` 提交。下表只列出改动范围与证据，不代表已提交。提交后，在 `.yuem/PATCHES.md` 对应条目中填写 PR 链接；上游合入后删除该条目，台账条数随之减少。

做法：从 `refs/heads/upstream` 新建分支，只带入该候选涉及的文件改动，再跑上游自带的测试（`tests/`）与相关的 YUEM 测试作为证据。PR 描述使用英文，写明问题、根因、修复与复现方法。

| 序号 | 候选 | 涉及文件 | 问题与证据 | 依赖 | 状态 |
|---|---|---|---|---|---|
| 1 | ERT 正演区域映射修复 | `forward/ert_forward.py` | 网格含标记 1 区域时，逐单元模型被映射到错误单元：二维两层模型误差 284%，三维正演合成数据误差 90%（F-08，P-0005；数值验证 V-ERT-02/03） | 无 | 待确认 |
| 2 | SimPEG 0.26 兼容 | `inversion/gravmag.py`、`inversion/fdem_inversion.py`、`inversion/tdem_inversion.py`、`data_processing/mt/inversion2d.py`，以及兼容辅助函数 | 按上游声明的 `simpeg>=0.24,<1.0` 新装 0.26 时，重磁、FDEM/TDEM 类反演与 MT 二维反演报错（F-07，P-0004；冒烟测试） | 上游无 `_internal/simpeg_compat.py`，需随 PR 一并提交 | 待确认 |
| 3 | 随机数可复现 | `inversion/joint_gravity_magnetics.py`、`core/kriging_3d.py` | 重磁联合反演在同一种子下两次运行相差 2.6%；三维克里金使用全局随机数（F-13/F-14，P-0006；`tests/yuem/test_rng.py`） | 无 | 待确认 |
| 4 | 依赖修复：`pftools` 单列为 extra，CuPy/ADTLERT 加平台标记 | `pyproject.toml`（仅这两处） | `.[geophysics]` 因 `pftools` 硬锁 PyYAML 而解析失败；`.[all]` 在 macOS 上不可安装（F-01/F-02，P-0002 ②③） | 无 | 待确认 |
| 5 | rustsolve 打包脚本不再改坏 conda 缓存 | `packaging/rustsolve/apply.py` | 原地写入被 conda 硬链接的文件，同一缓存创建的所有环境都通不过校验（F-06） | 无 | 待确认 |
| 6 | 插件注册中心 | `plugins.py`、`_internal/plugin_loader.py`，以及工作流注册表与页面表的加载钩子 | 外部包可通过入口点加入页面、工作流、读取器（`docs/yuem/plugins.md`，`tests/yuem/test_plugins.py`） | 改动上游 `qt_apps/modules/__init__.py` 与 `workflows/registry.py`，需与上游协商接口 | 待确认 |
| 7 | macOS 测试矩阵 | `.github/workflows/`（上游 CI） | 上游 CI 只覆盖 Ubuntu 与 Windows；macOS arm64 上 pgcore 只有 cp312 轮子、需 macOS 26，且 libblas 链接缺失（F-03/F-04），应在 CI 中暴露 | 需上游同意增加 runner | 待确认 |
| 8 | 中文路径与中文界面 | 冒烟测试中的中文目录用例；`qt_apps/i18n.py` 与翻译目录 | 工作流在含中文与空格的目录下运行（`tests/yuem/smoke`）；界面中文化（M4.1） | 中文化改动面大，建议拆成“翻译基础设施”与“中文目录”两个 PR | 待确认 |
| 9 | 环境自检 `phgx-doctor` | `doctor.py`、`pyproject.toml` 脚本入口、Studio “帮助 > 环境检查” | 一条命令检查 Python、pyGIMLi 核心、证书、Qt、VTK、中文字体、工程目录与可选引擎（`tests/yuem/test_doctor.py`） | 无 | 待确认 |

优先级建议：1、2、3 是数值与可用性问题，影响所有用户，宜最先提交；4、5 改动小，可与前三项同批提交；6 至 9 需要先与上游讨论接口与范围。
