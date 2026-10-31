# PHGX（YUEM 分叉）开发指南

本仓库是 PyHydroGeophysX 的 YUEM 软分叉。目标是在保留上游算法更新的前提下，把平台做成稳定、正确、专业、易维护、易移植的工业级软件。

## 1. 先读这些

- `docs/yuem/adr/0001-soft-fork.md`：分支模型、同步流程、回馈上游。
- `docs/yuem/adr/0002-toolchain-uv-conda-lock.md`：开发环境与打包环境。
- `docs/yuem/adr/0003-quality-gates.md`：每个 PR 必须通过的门禁和棘轮指标。
- `.yuem/ownership.toml`：哪些目录可以自由改（own），哪些改动必须登记（follow、shared），哪些禁止改（frozen）。

## 2. 建立开发环境

需要 uv（`brew install uv`）。在仓库根目录：

```bash
tools/yuem/dev_env.sh          # 建 .venv、按 uv.lock 安装、修复 macOS 已知问题、运行 phgx-doctor
source .venv/bin/activate
```

脚本会显式使用 PyPI 索引，不受本机 pip 镜像配置影响。

## 3. 日常开发

```bash
git switch yuem/main && git switch -c yuem/M1-<主题>   # 功能分支
# ……修改……
tools/yuem/gates.sh            # 快速门禁：格式、静态检查、类型、快速测试、棘轮、台账
tools/yuem/gates.sh --full     # 合入前：再加 gui、slow、numerical、golden 四层
```

提交信息用英文祈使句，说明“做了什么、为什么”。合入 `yuem/main` 和推送 `origin` 前须经项目负责人确认。

## 4. 改动 follow 或 shared 路径时

1. 改动尽量小，适配逻辑优先放在 own 层（例如 `workflows/` 的 handler 或 `qt_apps/workers.py` 的边界）。
2. 在 `.yuem/PATCHES.md` 登记一条，写明文件、摘要、原因、能否回馈上游。
3. `python tools/yuem/patch_ledger.py --check` 必须通过。

## 5. 测试分层

| 标记 | 内容 | 何时运行 |
|---|---|---|
| （无） | 快速单元测试 | 每次提交 |
| `gui` | Qt 页面，offscreen | 每次 PR |
| `slow` | 单例超过 10 秒 | 每次 PR |
| `numerical` | 数值验证集，`tests/yuem/verification/` | 合入前 |
| `golden` | 回归金标准，`tests/yuem/golden/` | 合入前 |
| `network` | 需要网络 | 手动 |
| `packaging` | 需要打包产物 | 发行前 |
| `benchmark` | 关键工作流计时，`tests/yuem/perf/` | 每周（CI）与发行前，经 `tools/yuem/perf.py` |

数值验证报告由 `python tools/yuem/verification_report.py` 生成到 `docs/yuem/verification.md`。

金标准更新必须说明原因：

```bash
python tools/yuem/golden.py --update --reason "<为什么结果应当改变>"
```

## 6. 指标与棘轮

```bash
python tools/yuem/metrics.py            # 打印当前指标与基线差值
python tools/yuem/metrics.py --check    # 门禁：任何指标变差即失败
```

## 7. 打包

```bash
tools/yuem/build_macos_dmg.sh           # 本机 macOS arm64 DMG，含自检和挂载复检
```

Full 打包环境见 `packaging/conda/`。

## 8. 专题文档

| 文档 | 内容 |
|---|---|
| `docs/yuem/plugins.md` | 插件：页面、工作流、读取器的注册与入口点 |
| `docs/yuem/compute_isolation.md` | 哪些计算在子进程中运行，判据与清单 |
| `docs/yuem/datastore.md` | 工程数据库 `phgx-dataset-v1`：结构、版本与外链、原始文件、适配器 |
| `docs/yuem/qc.md` | 质控：剔除、恢复、记录 |
| `docs/yuem/i18n.md` | 界面中文化与字体：约定与维护流程 |
| `docs/yuem/standards.md` | 各方法参数与行业规程的对应 |
| `docs/yuem/verification.md` | 数值验证报告（自动生成） |
| `docs/yuem/findings.md` | 改造中发现的问题与处理状态 |
| `docs/yuem/release_checklist.md` | 发布清单：门禁、打包、签名公证、发布 |
| `docs/yuem/upstream_prs.md` | 回馈上游的候选 PR |

上游同步：`tools/yuem/sync_upstream.sh`（每月，记入 `.yuem/SYNC_LOG.md`）。

## 9. 环境自检

```bash
phgx-doctor              # 0 正常，1 有警告，2 有错误
```

Studio 的“帮助”菜单中也有入口。
