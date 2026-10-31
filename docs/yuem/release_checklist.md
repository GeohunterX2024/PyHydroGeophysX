# 发布清单（M5.2）

发布由 `tools/yuem/release.sh` 串起，每一步失败即停止。推送标签、上传 GitHub Release 必须经负责人确认后，才加 `--publish` 执行。

## 1. 版本与记录

- [ ] 版本号形如 `<上游版本>+yuem.<N>`，`pyproject.toml` 与 `PyHydroGeophysX/__init__.py` 一致（脚本核对）
- [ ] `CHANGELOG-YUEM.md` 有该版本条目（脚本核对）
- [ ] `.yuem/PATCHES.md` 台账与 `.yuem/SYNC_LOG.md` 同步记录为最新
- [ ] 工作区无未提交改动（脚本核对）
- [ ] 标签：`yuem-<上游版本>.<N>`，如 `0.5.0+yuem.1` → `yuem-0.5.0.1`

## 2. 门禁（`tools/yuem/gates.sh --full`）

- [ ] 静态：ruff（基线与严格规则）、ruff format、mypy --strict、import-linter 分层契约、棘轮指标、翻译检查、补丁台账与变更记录
- [ ] 测试：fast、gui、slow、numerical、golden 各层
- [ ] `tools/yuem/verification_report.py --check`：数值验证报告与代码一致
- [ ] 性能：`tools/yuem/perf.py check` 无超过 20% 的变慢（告警须说明原因后方可发布）

## 3. 打包与冒烟

- [ ] macOS：`PHGX_RELEASE_AUDIT=1 PHGX_RELEASE_STRICT=1 tools/yuem/build_macos_dmg.sh`
  - 每一步均有校验：锁定的 conda 环境（含 rustsolve 校验）、PyInstaller、签名校验、`--self-test`，以及挂载镜像后再次 `--self-test`
  - `packaging/release_audit.py stage` 在镜像根目录写入 `BUILD_INFO.txt`（构建信息与组件清单）、`SOURCE_CODE.md` 与 `LICENSES/`，审计报告保存为 `dist/<名称>.audit.md`
  - 输出 `dist/<名称>.dmg` 与 `.sha256`
- [ ] Windows、Linux：沿用上游 `build-desktop.yml` 的打包与 `release_audit.py stage/verify/replace` 流程（需在对应平台的 CI 上运行）
- [ ] 安装冒烟：把镜像中的应用拖入 Applications，首次打开；在“帮助 > 环境检查”中确认无错误；切换语言后重启，确认中文界面显示正常

## 4. 签名与公证（M5.1）

| 平台 | 条件 | 做法 |
|---|---|---|
| macOS | 有 Apple Developer 账号 | `PHGX_SIGN_IDENTITY="Developer ID Application: <名称> (<TEAMID>)"`：由内到外逐个签名包内 Mach-O 文件，启用 hardened runtime 并加时间戳，授权文件为 `packaging/macos/entitlements.plist`（numba JIT、加载随包第三方库）。再设 `PHGX_NOTARY_PROFILE=<配置名>`（先执行 `xcrun notarytool store-credentials <配置名> --apple-id … --team-id …`）：签名镜像、`notarytool submit --wait`、`stapler staple`，最后 `spctl` 核验 |
| macOS | 无账号（当前） | ad-hoc 签名；镜像内《安装说明》写明首次打开的方法（按住 Control 点按“打开”，或执行 `xattr -cr`） |
| Windows | 有代码签名证书 | 用 `signtool sign /fd sha256 /tr <时间戳服务> /td sha256 /f <证书> /p <口令>` 对 `PyHydroGeophysX-Studio.exe` 及安装包签名，然后 `signtool verify /pa` 核验 |
| Windows | 无证书（当前） | 不签名，发布说明中注明 SmartScreen 提示的处理方法 |

## 5. 发布

- [ ] `tools/yuem/release.sh` 生成 `dist/RELEASE_NOTES-<标签>.md`（变更指向、签名方式、sha256），并打印 `gh release create … --draft` 命令
- [ ] 负责人确认后执行 `tools/yuem/release.sh --publish`，在 `GeohunterX2024/PyHydroGeophysX` 上创建草稿 Release，附 DMG 与 sha256
- [ ] 核对草稿后发布；把 `yuem/main` 的发布提交与标签记入 `CHANGELOG-YUEM.md`
