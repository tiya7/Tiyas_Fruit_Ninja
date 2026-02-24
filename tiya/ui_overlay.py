"""HUD and overlay drawing helpers."""
from __future__ import annotations

from typing import List, Optional, Tuple

import cv2
import numpy as np

from .config import (
    FONT,
    HUD_ALPHA,
    HUD_COLOR,
    MAX_LIVES,
    FRUIT_RADIUS,
)


# ── Sprite blitting ─────────────────────────────────────────────────────────

def overlay_sprite(
    frame: np.ndarray,
    sprite: np.ndarray,
    cx: int,
    cy: int,
    target_size: int,
    alpha_mul: float = 1.0,
) -> None:
    """Alpha-blend a 4-channel sprite centred at (cx, cy)."""
    h, w = frame.shape[:2]
    s = cv2.resize(sprite, (target_size, target_size), interpolation=cv2.INTER_AREA)

    x1 = cx - target_size // 2
    y1 = cy - target_size // 2
    x2 = x1 + target_size
    y2 = y1 + target_size

    fx1 = max(x1, 0); fy1 = max(y1, 0)
    fx2 = min(x2, w); fy2 = min(y2, h)
    sx1 = fx1 - x1;   sy1 = fy1 - y1
    sx2 = sx1 + (fx2 - fx1)
    sy2 = sy1 + (fy2 - fy1)

    if fx2 <= fx1 or fy2 <= fy1:
        return

    roi   = frame[fy1:fy2, fx1:fx2]
    patch = s[sy1:sy2, sx1:sx2]

    if patch.shape[2] == 4:
        alpha = (patch[:, :, 3:4].astype(np.float32) / 255.0) * alpha_mul
        bgr   = patch[:, :, :3].astype(np.float32)
        roi[:] = np.clip(roi * (1 - alpha) + bgr * alpha, 0, 255).astype(np.uint8)
    else:
        roi[:] = patch[:, :, :3]


# ── Blade trail ──────────────────────────────────────────────────────────────

def draw_trail(frame: np.ndarray, trail: List[Tuple[int, int]]) -> None:
    if len(trail) < 2:
        return
    pts = np.array(trail, dtype=np.int32)
    n   = len(pts)
    for i in range(1, n):
        t         = i / n
        thickness = max(1, int(t * 14))
        gold      = (int(30*(1-t)), int(200*t), int(255*t))
        overlay   = frame.copy()
        cv2.line(overlay, tuple(pts[i-1]), tuple(pts[i]), gold, thickness, cv2.LINE_AA)
        cv2.addWeighted(overlay, t*0.6, frame, 1-t*0.6, 0, frame)


# ── Particles ────────────────────────────────────────────────────────────────

def draw_particles(frame: np.ndarray, particles) -> None:
    for p in particles:
        if not p.alive:
            continue
        alpha  = p.alpha
        radius = max(2, int(5 * alpha))
        x, y   = int(p.x), int(p.y)
        if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
            overlay = frame.copy()
            cv2.circle(overlay, (x, y), radius, p.color, -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, alpha*0.85, frame, 1-alpha*0.85, 0, frame)


# ── HUD ──────────────────────────────────────────────────────────────────────

def draw_hud(
    frame: np.ndarray,
    score: int,
    lives: int,
    life_sprite: np.ndarray,
    high_score: int = 0,
    combo: int = 0,
    combo_label: Optional[str] = None,
) -> None:
    h, w = frame.shape[:2]

    # Score panel (top-left) — taller to fit both score + best
    _draw_panel(frame, 10, 10, 230, 95)

    # Current score
    cv2.putText(frame, f"SCORE  {score:>6}", (22, 48),
                FONT, 1.1, (255, 255, 200), 2, cv2.LINE_AA)

    # Divider line
    cv2.line(frame, (18, 58), (228, 58), (80, 100, 140), 1)

    # High score — gold colour, slightly smaller
    best_text = f"BEST   {high_score:>6}"
    # If current score beats best, flash yellow-green
    color = (0, 255, 180) if score > 0 and score >= high_score else (100, 200, 255)
    cv2.putText(frame, best_text, (22, 84),
                FONT, 0.85, color, 2, cv2.LINE_AA)

    # "NEW!" badge when player is beating their best
    if score > 0 and score >= high_score:
        cv2.putText(frame, "NEW!", (175, 84),
                    FONT, 0.7, (0, 255, 100), 2, cv2.LINE_AA)

    # Lives panel (top-right)
    panel_w = 50 + MAX_LIVES * 48
    _draw_panel(frame, w - panel_w - 10, 10, panel_w, 68)
    for i in range(MAX_LIVES):
        alpha = 1.0 if i < lives else 0.22
        lx    = w - panel_w + 14 + i * 48
        overlay_sprite(frame, life_sprite, lx + 20, 44, 42, alpha_mul=alpha)

    # Combo popup (centre screen)
    if combo >= 2 and combo_label:
        fs    = 2.2
        thick = 4
        (tw, _), _ = cv2.getTextSize(combo_label, FONT, fs, thick)
        tx = (w - tw) // 2
        ty = h // 3
        cv2.putText(frame, combo_label, (tx+3, ty+3), FONT, fs, (0,0,0),     thick+2, cv2.LINE_AA)
        cv2.putText(frame, combo_label, (tx,   ty),   FONT, fs, (0,215,255), thick,   cv2.LINE_AA)


def draw_game_over(frame: np.ndarray, score: int, high_score: int = 0) -> None:
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0,0), (w,h), (0,0,0), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    def _ct(text, y, scale, color, thick=2):
        (tw, _), _ = cv2.getTextSize(text, FONT, scale, thick)
        cv2.putText(frame, text, ((w-tw)//2, y), FONT, scale, (0,0,0),  thick+2, cv2.LINE_AA)
        cv2.putText(frame, text, ((w-tw)//2, y), FONT, scale,  color,   thick,   cv2.LINE_AA)

    _ct("GAME OVER",                          h//2 - 80, 3.0, (0, 60, 220),     4)
    _ct(f"Score:  {score}",                   h//2 +  0, 1.8, (255, 255, 200),  3)
    _ct(f"Best:   {high_score}",              h//2 + 55, 1.4, (0, 215, 255),    2)

    # "New record!" banner
    if score > 0 and score >= high_score:
        _ct("New Record!",                    h//2 + 105, 1.1, (0, 255, 150),   2)
        _ct("Press  R  to restart  |  Q  to quit", h//2 + 150, 0.9, (180,220,255), 2)
    else:
        _ct("Press  R  to restart  |  Q  to quit", h//2 + 110, 0.9, (180,220,255), 2)


def _draw_panel(frame: np.ndarray, x: int, y: int, pw: int, ph: int) -> None:
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x+pw, y+ph), HUD_COLOR, -1)
    cv2.rectangle(overlay, (x, y), (x+pw, y+ph), (80, 120, 180), 2)
    cv2.addWeighted(overlay, HUD_ALPHA, frame, 1-HUD_ALPHA, 0, frame)
