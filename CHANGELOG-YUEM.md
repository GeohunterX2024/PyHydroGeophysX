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

- 棘轮白名单 `.yuem/metrics_allowlist.toml`：只收边界代码（CLI 前端、诊断边界），逐文件写明理由，命中数单独报告。

- 运行溯源 `PyHydroGeophysX/_internal/provenance.py`：每个工作流结果的 `provenance` 记录分叉版本、`git describe`、Python 与平台、关键库版本（取自安装元数据，不读模块 `__version__`，因为 pyGIMLi 的 `__version__` 反映的是当前目录的 git 状态）、BLAS 实现与线程数、种子、输入校验和、参数摘要；Studio 页面在进程内计算的运行由 `ResultsStore.finish_run` 补记环境。
- `pyhydrogeophysx-workflow env-diff <run.json>` 比较记录环境与当前环境；`run` 重跑时若 recipe 旁有 `run.json`，自动提示环境差异。
- 环境自检 `phgx-doctor`（`PyHydroGeophysX/doctor.py`）：Python、包、核心库、pyGIMLi 核心（含 macOS libblas 缺失检测）、证书、Qt 平台插件、VTK/OpenGL、中文字体、工程目录空间与写权限、可选引擎；退出码 0/1/2。Studio“Help > Environment Check…”运行同一套检查。

### 修复（可回馈上游）

- SimPEG 0.26 兼容：`gravmag.invert`、`FDEMInversion`、`TDEMInversion`、MT 二维反演使用了 SimPEG 0.26 已删除的 `maxIterCG`/`tolCG`，在上游声明的依赖范围内新装即报错；改由 `_internal/simpeg_compat.cg_keywords` 按版本选择参数名（台账 P-0004）。冒烟测试发现。
- `packaging/rustsolve/apply.py`：替换 libgimli 前先删除目标文件。conda 以硬链接把包缓存中的文件装进环境，原地写入会改坏缓存中的 pgcore，之后从同一缓存创建的环境都通不过校验（本机复现）。

- `pftools` 移到独立的 `parflow-tools` extra：它硬锁 `pyyaml==6.0.1`，且部分版本元数据被 pip 拒收，导致 `geophysics` 整组无法安装。
- `gpu`、`all` 中的 CuPy 与 `adtlert` extra 中的 ADTLERT 加 `sys_platform != 'darwin'` 标记，`pip install ".[all]"` 在 macOS 上可以安装。
