# 棘轮基线变更记录

- 2026-10-31: 初始基线：上游 16930bb（0.5.0）的工程指标，脚本口径
- 2026-10-31: os_environ 改为只统计非 own 路径（算法层）：own 层在平台边界读取环境变量属正常；33 -> 23
- 2026-10-31: 新增 .yuem/metrics_allowlist.toml（CLI 前端与诊断边界，逐文件写明理由）：print_calls 315 -> 310（workflows/cli.py 上游原有 5 处 CLI 输出移入白名单），其余不变；白名单命中单独报告
- 2026-10-31: 新增指标 layer_exceptions（.importlinter 中容忍的上游跨层依赖条数）：初值 4
- 2026-10-31: M2.3/M2.4：own 代码中的静默宽泛捕获 144 -> 0（每处改为带堆栈写入应用日志）；CLI 中 3 处 psutil 捕获收窄；stall_watch 改用 logging；5 个 own 文件的协议输出与 CLI 输出列入白名单并写明理由。broad_except 805 -> 800，print_calls 310 -> 299，suppressions 713 -> 708，logging_getlogger 2 -> 48（改为只升不降）；新增只降不升指标 own_silent_broad_except，初值 0
