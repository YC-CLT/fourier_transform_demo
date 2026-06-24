import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fourier_core import generate_waveform, spectrum

N_SAMPLES = 800
N_PERIODS = 2.0
MAX_HARMONICS = 50

PI = np.pi
T_MAX = N_PERIODS * 2 * PI
T_TICKVALS = [0, PI, 2 * PI, 3 * PI, 4 * PI]
T_TICKTEXT = ["0", "π", "2π", "3π", "4π"]

C10 = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
]


def build_laTeX(n_harmonics):
    terms = []
    for k in range(n_harmonics):
        h = 2 * k + 1
        if h == 1:
            terms.append(r"\sin(t)")
        else:
            terms.append(r"\frac{1}{%d}\sin(%dt)" % (h, h))
    return r"f(t) = \frac{4}{\pi}\left[%s\right]" % " + ".join(terms)


def create_figure():
    harmonics, amplitudes = spectrum(MAX_HARMONICS)
    t, waveform, components = generate_waveform(MAX_HARMONICS, N_SAMPLES, N_PERIODS)

    colors = (C10 * 5)[:MAX_HARMONICS]

    fig = make_subplots(
        rows=3, cols=2,
        specs=[
            [{"type": "scatter3d", "rowspan": 3}, {"type": "scatter"}],
            [None, {"type": "bar"}],
            [None, {"type": "scatter"}],
        ],
        subplot_titles=("3D 时频谱", "时域波形", "频谱", "时频图"),
        horizontal_spacing=0.07,
        vertical_spacing=0.10,
        row_heights=[0.40, 0.30, 0.30],
    )

    for k in range(MAX_HARMONICS):
        n = 2 * k + 1
        fig.add_trace(
            go.Scatter3d(
                x=t, y=np.full_like(t, n), z=components[k],
                mode="lines",
                line=dict(width=2, color=colors[k]),
                name="谐波 %d" % n,
                showlegend=False,
                hoverinfo="skip",
            ),
            row=1, col=1,
        )

    fig.add_trace(
        go.Scatter3d(
            x=t, y=np.zeros_like(t), z=waveform,
            mode="lines",
            line=dict(width=4, color="#FFD700"),
            name="合成波形",
            showlegend=False,
            hoverinfo="skip",
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
            hoverinfo="skip",
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
            hoverinfo="skip",
        ),
        row=2, col=2,
    )

    for k in range(MAX_HARMONICS):
        n = 2 * k + 1
        fig.add_trace(
            go.Scatter(
                x=t, y=np.full_like(t, n) + components[k] * 0.35,
                mode="lines",
                line=dict(width=1, color=colors[k]),
                name="谐波 %d" % n,
                showlegend=False,
                hoverinfo="skip",
            ),
            row=3, col=2,
        )

    updatemenus = [
        dict(
            type="buttons",
            direction="right",
            x=0.0, y=1.18,
            buttons=[
                dict(method="relayout", label="正面(时域)",
                     args=[{"scene.camera.eye": {"x": 0, "y": -2.5, "z": 0.1}}]),
                dict(method="relayout", label="侧面(频域)",
                     args=[{"scene.camera.eye": {"x": 2.5, "y": 0, "z": 0.1}}]),
                dict(method="relayout", label="顶部(时频)",
                     args=[{"scene.camera.eye": {"x": 0, "y": 0, "z": 2.5}}]),
                dict(method="relayout", label="默认视角",
                     args=[{"scene.camera.eye": {"x": 1.5, "y": -1.5, "z": 1.2}}]),
            ],
        ),
    ]

    fig.update_layout(
        title=dict(
            text="傅里叶级数 — 方波合成 3D 时频谱",
            x=0.5, xanchor="center",
            font=dict(size=18, color="#c9d1d9"),
        ),
        updatemenus=updatemenus,
        scene=dict(
            xaxis_title="时间 t",
            yaxis_title="频率 f",
            zaxis_title="振幅 A",
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2)),
            xaxis=dict(
                tickvals=T_TICKVALS, ticktext=T_TICKTEXT,
                range=[0, T_MAX],
            ),
            yaxis=dict(range=[-1, 2 * MAX_HARMONICS + 2]),
            zaxis=dict(range=[-1.5, 1.5]),
        ),
        height=860,
        margin=dict(l=0, r=0, t=100, b=0),
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font=dict(color="#c9d1d9"),
    )

    fig.update_xaxes(
        title_text="时间 t",
        tickvals=T_TICKVALS, ticktext=T_TICKTEXT,
        range=[0, T_MAX], gridcolor="#30363d",
        row=1, col=2,
    )
    fig.update_yaxes(title_text="振幅 A", gridcolor="#30363d", row=1, col=2)

    fig.update_xaxes(
        title_text="频率 f (谐波次数)",
        gridcolor="#30363d",
        row=2, col=2,
    )
    fig.update_yaxes(title_text="振幅 A", gridcolor="#30363d", row=2, col=2)

    fig.update_xaxes(
        title_text="时间 t",
        tickvals=T_TICKVALS, ticktext=T_TICKTEXT,
        range=[0, T_MAX], gridcolor="#30363d",
        row=3, col=2,
    )
    fig.update_yaxes(title_text="谐波次数", gridcolor="#30363d", row=3, col=2)

    return fig


