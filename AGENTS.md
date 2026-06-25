# AGENTS.md

> Agent 协作与开发指南

## 项目概览

**傅里叶变换演示项目** —— 使用 Plotly 3D 交互式图表和 Manim 动画可视化方波的傅里叶级数合成。

### 核心功能

- **3D 交互式时频谱**：Plotly 生成可交互的 3D 可视化，支持动态调整谐波数量、切换视角
- **Manim 动画 A**：波形叠加动画，展示时域波形和频域幅度谱
- **Manim 动画 B**：旋转相量动画，展示相量矢量叠加实时合成波形

### 技术栈

| 依赖 | 版本要求 |
|:---|:---|
| Python | ≥ 3.11 |
| 包管理器 | uv |
| manim | ≥ 0.18.0 |
| plotly | ≥ 5.18.0 |
| numpy | ≥ 1.24.0 |

---

## 项目结构

```bash
fourier_transform_demo/
├── fourier_core.py                  # 共享核心：傅里叶级数计算
├── fourier_3d/
│   ├── plotly_spectrum.py           # 3D 交互式频谱生成器
│   └── spectrum.html                # 输出：静态 HTML 文件
├── fourier_manim/
│   ├── __init__.py
│   ├── scene_superposition.py       # Manim 波形叠加动画
│   └── scene_phasors.py             # Manim 旋转相量动画
├── manim.cfg                        # Manim 配置（LaTeX 禁用）
├── pyproject.toml                   # uv 依赖管理
└── README.md                        # 项目说明
```

---

## 环境设置

**Agent 必须执行**：

```bash
uv sync
```

这会创建虚拟环境并安装所有依赖。

---

## 常用命令

### 运行 3D 交互式频谱

```bash
uv run python fourier_3d/plotly_spectrum.py
```

在浏览器中打开生成的 `fourier_3d/spectrum.html` 即可交互。

### 预览 Manim 关键帧（输出图片）

```bash
# 波形叠加场景
uv run manim -s fourier_manim/scene_superposition.py FourierSuperposition

# 旋转相量场景
uv run manim -s fourier_manim/scene_phasors.py FourierPhasors
```

### 渲染 Manim 视频

```bash
# 低质量预览（较快）
uv run manim -pql fourier_manim/scene_superposition.py FourierSuperposition
uv run manim -pql fourier_manim/scene_phasors.py FourierPhasors

# 高质量渲染
uv run manim -pqh fourier_manim/scene_superposition.py FourierSuperposition
uv run manim -pqh fourier_manim/scene_phasors.py FourierPhasors
```

输出目录：

- 图片：`media/images/`
- 视频：`media/videos/`

---

## 代码约定

### 核心模块 `fourier_core.py`

提供纯计算函数，不包含可视化代码：

| 函数 | 功能 |
|:---|:---|
| `square_wave_fourier(t, n_harmonics)` | 计算合成波形值 |
| `harmonic_components(t, n_harmonics)` | 返回每个谐波分量 `shape (n_harmonics, len(t))` |
| `generate_waveform(n_harmonics, n_samples, n_periods)` | 生成完整波形采样 `(t, waveform, components)` |
| `spectrum(n_harmonics)` | 返回谐波频率和幅度 `(harmonics, amplitudes)` |

### 数学公式

方波的傅里叶级数展开（仅奇次谐波）：

$$f(t) = \frac{4}{\pi}\left[\sin(t) + \frac{1}{3}\sin(3t) + \frac{1}{5}\sin(5t) + \cdots\right]$$

### 命名约定

- `n_harmonics`: **谐波个数**，不是最高谐波次数。最高谐波次数 = `2 * n_harmonics - 1`
- `n_harm`: 同上
- `harmonics`: 谐波次数数组 `[1, 3, 5, ..., 2k+1]`
- `t`: 时间轴

---

## 配置说明

- `manim.cfg`: `tex_use_LaTeX = False` —— 禁用 LaTeX 编译避免环境依赖问题，使用 Manim 内置文本渲染
- `.python-version`: `3.11` —— Python 版本

---

## Git 忽略规则

已忽略：

- `.venv/` —— 虚拟环境
- `media/` —— Manim 输出（图片/视频）
- `__pycache__/` —— Python 缓存
- `.trae/` —— IDE 缓存

---

## Agent 协作指南

### 修改代码前

1. 确认功能归属模块：
   - 核心计算 → `fourier_core.py`
   - Plotly 3D → `fourier_3d/plotly_spectrum.py`
   - Manim 动画 → `fourier_manim/scene_*.py`

2. 保持 `fourier_core.py` 纯净：不引入可视化依赖

### 添加新功能

- 如果是新的 Manim 场景：在 `fourier_manim/` 下新建文件
- 如果是新的 Plotly 可视化：在 `fourier_3d/` 下新建文件
- 复用 `fourier_core.py` 中的现有函数

### 依赖管理

- 使用 `uv add <package>` 添加新依赖
- 不要提交 `uv.lock` 除非项目明确要求

---

## 故障排查

1. **Manim 中文/LaTeX 问题**：项目已禁用 LaTeX，如遇字体问题检查 Manim 配置
2. **依赖安装失败**：确认 Python ≥ 3.11，使用 `uv sync --refresh` 重新同步
3. **HTML 不显示**：检查 `fourier_3d/spectrum.html` 是否生成，重新运行脚本

---

## 关键帧配置

两个 Manim 场景都使用了 `KEY_FRAMES = [1, 5, 9, 15, 25, 39]`，对应显示以下最高谐波次数：

- 1 次谐波（1 个谐波）
- 5 次谐波（3 个谐波）
- 9 次谐波（5 个谐波）
- 15 次谐波（8 个谐波）
- 25 次谐波（13 个谐波）
- 39 次谐波（20 个谐波）
