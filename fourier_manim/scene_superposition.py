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

            wave_axes = Axes(
                x_range=[0, n_periods * 2 * PI, PI / 2],
                y_range=[-1.8, 1.8, 0.5],
                x_length=7,
                y_length=2.5,
                axis_config={"include_numbers": True},
            ).to_edge(UP, buff=0.5)
            wave_label = wave_axes.get_axis_labels(
                x_label="t", y_label="f(t)"
            )

            wave_graph = wave_axes.plot_line_graph(
                t, waveform,
                line_color=BLUE,
                add_vertex_dots=False,
            )

            spec_axes = Axes(
                x_range=[0, 2 * len(harmonics) + 2, 2],
                y_range=[0, 1.5, 0.5],
                x_length=7,
                y_length=2.5,
                axis_config={"include_numbers": True},
            ).to_edge(DOWN, buff=0.5)
            spec_label = spec_axes.get_axis_labels(
                x_label="Harmonic", y_label="Amplitude"
            )

            bars = VGroup()
            for h, a in zip(harmonics, amplitudes):
                bar = Rectangle(
                    width=0.6,
                    height=spec_axes.y_length * (a / 1.5),
                    fill_color=RED,
                    fill_opacity=0.8,
                    stroke_width=0,
                )
                bar.move_to(
                    spec_axes.c2p(h, a / 2),
                    aligned_edge=DOWN,
                )
                bars.add(bar)

            title = Text(
                f"Fourier Series — N = {n_harm} Harmonics",
                font_size=32,
                color=WHITE,
            ).to_edge(UP, buff=0.1)

            self.add(wave_axes, wave_label, wave_graph)
            self.add(spec_axes, spec_label, bars)
            self.add(title)
            self.wait(0.1)

    def render_all(self):
        self.render(preview=True)


if __name__ == "__main__":
    FourierSuperposition().render_all()