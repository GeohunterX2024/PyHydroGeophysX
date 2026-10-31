# 基点核对记录（M0.1）

- 核对时间：2026-10-31
- 上游仓库：https://github.com/geohang/PyHydroGeophysX
- 分叉基点：`16930bb6b50d20973a38bdc0890c1d1a876b77d3`（2026-10-23，"Fix review findings"）
- 基点来源：`PyHydroGeophysX-main.zip` 的 zip 注释
- 核对时上游 `main` 最新提交：同一提交（基点与上游头部之间 0 个提交）
- 对照目录：`/Users/geohunterx/Desktop/YUEM_Software/YUEM-1D2D3DINVERSION/PyHydroGeophysX-main`（只读保留）

## 方法

```bash
diff -rq -x .git -x .venv -x build -x dist -x .verify_run -x '*.egg-info' \
  -x __pycache__ -x app_icon.icns -x app_icon.ico -x .DS_Store <快照> <检出>
```

## 结果

源码与该提交的检出逐文件一致。快照中多出的 3 项均为本机运行产物，不属于源码：

| 路径 | 来源 |
|---|---|
| `build_studio.log` | 2026-10-30 本机 PyInstaller 打包日志 |
| `results/streamlit_workflow/` | Studio 无工程启动时的默认结果目录（`StudioState.from_context`） |
| `examples/data/MT/test/` | 在 Studio 中把工程建在示例数据目录下产生的运行记录 |

结论：差异为空，基点核对通过。

## 附带发现

- Studio 允许把工程目录建在 `examples/` 等源码目录内，运行记录会混入源码树。M2.5（显式工程上下文）中处理。
- 上游 `.gitignore` 忽略任何名为 `lib/` 的目录以及全部 `*.spec`（仅放行 `packaging/pyinstaller_studio.spec`）。新增目录命名时需避开。
