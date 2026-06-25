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
        subplot_titles=("3D Spectrogram", "Time Domain", "Spectrum", "Spectrogram"),
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
        amp = amplitudes[k]
        fig.add_trace(
            go.Scatter(
                x=[0, T_MAX],
                y=[n, n],
                mode="lines",
                line=dict(
                    width=2 + 4 * (amp / amplitudes[0]),
                    color=colors[k],
                ),
                name="谐波 %d" % n,
                showlegend=False,
                hoverinfo="skip",
            ),
            row=3, col=2,
        )

    updatemenus = []

    fig.update_layout(
        title=dict(
            text="傅里叶级数 — 方波合成 3D 时频谱",
            x=0.5, xanchor="center",
            font=dict(size=18, color="#c9d1d9"),
        ),
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

        tf_x = [0.0, T_MAX]
        tf_y = []
        for i in range(k):
            n = 2 * i + 1
            tf_y.append([n, n])

        all_data[str(h)] = {
            "k": k,
            "t": t_list,
            "waveform": wf.tolist(),
            "components": [c.tolist() for c in comps],
            "harmonics": harm.tolist(),
            "amplitudes": amp.tolist(),
            "formula": build_laTeX(k),
            "tf_x": tf_x,
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
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fourier Series — Square Wave Synthesis</title>
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
  #top-bar button.cam { background: #1a3a5c; border-color: #1f6feb; }
  #top-bar button.cam:hover { background: #1f6feb; }
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
  <label id="lbl-harmonic">Harmonics:</label>
  <button id="btn-down" title="Decrease">&#9664;</button>
  <input type="number" id="harmonic-input" value="1" min="1" max="99" step="2">
  <button id="btn-up" title="Increase">&#9654;</button>
  <button id="btn-play" title="Play/Pause">&#9654; Play</button>
  <span style="color:#484f58;">|</span>
  <button class="cam" id="btn-cam-front">Front(Time)</button>
  <button class="cam" id="btn-cam-side">Side(Freq)</button>
  <button class="cam" id="btn-cam-top">Top(TF)</button>
  <button class="cam" id="btn-cam-default">Default</button>
  <span id="status-text" style="font-size:12px;color:#8b949e;"></span>
  <span style="flex:1;"></span>
  <button id="btn-lang" style="font-size:11px;padding:3px 8px;">中文</button>
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
  var lblHarmonic = document.getElementById('lbl-harmonic');
  var btnLang = document.getElementById('btn-lang');
  var btnCamFront = document.getElementById('btn-cam-front');
  var btnCamSide = document.getElementById('btn-cam-side');
  var btnCamTop = document.getElementById('btn-cam-top');
  var btnCamDefault = document.getElementById('btn-cam-default');

  var MAX = """ + str(MAX_HARMONICS) + """;
  var N_TRACES = 2 * MAX + 3;
  var animTimer = null;
  var isPlaying = false;
  var animDirection = 1;
  var curLang = 'en';

  var I18N = {
    en: {
      title: "Fourier Series — Square Wave Synthesis 3D Spectrogram",
      docTitle: "Fourier Series — Square Wave Synthesis",
      subplot1: "3D Spectrogram",
      subplot2: "Time Domain",
      subplot3: "Spectrum",
      subplot4: "Spectrogram",
      sceneX: "Time t",
      sceneY: "Frequency f",
      sceneZ: "Amplitude A",
      xaxis: "Time t",
      yaxis: "Amplitude A",
      xaxis2: "Frequency f (Harmonic Order)",
      yaxis2: "Amplitude A",
      xaxis3: "Time t",
      yaxis3: "Harmonic Order",
      camFront: "Front (Time)",
      camSide: "Side (Freq)",
      camTop: "Top (TF)",
      camDefault: "Default",
      labelHarmonic: "Harmonics:",
      btnDownTitle: "Decrease",
      btnUpTitle: "Increase",
      btnPlayTitle: "Play/Pause",
      btnPlay: "▶ Play",
      btnPause: "⏸ Pause",
      statusFormat: "Square wave fit: {0}%",
      langBtn: "中文",
    },
    zh: {
      title: "傅里叶级数 — 方波合成 3D 时频谱",
      docTitle: "傅里叶级数 — 方波合成 3D 时频谱",
      subplot1: "3D 时频谱",
      subplot2: "时域波形",
      subplot3: "频谱",
      subplot4: "时频图",
      sceneX: "时间 t",
      sceneY: "频率 f",
      sceneZ: "振幅 A",
      xaxis: "时间 t",
      yaxis: "振幅 A",
      xaxis2: "频率 f (谐波次数)",
      yaxis2: "振幅 A",
      xaxis3: "时间 t",
      yaxis3: "谐波次数",
      camFront: "正面(时域)",
      camSide: "侧面(频域)",
      camTop: "顶部(时频)",
      camDefault: "默认",
      labelHarmonic: "谐波次数:",
      btnDownTitle: "减少",
      btnUpTitle: "增加",
      btnPlayTitle: "播放/暂停",
      btnPlay: "▶ 播放",
      btnPause: "⏸ 暂停",
      statusFormat: "方波近似度: {0}%",
      langBtn: "EN",
    },
  };

  function t(key) { return I18N[curLang][key] || key; }

  function switchLang() {
    curLang = (curLang === 'zh') ? 'en' : 'zh';
    var d = I18N[curLang];

    document.title = d.docTitle;
    btnLang.textContent = d.langBtn;
    lblHarmonic.textContent = d.labelHarmonic;
    btnDown.title = d.btnDownTitle;
    btnUp.title = d.btnUpTitle;
    btnPlay.title = d.btnPlayTitle;
    btnPlay.textContent = isPlaying ? d.btnPause : d.btnPlay;
    btnCamFront.textContent = d.camFront;
    btnCamSide.textContent = d.camSide;
    btnCamTop.textContent = d.camTop;
    btnCamDefault.textContent = d.camDefault;

    var graphDiv = plotEl.querySelector('.js-plotly-plot') || plotEl;
    Plotly.relayout(graphDiv, {
      'title.text': d.title,
      'scene.xaxis.title.text': d.sceneX,
      'scene.yaxis.title.text': d.sceneY,
      'scene.zaxis.title.text': d.sceneZ,
      'xaxis.title.text': d.xaxis,
      'yaxis.title.text': d.yaxis,
      'xaxis2.title.text': d.xaxis2,
      'yaxis2.title.text': d.yaxis2,
      'xaxis3.title.text': d.xaxis3,
      'yaxis3.title.text': d.yaxis3,
      'annotations[0].text': d.subplot1,
      'annotations[1].text': d.subplot2,
      'annotations[2].text': d.subplot3,
      'annotations[3].text': d.subplot4,
    });
    updateStatus();
  }

  btnLang.addEventListener('click', switchLang);

  function sigmoid(t) {
    var x = (t - 0.5) * 20;
    return 1 / (1 + Math.exp(-x));
  }

  function updateStatus() {
    var v = getCurrentHarmonic();
    var key = String(v);
    var d = ALL_DATA[key];
    if (!d) return;
    var sm = sigmoid(d.k / MAX);
    statusEl.textContent = I18N[curLang].statusFormat.replace('{0}', (sm * 100).toFixed(1));
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
        xAll[idx] = d.tf_x;
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

    formulaEl.innerHTML = '$$' + d.formula + '$$';
    if (window.MathJax) MathJax.typesetPromise([formulaEl]);
    inputEl.value = harmonicValue;
    updateStatus();
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
    btnPlay.textContent = I18N[curLang].btnPause;
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
    btnPlay.textContent = I18N[curLang].btnPlay;
    btnPlay.classList.remove('active');
    if (animTimer) { clearInterval(animTimer); animTimer = null; }
  }

  function setCamera(eye) {
    var graphDiv = plotEl.querySelector('.js-plotly-plot') || plotEl;
    Plotly.relayout(graphDiv, { 'scene.camera.eye': eye });
  }

  btnCamFront.addEventListener('click', function() { setCamera({x:0, y:-2.5, z:0.1}); });
  btnCamSide.addEventListener('click', function() { setCamera({x:2.5, y:0, z:0.1}); });
  btnCamTop.addEventListener('click', function() { setCamera({x:0, y:0, z:2.5}); });
  btnCamDefault.addEventListener('click', function() { setCamera({x:1.5, y:-1.5, z:1.2}); });

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

  setTimeout(function() { switchLang(); updateAll(1); }, 600);
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