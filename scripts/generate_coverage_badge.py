#!/usr/bin/env python3
"""Write a flat-style coverage badge SVG from coverage.py Cobertura XML (stdlib
only).

Setuptools 82+ removed pkg_resources, which breaks the ``coverage-badge`` package.
This script avoids that dependency entirely.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET


def _color(pct: float) -> str:
    if pct >= 95:
        return "#4c1"
    if pct >= 90:
        return "#97CA00"
    if pct >= 75:
        return "#a3a300"
    if pct >= 60:
        return "#dfb317"
    if pct >= 40:
        return "#fe7d37"
    return "#e05d44"


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: generate_coverage_badge.py <coverage.xml> <out.svg>",
            file=sys.stderr,
        )
        return 2
    xml_path, out_path = sys.argv[1], sys.argv[2]
    root = ET.parse(xml_path).getroot()
    line_rate = float(root.attrib.get("line-rate", "0"))
    pct = line_rate * 100
    color = _color(pct)
    value_text = f"{round(pct)}%"
    left_w, right_w = 62, max(28, 7 * len(value_text) + 10)
    total_w = left_w + right_w
    mid_right = left_w + right_w / 2
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="20" role="img" aria-label="coverage: {value_text}">
  <title>coverage: {value_text}</title>
  <linearGradient id="g" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r"><rect width="{total_w}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{left_w}" height="20" fill="#555"/>
    <rect x="{left_w}" width="{right_w}" height="20" fill="{color}"/>
    <rect width="{total_w}" height="20" fill="url(#g)"/>
  </g>
  <g fill="#fff" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{left_w / 2}" y="15" text-anchor="middle">coverage</text>
    <text x="{mid_right}" y="15" text-anchor="middle">{value_text}</text>
  </g>
</svg>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
