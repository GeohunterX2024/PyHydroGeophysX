# 插件开发指南

扩展包（DCIP、LOTEM、单位自有方法）通过 `PyHydroGeophysX.plugins` 接入，不修改 PHGX 源码。实现见 `PyHydroGeophysX/plugins.py`，端到端测试见 `tests/yuem/test_plugins.py`。

## 1. 声明入口

在扩展包的 `pyproject.toml` 中：

```toml
[project.entry-points."phgx.plugins"]
dcip = "phgx_dcip.plugin:register"
```

`register` 是一个无参数的函数，在其中完成全部注册。分组 `phgx.plugins` 为通用分组；`phgx.modules`、`phgx.workflows`、`phgx.readers` 供拆分注册使用，加载方式相同。

## 2. 注册

```python
from PyHydroGeophysX.plugins import (
    ModulePage, ReaderSpec, register_module, register_reader, register_short_code, register_workflow,
)
from PyHydroGeophysX.workflows.registry import WorkflowDescriptor


def register():
    register_workflow(WorkflowDescriptor(
        "dcip.invert", "phgx_dcip.workflows:run_invert", "2.5D DC/IP four-parameter inversion.",
        stochastic=False, module_key="dcip"))
    register_short_code("dcip.invert", "dcipinv")
    register_reader(ReaderSpec(
        name="gtem-las", method="DCIP", loader="phgx_dcip.io:read_las", suffixes=(".las",),
        sniff="phgx_dcip.io:is_gtem_las"))
    register_module(ModulePage(
        key="dcip", import_path="phgx_dcip.page", class_name="DcipPage", title="DC / IP",
        group="Geophysical Data Processing", label="DC / IP",
        workflow_ids=("dcip.invert",), result_key="dcip_processing"))
```

| 注册项 | 进入的表 | 说明 |
|---|---|---|
| `register_workflow` | 工作流注册表 | CLI、Studio 工作进程、AI 助手都能运行；handler 写成 `"模块:函数"`，按需导入 |
| `register_short_code` | `results_store._SHORT_CODES` | 运行目录名中的缩写，1–8 位字母或数字 |
| `register_reader` | 读取器表 | `find_reader(path, method)` 先试 `sniff`，再按后缀匹配 |
| `register_module` | 页面表、导航顺序（Project Map 之前）、导航树分组、模块描述 | 分组不存在时新建在 “Project” 之前 |

## 3. 约定

- **无界面也能加载**：`register_module` 不导入 Qt。页面表在 `qt_apps.modules` 被导入时才更新，所以无界面的工作进程加载同一插件时，工作流照常注册。插件的 `register()` 自身也不得在模块顶层导入 PySide6。
- **故障隔离**：某个插件导入或注册失败时，记录到 `plugins.load_failures()` 并写入日志，不影响其他插件和 Studio。`phgx-doctor` 会列出失败的插件。
- **键名唯一**：页面键与内置页面重名时拒绝并记录；工作流 ID 重复时抛出 `KeyError`（需要覆盖时传 `replace=True`）。
- **页面类**：继承 `PyHydroGeophysX.qt_apps.modules.base.BaseModule`，实现 `agent_describe()` 和 `agent_apply()`；重计算通过 `ProcessWorkflowWorker` 运行注册过的工作流。
- **质量门禁**：扩展包自身沿用本仓库的门禁标准（ruff 严格规则、`mypy --strict`、冒烟测试与数值验证）。
