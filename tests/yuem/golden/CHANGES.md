# 金标准变更记录

每次更新金标准都在此追加：日期、原因、各用例的最大变化。

- 2026-10-31（PyHydroGeophysX 0.5.0+yuem.1）：初始金标准：基点 16930bb 加分叉修复（SimPEG 兼容 P-0004、ERT 区域映射 P-0005）后的结果
  - `ert_single`：new
  - `ert_timelapse`：new
  - `srt`：new
  - `fdem_sounding`：new
  - `tem_lci_line`：new
  - `mt_occam1d`：new
  - `mt_processing`：new
  - `gravity_inversion`：new
  - `fdem_tdem_joint`：new
  - `gravity_processing`：new
- 2026-10-31（PyHydroGeophysX 0.5.0+yuem.1）：Gravity stations offset up to 0.5 m from a perfect grid: on the regular grid the Delaunay triangulation of the gridding was ambiguous, and Linux and macOS resolved it differently (up to 51 % in the observed grid). F-19.
  - `gravity_processing`：max relative change 3.00e+02 (gravmag_residual_csv.residual)
- 2026-10-31（PyHydroGeophysX 0.5.0+yuem.1）：Gravity stations offset up to 0.5 m from a perfect grid (the shared station layout of the gravity cases), see gravity_processing above. F-19.
  - `gravity_inversion`：max relative change 3.30e+01 (object.model3d)
