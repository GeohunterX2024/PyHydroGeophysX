# 补丁台账（follow / shared 路径的本地改动）

凡是改动 `.yuem/ownership.toml` 中 `follow` 或 `shared` 类路径，必须在下表登记一条；`frozen` 路径禁止改动。
`tools/yuem/patch_ledger.py --check` 会把 `upstream` 分支到当前提交的差异与本表逐文件核对，未登记的改动视为门禁失败。

规则：

- 一条补丁可以覆盖多个文件，`文件` 列用 `<br>` 或逗号分隔，路径相对仓库根目录。
- `可回馈` 取值：`是`（与业务无关的通用修复，计划向上游提 PR）、`否`（本分叉特有）。
- `状态` 取值：`生效`、`已回馈`（上游已合并，同步后本条删除）、`已撤销`。
- 条数只减不增是长期目标：回馈上游被合并、或上游自行修复后，同步时删除对应条目，并在 `SYNC_LOG.md` 记录。

| 编号 | 文件 | 改动摘要 | 原因 | 可回馈 | PR | 状态 |
|---|---|---|---|---|---|---|
| P-0001 | .gitignore | 末尾追加 YUEM 段：放行 `.yuem/`、`docs/yuem/`、`tests/yuem/` 下的 Markdown 和 `CHANGELOG-YUEM.md`；忽略 ruff、mypy、import-linter、benchmark 缓存 | 上游默认忽略全部 `*.md`，分叉的治理记录必须入库 | 否 | | 生效 |