def precompute_all_data():
    t = np.linspace(0, T_MAX, N_SAMPLES)
    t_list = t.tolist()

    all_data = {}
    for k in range(1, MAX_HARMONICS + 1):
        h = 2 * k - 1
        _, wf, comps = generate_waveform(k, N_SAMPLES, N_PERIODS)
        harm, amp = spectrum(k)

        tf_y = []
        for i in range(k):
            n = 2 * i + 1
            tf_y.append((np.full(N_SAMPLES, n) + comps[i] * 0.35).tolist())

        all_data[str(h)] = {
            "k": k,
            "t": t_list,
            "waveform": wf.tolist(),
            "components": [c.tolist() for c in comps],
            "harmonics": harm.tolist(),
            "amplitudes": amp.tolist(),
            "formula": build_laTeX(k),
            "tf_y": tf_y,
        }

    return json.dumps(all_data, separators=(",", ":"))


def build_html():
    fig = create_figure()
    plot_html = fig.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        config={"responsive": True},
    )

    all_data_json = precompute_all_data()

    html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>傅里叶级数 — 方波合成 3D 时频谱</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
window.MathJax = {
  tex: { inlineMath: [['$', '$'], ['\\(', '\\)']] },
  svg: { fontCache: 'global' }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" async></script>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: 'Microsoft YaHei','PingFang SC',sans-serif; background: #0d1117; }
  #top-bar {
    display: flex; align-items: center; justify-content: center; gap: 10px;
    padding: 6px 20px; background: #161b22; color: #c9d1d9; flex-wrap: wrap;
    border-bottom: 1px solid #30363d;
  }
  #top-bar label { font-size: 14px; white-space: nowrap; }
  #harmonic-input {
    width: 56px; text-align: center; font-size: 15px; padding: 3px 4px;
    border: 1px solid #30363d; border-radius: 4px; background: #0d1117; color: #c9d1d9;
  }
  #top-bar button {
    padding: 4px 10px; font-size: 13px; border: 1px solid #30363d;
    border-radius: 4px; background: #21262d; color: #c9d1d9; cursor: pointer;
    white-space: nowrap;
  }
  #top-bar button:hover { background: #30363d; }
  #top-bar button.active { background: #da3633; border-color: #da3633; color: #fff; }
  #formula-container {
    padding: 6px 20px; background: #161b22; color: #c9d1d9;
    text-align: center; font-size: 0.95em; min-height: 30px;
    border-bottom: 1px solid #30363d;
    overflow-x: auto; white-space: nowrap;
  }
  #plot-container { width: 100%; height: calc(100vh - 105px); }
  input[type=number]::-webkit-inner-spin-button { opacity: 1; }
</style>
</head>
<body>
<div id="top-bar">
  <label>谐波次数:</label>
  <button id="btn-down" title="减少">&#9664;</button>
  <input type="number" id="harmonic-input" value="1" min="1" max="99" step="2">
  <button id="btn-up" title="增加">&#9654;</button>
  <button id="btn-play" title="播放/暂停">&#9654; 播放</button>
  <span id="status-text" style="font-size:12px;color:#8b949e;"></span>
