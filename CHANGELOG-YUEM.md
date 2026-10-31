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
