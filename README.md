# 傅里叶级数 — 方波合成 3D 可视化

用 **Plotly 3D 交互图** + **Manim 动画** 两种方式可视化傅里叶级数中方波合成过程。

## 快速开始

```bash
uv sync
```

## 使用方式

### 3D 可交互时频谱

生成含动态 LaTeX 公式的纯静态 HTML，浏览器打开即可使用：

```bash
uv run python fourier_3d/plotly_spectrum.py
```

功能：

- 3D 坐标系 (t, f, A)：时间、频率、振幅
- 正面/侧面/顶部 一键切换视角观察时域/频域/时频图
- 数字输入框 + ◀/▶ 按钮 + 键盘上下箭头调节谐波 (1~99，仅奇次)
- 播放/暂停：自动循环 1→99→1
- 动态 LaTeX 公式实时更新
- 支持鼠标拖拽旋转、缩放、平移

### Manim 场景 A：经典叠加动画

上：时域合成波形（逼近方波），下：频谱柱状图。输出 6 张关键帧 PNG：
功能：
- 上轴：时域波形叠加，谐波越多越接近方波
- 下轴：频谱柱状图，仅奇次谐波有值
- 6 个关键帧：1, 5, 9, 15, 25, 39 次谐波

```bash
uv run manim -s fourier_manim/scene_superposition.py FourierSuperposition
```

图片位于 `media/images/scene_superposition/`。

### Manim 场景 B：旋转向量动画

左：旋转向量（phasor）首尾相连，每根向量以各自频率旋转。右：末端轨迹实时描出合成波形。输出 6 张关键帧 PNG：
功能：
- 左图：谐波向量按各自频率旋转，直观展示频域叠加
- 右图：向量末端随时间推移描出合成波形
- 6 个关键帧：1, 5, 9, 15, 25, 39 次谐波

```bash
uv run manim -s fourier_manim/scene_phasors.py FourierPhasors
```

图片位于 `media/images/scene_phasors/`。

> 去掉 `-s` 可渲染为 mp4 视频，如 `uv run manim -pql fourier_manim/scene_superposition.py FourierSuperposition`

## 项目结构

```bash
manim/
├── fourier_core.py                  # 共享核心：傅里叶级数计算
├── fourier_3d/
│   ├── plotly_spectrum.py           # 3D 可交互时频谱生成脚本
│   └── spectrum.html                # 输出：纯静态 HTML
├── fourier_manim/
│   ├── __init__.py
│   ├── scene_superposition.py       # Manim 叠加动画
│   └── scene_phasors.py             # Manim 旋转向量动画
├── manim.cfg                        # Manim 配置（禁用 LaTeX）
└── pyproject.toml                   # uv 依赖管理
```

## 数学原理

方波的傅里叶级数展开（仅奇次谐波）：

$$f(t) = \frac{4}{\pi}\left[\sin(t) + \frac{1}{3}\sin(3t) + \frac{1}{5}\sin(5t) + \frac{1}{7}\sin(7t) + \cdots\right]$$

谐波数量越多，合成波形越接近理想方波。在有限项截断时，跳变点附近会出现 Gibbs 现象（约 9% 过冲）。

## 技术栈

- Python 3.11+
- uv 包管理
- Manim Community v0.20+
- Plotly 5.18+
- NumPy
- MathJax 3 (CDN)