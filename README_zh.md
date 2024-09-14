# Sparks Lab SSY Color Book

[English](README.md) | **简体中文**

这是一份自制的电子色卡，包括几乎所有种类的颜色，旨在免去视觉设计时在调色盘上搓颜色的痛苦过程（许多软件的调色盘都不那么好用，HSV 颜色模型有时也非常反直觉）。

<p><img alt="Screenshot" src="./README_assets/screenshot.png" width=50%></p>

> ⚠️ **Firefox 对广色域显示器的支持不完整。如果你使用 Firefox，请确保将显示器设置为 sRGB 模式。**
>
> 基于 Chromium 的浏览器可以正常支持广色域显示器，前提是显示器的 ICC 文件中具有正确的色域信息。
>
> 色卡中的颜色使用 CSS 广色域标准实现。如果你的浏览器遵循该标准，你可以使用此色卡的任意版本，无论显示器的色域。但请注意，超出显示器色域的颜色不能准确显示。

此仓库仅包含生成色卡所需的代码。[如需直接查看或保存色卡请点击此处](https://sparkslab.art/colors/)。

还提供[十六进制 RGB 颜色值的下载](https://sparkslab.art/colors/palette/)。

## 简介

### 颜色编号体系

颜色编号体系类似于 HSV，但是更加设备独立并且符合直觉。

<p><img alt="48047 Color Sample" src="README_assets/color-sample.png" width="75" /></p>

```plain
4 8 0 4 7
\___/ | |
  |   | ** 表观亮度，从 0 到 C (12)。
  |   ** 饱和度，从 0 到 C (12)。
  ** 色相，用单色光波长表示，单位为 nm。
```

注：

- 计算过程中使用的白点永远是 D65（与标准的显示器或常见的日光灯接近）。
- 有的色相（比如品红）并不能对应某种单色光。它们以 400nm（蓝紫）和 700nm（红）之间的混合比例表示。例如，`L12` 表示 12% 的蓝紫色和 88% 的红色线性混合。
- 饱和度为 `0` 时，色相没有意义，因而省略。例如白色应当表示为 `0C`，而非 `4000C` 或 `5600C`.
- 亮度为 `0` 时颜色只能是黑色。我们规定黑色表示为 `00`。
- 在显示器或印刷/印染设备中，亮度为最大值 `C` 的颜色只能是白色，因为不可能在不降低亮度的情况下实现其他颜色。

### 色域指示符号的含义

<p><img alt="Gamut indicators" src="README_assets/gamut-indicators.png" width="340" /></p>

| 指示符号 | 能否显示 | 能否通过 CMYK 复现 |
| - | - | - |
| ` ` | + | + |
| `—` | + | - |
| `＋` | - | + |
| `×` | - | - |

CMYK 基于广泛使用的 JapanColor2001Coated 标准，白点转移到 D65。

## 原则

此色卡的设计原则如下：

1. 颜色集不应当有偏向性，而应当包含几乎所有种类的颜色，包括很亮的、很暗的、低对比度的以及低饱和度的（但不必包含显示器所能显示的**最**饱和颜色）。
2. 每个颜色应当有一个不太长的、方便记忆的编号，编号应当符合直觉。
3. 每个颜色都应当有设备无关的表示，并且（在可用的情况下）提供 sRGB、DisplayP3 和 AdobeRGB 下的 RGB 数值。
4. 可显示的颜色总数不能超过 2400。

## 技术细节

### 从色号到 SSY 坐标

色卡基于一种自行实现的颜色坐标，称为 `SSY`。以 `48047` 颜色为例：

```plain
ssy(480 0.215 0.500)
    \_/ \___/ \___/
     |    |     |
     |    |     ** 表观亮度，范围 [0, 1]
     |    ** 饱和度，范围 [0, 1]
     ** 光谱波长，[400, 700] ∪ [-1, -99]
// 负数波长表示 700nm 红色与 400nm 蓝紫色的混合比例
```

饱和度与亮度的计算规则为：

```python
saturation = (saturation_digit / 12) ** 1.4

brightness_temp = brightness_digit - 2
if brightness_temp < 2:
  # 将 [-2, 2] 范围映射到 [0, 2]
  brightness_temp = brightness_temp / 2 + 1
brightness = brightness_temp / 12
```

这样的规则设计使色卡在低亮度和低饱和度区域有更细的颜色区分粒度。

### 从 SSY 到 RGB

<p><img alt="chromaticity diagram" src="README_assets/CIE1931xy_blank.svg.png" width="240" /></p>

SSY 首先转换到 [CIE-xyY](https://en.wikipedia.org/wiki/CIE_1931_color_space#CIE_xy_chromaticity_diagram_and_the_CIE_xyY_color_space) 坐标。继续上面的例子：

1. 首先找到波长 480nm 对应的色品图 xy 坐标 `xy(0.091 0.133)`。
2. 找到 D65 白点对应的坐标 `xy(0.313 0.329)`。
3. 按照饱和度比例 `0.215`，将 21.5% 的 480nm 和 78.5% 的 D65 坐标混合，生成新的 xy 坐标 `xy(0.265 0.287)`。
4. 将亮度值直接用作 CIE-xyY 的 Y 分量，得到 `xyY(0.265 0.287 0.500)`。

在假定白点是 D65，我们利用 `python-colormath` 获得 sRGB 和 AdobeRGB 坐标。`python-colormath` 默认保留超出色域的数值，因此很容易判断颜色是否超出色域。

`python-colormath` 并不原生支持 DisplayP3 标准。我们自行实现了转换矩阵以将 sRGB 转换到 DisplayP3。欲了解细节，请阅读 [specsy.py](./specsy.py)。

颜色被认为超出色域，当且仅当 RGB 中至少一个分量存在超出 `[0, 1]` 范围的非法值。

### 从 SSY 到 CMYK（JapanColor2001）

首先我们将 CIE-xyY 坐标直接转换到 CIE-xyz。

我们使用 `littlecms` 将 CIE-xyY 坐标在 `perceptual` 模式下转换为 CMYK 值。这一步需要查表完成，因此 `littlecms` 不会保留超出色域的数值。为了检查颜色是否超出色域，我们采用如下方法：

1. 将 CIE-xyz 转换到 CMYK。
2. 将 CMYK 用同样的配置文件转换回 CIE-xyz。
3. 将获得的颜色与原来的比较。如果它们的 [CMC delta E](https://en.wikipedia.org/wiki/Color_difference#CMC_l:c_(1984)) 色差不小于 3，则认为颜色不能用 CMYK 复现。

### 色相的选择

颜色在波长上的分布非常不均匀。目前，色卡中使用的波长值是手动挑选的。欲了解细节，请阅读 [main.py](main.py)。
