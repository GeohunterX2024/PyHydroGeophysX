# ADR 0002：开发用 uv，Full 桌面打包用 conda-forge 加 conda-lock

- 状态：已接受
- 日期：2026-10-31

## 1. 背景

- 上游只给出宽松的依赖范围（例如 `pandas>=1.3.0` 不设上限），没有锁文件，环境不可复现。
- 上游 Full 桌面构建在 CI 中用 conda-forge 和 gimli 通道安装 pyGIMLi、VTK、Qt，再用 pip 装 SimPEG 和 PyInstaller（见 `.github/workflows/build-desktop.yml`）。conda-forge 的 VTK 依赖 conda-forge 的 Qt，与 PyPI 的 PySide6 不能混用。
- 本机 2026-10-30 用 python.org Python 3.12 加 PyPI 轮子安装时遇到三个问题：
  1. `geophysics` extra 中的 `pftools` 元数据无效，整组依赖解析失败；
  2. `pgcore` 1.6.0 的 macOS arm64 轮子缺少 `libblas.3.dylib`，pyGIMLi 无法导入；
  3. python.org Python 没有配置 SSL 证书，访问 HTTPS 失败。
- 本机 pip 默认索引是清华镜像，曾出现 SSL 中断。

## 2. 决策

1. 开发和测试环境用 uv 管理，依赖来自 PyPI，锁文件为仓库根目录的 `uv.lock`。入口脚本 `tools/yuem/dev_env.sh`。
2. Full 桌面打包环境沿用上游的 conda-forge 加 gimli 通道，用 conda-lock 锁定 osx-arm64、win-64、linux-64 三个平台，文件在 `packaging/conda/`。
3. 两套环境严格分离：开发环境在仓库的 `.venv`，打包环境是独立的 conda 环境 `phgx-full`，不在同一环境中混装 pip 和 conda 的科学栈。
4. 索引一律显式指定：uv 用 `https://pypi.org/simple`，conda 用 `conda-forge` 和 `gimli`。
5. 上述三个本机问题的处理固化到脚本：
   - `pftools` 移到独立的 `parflow-tools` extra（`.yuem/PATCHES.md` 登记，可回馈上游）；
   - `dev_env.sh` 检测 `pgcore/.dylibs/libblas.3.dylib`，缺失时链接到同目录的 `libopenblas.0.dylib`；
   - `dev_env.sh` 和 `phgx-doctor` 检查证书，缺失时把 `SSL_CERT_FILE` 指向 certifi。

## 3. Python 版本

- 主力 3.12；CI 同时测 3.11（上游 CI 版本）和 3.12。
- `requires-python` 保持上游的 `>=3.10`。

## 4. 影响

- 新成员一条命令建好开发环境，依赖版本可复现。
- 依赖升级通过更新锁文件完成，在 PR 中可审查。
- 打包环境与上游 CI 一致，减少与上游打包脚本的差异。
