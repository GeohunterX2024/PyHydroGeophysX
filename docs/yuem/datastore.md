# 工程数据库：phgx-dataset-v1

模块：`PyHydroGeophysX/datastore/`。设计借鉴 DCIP 的 `dcip-line-v3`。

## 存放位置

```
<工程目录>/datasets/index.json             索引（可从文件重建）
<工程目录>/datasets/<数据集ID>/v0001.h5   每个版本一个文件，写入后只读
```

## 数据集结构（HDF5）

根属性：`schema = "phgx-dataset-v1"`、`method`（ERT、IP、EM、MT、SEISMIC 等）、`kind`（生成该数据集的适配器）。

| 分组 | 内容 |
|---|---|
| `meta` | 方法细节、各字段单位 `units`、坐标系 `crs`、标签、版本号、创建时间 |
| `geometry` | 电极、源、接收点、测点坐标，采样轴（频率、时间） |
| `observations` | 观测值 |
| `errors` | 观测误差 |
| `masks` | 布尔遮罩（参与反演的数据） |
| `provenance` | 原始文件引用（路径、sha256、大小）、适配器、处理步骤 |

每个分组都是一棵树。数组存为 HDF5 数据集，保留原始 dtype（Unicode 以 UTF-8 存储并恢复原宽度）。嵌套映射存为子分组。其余值（None、布尔、整数、浮点含 NaN 与 inf、复数、字符串、NumPy 标量、元组与列表）存入分组的 `phgx_tree` JSON 属性，并带类型标记，键的顺序也保留。因此各适配器都能无损往返。

## 版本与外链

- 版本不可变：目标文件已存在时拒绝写入；先写临时文件再原子替换，完成后设为只读。
- 新版本与上一版本完全相同的数组（形状、dtype、数值一致，NaN 视为相等）不再复制，而是以 HDF5 外链指向上一版本中的位置。外链使用相对路径，整个工程目录移动后仍可读取。只修改了遮罩的新版本只占遮罩的空间。

## 原始文件

`DatasetStore.reference_raw(path)` 以只读方式引用原始文件，不复制、不修改。位于工程目录内的文件记录相对路径，目录外的记录绝对路径；同时记录 sha256 和大小。`verify_raw(dataset)` 报告缺失或已被改动的原始文件。

## 适配器

| 对象 | kind | 说明 |
|---|---|---|
| pyGIMLi `DataContainerERT` | `pygimli.DataContainerERT` | 电极坐标与 a/b/m/n 入 geometry；`err`、`iperr` 入 errors；`valid` 转为布尔遮罩；token 列表与索引基数入 meta |
| EM 测深字典（`workflows.em1d.load_sounding`） | `em.sounding` | 顶层键按几何、观测、误差、描述分组，键顺序保留 |
| MT `TransferFunction` | `mt.transfer_function` | 阻抗与倾子入 observations，误差与协方差入 errors，测点信息入 meta |
| `SeismicDataset`（SEG-Y） | `seismic.segy` | 道数据入 observations，采样时间与逐列道头入 geometry，SEG-Y 摘要入 meta |

`to_dataset(obj)` 按对象类型选择适配器，`from_dataset(ds)` 按 `kind` 还原。插件可用 `datastore.adapters.register` 增加适配器。

## 单位与坐标系

单位取自 `results/units.py` 的注册表（不引入 pint），写入时校验 `meta.units`。坐标系以 `results.units.crs_record("EPSG:4544")` 的形式保存为 WKT 加 EPSG 代码（例如 CGCS2000 / 3 度带 117°E）。

## 测试

`tests/yuem/test_datastore.py` 覆盖以下内容：四类适配器无损往返（ERT、FDEM、TDEM 测线、MT、SEG-Y）；树结构中的各类值；新版本外链与工程目录移动；版本不可变；索引删除或损坏后重建；原始文件校验；单位与遮罩校验。
