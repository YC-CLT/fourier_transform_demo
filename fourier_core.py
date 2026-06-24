import numpy as np


def square_wave_fourier(t, n_harmonics):
    """计算方波傅里叶级数在 t 时刻的值（仅奇次谐波）。

    f(t) = (4/π) * Σ_{k=0}^{n_harmonics-1} sin((2k+1)*t) / (2k+1)

    Args:
        t: 时间（标量或数组）
        n_harmonics: 谐波数量（1~20，对应 1,3,5,...,39 次谐波）

    Returns:
        合成波形值
    """
    result = np.zeros_like(t, dtype=float)
    for k in range(n_harmonics):
        n = 2 * k + 1
        result += np.sin(n * t) / n
    return (4.0 / np.pi) * result


def harmonic_components(t, n_harmonics):
    """计算每个谐波分量在 t 时刻的瞬时值。

    Args:
        t: 时间（标量或数组）
        n_harmonics: 谐波数量

    Returns:
        shape (n_harmonics, len(t)) 的数组，第 k 行为第 k 个谐波分量
    """
    t = np.atleast_1d(t)
    components = np.zeros((n_harmonics, len(t)))
    for k in range(n_harmonics):
        n = 2 * k + 1
        components[k] = (4.0 / np.pi) * np.sin(n * t) / n
    return components


def generate_waveform(n_harmonics, n_samples=1000, n_periods=2.0):
    """生成完整波形采样数据。

    Args:
        n_harmonics: 谐波数量
        n_samples: 采样点数
        n_periods: 时间跨度（周期数，基频周期=2π）

    Returns:
        (t, waveform, components)
        - t: shape (n_samples,) 时间轴
        - waveform: shape (n_samples,) 合成波形
        - components: shape (n_harmonics, n_samples) 各谐波分量
    """
    t = np.linspace(0, n_periods * 2 * np.pi, n_samples)
    waveform = square_wave_fourier(t, n_harmonics)
    components = harmonic_components(t, n_harmonics)
    return t, waveform, components


def spectrum(n_harmonics):
    """返回谐波频率和幅度。

    Args:
        n_harmonics: 谐波数量

    Returns:
        (harmonics, amplitudes)
        - harmonics: shape (n_harmonics,) 谐波次数 [1, 3, 5, ...]
        - amplitudes: shape (n_harmonics,) 幅度 [4/π, 4/(3π), 4/(5π), ...]
    """
    harmonics = np.array([2 * k + 1 for k in range(n_harmonics)], dtype=float)
    amplitudes = (4.0 / np.pi) / harmonics
    return harmonics, amplitudes