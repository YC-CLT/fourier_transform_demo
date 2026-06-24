import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fourier_core import generate_waveform, spectrum, harmonic_components

N_SAMPLES = 800
N_PERIODS = 2.0
MAX_HARMONICS = 20


def create_figure():
    """创建包含 3D 图、子图、滑块、按钮、动画帧的完整 Figure。"""
    harmonics, amplitudes = spectrum(MAX_HARMONICS)
    t, waveform, components = generate_waveform(MAX_HARMONICS, N_SAMPLES, N_PERIODS)

    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{"type": "scatter3d", "rowspan": 2}, {"type": "scatter"}],
            [None, {"type": "bar"}],
        ],
        subplot_titles=("3D 时频谱", "时域波形", "频谱"),
        horizontal_spacing=0.08,
        vertical_spacing=0.12,
    )

    colors_3d = [
        "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
        "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
        "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
        "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
    ]

    for k in range(MAX_HARMONICS):
        n = 2 * k + 1
        fig.add_trace(
            go.Scatter3d(
                x=t, y=np.full_like(t, n), z=components[k],
                mode="lines",
                line=dict(width=2, color=colors_3d[k]),
                name=f"谐波 {n}",
                showlegend=False,
            ),
            row=1, col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=t, y=waveform,
            mode="lines",
            line=dict(width=2, color="#636EFA"),
            name="合成波形",
            showlegend=False,
        ),
        row=1, col=2,
    )

    fig.add_trace(
        go.Bar(
            x=harmonics,
            y=amplitudes,
            marker_color="#EF553B",
            name="幅度",
            showlegend=False,
        ),
        row=2, col=2,
    )

    slider_steps = []
    for k in range(1, MAX_HARMONICS + 1):
        _, wf, comps = generate_waveform(k, N_SAMPLES, N_PERIODS)
        harm, amp = spectrum(k)

        visible_3d = [False] * MAX_HARMONICS + [True, True]
        for i in range(k):
            visible_3d[i] = True

        slider_steps.append(
            dict(
                method="update",
                label=str(2 * k - 1),
                args=[
                    {
                        "visible": visible_3d + [True, True],
                        "x": [None] * MAX_HARMONICS + [t, harm],
                        "y": [None] * MAX_HARMONICS + [wf, amp],
                        "z": [None] * MAX_HARMONICS + [None, None],
                    },
                    {"title": f"3D 时频谱 — N={2*k-1} 次谐波"},
                ],
            )
        )

    sliders = [dict(
        active=MAX_HARMONICS - 1,
        currentvalue={"prefix": "最高谐波: "},
        pad={"t": 50},
        steps=slider_steps,
    )]

    updatemenus = [
        dict(
            type="buttons",
            direction="right",
            x=0.0, y=1.12,
            buttons=[
                dict(
                    method="relayout",
                    label="正面",
                    args=[{"scene.camera.eye": {"x": 0, "y": -2.5, "z": 0.1}}],
                ),
                dict(
                    method="relayout",
                    label="侧面",
                    args=[{"scene.camera.eye": {"x": 2.5, "y": 0, "z": 0.1}}],
                ),
                dict(
                    method="relayout",
                    label="顶部",
                    args=[{"scene.camera.eye": {"x": 0, "y": 0, "z": 2.5}}],
                ),
                dict(
                    method="relayout",
                    label="默认",
                    args=[{"scene.camera.eye": {"x": 1.5, "y": -1.5, "z": 1.2}}],
                ),
            ],
        ),
        dict(
            type="buttons",
            direction="right",
            x=0.6, y=1.12,
            buttons=[
                dict(
                    method="animate",
                    label="播放",
                    args=[
                        None,
                        {
                            "frame": {"duration": 200, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 100},
                        },
                    ],
                ),
            ],
        ),
    ]

    frames = []
    for k in range(1, MAX_HARMONICS + 1):
        _, wf, comps = generate_waveform(k, N_SAMPLES, N_PERIODS)
        harm, amp = spectrum(k)

        frame_data = []
        for i in range(MAX_HARMONICS):
            if i < k:
                frame_data.append(
                    go.Scatter3d(
                        x=t, y=np.full_like(t, 2 * i + 1), z=comps[i],
                    )
                )
            else:
                frame_data.append(
                    go.Scatter3d(x=[], y=[], z=[])
                )
        frame_data.append(go.Scatter(x=t, y=wf))
        frame_data.append(go.Bar(x=harm, y=amp))

        frames.append(go.Frame(
            data=frame_data,
            name=f"n{k}",
            layout=dict(title=f"3D 时频谱 — N={2*k-1} 次谐波"),
        ))

    fig.update_layout(
        title="3D 时频谱 — 方波傅里叶级数合成",
        sliders=sliders,
        updatemenus=updatemenus,
        scene=dict(
            xaxis_title="时间 t",
            yaxis_title="频率 f (谐波次数)",
            zaxis_title="振幅 A",
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2)),
        ),
        height=800,
        margin=dict(l=0, r=0, t=80, b=0),
        xaxis2=dict(title="时间 t"),
        yaxis2=dict(title="幅值"),
        xaxis3=dict(title="谐波次数"),
        yaxis3=dict(title="幅度"),
    )

    fig.frames = frames

    fig.update_scenes(
        xaxis_range=[0, N_PERIODS * 2 * np.pi],
        yaxis_range=[0, 2 * MAX_HARMONICS + 1],
        zaxis_range=[-1.5, 1.5],
    )

    return fig


