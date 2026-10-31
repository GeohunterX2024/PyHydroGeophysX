# ADR 0003：质量门禁与棘轮指标

- 状态：已接受
- 日期：2026-10-31

## 1. 背景

基点 0.5.0 的工程基线（`.yuem/metrics/baseline-0.5.0.json`）：

- 18.8 万行代码，公开测试 4 个文件、197 个测试；
- 没有 ruff、mypy、pytest 配置；
- 808 处宽泛异常捕获，221 处 `print(`，713 处 `noqa` 或 `type: ignore`；
- 17 个文件超过 2000 行，`logging.getLogger` 只出现 1 次；
- CI 只在 Ubuntu 和 Windows 上用 Python 3.11 测试。

一次性清理不现实，也会与上游严重冲突。需要一种既能阻止恶化、又允许逐步改善的机制。

## 2. 决策

### 2.1 每个 PR 的完成定义

本地 `tools/yuem/gates.sh`（pre-commit 调用其中的快速部分）与 CI `yuem-ci.yml` 执行同一套检查：

1. `ruff format --check` 与 `ruff check`。存量目录只启用当前能通过的规则；own 新模块启用完整规则集。
2. own 新模块通过 `mypy --strict`。
3. 快速层测试：`pytest -m "not slow and not golden and not numerical"`。
4. import-linter 分层契约（M2.2 起）。
5. 棘轮：`python tools/yuem/metrics.py --check`。
6. 新增或改动的 Python 文件不得超过 1500 行（存量超长文件只要求不变长）。横切的可靠性改造（例如 M2.4 给吞掉的异常加日志）不可避免地让存量超长文件增加几行时，在 `.yuem/metrics_allowlist.toml` 的 `[file_length]` 中登记该文件的行数上限并写明理由；上限只降不升，文件拆到 1500 行以内后删除条目。新增条目与基线变更同等审查。
7. 补丁台账：`python tools/yuem/patch_ledger.py --check`。
8. `CHANGELOG-YUEM.md` 有对应条目。

合入 `yuem/main` 前加跑：`pytest -m "golden or numerical"`。

### 2.2 棘轮规则

`metrics.py` 统计下列指标并与 `.yuem/metrics/baseline-0.5.0.json` 比较：

- 只降不升：宽泛异常捕获、`print(`、`noqa` 与 `type: ignore`、超过 2000 行的文件数、`os.environ` 读取、全局 `np.random` 调用、进程内计算模块数、分层例外数、own 代码中的静默宽泛捕获（`own_silent_broad_except`）。
- 只升不降：测试函数数量、`logging.getLogger` 使用数。

静默宽泛捕获指 `except Exception`（或裸 `except`）的处理块既不重新抛出、不引用异常对象，也不写日志或告知用户。界面代码中的宽泛捕获有其道理（Qt 槽函数里的异常不能冒到事件循环），但必须留下痕迹；该指标在 M2 降为 0 后保持为 0，由 AST 统计（`metrics.silent_broad_excepts`）。

改善后用 `metrics.py --update-baseline --reason "<原因>"` 下调基线，原因写入 `.yuem/metrics/CHANGES.md`。基线不允许上调；确需上调（例如同步上游带入新代码）时，同样记录原因，并在合入时由负责人确认。

### 2.3 测试分层标记

- 无标记：快速单元测试，每次提交运行。
- `gui`：需要 Qt，offscreen 运行。
- `slow`：单例超过 10 秒。
- `numerical`：数值验证集（解析解或交叉代码对照）。
- `golden`：回归金标准。
- `network`：需要网络。
- `packaging`：需要打包产物。

## 3. 影响

- 新代码必须达到完整标准，存量代码不会变差。
- 指标下降的过程可追溯。
