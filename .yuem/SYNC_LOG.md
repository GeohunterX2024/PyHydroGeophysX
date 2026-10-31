# 上游同步日志

每次从 `upstream` 挑拣合并都追加一节，按时间倒序。流程见 `docs/yuem/adr/0001-soft-fork.md` 第 4 节。

每节必须包含：

- 上游区间：`<旧 upstream 提交>..<新 upstream 提交>`
- 挑拣的提交：提交号、标题、涉及的 follow 路径
- 跳过的提交及理由（例如只改动了 own 路径、与本分叉改造冲突、上游实验性功能）
- 台账变化：删除或新增的 `PATCHES.md` 条目
- 门禁结果：fast、gui、golden、verification 各层的通过情况
- 合入确认人与日期

---

## 2026-10-31 月度同步检查（M5.4）

- 上游区间：`16930bb6b50d20973a38bdc0890c1d1a876b77d3..16930bb6b50d20973a38bdc0890c1d1a876b77d3`（`git fetch upstream main` 后 `upstream/main` 头部未变）
- 挑拣的提交：无（上游自基点以来没有新提交）
- 跳过的提交：无
- 台账变化：无
- 门禁结果：未触发同步，不需重跑；本分支门禁照常全部通过
- 工具：新增 `tools/yuem/sync_upstream.sh`（拉取、快进 `upstream` 分支、按 follow 路径列出候选提交、可选创建 `yuem/sync-YYYYMM`；不推送、不自动挑拣）
- 合入确认人与日期：不适用（无变更）

## 2026-10-31 建立分叉

- 上游区间：无（初始基点）
- 基点：`16930bb6b50d20973a38bdc0890c1d1a876b77d3`（上游 `main` 头部，2026-10-23）
- 挑拣的提交：无
- 台账变化：无
- 门禁结果：基点核对通过，见 `.yuem/baseline_diff.md`