def build_html():
    """构建含 MathJax 动态公式的完整 HTML 页面。"""
    fig = create_figure()
    plot_html = fig.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        config={"responsive": True},
    )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>傅里叶级数 — 方波合成 3D 时频谱</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
window.MathJax = {{
  tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']] }},
  svg: {{ fontCache: 'global' }}
}};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" async></script>
<style>
  body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
  #formula-container {{
    padding: 16px 24px;
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    text-align: center;
    font-size: 1.2em;
    min-height: 40px;
  }}
  #plot-container {{ width: 100%; height: calc(100vh - 80px); }}
</style>
</head>
<body>
<div id="formula-container">$$ f(t) = \\frac{{4}}{{\\pi}}\\left[\\sin(t) + \\frac{{1}}{{3}}\\sin(3t) + \\cdots + \\frac{{1}}{{39}}\\sin(39t)\\right] $$</div>
<div id="plot-container">{plot_html}</div>
<script>
(function() {{
  var plotEl = document.getElementById('plot-container');
  var formulaEl = document.getElementById('formula-container');

  function buildFormula(n) {{
    var terms = [];
    for (var k = 0; k < n; k++) {{
      var h = 2 * k + 1;
      if (h === 1) {{
        terms.push('\\sin(t)');
      }} else {{
        terms.push('\\frac{{1}}{{' + h + '}}\\sin(' + h + 't)');
      }}
    }}
    return '$$ f(t) = \\frac{{4}}{{\\pi}}\\left[' + terms.join(' + ') + '\\right] $$';
  }}

  if (plotEl && plotEl._gs) {{
    plotEl.on('plotly_sliderchange', function(data) {{
      var step = data.step;
      if (step && step._index !== undefined) {{
        var n = step._index + 1;
        formulaEl.innerHTML = buildFormula(n);
        if (window.MathJax) {{
          MathJax.typesetPromise([formulaEl]);
        }}
      }}
    }});
  }}

  document.addEventListener('DOMContentLoaded', function() {{
    if (window.MathJax) {{
      MathJax.typesetPromise([formulaEl]);
    }}
  }});
}})();
</script>
</body>
</html>"""

    return html


def main():
    html = build_html()
    output_path = "fourier_3d/spectrum.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成: {output_path}")
    import webbrowser
    webbrowser.open(output_path)


if __name__ == "__main__":
    main()