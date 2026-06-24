import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from fourier_core import generate_waveform, spectrum


class FourierSuperposition(Scene):
    KEY_FRAMES = [1, 5, 9, 15, 25, 39]

    def construct(self):
        n_samples = 600
        n_periods = 2.0

        for n_harm in self.KEY_FRAMES:
            t, waveform, _ = generate_waveform(
                int((n_harm + 1) / 2), n_samples, n_periods
            )
            harmonics, amplitudes = spectrum(int((n_harm + 1) / 2))

            self.clear()

            title = Text(
                f"Fourier Series — N = {n_harm} Harmonics",
                font_size=36,
                color=WHITE,
            ).to_edge(UP, buff=0.3)

            wave_axes = Axes(
                x_range=[0, n_periods * 2 * PI, PI],
                y_range=[-1.8, 1.8, 0.5],
                x_length=6.5,
                y_length=2.2,
                axis_config={"include_numbers": True, "font_size": 14},
                x_axis_config={"include_numbers": False},
            )
            wave_axes.next_to(title, DOWN, buff=0.5)
            wave_label = wave_axes.get_axis_labels(
                x_label="t", y_label="f(t)"
            )

            pi_labels = VGroup()
            for i in range(5):
                val = i * PI
                if val == 0:
                    tex = "0"
                elif val == PI:
                    tex = r"\pi"
                else:
                    tex = rf"{i}\pi"
                lbl = MathTex(tex, font_size=24)
                lbl.next_to(wave_axes.c2p(val, 0), DOWN, buff=0.15)
                pi_labels.add(lbl)

            wave_graph = wave_axes.plot_line_graph(
                t, waveform,
                line_color=BLUE,
                add_vertex_dots=False,
            )

            spec_axes = Axes(
                x_range=[0, n_harm + 3, 2],
                y_range=[0, 1.5, 0.5],
                x_length=6.5,
                y_length=2.2,
                axis_config={"include_numbers": True, "font_size": 14},
            )
            spec_axes.next_to(wave_axes, DOWN, buff=0.6)
            spec_label = spec_axes.get_axis_labels(
                x_label="Harmonic", y_label="Amplitude"
            )

            bar_width_data = 1.4
            bar_width = spec_axes.c2p(bar_width_data, 0)[0] - spec_axes.c2p(0, 0)[0]

            bars = VGroup()
            for h, a in zip(harmonics, amplitudes):
                bar_height = spec_axes.c2p(0, a)[1] - spec_axes.c2p(0, 0)[1]
                bar = Rectangle(
                    width=bar_width,
                    height=bar_height,
                    fill_color=RED,
                    fill_opacity=0.8,
                    stroke_width=0,
                )
                bar.move_to(
                    spec_axes.c2p(h, 0),
                    aligned_edge=DOWN,
                )
                bars.add(bar)

            self.add(title, wave_axes, wave_label, wave_graph, pi_labels)
            self.add(spec_axes, spec_label, bars)
            self.wait(1.0)

    def render_all(self):
        self.render(preview=True)


if __name__ == "__main__":
    FourierSuperposition().render_all()