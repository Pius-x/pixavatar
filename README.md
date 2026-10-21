**简体中文** | [English](README.en.md)

# pixavatar

用 Python 生成 GitHub 风格头像：左右镜像的 identicon、字母头像、自定义像素图案。支持固定种子复现、配色、透明背景，输出尺寸随意。

![examples](examples/sheet.png)

## 特性

- **Identicon** — 左右镜像的 N×N 网格，填充密度限制在 30%–80%，不会太空也不会糊
- **可复现** — `--seed` 固定后，每次生成同一个形状
- **配色** — 单色或色池随机，支持自定义背景、透明背景
- **字母** — 内置 5×7 点阵字体，支持 A–Z
- **自定义图案** — `--mask` 只写左半边，右侧自动镜像
- **任意尺寸** — `--cell-size` 和 `--padding` 控制分辨率，1024px 以上没问题

## 安装

需要 Python 3.8+ 和 [Pillow](https://python-pillow.org/)。

```bash
pip install pillow
```

无其他依赖。

## 用法

```bash
# 随机头像
python pixavatar.py --out avatar.png

# 固定形状和颜色
python pixavatar.py --seed 42 --color 2EA44F --out avatar.png

# 从色池里随机取一个颜色
python pixavatar.py --seed 42 --color 2EA44F,0969DA,8250DF --out avatar.png

# 7×7 字母头像
python pixavatar.py --letter X --cell-count 7 --color 1B7C83 --out letter.png

# 自定义图案：5 行，每行 3 个字符（左半边），右侧自动镜像
python pixavatar.py --mask 010,111,001,011,001 --color 8250DF --out pattern.png

# 透明背景、1024px 画布
python pixavatar.py --seed 42 --color E36209 --cell-size 128 --padding 64 --transparent --out avatar.png

# 一次生成 6 个候选
python pixavatar.py --count 6 --color 2EA44F,0969DA,8250DF --out candidate.png
```

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--seed` | 随机 | 整数种子，固定后形状可复现 |
| `--color` | 随机 | 前景色，十六进制，可逗号分隔多个 |
| `--bg` | `F1F1F1` | 背景色 |
| `--cell-count` | `5` | 网格边长（N×N） |
| `--cell-size` | `64` | 每格像素 |
| `--padding` | `32` | 网格四周留白像素 |
| `--transparent` | 关 | 透明背景 |
| `--density-min` / `--density-max` | `0.3` / `0.8` | identicon 填充密度范围 |
| `--mask` | — | 自定义图案，逗号分隔每行左半边 |
| `--letter` | — | 字母 `A`–`Z` |
| `--count` | `1` | 生成数量 |
| `--out` | `avatar.png` | 输出文件；多张时作为前缀 |

## 自定义图案

`--mask` 每行一个字符串，每个字符串是图案的**左半边**（`0` = 空，`1` = 填充），右半边自动镜像。

一个 5×5 的心形：

```
010
111
111
011
001
```

```bash
python pixavatar.py --mask 010,111,111,011,001 --color D1242F --out heart.png
```

列数必须等于 `ceil(cell_count / 2)`，行数必须等于 `cell_count`。

## 算法说明

思路来自 [afkbrb/github-avatar-generator](https://github.com/afkbrb/github-avatar-generator)：

1. 随机填充 N×N 网格的左半边，镜像到右半边。
2. 统计填充格数，不在半边面积的 30%–80% 之间就整块重抽——避免头像太空或太满。
3. 随机选前景色，过滤掉过暗、过亮、接近灰的颜色。

相比原项目的增强：固定种子可复现、色池、点阵字母、自定义图案、透明背景。

## 致谢

灵感来自 [afkbrb/github-avatar-generator](https://github.com/afkbrb/github-avatar-generator)（Java AWT）。本项目是独立的 Python 实现，并增加了固定种子、色池、字母点阵、自定义图案和透明输出。

## 许可证

[MIT](LICENSE)
