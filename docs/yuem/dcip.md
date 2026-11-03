# DCIP 插件（phgx-dcip）

时间域直流电阻率与激发极化（DCIP）以插件包 **phgx-dcip** 接入 PHGX，与 ERT、EM、MT、GPR 并列，位于导航“地球物理数据处理”下的“DCIP / 激发极化”。插件通过 `docs/yuem/plugins.md` 所述的公开接口注册，不修改 PHGX 源码；它是该接口的第一个完整实例。

插件仓库为私有仓库（开发检出 `~/Developer/phgx-dcip`）。用户说明见插件仓库的 `docs/dcip_user_guide.md`，架构见 `docs/architecture.md`，金标准与数值验证见 `docs/golden.md`。

## 能力

- 输入：GTEM ASCII LAS（每炮一个文件），重复炮的取舍、地形、电流声明、几何因子口径（水平距离或斜距）。
- 处理：衰减曲线与时窗充电率、电流校正（实测、校正表或由参考 .dat 反算）、地形与电极改正、三级质控（炮、测道、门值，PHGX `QCLog` 记录）、全波形去噪与标定、打包。
- 计算：2.5D 有限体积直流正演与 Cole-Cole 时间域 IP 正演；分阶段四参数反演（ρ0、m、τ、c），DOI、后验不确定度；异常体识别与 τ 剖面似然、CRLB；正演试算与参数测试。
- 结果：每次反演写出 `model_result.phgx.h5`（`ModelResultV2`），模型查看器、工程地图、GRD/XYZ 导出直接可用；另有 RES2DINV 三极 .dat、处理后 LAS、VTK、CSV/XYZ、图件编排与 HTML/PDF 报告。
- 兼容：YUEM `.yuem` 工程可整体迁入（`python -m phgx_dcip.migrate`，或页面导入步骤中的“导入 YUEM 工程…”）。

## 安装

插件需要 PHGX 0.5.0+yuem 与 Python 3.11 或 3.12。

| 方式 | 做法 |
|---|---|
| 开发 | 插件仓库 `tools/dev_env.sh`（`PHGX_ROOT` 指向本仓库检出）；环境与本仓库的 `uv.lock` 相同，PHGX 与插件均为可编辑安装 |
| 已有环境 | 插件仓库 `uv build --wheel`，在 PHGX 环境中 `pip install --no-deps dist/phgx_dcip-*.whl` |
| 桌面安装包 | `PHGX_PLUGIN_WHEELS=/path/phgx_dcip-0.4.0-py3-none-any.whl tools/yuem/build_macos_dmg.sh`；脚本在构建前确认插件登记的工作流，自检后确认冻结的 Studio 能列出它们 |

## 工作流

| 工作流 | 运行目录简称 | 作用 |
|---|---|---|
| `dcip.import` | IPIMP | LAS 目录导入为测线第 1 版 |
| `dcip.process` | IPPRC | 衰减、电流、质控、几何改正、打包，每步一个新版本 |
| `dcip.denoise` | IPDN | 全波形去噪并打包 |
| `dcip.calibrate` | IPCAL | 去噪标定（逐门 σ 放大） |
| `dcip.tc_fit` | IPTC | 全线 τ、c 参考值 |
| `dcip.forward` | IPFWD | 正演试算 |
| `dcip.param_test` | IPTST | 参数网格上的多次反演（至多 8 次） |
| `dcip.invert` | IPINV | 四参数反演 |
| `dcip.anomaly` | IPANO | 单个异常体的 τ 剖面似然与 CRLB |

全部在独立进程中运行（`python -m PyHydroGeophysX.workflows.cli run`），工程目录为根，测线版本存于工程数据库。

## 验证

- 测线 4 实测数据上 YUEM 的金标准 G1–G6 在插件中全部通过，G5、G6 的数字与 YUEM 记录一致（G6：阶段 1 秩相关 0.9949，χ² 0.6186）。
- 与 YUEM 自身输出逐元素比对：导入、衰减、电流、去噪打包完全一致；迁入的 YUEM 工程在 PHGX 中重跑同一反演，χ² 一致到 1e-10。
- 数值验证：半空间正反演、IP 恒等式、几何因子口径与 pyGIMLi 对照、与 PHGX ERT 反演交叉校核、引擎自带的 validate（对 SimPEG 与解析解）。

## 已知限制

- “ERT → 含水量”页只读 pyGIMLi 网格目录（`mesh_res.bms` 等），不接受 `ModelResultV2`，DCIP 的 ρ0 暂不能直接作为其输入。
- Studio 的语言切换在重启后生效，插件随之切换。
