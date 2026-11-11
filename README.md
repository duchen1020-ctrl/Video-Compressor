# Video Compressor · 视频压缩工具

一个**单文件、零依赖、纯本地**的视频压缩与处理工具。启动后自动打开网页界面，
所有解析与编码都在你自己的机器上完成——**不联网上传、不收集任何数据、不需要账号**。

> 底层调用 `ffmpeg` / `ffprobe`，界面与界面里的所有逻辑都写在一个 Python 文件里，
> 只用标准库，没有任何第三方 Python 包。

---

## ✨ 主要功能

### 压缩
| 模式 | 说明 |
|---|---|
| 画质优先 (CRF) | 经典质量档，CRF 越小越清晰、体积越大 |
| 智能体积 | 抽片试压拟合并反推 CRF，**精准命中目标 MB**，且只编码一遍（比两遍编码快约 2 倍） |
| 画质目标 | 先定 SSIM 下限（如 0.99），自动反推满足该画质的最小体积 CRF |
| 目标比例 / 固定体积 | 按百分比或 MB 压缩 |

### 画质增强（可选，按需叠加）
去隔行 · 去压缩块 · 降噪（hqdn3d / nlmeans / atadenoise 三种强度）· 去色带 ·
Lanczos 超清放大 · 锐化（unsharp / CAS）· 调色（亮度/对比度/饱和度/gamma）· 帧率插帧。

### 画幅转换
9:16 竖屏 / 1:1 方形 / 3:4 / 4:3 / 16:10 / 16:9，三种填法：
**裁切填满**（不留边）／**纯色边框**（主体完整）／**模糊填充**（主体完整，留白用自身画面模糊）。

### 音频
音量归一化（loudnorm −14 / −16 LUFS）· 底噪降噪（afftdn）· 自定义码率／采样率／声道 · 保留原音轨。

### 水印与字幕
文字水印（系统字体 + 阴影，位置／大小／透明度可调）· 图片水印（相对视频宽缩放 + 透明）·
外挂 srt/ass 与内嵌字幕轨直接烧进画面。

### 工具箱
转 GIF · 截取片段 · 防抖（deshake）· 按旋转元数据自动转正 · 抽帧截图 · **拼接多个视频**。

### 编码格式
H.265 / H.264，另有 **AV1**（libsvtav1 / libaom-av1）与 **VP9**（libvpx-vp9）可选，
同画质下比 H.265 再小 20–30%（编码较慢，适合归档）。

### 质量保障
- **输出自动验收**：编码后核对容器／时长／音轨／字幕数并实际解码（抽 3 段或整片），坏输出直接丢弃。
- **A/B 滑动对比**：同一时间点取原片与输出两帧，左右拖动擦除对比，支持 1×/2×/3× 放大逐帧查看。
- **失败自愈**：硬件编码或滤镜导致失败时，自动降级为软件编码 / 关闭滤镜重试一次。
- 硬件编码自动探测（NVIDIA NVENC / Intel QSV / AMD AMF），压缩后反而变大时自动保留原片。

### 效率
多文件并行（1–4 线程）· 智能直传（码率已够低直接无损封装）· 限高缩放 · 断点续跑 · 磁盘空间预检。

### 其它
命名方案存取 · 队列导入导出 · 任务历史与节省统计 · 输出文件名模板 · 深浅色主题 · 纯命令行批处理模式。

---

## 📋 环境要求

- **Python 3.8+**（只用标准库，无需 pip 安装任何东西）
- **ffmpeg + ffprobe**：本仓库不附带二进制（许可证与体积原因），三选一即可
  1. 把 `ffmpeg.exe` 与 `ffprobe.exe` 直接放进本目录；
  2. 装成系统 PATH 里的命令（Windows 建议用 [winget](https://winget.run/) 或 [BtbN builds](https://github.com/BtbN/FFmpeg-Builds)）；
  3. 启动后在界面底部粘贴 `ffmpeg.exe` 的完整路径。

---

## 🚀 快速开始

**Windows**：双击 `start.bat`

**macOS / Linux**：
```bash
python3 video_compressor.py
```

启动后浏览器会自动打开 <http://127.0.0.1:8765>。选文件夹 → 扫描 → 调参数 → 开始压缩。

> 首次使用建议先点「智能分析」，它会采样检测黑边、隔行、亮度、动态范围，并给出一套带解释的推荐参数。

---

## ⌨️ 命令行模式

无需浏览器，适合批量与脚本化：

```bash
# 压缩整个目录（递归），加载已保存的方案
python video_compressor.py --cli -i "D:\videos" --recursive --scheme 壁纸方案

# 指定参数，输出 JSON 汇总便于脚本解析
python video_compressor.py --cli -i a.mp4 b.mp4 --crf 26 --workers 3 --json

# 按画质目标反推 CRF
python video_compressor.py --cli -i a.mp4 --mode quality --quality-target 0.99

# 智能体积：精准命中 50MB
python video_compressor.py --cli -i a.mp4 --mode smart --target-mb 50

# 转 9:16 竖屏并按模板命名
python video_compressor.py --cli -i a.mp4 --aspect 9:16 --aspect-mode blur \
    --name-template "{date}_{index}_{name}_c{crf}"

# 工具箱：拼接多个视频
python video_compressor.py --cli --tool concat --tool-sources "a.mp4|b.mp4" --tool-out 合并.mp4
```

完整参数见 `python video_compressor.py --cli --help`。

---

## 🗂 目录结构

```
video-compressor/
├── video_compressor.py   # 主程序（单文件，含全部界面与逻辑）
├── start.bat             # Windows 启动脚本（自动探测 Python）
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

运行时会在本目录自动生成 `logs/`（任务日志）、`history.jsonl`（历史统计）、`schemes.json`（参数方案），
均已加入 `.gitignore`——它们含有本机路径与文件名，不应上传。

---

## 🔒 隐私

- 所有视频处理都在本机完成，**不会把任何文件传到网络**。
- 程序不含任何网络请求代码，不联网上报统计、不需要登录。
- 界面里的「便携版」按钮只在**本机**做硬链接/复制，不涉及外网。
- 运行时生成的数据（历史、日志、方案）都保存在程序目录，可随时删除。

---

## ❓ 常见问题

**Q：界面提示「未找到 ffmpeg」怎么办？**
把 `ffmpeg.exe`、`ffprobe.exe` 放进本目录，或在界面底部粘贴完整路径。

**Q：编码很慢？**
把预设从 `slow` 改成 `fast`；或在「速度与保护」里勾选智能直传与限高；
有独显会自动使用 NVENC/QSV 硬件编码。

**Q：输出比原文件还大？**
默认已开启「压缩后变大时保留原片」，不会产出反而更大的文件。想真正压小请调高 CRF。

**Q：想批量处理又要能看进度？**
用网页界面（支持实时进度、ETA、中止、断点续跑）；命令行模式适合无人值守。

---

## 📄 License

MIT License — 详见 [LICENSE](LICENSE)。

本项目调用 `ffmpeg`，其本身采用 LGPL/GPL，你需自行遵守对应许可证。