</div>
<div id="formula-container"></div>
<div id="plot-container">""" + plot_html + """</div>
<script>
(function() {
  var ALL_DATA = """ + all_data_json + """;
  var plotEl = document.getElementById('plot-container');
  var formulaEl = document.getElementById('formula-container');
  var inputEl = document.getElementById('harmonic-input');
  var btnUp = document.getElementById('btn-up');
  var btnDown = document.getElementById('btn-down');
  var btnPlay = document.getElementById('btn-play');
  var statusEl = document.getElementById('status-text');

  var MAX = """ + str(MAX_HARMONICS) + """;
  var N_TRACES = 2 * MAX + 3;
  var animTimer = null;
  var isPlaying = false;
  var animDirection = 1;

  function sigmoid(t) {
    var x = (t - 0.5) * 20;
    return 1 / (1 + Math.exp(-x));
  }

  function updateAll(harmonicValue) {
    var key = String(harmonicValue);
    var d = ALL_DATA[key];
    if (!d) return;
    var k = d.k;

    var graphDiv = plotEl.querySelector('.js-plotly-plot') || plotEl;

    var xAll = new Array(N_TRACES);
    var yAll = new Array(N_TRACES);
    var zAll = new Array(N_TRACES);
    var visAll = new Array(N_TRACES);

    var idx = 0;

    for (var i = 0; i < MAX; i++) {
      if (i < k) {
        xAll[idx] = d.t;
        yAll[idx] = new Array(d.t.length).fill(2 * i + 1);
        zAll[idx] = d.components[i];
        visAll[idx] = true;
      } else {
        xAll[idx] = [];
        yAll[idx] = [];
        zAll[idx] = [];
        visAll[idx] = false;
      }
      idx++;
    }

    xAll[idx] = d.t;
    yAll[idx] = new Array(d.t.length).fill(0);
    zAll[idx] = d.waveform;
    visAll[idx] = true;
    idx++;

    xAll[idx] = d.t;
    yAll[idx] = d.waveform;
    visAll[idx] = true;
    idx++;

    xAll[idx] = d.harmonics;
    yAll[idx] = d.amplitudes;
    visAll[idx] = true;
    idx++;

    for (var i = 0; i < MAX; i++) {
      if (i < k) {
        xAll[idx] = d.t;
        yAll[idx] = d.tf_y[i];
        visAll[idx] = true;
      } else {
        xAll[idx] = [];
        yAll[idx] = [];
        visAll[idx] = false;
      }
      idx++;
    }

    var maxH = 2 * k - 1;
    var yMax3D = maxH + 2;
    var yMaxFreq = maxH + 2;
    var maxAmp = Math.max.apply(null, d.amplitudes);

    Plotly.restyle(graphDiv, {
      x: xAll, y: yAll, z: zAll, visible: visAll
    });

    Plotly.relayout(graphDiv, {
      'scene.yaxis.range': [-1, yMax3D],
      'xaxis2.range': [0, yMaxFreq],
      'yaxis2.range': [0, maxAmp * 1.15],
      'yaxis3.range': [0, yMaxFreq],
    });

    var sm = sigmoid(k / MAX);
    statusEl.textContent = '方波近似度: ' + (sm * 100).toFixed(1) + '%';

    formulaEl.innerHTML = '$$' + d.formula + '$$';
    if (window.MathJax) MathJax.typesetPromise([formulaEl]);
    inputEl.value = harmonicValue;
  }

  function getCurrentHarmonic() {
    var v = parseInt(inputEl.value) || 99;
    if (v < 1) v = 1;
    if (v > 99) v = 99;
    if (v % 2 === 0) v = Math.max(1, v - 1);
    return v;
  }

  function stepUp() {
    var v = getCurrentHarmonic();
    if (v < 99) { v += 2; updateAll(v); }
  }

  function stepDown() {
    var v = getCurrentHarmonic();
    if (v > 1) { v -= 2; updateAll(v); }
  }

  function togglePlay() {
    if (isPlaying) { stopPlay(); }
    else { startPlay(); }
  }

  function startPlay() {
    isPlaying = true;
    btnPlay.textContent = '⏸ 暂停';
    btnPlay.classList.add('active');
    animDirection = 1;
    var v = getCurrentHarmonic();
    if (v >= 99) { v = 1; animDirection = 1; }
    if (v <= 1) { v = 1; animDirection = 1; }
    updateAll(v);

    animTimer = setInterval(function() {
      var v = getCurrentHarmonic();
      v += 2 * animDirection;
      if (v >= 99) { v = 99; animDirection = -1; }
      if (v <= 1) { v = 1; animDirection = 1; }
      updateAll(v);
    }, 500);
  }

  function stopPlay() {
    isPlaying = false;
    btnPlay.textContent = '▶ 播放';
    btnPlay.classList.remove('active');
    if (animTimer) { clearInterval(animTimer); animTimer = null; }
  }

  btnUp.addEventListener('click', function() { if (isPlaying) stopPlay(); stepUp(); });
  btnDown.addEventListener('click', function() { if (isPlaying) stopPlay(); stepDown(); });
  btnPlay.addEventListener('click', togglePlay);

  inputEl.addEventListener('change', function() {
    if (isPlaying) stopPlay();
    updateAll(getCurrentHarmonic());
  });

  inputEl.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowUp') { e.preventDefault(); if (isPlaying) stopPlay(); stepUp(); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); if (isPlaying) stopPlay(); stepDown(); }
  });

  setTimeout(function() { updateAll(1); }, 600);
})();
</script>
</body>
</html>"""

    return html


def main():
    html = build_html()
    output_path = "fourier_3d/spectrum.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Generated: " + output_path)
    import webbrowser
    webbrowser.open("D:/CodeFile/manim/" + output_path)


if __name__ == "__main__":
    main()