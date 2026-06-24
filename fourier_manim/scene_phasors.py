import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from fourier_core import spectrum


class FourierPhasors(Scene):
    KEY_FRAMES = [1, 5, 9, 15, 25, 39]

    def build_phasor_tip(self, t, harmonics, amplitudes, axes):
        origin = axes.c2p(0, 0)
        current = origin
        cx, cy = 0.0, 0.0
        for h, amp in zip(harmonics, amplitudes):
            angle = h * t
            cx += amp * np.cos(angle)
            cy += amp * np.sin(angle)
        return axes.c2p(cx, cy)

    def get_phasors(self, t, harmonics, amplitudes, axes):
        origin = axes.c2p(0, 0)
        current = origin
        cx, cy = 0.0, 0.0
        arrows = VGroup()
        for i, (h, amp) in enumerate(zip(harmonics, amplitudes)):
            angle = h * t
            cx += amp * np.cos(angle)
            cy += amp * np.sin(angle)
            end = axes.c2p(cx, cy)
            arrow = Arrow(
                current, end,
                buff=0,
                stroke_width=3,
                color=color_gradient([BLUE, RED], len(harmonics))[i],
                max_tip_length_to_length_ratio=0.15,
            )
            arrows.add(arrow)
            current = end
        return arrows

    def construct(self):
        for n_harm in range(1, 21):
            highest_harmonic = 2 * n_harm - 1
            if highest_harmonic not in self.KEY_FRAMES:
                continue

            self.clear()

            harmonics, amplitudes = spectrum(n_harm)

            title = Text(
                f"Rotating Phasors — {highest_harmonic} Harmonics",
                font_size=36,
                color=WHITE,
            ).to_edge(UP, buff=0.3)

            left_axes = Axes(
                x_range=[-2, 2, 0.5],
                y_range=[-2, 2, 0.5],
                x_length=5.5,
                y_length=5.5,
                axis_config={"include_numbers": False},
            ).to_edge(LEFT, buff=0.8)

            right_axes = Axes(
                x_range=[0, 2 * PI, PI / 2],
                y_range=[-2, 2, 0.5],
                x_length=5.5,
                y_length=5.5,
                axis_config={"include_numbers": True, "font_size": 14},
            ).to_edge(RIGHT, buff=0.8)

            left_label = Text("Phasors", font_size=20, color=GRAY).next_to(
                left_axes, DOWN, buff=0.2
            )
            right_label = Text("Waveform", font_size=20, color=GRAY).next_to(
                right_axes, DOWN, buff=0.2
            )

            self.add(title, left_axes, right_axes, left_label, right_label)

            t_tracker = ValueTracker(0)

            phasors = always_redraw(
                lambda: self.get_phasors(
                    t_tracker.get_value(), harmonics, amplitudes, left_axes
                )
            )

            def get_trace():
                t_now = t_tracker.get_value()
                if t_now < 0.01:
                    return VGroup()
                t_vals = np.linspace(0, t_now, 300)
                y_vals = np.zeros_like(t_vals)
                for j, tv in enumerate(t_vals):
                    s = 0.0
                    for h, amp in zip(harmonics, amplitudes):
                        s += amp * np.sin(h * tv)
                    y_vals[j] = s
                line = right_axes.plot_line_graph(
                    t_vals, y_vals,
                    line_color=YELLOW,
                    add_vertex_dots=False,
                )
                return line

            trace = always_redraw(get_trace)

            self.add(phasors, trace)
            self.wait(0.3)

            max_t = 2 * PI
            self.play(
                t_tracker.animate.set_value(max_t),
                run_time=4.0,
                rate_func=linear,
            )
            self.wait(1.0)

    def render_all(self):
        self.render(preview=True)


if __name__ == "__main__":
    FourierPhasors().render_all()