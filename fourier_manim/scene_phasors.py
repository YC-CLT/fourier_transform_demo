import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from fourier_core import spectrum


class FourierPhasors(Scene):
    KEY_FRAMES = [1, 5, 9, 15, 25, 39]

    def get_phasor_tip(self, t, harmonics, amplitudes, axes):
        cx, cy = 0.0, 0.0
        for h, amp in zip(harmonics, amplitudes):
            cx += amp * np.cos(h * t)
            cy += amp * np.sin(h * t)
        return axes.c2p(cx, cy)

    def get_phasors(self, t, harmonics, amplitudes, axes):
        origin = axes.c2p(0, 0)
        current = origin
        cx, cy = 0.0, 0.0
        arrows = VGroup()
        colors = color_gradient([BLUE, RED], len(harmonics))
        for i, (h, amp) in enumerate(zip(harmonics, amplitudes)):
            angle = h * t
            cx += amp * np.cos(angle)
            cy += amp * np.sin(angle)
            end = axes.c2p(cx, cy)
            arrow = Arrow(
                current, end,
                buff=0,
                stroke_width=3,
                color=colors[i],
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
                x_axis_config={"include_numbers": False},
            ).to_edge(RIGHT, buff=0.8)

            pi_labels = VGroup()
            for val, tex in [
                (0, "0"),
                (PI / 2, r"\frac{\pi}{2}"),
                (PI, r"\pi"),
                (3 * PI / 2, r"\frac{3\pi}{2}"),
                (2 * PI, r"2\pi"),
            ]:
                lbl = MathTex(tex, font_size=28)
                lbl.next_to(right_axes.c2p(val, 0), DOWN, buff=0.15)
                pi_labels.add(lbl)

            left_label = Text("Phasors", font_size=20, color=GRAY).next_to(
                left_axes, DOWN, buff=0.2
            )
            right_label = Text("Waveform", font_size=20, color=GRAY).next_to(
                right_axes, DOWN, buff=0.2
            )

            self.add(title, left_axes, right_axes, left_label, right_label, pi_labels)

            t_tracker = ValueTracker(0)

            phasors = always_redraw(
                lambda: self.get_phasors(
                    t_tracker.get_value(), harmonics, amplitudes, left_axes
                )
            )

            def get_tip_dot():
                t_now = t_tracker.get_value()
                tip = self.get_phasor_tip(t_now, harmonics, amplitudes, left_axes)
                dot = Dot(tip, radius=0.04, color=WHITE)
                return dot

            first_amp = amplitudes[0]
            first_circle = Circle(
                radius=left_axes.x_length * (first_amp / 4.0),
                color=BLUE_C,
                stroke_width=1.5,
            )
            first_circle.move_to(left_axes.c2p(0, 0))

            def get_connector_line():
                t_now = t_tracker.get_value()
                tip = self.get_phasor_tip(t_now, harmonics, amplitudes, left_axes)
                wy = 0.0
                for h, amp in zip(harmonics, amplitudes):
                    wy += amp * np.sin(h * t_now)
                right_point = right_axes.c2p(t_now, wy)
                line = Line(
                    tip, right_point,
                    color=WHITE,
                    stroke_width=1.5,
                )
                return line

            def get_wave_dot():
                t_now = t_tracker.get_value()
                wy = 0.0
                for h, amp in zip(harmonics, amplitudes):
                    wy += amp * np.sin(h * t_now)
                point = right_axes.c2p(t_now, wy)
                dot = Dot(point, radius=0.06, color=YELLOW)
                return dot

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

            tip_dot = always_redraw(get_tip_dot)
            connector = always_redraw(get_connector_line)
            wave_dot = always_redraw(get_wave_dot)
            trace = always_redraw(get_trace)

            self.add(phasors, tip_dot, first_circle, connector, wave_dot, trace)
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