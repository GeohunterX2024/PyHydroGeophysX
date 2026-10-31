# ADR 0001：以软分叉方式维护 PyHydroGeophysX

- 状态：已接受
- 日期：2026-10-31

## 1. 背景

PyHydroGeophysX（PHGX）0.5.0 是本项目的主框架。要把它做成工业级软件，需要对平台层和界面层做大量改造：异常体系、日志、分层约束、插件化、中文化、拆分超大页面等。上游仍在频繁更新算法模块，`CHANGELOG.md` 的未发布部分已有几十条改动。

可选方案：

1. 最小补丁：只在 PHGX 加钩子，所有改造放外部扩展包。同步上游最省事，但改造深度受限，无法拆分页面或统一异常和日志。
2. 硬分叉：从 0.5.0 起独立发展。改造自由，但失去上游后续的算法更新。
3. 软分叉：平台层和界面层自主演进，算法层继续跟随上游，按路径挑拣合并。

## 2. 决策

采用方案 3，软分叉。

## 3. 仓库约定

- 本地仓库：`/Users/geohunterx/Desktop/YUEM_Software/PHGX`，与 YUEM 仓库平级。
- `origin`：`https://github.com/GeohunterX2024/PyHydroGeophysX`（fork）。
- `upstream`：`https://github.com/geohang/PyHydroGeophysX`，推送地址设为 `DISABLED`，防止误推。
- 分叉基点：`16930bb6b50d20973a38bdc0890c1d1a876b77d3`，核对记录见 `.yuem/baseline_diff.md`。

分支：

- `upstream`：只镜像 `upstream/main`，禁止本地提交。
- `yuem/main`：分叉主线，fork 的默认分支。
- `yuem/<阶段>-<主题>`：功能分支，门禁通过并经项目负责人确认后合入 `yuem/main`。
- `yuem/sync-YYYYMM`：上游同步分支。

上游自带的 `.github/workflows/*.yml` 只在 `main` 上触发，保持原样；本分叉的 CI 在 `.github/workflows/yuem-ci.yml`。

## 4. 同步流程（每月一次）

1. `git fetch upstream`，把 `upstream` 分支快进到 `upstream/main`。
2. 记下旧头部 `OLD` 和新头部 `NEW`，对每个 follow 路径执行 `git log --oneline OLD..NEW -- <路径>`。
3. 从 `yuem/main` 新建 `yuem/sync-YYYYMM`，逐个 `git cherry-pick -x` 需要的提交；只改动 own 路径的提交跳过，必要时人工移植。
4. 冲突以上游为准解决，本地补丁按 `.yuem/PATCHES.md` 重新应用；上游已修复的补丁从台账删除。
5. 运行全部门禁，加跑 golden 和 verification 两层（`tools/yuem/gates.sh --full`）。
6. 在 `.yuem/SYNC_LOG.md` 追加记录，经确认后合入。

## 5. 代码归属

归属清单在 `.yuem/ownership.toml`，分四类：

- own：本分叉维护，例如 `qt_apps/`、`workflows/`、新增的平台模块、`packaging/`。
- follow：跟随上游，例如 `forward/`、`inversion/`、`data_processing/`；本地改动必须登记 `.yuem/PATCHES.md`。
- shared：仓库级文件，例如 `pyproject.toml`、`.gitignore`；本地改动同样登记。
- frozen：保持上游原样，例如 `agents/`、`llm/`；禁止改动。

适配逻辑（异常转换、日志桥接、溯源补齐）一律放在 own 层，不改 follow 层源码。

## 6. 回馈上游

与业务无关的通用改进（插件注册、依赖修复、随机数确定性、跨平台修复、环境自检）整理成独立分支，从 fork 向上游发 PR。每个 PR 单独征得项目负责人同意。被上游合并后，下次同步时删除对应台账条目。

## 7. 影响

- 平台层改造不受上游节奏约束。
- 同步成本与台账条数成正比，台账条数是长期跟踪指标。
- 本分叉不向上游推送任何内容。
