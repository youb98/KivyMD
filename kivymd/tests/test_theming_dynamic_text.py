"""
Unit tests for :mod:`kivymd.theming_dynamic_text`.

These test the pure color math used to pick a readable (black or white) text
color for a given background color. No graphics/window is required.
"""

from kivymd.theming_dynamic_text import (
    _black_or_white_by_color_brightness,
    _black_or_white_by_contrast_ratio,
    _color_brightness,
    _luminance,
    _normalized_channel,
    get_contrast_text_color,
)

WHITE = (1, 1, 1)
BLACK = (0, 0, 0)


def test_color_brightness_bounds():
    assert _color_brightness(BLACK) == 0
    # 299 + 587 + 114 == 1000 for a fully white color.
    assert _color_brightness(WHITE) == 1000


def test_black_or_white_by_color_brightness():
    # Bright backgrounds -> black text, dark backgrounds -> white text.
    assert _black_or_white_by_color_brightness(WHITE) == "black"
    assert _black_or_white_by_color_brightness(BLACK) == "white"


def test_black_or_white_by_color_brightness_threshold():
    # brightness == 500 is the inclusive boundary that maps to black.
    on_threshold = (500 / 1000, 500 / 1000, 500 / 1000)
    assert _color_brightness(on_threshold) == 500
    assert _black_or_white_by_color_brightness(on_threshold) == "black"

    just_below = (0.499, 0.499, 0.499)
    assert _color_brightness(just_below) < 500
    assert _black_or_white_by_color_brightness(just_below) == "white"


def test_normalized_channel():
    # Linear branch for small values (color <= 0.03928).
    assert _normalized_channel(0.0) == 0.0
    assert _normalized_channel(0.03928) == 0.03928 / 12.92
    # Gamma branch for larger values.
    assert _normalized_channel(1.0) == 1.0
    assert 0.0 < _normalized_channel(0.5) < 1.0


def test_luminance_bounds():
    assert _luminance(BLACK) == 0.0
    # Weights sum to 1, so pure white has luminance 1.
    assert abs(_luminance(WHITE) - 1.0) < 1e-9


def test_black_or_white_by_contrast_ratio():
    assert _black_or_white_by_contrast_ratio(WHITE) == "black"
    assert _black_or_white_by_contrast_ratio(BLACK) == "white"


def test_get_contrast_text_color_brightness():
    assert get_contrast_text_color(WHITE) == (0, 0, 0, 1)
    assert get_contrast_text_color(BLACK) == (1, 1, 1, 1)


def test_get_contrast_text_color_contrast_ratio():
    assert get_contrast_text_color(WHITE, use_color_brightness=False) == (
        0,
        0,
        0,
        1,
    )
    assert get_contrast_text_color(BLACK, use_color_brightness=False) == (
        1,
        1,
        1,
        1,
    )


def test_get_contrast_text_color_returns_opaque_rgba():
    for color in (WHITE, BLACK, (0.2, 0.6, 0.9)):
        for use_brightness in (True, False):
            result = get_contrast_text_color(
                color, use_color_brightness=use_brightness
            )
            assert len(result) == 4
            # Alpha channel is always fully opaque.
            assert result[3] == 1
            assert set(result[:3]) <= {0, 1}
