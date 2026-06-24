import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from fourier_core import spectrum


class FourierPhasors(Scene):
    KEY_FRAMES = [1, 5, 9, 15, 25, 39]

    def construct(self):
        for n_harm in range(1, 21):
            highest_harmonic = 2 * n_harm - 1
            if highest_harmonic not in self.KEY_FRAMES:
                continue

            self.clear()

            title = Text(
                f"Rotating Phasors — {highest_harmonic} Harmonics",
                font_size=32,
                color=WHITE,
            ).to_edge(UP, buff=0.3)

            harmonics, amplitudes = spectrum(n_harm)

            left_axes = Axes(
                x_range=[-2, 2, 0.5],
                y_range=[-2, 2, 0.5],
                x_length=5,
                y_length=5,
                axis_config={"include_numbers": False},
            ).to_edge(LEFT, buff=0.5)

            right_axes = Axes(
                x_range=[0, 4 * PI, PI],
                y_range=[-2, 2, 0.5],
                x_length=5,
                y_length=5,
                axis_config={"include_numbers": False},
            ).to_edge(RIGHT, buff=0.5)

            self.add(left_axes, right_axes, title)

            t_snapshot = 0.0
            origin = left_axes.c2p(0, 0)
            current = origin

            vectors = VGroup()
            for i, (h, amp) in enumerate(zip(harmonics, amplitudes)):
                angle = h * t_snapshot
                dx = amp * np.cos(angle)
                dy = amp * np.sin(angle)
                end = left_axes.c2p(
                    left_axes.p2c(current)[0] + dx,
                    left_axes.p2c(current)[1] + dy,
                )
                arrow = Arrow(
                    current, end,
                    buff=0,
                    color=color_gradient([BLUE, RED], len(harmonics))[i],
                    max_tip_length_to_length_ratio=0.15,
                )
                vectors.add(arrow)
                current = end

            self.add(vectors)

            t_vals = np.linspace(0, 2 * PI, 200)
            tip_positions = np.zeros(len(t_vals))
            for j, tv in enumerate(t_vals):
                s = 0.0
                for h, amp in zip(harmonics, amplitudes):
                    s += amp * np.sin(h * tv)
                tip_positions[j] = s

            trace = right_axes.plot_line_graph(
                t_vals, tip_positions,
                line_color=YELLOW,
                add_vertex_dots=False,
            )
            self.add(trace)

            self.wait(0.1)

    def render_all(self):
        self.render(preview=True)


if __name__ == "__main__":
    FourierPhasors().render_all()