"""An ERT survey (a pyGIMLi ``DataContainerERT`` or its arrays) as survey-view descriptions.

* The layout: the electrodes at the container's sensor positions. A 2-D line
  gives ``(x, elevation)`` (the second coordinate is the height, the third is
  zero), drawn with ``x`` as the distance along the line; a 3-D survey gives
  ``(x, y, z)``. Each current injection (an A-B pair) is a group, with its AB
  link and the MN links of its readings.
* The pseudo-depth points: the ERT page's own placement
  (``ert_io.pseudosection_points``, the ``"pygimli"`` convention), keyed by
  reading, with apparent resistivity, error, geometric factor and validity.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from PyHydroGeophysX.survey import attributes
from PyHydroGeophysX.survey.layout import SurveyLayout, SurveyLinks, SurveyPoints, TopographyProfile
from PyHydroGeophysX.survey.pseudo import PseudoPoints, pygimli_coordinates
from PyHydroGeophysX.survey.traces import TraceSet


def injection_name(a: int, b: int) -> str:
    """The group of a reading injected through electrodes ``a`` and ``b`` (0-based)."""
    return f"A{a + 1}-B{b + 1}" if b >= 0 else f"A{a + 1}"


class ERTSurvey:
    """The survey provider of an ERT data set."""

    def __init__(
        self,
        sensors: ArrayLike,
        a: ArrayLike,
        b: ArrayLike,
        m: ArrayLike,
        n: ArrayLike,
        values: dict[str, ArrayLike] | None = None,
    ) -> None:
        positions = np.atleast_2d(np.asarray(sensors, dtype=float))
        if positions.shape[1] == 2:
            positions = np.column_stack([positions, np.zeros(positions.shape[0])])
        self.sensors = positions
        self.a, self.b, self.m, self.n = (np.asarray(v, dtype=np.int64).ravel() for v in (a, b, m, n))
        self.values = {name: np.asarray(v, dtype=float).ravel() for name, v in (values or {}).items()}
        self.two_d = bool(np.allclose(positions[:, 2], 0.0)) if positions.size else True
        self._layout: SurveyLayout | None = None
        self._pseudo: PseudoPoints | None = None

    @classmethod
    def from_container(cls, data: Any) -> ERTSurvey:
        """From a pyGIMLi ERT data container: sensors, a/b/m/n and the values it has."""
        values: dict[str, ArrayLike] = {}
        for token, name in (
            ("rhoa", attributes.APPARENT_RESISTIVITY),
            ("err", attributes.ERROR),
            ("k", attributes.GEOMETRIC_FACTOR),
            ("ip", attributes.CHARGEABILITY),
        ):
            if data.haveData(token):
                column = np.asarray(data[token], dtype=float)
                values[name] = column * 100.0 if token == "err" else column
        if data.haveData("valid"):
            values[attributes.REJECTED] = 1.0 - np.asarray(data["valid"], dtype=float)
        return cls(
            np.asarray(data.sensors(), dtype=float), data["a"], data["b"], data["m"], data["n"], values
        )

    # -- groups -------------------------------------------------------------------------------------
    def injections(self) -> list[tuple[str, int]]:
        """Each injection and its number of readings, in the order the data first use them."""
        counts: dict[str, int] = {}
        for a, b in zip(self.a, self.b, strict=True):
            name = injection_name(int(a), int(b))
            counts[name] = counts.get(name, 0) + 1
        return list(counts.items())

    # -- SurveyProvider -------------------------------------------------------------------------
    def survey_capabilities(self) -> frozenset[str]:
        if self.sensors.size == 0:
            return frozenset()
        return frozenset({"layout", "pseudo"} if self.a.size else {"layout"})

    def survey_traces(self, group: str, channels: Sequence[str]) -> TraceSet | None:
        return None

    def along(self) -> np.ndarray:
        """Each electrode's distance along the line: its first coordinate (as the pseudosection)."""
        return np.asarray(self.sensors[:, 0], dtype=float)

    def elevation(self) -> np.ndarray:
        return np.asarray(self.sensors[:, 1] if self.two_d else self.sensors[:, 2], dtype=float)

    def terrain(self) -> TopographyProfile | None:
        elevation = self.elevation()
        if self.sensors.shape[0] >= 2 and np.any(elevation != 0):
            return TopographyProfile(self.along(), elevation)
        return None

    def survey_layout(self) -> SurveyLayout | None:
        if self._layout is None and self.sensors.size:
            self._layout = self._build_layout()
        return self._layout

    def survey_pseudo(self) -> PseudoPoints | None:
        if self._pseudo is None and self.a.size:
            self._pseudo = self._build_pseudo()
        return self._pseudo

    def _build_layout(self) -> SurveyLayout:
        count = self.sensors.shape[0]
        east = self.along() if self.two_d else self.sensors[:, 0]
        north = np.zeros(count) if self.two_d else self.sensors[:, 1]
        xyz = np.column_stack([east, north, self.elevation()])
        points = SurveyPoints(
            tuple(f"e{i + 1}" for i in range(count)),
            ("electrode",) * count,
            xyz,
            label=tuple(str(i + 1) for i in range(count)),
            keys=tuple(("electrode", i) for i in range(count)),
            along=self.along(),
            attrs={attributes.ELEVATION: self.elevation()},
        )
        starts: list[int] = []
        ends: list[int] = []
        kinds: list[str] = []
        groups: list[str] = []
        keys: list[tuple[Any, ...]] = []
        seen: set[str] = set()
        inside = (
            (self.a >= 0)
            & (self.a < count)
            & (self.m >= 0)
            & (self.m < count)
            & (self.n >= 0)
            & (self.n < count)
        )
        for row in np.flatnonzero(inside):
            a, b, m, n = (int(v) for v in (self.a[row], self.b[row], self.m[row], self.n[row]))
            group = injection_name(a, b)
            if group not in seen and 0 <= b < count:
                seen.add(group)
                starts.append(a)
                ends.append(b)
                kinds.append("AB")
                groups.append(group)
                keys.append(("injection", group))
            starts.append(m)
            ends.append(n)
            kinds.append("MN")
            groups.append(group)
            keys.append(("reading", int(row)))
        links = SurveyLinks(np.asarray(starts), np.asarray(ends), tuple(kinds), tuple(groups), tuple(keys))
        return SurveyLayout(points, links, topography=self.terrain(), title="ERT")

    def _build_pseudo(self) -> PseudoPoints | None:
        x, depth, inside = pygimli_coordinates(self.along(), self.a, self.b, self.m, self.n)
        if x.size == 0:
            return None
        rows = np.flatnonzero(inside)
        groups = tuple(injection_name(int(self.a[r]), int(self.b[r])) for r in rows)
        attrs = {name: values[rows] for name, values in self.values.items() if values.size == self.a.size}
        points = PseudoPoints(
            x,
            depth,
            "pygimli",
            keys=tuple(("reading", int(r)) for r in rows),
            group=groups,
            attrs=attrs,
        )
        return points.on_ground(self.terrain())


__all__ = ["ERTSurvey", "injection_name"]
