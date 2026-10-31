# 数值验证报告

由 `python tools/yuem/verification_report.py` 生成，请勿手工编辑。用例在 `tests/yuem/verification/`，标记 `numerical`。

- 生成日期：2026-10-31
- 环境：PyHydroGeophysX 0.5.0+yuem.1 (v0.5.0-57-gfdd4c79-dirty); Python 3.12.6 on Darwin arm64; numpy 2.5.4, scipy 1.18.1, pygimli 1.6.1, pgcore 1.6.0, simpeg 0.26.0, empymod 2.6.1; BLAS accelerate unknown
- 结果：15/15 通过

| 编号 | 方法 | 用例 | 被测实现 | 参考解 | 误差指标 | 实测 | 容差 | 结论 |
|---|---|---|---|---|---|---|---|---|
| V-ERT-01 | ERT 2.5D | ERT homogeneous half-space, Wenner, 48 electrodes | PHGX ERTForwardModeling (pyGIMLi core) | analytic: apparent resistivity equals 100 ohm-m | max relative error of rhoa | 1.41e-03 | 5e-03 | 通过 |
| V-ERT-02 | ERT 2.5D | ERT two-layer earth (100/10 ohm-m, h = 5 m), Wenner, per-cell model | PHGX ERTForwardModeling (pyGIMLi core) | image series, Telford et al. (1990) | max relative error of rhoa | 2.96e-03 | 1e-02 | 通过 |
| V-ERT-03 | ERT 3D | ERT 3D, per-cell layered model on a mesh with a marker-1 outer region | PHGX ERTForwardModeling (as used by ert3d.forward) | pyGIMLi ERTModelling with the region manager ignored (as ert.simulate) | max relative difference of rhoa | 0.00e+00 | 1e-10 | 通过 |
| V-ERT-04 | ERT 3D | ERT 3D homogeneous half-space, surface grid at 100 m elevation | PHGX create_3d_ert_data_container + ERTForwardModeling (as used by ert3d.forward) | analytic: apparent resistivity equals 100 ohm-m | max relative error of rhoa | 2.80e-10 | 1e-03 | 通过 |
| V-FDEM-01 | FDEM 1D | FDEM vertical magnetic dipole, 30 m height, 10 m offset, 100 ohm-m half-space, 0.1-10 kHz | PHGX em1d.fdem_forward (SimPEG) | empymod (cross-code) | max relative error of secondary Hz | 2.81e-04 | 1e-03 | 通过 |
| V-FDEM-02 | FDEM 1D | FDEM vertical magnetic dipole over 50/200/20 ohm-m (10/20 m), 0.1-10 kHz | PHGX em1d.fdem_forward (SimPEG) | empymod (cross-code) | max relative error of secondary Hz | 2.39e-04 | 1e-03 | 通过 |
| V-GRAV-01 | Gravity | Gravity of a 100 km wide, 10 m thick prism under its centre | PHGX forward.gravmag.gravity_prism (Nagy 1966) | analytic: infinite Bouguer slab 2 pi G drho t | relative error of gz | 2.70e-04 | 1e-03 | 通过 |
| V-GRAV-02 | Gravity | Gravity of a 2 m cube and an equal-mass sphere at 50 m depth, 200 m profile | PHGX gravity_prism and gravity_sphere | analytic point mass G M z / r^3 | max relative error of gz (both bodies) | 1.87e-07 | 1e-03 | 通过 |
| V-MAG-01 | Magnetics | Total-field anomaly of an induced sphere at the magnetic pole (I = 90 deg) | PHGX forward.gravmag.magnetic_dipole | analytic vertical dipole field mu0 m (2z^2 - x^2) / (4 pi r^5) | max absolute error / peak anomaly | 2.30e-16 | 1e-10 | 通过 |
| V-MT-01 | MT 1D | MT 1D homogeneous half-space, 100 ohm-m, 1 mHz-1 kHz | PHGX data_processing.mt.impedance_1d | analytic: rho_a = 100 ohm-m, phase = 45 deg | max relative error of rho_a and phase | 5.68e-16 | 1e-10 | 通过 |
| V-MT-02 | MT 1D | MT 1D three layers (100/10/1000 ohm-m, 500/2000 m), 1 mHz-1 kHz | PHGX data_processing.mt.impedance_1d | independent impedance recursion, Wait (1954) | max relative error of |Z| and absolute error of |phase| (rad) | 8.05e-16 | 1e-09 | 通过 |
| V-PET-01 | Petrophysics | Waxman-Smits water content -> resistivity -> water content (sigma_sur = 0.0) | PHGX petrophysics.resistivity_models | identity (forward then inverse) | max absolute error of water content | 1.11e-16 | 1e-08 | 通过 |
| V-PET-02 | Petrophysics | Waxman-Smits water content -> resistivity -> water content (sigma_sur = 0.002) | PHGX petrophysics.resistivity_models | identity (forward then inverse) | max absolute error of water content | 8.03e-14 | 1e-08 | 通过 |
| V-SRT-01 | SRT | SRT two-layer refraction (500/2000 m/s, h = 10 m), 51 geophones | PHGX SeismicForwardModeling (pyGIMLi Dijkstra) | analytic first arrival: direct wave and head wave | max relative error of first-arrival time | 1.28e-02 | 2e-02 | 通过 |
| V-TDEM-01 | TDEM 1D | TDEM central loop (a = 10 m) on a 100 ohm-m half-space, step-off Bz, 10 us-1 ms | PHGX em1d.tdem_forward (SimPEG) | analytic, Ward & Hohmann (1988) eq. 4.98 | max relative error of Bz | 5.86e-04 | 2e-03 | 通过 |

## 说明

- **V-ERT-02**：Before the fix of 2026-10-31 a per-cell model on a mesh with a marker-1 region was mapped onto the wrong cells (error up to 284 %).
- **V-ERT-03**：Regression guard for the region-mapping fix (台账 P-0005).
- **V-ERT-04**：With singularity removal a homogeneous model's response is the analytic primary field, so the error is that of the geometric factor alone. Before the fix of 2026-10-31 PyGIMLi's factor treated the array as buried 100 m deep and rhoa was about 200 ohm-m (F-09, 台账 P-0007).
- **V-FDEM-01**：Reference: reflected field only (xdirect=None) with the 801-point Anderson filter; empymod's shorter filters disagree with it by several percent above ~5 kHz at this geometry, so the band is limited to 10 kHz.
- **V-FDEM-02**：Reference: reflected field only (xdirect=None) with the 801-point Anderson filter; empymod's shorter filters disagree with it by several percent above ~5 kHz at this geometry, so the band is limited to 10 kHz.
- **V-GRAV-01**：The finite width contributes about t/w ~ 1e-4.
- **V-SRT-01**：Shortest-path ray tracing on a 2 m^2 mesh; the error is the graph discretisation.
- **V-TDEM-01**：Loop 1 cm above ground; the analytic solution is for a loop on the surface.
