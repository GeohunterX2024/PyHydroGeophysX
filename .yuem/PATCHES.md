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
| P-0001 | .gitignore | 末尾追加 YUEM 段：放行 `.yuem/`、`docs/yuem/`、`tests/yuem/` 下的 Markdown 和 `CHANGELOG-YUEM.md`；忽略 `.conda/`（打包环境）与 ruff、mypy、import-linter、benchmark 缓存 | 上游默认忽略全部 `*.md`，分叉的治理记录必须入库 | 否 | | 生效 |
| P-0002 | pyproject.toml | ① 版本号改为 `0.5.0+yuem.1`；② `pftools` 移出 `geophysics` 和 `all`，新增 `parflow-tools` extra；③ `gpu`、`all` 中的 `cupy-cuda12x` 与 `adtlert` extra 中的 `adtlert` 加 `sys_platform != 'darwin'` 标记；④ `dev` extra 与 `all` 中的 black、flake8 换成 ruff、mypy、import-linter、pytest-qt、pytest-benchmark、hypothesis、empymod，新增同内容的 `[dependency-groups] dev`；⑤ 末尾追加 `[tool.uv]`（PyPI 索引、按 pgcore 轮子覆盖限定的锁定平台、`pygimli>=1.6.1` 锁定约束）以及 ruff、pytest、mypy、coverage 配置段；⑥ `[project.scripts]` 新增 `phgx-doctor` | ① 分叉版本可识别；② pftools 硬锁 `pyyaml==6.0.1`（无 3.13/3.14 轮子，与需要新版 PyYAML 的包冲突），1.3.2–1.3.5 元数据被 pip 拒收，导致整组 extra 解析失败，而 ParFlow 读取器有不依赖 pftools 的 PFB 后备；③ CuPy 与 ADTLERT 没有 macOS 轮子，上游 `all` 在 Mac 上不可安装；④⑤ ADR 0002、0003 的工具链，pygimli 1.5.5 是不含 pgcore 的纯 Python 轮子 | ②③ 是；①④⑤ 否 | | 生效 |
| P-0003 | PyHydroGeophysX/__init__.py | `__version__` 改为 `0.5.0+yuem.1`，与 pyproject 一致 | 运行溯源和“关于”页显示分叉版本 | 否 | | 生效 |
| P-0004 | PyHydroGeophysX/inversion/gravmag.py<br>PyHydroGeophysX/inversion/fdem_inversion.py<br>PyHydroGeophysX/inversion/tdem_inversion.py<br>PyHydroGeophysX/data_processing/mt/inversion2d.py | SimPEG 优化器的 CG 参数改由 `_internal/simpeg_compat.cg_keywords` 按构造函数签名选择（`cg_maxiter`/`cg_rtol` 或旧的 `maxIterCG`/`tolCG`） | SimPEG 0.25 改名、0.26 删除旧参数名；上游声明 `simpeg>=0.24,<1.0`，按此新装 SimPEG 0.26 时重磁反演、FDEM/TDEM 类反演与 MT 二维反演直接报 `NotImplementedError`（冒烟测试发现） | 是 | | 生效 |
| P-0005 | PyHydroGeophysX/forward/ert_forward.py | `ERTForwardModeling` 新增 `_operator_for()`：模型长度等于区域参数数时用原算子，等于单元数时用忽略区域管理器的逐单元算子（同 `ert.simulate`），两者都不符时报错；`forward` 与 `forward_and_jacobian` 经它取算子 | 网格含标记 1 区域（pyGIMLi 视为背景，如三维网格的外围区）时，逐单元模型被静默映射到错误单元：二维两层模型误差达 284%，三维分层模型（`ert3d.forward` 的合成数据）误差达 90%（数值验证 V-ERT-02/03 发现） | 是 | | 生效 |
| P-0006 | PyHydroGeophysX/inversion/joint_gravity_magnetics.py<br>PyHydroGeophysX/core/kriging_3d.py | ① 重力+磁法联合反演把种子直接赋给 `PairedBetaEstimate_ByEig.seed`；② `optimize_variogram_model`、`krige_seismic_velocity_3d` 新增 `random_seed`，改用 `np.random.default_rng` | ① SimPEG ≥ 0.23 的该 directive 用自身 `seed` 建随机数发生器，不读全局状态，上游的全局设种对它无效：同一种子两次运行结果相差 2.6%（本机复现）；② 变差函数随机搜索与训练/验证划分使用全局随机数，结果不可复现 | 是 | | 生效 |
