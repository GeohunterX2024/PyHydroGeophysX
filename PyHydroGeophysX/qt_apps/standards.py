"""Industry standards behind the Studio's parameters, shown beside them (plan M4.6).

:data:`STANDARDS` lists the standards ``docs/yuem/standards.md`` maps the
methods to; :data:`ANNOTATIONS` names, per page, the controls whose subject a
standard covers. :func:`annotate` appends the standard to each control's
tooltip when the page is built, so the source is one hover away. The
standards set requirements for survey design, acquisition, processing and
reporting; the Studio's default values are its own, not values quoted from
them.
"""

from __future__ import annotations

# i18n: own language - the titles and subjects below are held in both languages here.

from typing import Any, Dict, Tuple

from PySide6.QtCore import QCoreApplication

#: Code -> (Chinese title, English title), as published.
STANDARDS: Dict[str, Tuple[str, str]] = {
    "DZ/T 0072-2020": ("电阻率测深法技术规范", "Technical specification for resistivity sounding"),
    "DZ/T 0073-2016": ("电阻率剖面法技术规程", "Technical specifications for resistivity profiling method"),
    "DZ/T 0070-2016": ("时间域激发极化法技术规程", "Technical specification for time-domain induced polarization"),
    "DZ/T 0187-2016": ("地面磁性源瞬变电磁法技术规程",
                       "Technical specification for ground magnetic source transient electromagnetic method"),
    "DZ/T 0173-2022": ("大地电磁测深法技术规程", "Technical specification for magnetotelluric sounding"),
    "DZ/T 0170-2020": ("浅层地震勘查技术规范", "Technical specification for shallow seismic exploration"),
    "DZ/T 0082-2021": ("区域重力调查规范", "The standard for regional gravity survey"),
    "DZ/T 0071-2025": ("地面高精度磁测技术规程", "Technical specification for ground high-precision magnetic survey"),
    "DZ/T 0361-2020": ("地球物理勘查计量单位", "Units of measurement for geophysical exploration"),
    "SY/T 6589-2024": ("陆上可控源电磁法勘探采集技术规程",
                       "Technical specification for land acquisition with controlled source electromagnetic method"),
    "SY/T 7073-2016": ("陆上可控源电磁法勘探资料处理解释技术规程",
                       "Technical specifications for processing and interpretation of land controlled source "
                       "electromagnetic data"),
    "CJJ/T 7-2017": ("城市工程地球物理探测标准", "Standard for urban engineering geophysical exploration"),
}

#: Page key -> control attribute -> (standards, subject in Chinese, subject in English).
ANNOTATIONS: Dict[str, Dict[str, Tuple[Tuple[str, ...], str, str]]] = {
    "ert": {
        "_qc_max_recip": (("DZ/T 0073-2016", "DZ/T 0072-2020"), "观测精度检查（重复与互易观测）",
                          "accuracy checks (repeat and reciprocal readings)"),
        "_qc_max_stack": (("DZ/T 0073-2016",), "观测精度检查", "accuracy checks"),
        "_qc_max_rc": (("DZ/T 0073-2016", "DZ/T 0072-2020"), "接地条件", "electrode grounding"),
        "_qc_min_v": (("DZ/T 0073-2016",), "测量电压与信号强度", "measured voltage and signal strength"),
        "_qc_min_i": (("DZ/T 0073-2016",), "供电电流", "injected current"),
        "_max_err": (("DZ/T 0073-2016",), "资料处理：数据取舍", "processing: data selection"),
        "_lam": (("DZ/T 0073-2016", "CJJ/T 7-2017"), "资料处理与反演", "processing and inversion"),
        "_target_chi2": (("DZ/T 0073-2016",), "资料处理与反演", "processing and inversion"),
    },
    "em": {
        "_tail_cut": (("DZ/T 0187-2016",), "资料处理：晚期道取舍", "processing: late-gate selection"),
        "_gate_rejection": (("DZ/T 0187-2016",), "资料处理：数据取舍", "processing: data selection"),
        "_target_chi2": (("DZ/T 0187-2016",), "反演解释", "inversion and interpretation"),
    },
    "mt": {
        "_error_floor_1d": (("DZ/T 0173-2022",), "数据处理与反演：误差", "processing and inversion: errors"),
        "_static_shift": (("DZ/T 0173-2022",), "静态偏移校正", "static shift correction"),
        "_target_rms": (("DZ/T 0173-2022",), "反演拟合", "inversion fit"),
    },
    "gravmag": {
        "_rel_error": (("DZ/T 0082-2021", "DZ/T 0071-2025"), "精度评价", "accuracy assessment"),
        "_noise_floor": (("DZ/T 0082-2021", "DZ/T 0071-2025"), "精度评价", "accuracy assessment"),
    },
}


def reference(codes: Tuple[str, ...], subject_zh: str, subject_en: str) -> str:
    """The tooltip line: the standards with their titles and the subject, in the Studio's language."""
    chinese = QCoreApplication.translate("PHGX", "Standard") != "Standard"
    if chinese:
        names = "；".join(f"{code}《{STANDARDS[code][0]}》" for code in codes)
        return f"规程：{names}（{subject_zh}）"
    names = "; ".join(f"{code}, {STANDARDS[code][1]}" for code in codes)
    return f"Standard: {names} ({subject_en})"


def annotate(page: Any, key: str) -> int:
    """Append the standards to the tooltips of ``page``'s controls; returns how many were annotated."""
    count = 0
    for attribute, (codes, subject_zh, subject_en) in ANNOTATIONS.get(key, {}).items():
        widget = getattr(page, attribute, None)
        if widget is None or not hasattr(widget, "setToolTip"):
            continue
        tip = widget.toolTip()
        line = reference(codes, subject_zh, subject_en)
        if line not in tip:
            widget.setToolTip(f"{tip}\n\n{line}" if tip else line)  # i18n: as written
            count += 1
    return count


__all__ = ["ANNOTATIONS", "STANDARDS", "annotate", "reference"]
