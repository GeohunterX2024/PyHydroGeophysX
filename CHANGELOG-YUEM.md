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
- 新增 `uv.lock` 与 `tools/yuem/dev_env.sh`：显式使用 PyPI；锁定平台按 pgcore 轮子实际覆盖限定；自动修复 macOS 上 pgcore 缺 `libblas.3.dylib` 与解释器缺 CA 证书两个问题。

### 修复（可回馈上游）

- `pftools` 移到独立的 `parflow-tools` extra：它硬锁 `pyyaml==6.0.1`，且部分版本元数据被 pip 拒收，导致 `geophysics` 整组无法安装。
- `gpu`、`all` 中的 CuPy 与 `adtlert` extra 中的 ADTLERT 加 `sys_platform != 'darwin'` 标记，`pip install ".[all]"` 在 macOS 上可以安装。
