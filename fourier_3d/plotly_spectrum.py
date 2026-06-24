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

    colors_3d = (
        ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
         "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"] * 5
    )

    for k in range(MAX_HARMONICS):
        n = 2 * k + 1
        fig.add_trace(
            go.Scatter3d(
                x=t, y=np.full_like(t, n), z=components[k],
                mode="lines",
                line=dict(width=2, color=colors_3d[k]),
                name="谐波 %d" % n,
                showlegend=False,
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

    updatemenus = [
        dict(
            type="buttons",
            direction="right",
            x=0.0, y=1.18,
            buttons=[
                dict(method="relayout", label="正面(时域)", args=[{"scene.camera.eye": {"x": 0, "y": -2.5, "z": 0.1}}]),
                dict(method="relayout", label="侧面(频域)", args=[{"scene.camera.eye": {"x": 2.5, "y": 0, "z": 0.1}}]),
                dict(method="relayout", label="顶部(时频)", args=[{"scene.camera.eye": {"x": 0, "y": 0, "z": 2.5}}]),
                dict(method="relayout", label="默认视角", args=[{"scene.camera.eye": {"x": 1.5, "y": -1.5, "z": 1.2}}]),
            ],
        ),
    ]

    fig.update_layout(
        title="傅里叶级数 — 方波合成 3D 时频谱",
        updatemenus=updatemenus,
        scene=dict(
            xaxis_title="时间 t",
            yaxis_title="频率 f (谐波次数)",
            zaxis_title="振幅 A",
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2)),
        ),
        height=800,
        margin=dict(l=0, r=0, t=100, b=0),
        xaxis2=dict(title="时间 t"),
        yaxis2=dict(title="幅值"),
        xaxis3=dict(title="谐波次数"),
        yaxis3=dict(title="幅度"),
    )

    fig.update_scenes(
        xaxis_range=[0, N_PERIODS * 2 * np.pi],
        yaxis_range=[-1, 2 * MAX_HARMONICS + 2],
        zaxis_range=[-1.5, 1.5],
    )

    return fig


def precompute_all_data():
    t = np.linspace(0, N_PERIODS * 2 * np.pi, N_SAMPLES)
    t_list = t.tolist()

    all_data = {}
    for k in range(1, MAX_HARMONICS + 1):
        h = 2 * k - 1
        _, wf, comps = generate_waveform(k, N_SAMPLES, N_PERIODS)
        harm, amp = spectrum(k)

        all_data[str(h)] = {
            "k": k,
            "t": t_list,
            "waveform": wf.tolist(),
            "components": [c.tolist() for c in comps],
            "harmonics": harm.tolist(),
            "amplitudes": amp.tolist(),
            "formula": build_laTeX(k),
        }

    return json.dumps(all_data)


def build_html():
    fig = create_figure()
    plot_html = fig.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        config={"responsive": True},
    )

    all_data_json = precompute_all_data()

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>傅里叶级数 — 方波合成 3D 时频谱</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
window.MathJax = {
  tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']] },
  svg: { fontCache: 'global' }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" async></script>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; background: #0d1117; }
  #top-bar {
    display: flex; align-items: center; justify-content: center; gap: 10px;
    padding: 8px 20px; background: #161b22; color: #c9d1d9; flex-wrap: wrap;
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
    padding: 8px 20px; background: #161b22; color: #c9d1d9;
    text-align: center; font-size: 1.1em; min-height: 32px;
    border-bottom: 1px solid #30363d;
  }
  #plot-container { width: 100%; height: calc(100vh - 110px); }
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
  <span id="status-text" style="font-size:12px; color:#8b949e;"></span>
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

  var MAX_HARMONICS = """ + str(MAX_HARMONICS) + """;
  var animTimer = null;
  var isPlaying = false;
  var animDirection = 1;

  function getHarmonicKey(v) {
    return String(v);
  }

  function updateAll(harmonicValue) {
    var key = getHarmonicKey(harmonicValue);
    var d = ALL_DATA[key];
    if (!d) return;
    var k = d.k;

    var graphDiv = plotEl.querySelector('.js-plotly-plot') || plotEl;

    var xAll = [], yAll = [], zAll = [], visAll = [];

    for (var i = 0; i < MAX_HARMONICS; i++) {
      if (i < k) {
        xAll.push(d.t);
        yAll.push(new Array(d.t.length).fill(2 * i + 1));
        zAll.push(d.components[i]);
      } else {
        xAll.push([]);
        yAll.push([]);
        zAll.push([]);
      }
      visAll.push(i < k);
    }

    xAll.push(d.t);
    yAll.push(new Array(d.t.length).fill(0));
    zAll.push(d.waveform);
    visAll.push(true);

    xAll.push(d.t);
    yAll.push(d.waveform);
    zAll.push(null);
    visAll.push(true);

    xAll.push(d.harmonics);
    yAll.push(d.amplitudes);
    zAll.push(null);
    visAll.push(true);

    Plotly.restyle(graphDiv, {
      x: xAll, y: yAll, z: zAll, visible: visAll
    });

    formulaEl.innerHTML = '$$ ' + d.formula + ' $$';
    if (window.MathJax) {
      MathJax.typesetPromise([formulaEl]);
    }
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
    statusEl.textContent = '';
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