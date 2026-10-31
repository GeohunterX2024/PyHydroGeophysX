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
| P-0002 | pyproject.toml | ① 版本号改为 `0.5.0+yuem.1`；② `pftools` 移出 `geophysics` 和 `all`，新增 `parflow-tools` extra；③ `gpu`、`all` 中的 `cupy-cuda12x` 与 `adtlert` extra 中的 `adtlert` 加 `sys_platform != 'darwin'` 标记；④ `dev` extra 与 `all` 中的 black、flake8 换成 ruff、mypy、import-linter、pytest-qt、pytest-benchmark、hypothesis、empymod，新增同内容的 `[dependency-groups] dev`；⑤ 末尾追加 `[tool.uv]`（PyPI 索引、按 pgcore 轮子覆盖限定的锁定平台、`pygimli>=1.6.1` 锁定约束）以及 ruff、pytest、mypy、coverage 配置段 | ① 分叉版本可识别；② pftools 硬锁 `pyyaml==6.0.1`（无 3.13/3.14 轮子，与需要新版 PyYAML 的包冲突），1.3.2–1.3.5 元数据被 pip 拒收，导致整组 extra 解析失败，而 ParFlow 读取器有不依赖 pftools 的 PFB 后备；③ CuPy 与 ADTLERT 没有 macOS 轮子，上游 `all` 在 Mac 上不可安装；④⑤ ADR 0002、0003 的工具链，pygimli 1.5.5 是不含 pgcore 的纯 Python 轮子 | ②③ 是；①④⑤ 否 | | 生效 |
| P-0003 | PyHydroGeophysX/__init__.py | `__version__` 改为 `0.5.0+yuem.1`，与 pyproject 一致 | 运行溯源和“关于”页显示分叉版本 | 否 | | 生效 |
