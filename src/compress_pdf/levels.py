# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 It's FOSS
"""Compression levels and the Ghostscript settings behind them."""

from dataclasses import dataclass


def N_(message):
    """Mark a string for translation without translating it yet."""
    return message


@dataclass(frozen=True)
class Level:
    id: str
    label: str
    description: str
    image_dpi: int
    mono_dpi: int
    jpeg_qfactor: float


LEVELS = (
    Level('high', N_('High Quality'), N_('Good for printing'), 200, 600, 0.4),
    Level('balanced', N_('Balanced'), N_('Good for email and sharing'), 150, 300, 0.76),
    Level('small', N_('Small'), N_('Good for upload portals'), 100, 200, 1.0),
    Level('smallest', N_('Smallest'), N_('Lowest image quality'), 72, 150, 1.3),
)

DEFAULT_LEVEL = 'balanced'


def get_level(level_id):
    for level in LEVELS:
        if level.id == level_id:
            return level
    raise KeyError(level_id)
