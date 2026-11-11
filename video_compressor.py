#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频压缩工具 (本地 Web 界面) v12
v12 新增 (竖屏画幅 + AB 对比 + 文件名模板 + 视频拼接):
  - 画幅转换: 9:16 竖屏 / 1:1 方形 / 3:4 / 4:3 / 16:10 / 16:9 三种填充方式,
    裁切填满 (铺满不留边)、纯色边框 (主体完整)、模糊填充 (背景取自身模糊画面)。
    模糊填充需要「背景+主体」两路输入合成, 走 filter_complex 而非 -vf
  - A/B 滑动对比: 同一时间点取原片与输出两帧, 左右拖动擦除对比, 支持 1×/2×/3× 放大
    逐帧查看压缩细节, 并直接显示 SSIM / PSNR 与结论 (修掉了旧版两图取各自中点、
    对比的其实不是同一时刻的问题)
  - 输出文件名模板: {name} {crf} {size} {codec} {mode} {aspect} {date} {time} {index} {ext},
    批量处理时可自动命名, 自动清理 Windows 非法字符
  - 视频拼接: 工具箱新增「拼接多个视频」, 按待处理列表顺序合并; 编码参数一致时无损拼接,
    不一致时自动回退统一重编码 (统一分辨率/帧率/音轨, 缺音轨补静音)
  - CLI 同步: --aspect / --aspect-mode / --name-template / --tool concat
保留 v11 (音频增强 + 水印字幕 + 新编码器 + 视频工具箱):
  - 音频增强: 音量归一化 (loudnorm -14/-16 LUFS)、降噪 (afftdn)、自定义码率/采样率/声道,
    手机/网课录音忽大忽小、有底噪时一键提升听感, 全部走重编码链路
  - 水印与字幕烧录: 文字水印 (系统字体 + 阴影 + 可透明度/位置/大小)、图片水印 (相对视频宽缩放 + 透明),
    外挂/内嵌字幕直接烧进画面 (适合发短视频平台), 与增强滤镜链同图级联
  - 新编码器: AV1 (libsvtav1/libaom-av1) 与 VP9 (libvpx-vp9), 同画质下比 H.265 再小 20-30%,
    默认关、自动探测本机可用性, 仅软件编码 (编码慢, 适合归档)
  - 视频工具箱 (独立面板): 视频转 GIF、截取片段、防抖 (deshake)、按旋转元数据自动转正、抽帧截图
  - CLI 同步: --audio-* / --wm-* / --codec av1|vp9 / --tool gif|clip|deshake|rotate|frame
保留 v10 (画质目标 + 精细控制 + 可观测性):
  - 画质目标模式 quality: 抽段试压 3 档 CRF, 逐段算 SSIM, 拟合「CRF → 画质」曲线,
    反推满足目标 SSIM 的最大 CRF (即最小体积), 只编码一遍全片; 可先「试算画质曲线」看各档质量与体积
  - 逐文件微调: 队列里可对单个视频覆盖 CRF / 目标体积 / 限高 / 裁黑边 / 增强开关等, 不再全队列一刀切
  - 任务历史: 每次任务汇总写入 history.jsonl, 界面展示累计节省、成功率与近期节省率趋势, 支持导出与清空
  - 失败自愈: 硬件编码或增强滤镜导致 ffmpeg 失败时, 自动降级为软件编码 / 关闭滤镜重试一次
  - CLI 同步支持 --mode quality / --quality-target / --no-fallback
保留 v9 (智能分析 + 自动化工作流):
  - 智能分析: 采样 cropdetect / idet / signalstats 检测黑边、隔行、亮度、饱和度、运动量,
    结合码率密度推导一套带解释的推荐参数, 界面「一键采用」即可套用
  - 自动裁黑边 (crop=w:h:x:y) 接入滤镜链, 增强预览与编码同步生效
  - 输出验收: 编码后核对容器 / 时长 / 音轨 / 字幕数并实际解码(抽3段或整片),
    判定损坏的输出直接丢弃并标记失败, 结果表可点开逐项明细、随时复验
  - 参数方案: 命名保存/应用/删除 (schemes.json), 队列导出/导入 JSON
  - CLI 无界面批处理: --cli -i 文件或目录, --scheme 加载方案, --json 输出汇总
  - /api/start 参数构造抽成 make_opts, Web 与 CLI 共用同一套规则
保留 v8 (精准体积 + 完整保留 + 可续跑):
  - 智能体积模式: 片头/中/尾采样试压两档 CRF, 拟合「CRF→体积」曲线反推目标 CRF,
    只编码一遍全片即可精准命中目标 MB; 偏差 >15% 自动精修一次 (替代慢速两遍编码)
  - 流保留策略: 全部音轨 / 字幕 / 章节 / 元数据 / HDR 色彩标记, MP4 字幕自动转 mov_text
  - 压缩前后完整参数对比 (分辨率/帧率/编码/码率/音轨/字幕/章节/HDR), 点结果文件名查看
  - 磁盘空间预检 (启动前按输出目录估算, 不足则拦截并可确认忽略)
  - 断点续跑 (输出已存在且比源新时跳过)、原生多选文件对话框、深浅色主题
  - 修复: MKV/WebM 等容器误用 movflags 导致 ffmpeg 报错
保留 v7 (提速 + 继续升级):
  - 多文件并行压缩 (1-4 并发), 短视频批量处理吃满 CPU, 进度/ETA/中止全部线程安全
  - 极速方案: 一键 veryfast + 8bit + 自动硬件 + 智能直传 + 并行
  - 自动编码引擎 (检测到显卡自动用 NVENC/QSV/AMF, 没有就回退软件)
  - 智能直传: 源码率已低于阈值时不重编码, 直接无损封装 (秒级完成)
  - 最大高度限制 (1080p/720p/540p, 只降不升), 像素少了编码自然更快
  - 两遍编码首遍 fast-firstpass 加速、NVENC 快速档
  - 压缩后反而变大 → 自动保留原文件 (不再产出 119% 体积的文件)
  - 失败项一键重试、实时倍速显示、完成后自动打开输出目录、任务耗时汇总
保留 v6: 画质增强滤镜链/同帧预览/仅增强模式/滤镜能力探测
保留 v5 及更早: 预设/日志落盘/SSIM·PSNR/便携化/两遍编码/设置记忆
纯标准库实现, 无需联网安装依赖。
"""
import http.server
import socketserver
import threading
import subprocess
import json
import os
import re
import time
import tempfile
import shutil
import webbrowser
import base64
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
PORT = 8765
def _default_work_dir():
    """默认工作目录: 优先系统「视频」目录, 其次桌面, 再否则用户主目录。"""
    home = os.path.expanduser("~")
    for name in ("Videos", "视频", "Desktop", "桌面", "Downloads", "下载"):
        p = os.path.join(home, name)
        try:
            if os.path.isdir(p):
                return p
        except Exception:
            pass
    return home or BASE_DIR


DEFAULT_FOLDER = _default_work_dir()

VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv", ".m4v", ".ts"}

# ffmpeg 查找顺序: 界面手动指定 → 工具目录 → 常见安装位置 → 系统 PATH。
# 本目录不自带 ffmpeg 二进制 (许可证与体积原因): 自行下载后放进本目录,
# 或在界面上粘贴 ffmpeg.exe / ffprobe.exe 的完整路径。
FFMPEG_CANDIDATES = [
    os.path.join(BASE_DIR, "ffmpeg.exe"),
    os.path.join(BASE_DIR, "ffmpeg", "bin", "ffmpeg.exe"),
    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    r"C:\ffmpeg\bin\ffmpeg.exe",
    "/usr/local/bin/ffmpeg",
    "/opt/homebrew/bin/ffmpeg",
]
FFPROBE_CANDIDATES = [
    os.path.join(BASE_DIR, "ffprobe.exe"),
    os.path.join(BASE_DIR, "ffmpeg", "bin", "ffprobe.exe"),
    r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
    r"C:\ffmpeg\bin\ffprobe.exe",
    "/usr/local/bin/ffprobe",
    "/opt/homebrew/bin/ffprobe",
]
USER_FFMPEG = {"path": None}
USER_FFPROBE = {"path": None}

HW = {"hevc": None, "h264": None, "probed": False, "label": ""}
HW_FRIENDLY = {
    "nvenc": "NVIDIA 显卡", "qsv": "Intel 核显", "amf": "AMD 显卡",
    "d3d12va": "Direct3D12", "mf": "系统(MediaFoundation)",
    "vaapi": "VAAPI", "vulkan": "Vulkan",
}

JOB = {"log_file": ""}
LOG_LOCK = threading.Lock()   # 并行时多个线程会同时写任务日志

# 并行任务进度: 每个文件按索引记录 0-100, 汇总成整体进度与 ETA
FILE_PCT = {}
DURS = []
ACTIVE = {}
RESULTS_BUF = []

state_lock = threading.Lock()
state = {
    "running": False, "stop": False, "ffmpeg_ok": False,
    "current_index": -1, "current_name": "", "current_pct": 0,
    "overall_pct": 0, "total": 0, "finished": 0,
    "total_duration": 0.0, "processed_dur": 0.0, "effective_dur": 0.0,
    "job_start": 0.0, "speed": 0.0, "workers": 1, "active_names": [],
    "eta": "", "log": [], "results": [], "error": None, "out_folder": "",
    "log_file": "", "started_at": "", "enhance_label": "",
}


def find_ffmpeg():
    for p in ([USER_FFMPEG["path"]] if USER_FFMPEG["path"] else []) + FFMPEG_CANDIDATES:
        if p and os.path.isfile(p):
            return p
    try:
        from shutil import which
        r = which("ffmpeg.exe") or which("ffmpeg")
        if r:
            return r
    except Exception:
        pass
    return None


def find_ffprobe():
    for p in ([USER_FFPROBE["path"]] if USER_FFPROBE["path"] else []) + FFPROBE_CANDIDATES:
        if p and os.path.isfile(p):
            return p
    try:
        from shutil import which
        r = which("ffprobe.exe") or which("ffprobe")
        if r:
            return r
    except Exception:
        pass
    return None


# ==================== 画质增强 v6 ====================
# 子进程统一用 UTF-8 解码 + 容错替换。Windows 中文版默认用 GBK 读取 ffmpeg 输出,
# 一旦 stderr 里出现中文文件名(UTF-8 字节)就会抛 UnicodeDecodeError 把任务判成失败。
UTF8_KW = {"text": True, "encoding": "utf-8", "errors": "replace"}

FILTERS = {"names": set(), "probed": False, "ff": ""}

ENH_DEFAULTS = {
    "enh_on": False,
    "enh_denoise": "off",          # off / light / medium / strong / ultra
    "enh_dn_method": "fast",       # fast(hqdn3d) / hq(nlmeans) / temporal(atadenoise)
    "enh_deblock": False,
    "enh_deband": False,
    "enh_sharpen": "off",          # off / light / medium / strong / cas
    "enh_upscale": "off",          # off / 1.5 / 2
    "enh_brightness": 0.0,
    "enh_contrast": 1.0,
    "enh_saturation": 1.0,
    "enh_gamma": 1.0,
    "enh_deinterlace": False,
    "enh_interp": "off",           # off / 60 / 120
    "enh_only": False,             # 仅增强不压缩
    "enh_crf": 16,
    "enh_crop": "",                # v9 自动裁黑边 "w:h:x:y", 由智能分析给出
    "max_height": 0,               # 限高 (0=不限), 属于提速选项但走同一条滤镜链
}

ENH_FILTER_NAMES = ["yadif", "deblock", "hqdn3d", "nlmeans", "atadenoise",
                    "gradfun", "scale", "unsharp", "cas", "eq", "minterpolate", "crop"]

DN_FAST = {
    "light":  "hqdn3d=1.5:1.2:3:2.5",
    "medium": "hqdn3d=3:2.5:6:5",
    "strong": "hqdn3d=5:4:9:8",
    "ultra":  "hqdn3d=8:6:14:12",
}
DN_HQ = {
    "light":  "nlmeans=s=2:p=3:r=5",
    "medium": "nlmeans=s=4:p=5:r=7",
    "strong": "nlmeans=s=7:p=5:r=11",
    "ultra":  "nlmeans=s=10:p=7:r=15",
}
DN_TEMP = {
    "light":  "atadenoise=s=9:0a=0.01:0b=0.02:1a=0.01:1b=0.02:2a=0.01:2b=0.02",
    "medium": "atadenoise=s=9:0a=0.02:0b=0.04:1a=0.02:1b=0.04:2a=0.02:2b=0.04",
    "strong": "atadenoise=s=13:0a=0.04:0b=0.08:1a=0.04:1b=0.08:2a=0.04:2b=0.08",
    "ultra":  "atadenoise=s=17:0a=0.06:0b=0.12:1a=0.06:1b=0.12:2a=0.06:2b=0.12",
}
SHARP_MAP = {
    "light":  "unsharp=5:5:0.4",
    "medium": "unsharp=5:5:0.7",
    "strong": "unsharp=5:5:1.1",
    "cas":    "cas=strength=0.35",
}

# ---- v11: 水印位置 (drawtext 用 tw/th, overlay 用 w/h, 这里统一用 overlay 坐标) ----
WM_POS = {
    "br": "x=W-w-20:y=H-h-20",
    "bl": "x=20:y=H-h-20",
    "tr": "x=W-w-20:y=20",
    "tl": "x=20:y=20",
    "cc": "x=(W-w)/2:y=(H-h)/2",
}

# ---- v11: 额外可探测的软件视频编码器 (HEVC/H.264 用硬件自动探测, 这里只补 AV1/VP9) ----
EXTRA_ENCODERS = {
    "av1": ["libsvtav1", "libaom-av1"],
    "vp9": ["libvpx-vp9"],
}
VIDEO_CODECS_AVAIL = {}   # 运行期探测结果: {"av1": "libsvtav1", "vp9": "libvpx-vp9"}

# ---- v12: 画幅转换预设 (目标宽高) 与填充方式 ----
ASPECT_PRESETS = {
    "keep": None,
    "9:16": (1080, 1920),   # 竖屏, 抖音/视频号/小红书
    "1:1": (1080, 1080),    # 方形, 朋友圈/图文
    "3:4": (1080, 1440),    # 竖版海报
    "4:3": (1440, 1080),    # 传统 4:3
    "16:10": (1728, 1080),  # 桌面宽屏
    "16:9": (1920, 1080),   # 标准横屏
}
ASPECT_MODES = {
    "crop": "裁切填满",   # 铺满画面, 超出部分裁掉
    "pad": "纯色边框",   # 主体完整, 不足处补纯色
    "blur": "模糊填充",  # 主体完整, 不足处用自身模糊背景 (需多输入合成)
}
# 滤镜图标记: 说明后面跟的是 filter_complex 图而非 -vf 链
# 载荷格式: FC_MARK + 末节点标签 + "\n" + 滤镜图
FC_MARK = "\x01fc:"


def get_video_codecs(ff):
    """探测本机 ffmpeg 是否带 AV1/VP9 软件编码器, 结果缓存。"""
    global VIDEO_CODECS_AVAIL
    if VIDEO_CODECS_AVAIL:
        return VIDEO_CODECS_AVAIL
    found = {}
    if ff:
        for codec, cands in EXTRA_ENCODERS.items():
            for enc in cands:
                if _test_enc(ff, enc):
                    found[codec] = enc
                    break
    VIDEO_CODECS_AVAIL = found
    return found


def find_font():
    """定位一个系统字体用于 drawtext 文字水印 (Windows 优先, 其他系统回退扫描常见路径)。"""
    cands = [
        r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    # 扫描 Windows 字体目录兜底
    wf = r"C:\Windows\Fonts"
    if os.path.isdir(wf):
        for n in ("msyh.ttc", "simhei.ttf", "arial.ttf"):
            p = os.path.join(wf, n)
            if os.path.isfile(p):
                return p
    return None


def _esc_filter(s):
    """滤镜字符串转义: 反斜杠与英文冒号需转义, 单引号成对转义。"""
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def _esc_quoted(s):
    """单引号包裹的文本值转义: 引号内冒号仍需转义(否则 drawtext 解析失败), 只处理反斜杠/单引号/冒号。"""
    return str(s).replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")


def get_filter_names(ff):
    """探测当前 ffmpeg 支持哪些滤镜, 结果缓存(切换 ffmpeg 后自动重探)。"""
    if FILTERS["probed"] and FILTERS["ff"] == (ff or ""):
        return FILTERS["names"]
    names = set()
    if ff:
        try:
            r = subprocess.run([ff, "-hide_banner", "-filters"],
                               capture_output=True, timeout=30, **UTF8_KW)
            for line in (r.stdout or "").splitlines():
                parts = line.split()
                for i, tok in enumerate(parts[:4]):
                    if "->" in tok and i >= 1:
                        names.add(parts[i - 1])
                        break
        except Exception:
            pass
    FILTERS.update({"names": names, "probed": True, "ff": ff or ""})
    return names


def _num(v, lo, hi, d):
    try:
        x = float(v)
    except Exception:
        return d
    return max(lo, min(hi, x))


def _bool(v):
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "yes", "on")
    return bool(v)


def parse_enh(p):
    """把前端传来的增强参数规范化并夹到合法范围, 防止拼出非法滤镜参数。"""
    e = dict(ENH_DEFAULTS)
    if not isinstance(p, dict):
        return e
    for k in ("enh_on", "enh_deblock", "enh_deband", "enh_deinterlace", "enh_only"):
        if k in p:
            e[k] = _bool(p[k])
    for k, allowed in (
        ("enh_denoise", {"off", "light", "medium", "strong", "ultra"}),
        ("enh_dn_method", {"fast", "hq", "temporal"}),
        ("enh_sharpen", {"off", "light", "medium", "strong", "cas"}),
        ("enh_upscale", {"off", "1.5", "2"}),
        ("enh_interp", {"off", "60", "120"}),
    ):
        v = str(p.get(k, e[k]))
        if v in allowed:
            e[k] = v
    e["enh_brightness"] = _num(p.get("enh_brightness", 0), -0.3, 0.3, 0.0)
    e["enh_contrast"] = _num(p.get("enh_contrast", 1), 0.5, 2.0, 1.0)
    e["enh_saturation"] = _num(p.get("enh_saturation", 1), 0.0, 3.0, 1.0)
    e["enh_gamma"] = _num(p.get("enh_gamma", 1), 0.5, 2.0, 1.0)
    e["enh_crf"] = int(_num(p.get("enh_crf", 16), 10, 28, 16))
    # v9 自动裁黑边: 只接受严格的 w:h:x:y, 杜绝把任意文本拼进滤镜链
    _crop = str(p.get("enh_crop", "") or "").strip()
    e["enh_crop"] = _crop if re.fullmatch(r"\d+:\d+:\d+:\d+", _crop) else ""
    # 限高由 /api/start 单独管理, 这里只供增强预览复用; 不再用固定白名单,
    # 否则自定义高度会被静默丢弃, 且会反向覆盖 opts 里已设好的值。
    e["max_height"] = int(_num(p.get("max_height", 0), 0, 4096, 0))
    return e


def build_vf(opts, ff=None, preview=False, src=None):
    """生成 -vf 滤镜链。返回 (滤镜链, 已启用说明列表, 跳过说明列表)。
    顺序: 裁黑边 → 去隔行 → 限高 → 去压缩块 → 降噪 → 去色带 → 放大 → 锐化 → 色彩 → 插帧,
    之后级联 v11 的水印与字幕烧录 (都在同一滤镜图里, 与主链共享像素格式)。
    限高/裁黑边属于提速选项, 即使没开画质增强也要生效, 不能因 enh_on=False 直接返回。
    """
    mh = int(_num(opts.get("max_height", 0), 0, 4096, 0))
    crop = str(opts.get("enh_crop", "") or "")
    if re.fullmatch(r"\d+:\d+:\d+:\d+", crop) is None:
        crop = ""
    wm_on = str(opts.get("wm_type", "off") or "off") != "off"
    sub_on = str(opts.get("wm_sub", "off") or "off") != "off"
    asp = str(opts.get("aspect", "keep") or "keep")
    asp_on = asp in ASPECT_PRESETS and ASPECT_PRESETS.get(asp) is not None
    # 仅设水印/字幕/画幅、未开画质增强且无限高/裁黑边时, 仍需进入滤镜图构建, 否则这些设置不生效
    if (not opts.get("enh_on") and mh <= 0 and not crop
            and not wm_on and not sub_on and not asp_on):
        return "", [], []
    caps = get_filter_names(ff)
    chain, labels, skipped = [], [], []

    def add(name, expr, label):
        if caps and name not in caps:
            skipped.append(label)
            return
        chain.append(expr)
        labels.append(label)

    if crop:
        add("crop", "crop=" + crop, "自动裁黑边 " + crop)
    if opts.get("enh_deinterlace"):
        add("yadif", "yadif=mode=0:parity=-1:deint=0", "去隔行")
    if mh > 0:
        add("scale", "scale=-2:'min(%d,ih)'" % mh, "限高%dp" % mh)
    if opts.get("enh_deblock"):
        add("deblock", "deblock=filter=weak:block=8", "去压缩块")
    dn = opts.get("enh_denoise", "off")
    if dn != "off":
        method = opts.get("enh_dn_method", "fast")
        table, fname = {
            "fast": (DN_FAST, "hqdn3d"),
            "hq": (DN_HQ, "nlmeans"),
            "temporal": (DN_TEMP, "atadenoise"),
        }[method]
        add(fname, table[dn], "降噪-%s/%s" % (dn, method))
    if opts.get("enh_deband"):
        add("gradfun", "gradfun=1.5:16", "去色带")
    up = opts.get("enh_upscale", "off")
    if up != "off" and mh > 0:
        skipped.append("超清放大(与限高冲突, 已忽略)")
    elif up != "off":
        m = "3/2" if up == "1.5" else "2"
        add("scale",
            "scale=trunc(iw*%s/2)*2:trunc(ih*%s/2)*2:flags=lanczos" % (m, m),
            "超清放大%s×" % up)
    sh = opts.get("enh_sharpen", "off")
    if sh != "off":
        add("cas" if sh == "cas" else "unsharp", SHARP_MAP[sh], "锐化-%s" % sh)
    cp = []
    if abs(opts.get("enh_brightness", 0.0)) > 1e-6:
        cp.append("brightness=%.3f" % opts["enh_brightness"])
    if abs(opts.get("enh_contrast", 1.0) - 1.0) > 1e-6:
        cp.append("contrast=%.3f" % opts["enh_contrast"])
    if abs(opts.get("enh_saturation", 1.0) - 1.0) > 1e-6:
        cp.append("saturation=%.3f" % opts["enh_saturation"])
    if abs(opts.get("enh_gamma", 1.0) - 1.0) > 1e-6:
        cp.append("gamma=%.3f" % opts["enh_gamma"])
    if cp:
        add("eq", "eq=" + ":".join(cp), "色彩调整")
    it = opts.get("enh_interp", "off")
    if it != "off" and not preview:
        add("minterpolate",
            "minterpolate=fps=%s:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" % it,
            "插帧→%sfps" % it)

    # ---- v12: 画幅转换 (竖屏/方形等), 放在增强链之后, 决定最终画面比例 ----
    amode = str(opts.get("aspect_mode", "crop") or "crop")
    target = ASPECT_PRESETS.get(asp)
    fc_mode = False
    if target and asp != "keep":
        W, H = target
        alabel = "画幅 %s %s" % (asp, ASPECT_MODES.get(amode, ""))
        need = ["scale", "pad"] if amode == "pad" else ["scale", "crop"]
        missing = [n for n in need if caps and n not in caps]
        if missing:
            skipped.append("画幅转换(%s): 缺少 %s 滤镜" % (asp, "/".join(missing)))
        elif amode == "pad":
            color = str(opts.get("aspect_color", "black") or "black")
            if color not in ("black", "white", "gray", "red", "green", "blue", "yellow"):
                color = "black"
            chain.append("scale=%d:%d:force_original_aspect_ratio=decrease" % (W, H))
            chain.append("pad=%d:%d:(ow-iw)/2:(oh-ih)/2:%s" % (W, H, color))
            labels.append(alabel)
        elif amode == "blur":
            # 模糊填充需要「背景 + 主体」两路输入合成, 只能走 filter_complex
            fc_mode = True
            labels.append(alabel)
        else:
            chain.append("scale=%d:%d:force_original_aspect_ratio=increase" % (W, H))
            chain.append("crop=%d:%d" % (W, H))
            labels.append(alabel)

    # ---- v11: 水印 + 字幕烧录, 与主链级联到同一滤镜图 ----
    # 末节点直接输出, 不要用 `null` 透传改名 (本机 ffmpeg 解析会失败)。
    if fc_mode:
        W, H = target
        blur = int(_num(opts.get("aspect_blur", 20), 2, 60, 20))
        stmts = [
            "[0:v]" + (",".join(chain) if chain else "null") + ",split=2[bgsrc][fgsrc]",
            "[bgsrc]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,boxblur=%d[bgr]"
            % (W, H, W, H, blur),
            "[fgsrc]scale=%d:%d:force_original_aspect_ratio=decrease[fg]" % (W, H),
        ]
        wm_stmts, wm_out, wm_sk = build_watermark(opts, caps, "[base]", out_tag="wm1")
        sub_in = wm_out if wm_stmts else "[base]"
        sub_stmts, sub_out, sub_sk = build_subtitle_burn(opts, caps, src, sub_in, out_tag="sub1")
        skipped += wm_sk + sub_sk
        # 末节点统一输出 [vout]: 谁是最后一段就用谁直接输出 vout (避免额外改名节点)
        if sub_stmts:
            sub_stmts, _, _ = build_subtitle_burn(opts, caps, src, sub_in, out_tag="vout")
            final_stmts, base_out = wm_stmts + sub_stmts, "base"
        elif wm_stmts:
            wm_stmts, _, _ = build_watermark(opts, caps, "[base]", out_tag="vout")
            final_stmts, base_out = wm_stmts, "base"
        else:
            final_stmts, base_out = [], "vout"
        stmts.append("[bgr][fg]overlay=(W-w)/2:(H-h)/2[%s]" % base_out)
        stmts += final_stmts
        post_labels = []
        if wm_stmts:
            post_labels.append("水印")
        if sub_stmts:
            post_labels.append("字幕烧录")
        if post_labels:
            labels.append(" + ".join(post_labels))
        return FC_MARK + "[vout]" + "\n" + ";".join(stmts), labels, skipped

    in_label = "[v]" if chain else "[in]"
    wm_stmts, wm_out, wm_sk = build_watermark(opts, caps, in_label)
    sub_stmts, sub_out, sub_sk = build_subtitle_burn(opts, caps, src, wm_out)
    skipped += wm_sk + sub_sk
    post_labels = []
    if wm_stmts:
        post_labels.append("水印")
    if sub_stmts:
        post_labels.append("字幕烧录")
    if post_labels:
        labels.append(" + ".join(post_labels))

    if not chain and not wm_stmts and not sub_stmts:
        return "", labels, skipped
    if not wm_stmts and not sub_stmts:
        # 没有水印/字幕时维持旧行为: 直接返回主链
        return ",".join(chain), labels, skipped
    statements = []
    if chain:
        statements.append("[in]" + ",".join(chain) + "[v]")
    statements += wm_stmts + sub_stmts
    return ";".join(statements), labels, skipped


def build_watermark(opts, caps, in_label="[v]", out_tag="wmo"):
    """返回 (语句列表, 输出标签, 跳过说明)。语句以 in_label 为输入, 以 [out_tag] 为输出。"""
    stmts, skipped, out_label = [], [], in_label
    t = str(opts.get("wm_type", "off") or "off")
    if t == "off":
        return stmts, out_label, skipped
    if "drawtext" not in caps and "overlay" not in caps:
        skipped.append("水印: 编码器不支持 drawtext/overlay")
        return stmts, out_label, skipped
    pos = WM_POS.get(opts.get("wm_pos", "br"), WM_POS["br"])
    alpha = float(_num(opts.get("wm_opacity", 0.6), 0.05, 1.0, 0.6))
    if t == "text":
        if "drawtext" not in caps:
            skipped.append("文字水印: 不支持 drawtext")
            return stmts, out_label, skipped
        font = find_font()
        if not font:
            skipped.append("文字水印: 未找到系统字体 (无法渲染文字)")
            return stmts, out_label, skipped
        text = str(opts.get("wm_text", "") or "水印")
        text = _esc_quoted(text)
        size = int(_num(opts.get("wm_size", 36), 8, 200, 36))
        # 滤镜里的 Windows 路径必须「加引号 + 转义冒号」同时满足, 否则解析失败
        fontp = _esc_filter(font.replace("\\", "/"))
        # drawtext 引用 in_label 作为输入并输出 [wmo]
        expr = (in_label + "drawtext=fontfile='%s':text='%s':fontsize=%d:"
                "fontcolor=white@%.2f:shadowcolor=black@0.5:shadowx=2:shadowy=2:%s[%s]"
                % (fontp, text, size, alpha, pos, out_tag))
        stmts.append(expr)
        out_label = "[%s]" % out_tag
    elif t == "image":
        img = str(opts.get("wm_image", "") or "")
        if not img or not os.path.isfile(img):
            skipped.append("图片水印: 文件不存在或路径无效")
            return stmts, out_label, skipped
        imgp = _esc_filter(img.replace("\\", "/"))
        pct = int(_num(opts.get("wm_size", 20), 4, 80, 20))   # 水印最大宽度占视频宽度百分比
        # movie 生成水印 → scale2ref 相对主视频宽缩放 → 透明 → overlay
        # 注意: 主视频宽在 scale2ref 里是 main_w (W 指的是被缩放的那一路)
        stmts.append("movie=filename='%s'[wmi]" % imgp)
        stmts.append("[wmi]%sscale2ref=w='min(iw\\,main_w*%.2f)':h=-1[wm][wref]"
                     % (in_label, pct / 100.0))
        stmts.append("[wm]format=rgba,colorchannelmixer=aa=%.2f[wma]" % alpha)
        # overlay 的主输入必须用 [wref] (scale2ref 的参考直通输出);
        # 直接用 [in]/[v] 会让同一路视频被消费两次, ffmpeg 报 Invalid argument。
        stmts.append("[wref][wma]overlay=%s:format=auto[%s]" % (pos, out_tag))
        out_label = "[%s]" % out_tag
    else:
        skipped.append("水印: 未知类型 %s" % t)
    return stmts, out_label, skipped


def build_subtitle_burn(opts, caps, src, in_label="[wmo]", out_tag="out"):
    """返回 (语句列表, 输出标签, 跳过说明)。从 in_label 烧录字幕到 [out_tag]。"""
    stmts, skipped, out_label = [], [], in_label
    s = str(opts.get("wm_sub", "off") or "off")
    if s == "off":
        return stmts, out_label, skipped
    if "subtitles" not in caps:
        skipped.append("字幕烧录: 不支持 subtitles 滤镜")
        return stmts, out_label, skipped
    expr = None
    if s == "embedded":
        if not src or not os.path.isfile(src):
            skipped.append("字幕烧录: 缺少源文件路径")
            return stmts, out_label, skipped
        idx = int(_num(opts.get("wm_sub_index", 0), 0, 31, 0))
        expr = "filename='%s':si=%d" % (_esc_filter(src.replace("\\", "/")), idx)
    elif s == "external":
        f = str(opts.get("wm_sub_file", "") or "")
        if not f or not os.path.isfile(f):
            skipped.append("字幕烧录: 外部字幕文件不存在")
            return stmts, out_label, skipped
        expr = "filename='%s'" % _esc_filter(f.replace("\\", "/"))
    else:
        skipped.append("字幕烧录: 未知来源 %s" % s)
        return stmts, out_label, skipped
    stmts.append("%ssubtitles=%s[%s]" % (in_label, expr, out_tag))
    out_label = "[%s]" % out_tag
    return stmts, out_label, skipped


def _job_write(msg):
    p = JOB["log_file"]
    if not p:
        return
    # 并行任务里多个线程会同时追加, 必须串行化, 否则日志行会互相穿插
    with LOG_LOCK:
        try:
            with open(p, "a", encoding="utf-8") as f:
                f.write("[" + time.strftime("%H:%M:%S") + "] " + msg + "\n")
        except Exception:
            pass


def log(msg):
    with state_lock:
        state["log"].append(msg)
        if len(state["log"]) > 500:
            state["log"] = state["log"][-500:]
    if CLI_MODE["on"]:
        try:
            print(msg, flush=True)
        except Exception:
            pass
    _job_write(msg)


def set_cur(pct):
    with state_lock:
        state["current_pct"] = round(max(0.0, min(100.0, pct)), 1)


def set_file_pct(idx, pct):
    """按文件索引记录进度, 汇总成整体进度和「已等效处理时长」供 ETA 使用。"""
    p = max(0.0, min(100.0, pct))
    with state_lock:
        if p < FILE_PCT.get(idx, 0):
            return
        FILE_PCT[idx] = p
        n = max(1, len(DURS))
        state["overall_pct"] = round(sum(FILE_PCT.values()) / n, 1)
        state["effective_dur"] = sum(
            DURS[i] * FILE_PCT.get(i, 0) / 100.0 for i in range(len(DURS)))
        state["current_pct"] = round(p, 1)


def mark_done(idx):
    set_file_pct(idx, 100)


def set_active(idx, name):
    with state_lock:
        ACTIVE[idx] = name
        state["active_names"] = list(ACTIVE.values())


def clear_active(idx):
    with state_lock:
        ACTIVE.pop(idx, None)
        state["active_names"] = list(ACTIVE.values())


def push_result(idx, result):
    with state_lock:
        RESULTS_BUF[idx] = result
        state["results"] = [r for r in RESULTS_BUF if r is not None]


def hms_to_sec(s):
    try:
        parts = [float(x) for x in s.split(":")]
    except Exception:
        return 0.0
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] if parts else 0.0


def probe_file(ffprobe, path):
    try:
        out = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries",
             "stream=codec_name,width,height:format=duration",
             "-of", "json", path],
            capture_output=True, timeout=30, **UTF8_KW)
        data = json.loads(out.stdout or "{}")
        dur = 0.0
        w = h = 0
        codec = ""
        for st in data.get("streams", []):
            if st.get("codec_type") == "video" or st.get("width"):
                w = st.get("width") or w
                h = st.get("height") or h
                codec = st.get("codec_name") or codec
        try:
            dur = float(data.get("format", {}).get("duration", 0) or 0)
        except Exception:
            dur = 0.0
        return {"duration": dur, "width": w, "height": h, "codec": codec}
    except Exception as e:
        return {"duration": 0.0, "width": 0, "height": 0, "codec": "", "err": str(e)}


def probe_streams(ffprobe, path):
    """完整媒体信息: 供多音轨/字幕保留、HDR 色彩标记与「压缩前后参数对比」使用。"""
    empty = {"duration": 0.0, "size": 0, "bitrate": 0, "fps": 0.0,
             "width": 0, "height": 0, "codec": "", "pix_fmt": "",
             "audio": 0, "subtitle": 0, "other": 0, "chapters": 0,
             "format": "", "hdr": False, "rotation": 0,
             "color_primaries": "", "color_transfer": "", "color_space": "",
             "color_range": "", "audio_codecs": [], "subtitle_codecs": []}
    if not ffprobe or not path or not os.path.isfile(path):
        return dict(empty, err="文件不存在")
    try:
        r = subprocess.run(
            [ffprobe, "-v", "error", "-show_streams", "-show_format",
             "-show_chapters", "-of", "json", path],
            capture_output=True, timeout=45, **UTF8_KW)
        d = json.loads(r.stdout or "{}")
    except Exception as e:
        return dict(empty, err=str(e))

    def _i(x, dv=0):
        try:
            return int(float(x))
        except Exception:
            return dv

    def _f(x, dv=0.0):
        try:
            return float(x)
        except Exception:
            return dv

    streams = d.get("streams", []) or []
    fmt = d.get("format", {}) or {}
    v = next((s for s in streams if s.get("codec_type") == "video"), {}) or {}
    auds = [s for s in streams if s.get("codec_type") == "audio"]
    subs = [s for s in streams if s.get("codec_type") == "subtitle"]
    fps = 0.0
    fr = str(v.get("avg_frame_rate") or v.get("r_frame_rate") or "0/1")
    if "/" in fr:
        a, b = fr.split("/", 1)
        if _f(b, 0):
            fps = _f(a, 0) / _f(b, 1)
    rot = 0
    for sd in (v.get("side_data_list") or []):
        if sd.get("rotation") is not None:
            rot = _i(sd.get("rotation"), rot)
    # 部分老编码器/工具只写 legacy `rotate` 标签而不写 display matrix, 作为回退读取
    if rot == 0:
        rt = (v.get("tags") or {}).get("rotate")
        if rt is not None:
            rot = _i(rt, 0)
    prim = str(v.get("color_primaries") or "")
    trc = str(v.get("color_transfer") or "")
    try:
        fsize = _i(fmt.get("size"), 0) or os.path.getsize(path)
    except Exception:
        fsize = 0
    return {
        "duration": _f(fmt.get("duration") or v.get("duration"), 0.0),
        "size": fsize, "bitrate": _i(fmt.get("bit_rate") or v.get("bit_rate"), 0),
        "fps": round(fps, 3),
        "width": _i(v.get("width"), 0), "height": _i(v.get("height"), 0),
        "codec": str(v.get("codec_name") or ""),
        "pix_fmt": str(v.get("pix_fmt") or ""),
        "audio": len(auds), "subtitle": len(subs),
        "other": max(0, len(streams) - 1 - len(auds) - len(subs)),
        "chapters": len(d.get("chapters") or []),
        "format": str(fmt.get("format_name") or ""),
        "audio_codecs": [str(s.get("codec_name") or "?") for s in auds],
        "subtitle_codecs": [str(s.get("codec_name") or "?") for s in subs],
        "rotation": rot,
        "color_primaries": prim, "color_transfer": trc,
        "color_space": str(v.get("color_space") or ""),
        "color_range": str(v.get("color_range") or ""),
        "hdr": prim == "bt2020" or trc in ("smpte2084", "arib-std-b67"),
    }


def check_disk(files, out_mode, out_sub):
    """按输出目录分组估算所需空间, 避免压到一半磁盘写满。"""
    groups = {}
    for f in files:
        try:
            sz = os.path.getsize(f)
        except Exception:
            continue
        d = os.path.dirname(os.path.abspath(f))
        if out_mode == "sub":
            d = os.path.join(d, out_sub or "已压缩")
        groups.setdefault(d, 0)
        groups[d] += sz
    checks, ok = [], True
    for d, need_src in groups.items():
        p = d
        while not os.path.isdir(p) and os.path.dirname(p) != p:
            p = os.path.dirname(p)
        try:
            du = shutil.disk_usage(p)
        except Exception:
            continue
        # 最坏情况: 临时输出 + 最终结果 + 原文件同时存在, 留 20% 余量
        need = int(need_src * 1.2 + 64 * 1024 * 1024)
        fit = du.free > need
        if not fit:
            ok = False
        checks.append({"dir": d, "free": du.free, "need": need, "ok": fit})
    return {"ok": ok, "checks": checks}


# ==================== v9: 智能分析 / 输出验收 / 方案存取 ====================
SCHEMES_FILE = os.path.join(BASE_DIR, "schemes.json")
SCHEME_LOCK = threading.Lock()
CLI_MODE = {"on": False}

# ==================== v10: 画质目标 / 逐文件微调 / 任务历史 ====================
HISTORY_FILE = os.path.join(BASE_DIR, "history.jsonl")
HISTORY_LOCK = threading.Lock()

# 目标 SSIM 档位: 数值越高越接近原片, 对应 CRF 越低、体积越大
QUALITY_LEVELS = {
    "lossless": 0.995,   # 肉眼完全无法分辨
    "high": 0.990,       # 几乎无差异 (推荐)
    "balanced": 0.980,   # 需放大对比才能看出
    "compact": 0.950,    # 轻微损失, 体积优先
}

# 逐文件微调: 严格白名单 + 逐项夹取, 防止把任意字段(并发数/引擎/路径)注入编码参数
OVERRIDE_NUM = {
    "crf": (0, 51), "target_mb": (0.1, 1000000.0), "ratio": (0.01, 1.0),
    "max_height": (0, 4096), "quality_target": (0.80, 0.9999),
    # v11 音频增强 / 水印
    "audio_bitrate": (32, 512), "audio_samplerate": (0, 192000),
    "audio_channels": (0, 8), "wm_size": (4, 200), "wm_opacity": (0.05, 1.0),
    "wm_sub_index": (0, 31), "aspect_blur": (2, 60),
}
OVERRIDE_ENUM = {
    "codec": {"hevc", "h264", "av1", "vp9"},
    "pix": {"8", "10"},
    "audio": {"strip", "copy", "reencode"},
    "preset": {"ultrafast", "superfast", "veryfast", "faster", "fast",
               "medium", "slow", "slower", "veryslow"},
    "tune": {"none", "animation", "film", "grain"},
    "streams": {"single", "allaudio", "all"},
    "verify": {"off", "quick", "full"},
    "enh_denoise": {"off", "light", "medium", "strong", "ultra"},
    "enh_sharpen": {"off", "light", "medium", "strong", "cas"},
    "enh_upscale": {"off", "1.5", "2"},
    # v11 音频增强
    "audio_normalize": {"off", "-14", "-16"},
    "audio_denoise": {"off", "light", "strong"},
    # v11 水印与字幕
    "wm_type": {"off", "text", "image"}, "wm_pos": {"br", "bl", "tr", "tl", "cc"},
    "wm_sub": {"off", "embedded", "external"},
    # v12 画幅转换
    "aspect": set(ASPECT_PRESETS.keys()),
    "aspect_mode": set(ASPECT_MODES.keys()),
    "aspect_color": {"black", "white", "gray", "red", "green", "blue", "yellow"},
}
OVERRIDE_BOOL = {"enh_on", "enh_deblock", "enh_deband", "enh_deinterlace",
                 "enh_only", "keep_smaller", "smart_copy"}


def merge_opts(base, ov):
    """把单个文件的微调参数合并进全局参数。非法值一律忽略, 返回新的 dict。"""
    o = dict(base)
    if not isinstance(ov, dict):
        return o
    keys = []
    for k, (lo, hi) in OVERRIDE_NUM.items():
        if k in ov and ov[k] not in (None, ""):
            try:
                v = float(ov[k])
                if lo <= v <= hi:
                    o[k] = int(v) if k in ("crf", "max_height") else v
                    keys.append(k)
            except Exception:
                pass
    for k, allowed in OVERRIDE_ENUM.items():
        if k in ov and str(ov[k]) in allowed:
            o[k] = str(ov[k])
            keys.append(k)
    for k in OVERRIDE_BOOL:
        if k in ov:
            o[k] = _bool(ov[k])
            keys.append(k)
    if "enh_crop" in ov:
        c = str(ov["enh_crop"] or "").strip()
        if not c or re.fullmatch(r"\d+:\d+:\d+:\d+", c):
            o["enh_crop"] = c
            keys.append("enh_crop")
    o["_ov_keys"] = keys
    return o


def append_history(entry):
    with HISTORY_LOCK:
        try:
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return True
        except Exception:
            return False


def load_history(limit=60):
    try:
        limit = max(1, min(500, int(limit)))
    except Exception:
        limit = 60
    with HISTORY_LOCK:
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()[-limit:]
        except Exception:
            return []
    out = []
    for line in lines:
        try:
            d = json.loads(line)
            if isinstance(d, dict):
                out.append(d)
        except Exception:
            pass
    return out[::-1]


def clear_history():
    with HISTORY_LOCK:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                f.write("")
            return True
        except Exception:
            return False


def history_stats(items):
    jobs = len(items)
    files = ok = bad = 0
    before = after = 0
    speeds = []
    for h in items:
        files += int(h.get("total") or 0)
        ok += int(h.get("ok") or 0)
        bad += int(h.get("failed") or 0)
        before += int(h.get("before") or 0)
        after += int(h.get("after") or 0)
        try:
            speeds.append(float(h.get("speed") or 0))
        except Exception:
            pass
    return {"jobs": jobs, "files": files, "ok": ok, "failed": bad,
            "before": before, "after": after,
            "saved_bytes": max(0, before - after),
            "saved_pct": round(100 - after / before * 100, 1) if before else 0.0,
            "avg_speed": round(sum(speeds) / len(speeds), 2) if speeds else 0.0}

# 一条滤镜链同时拿到三类信息: cropdetect 写 stderr, idet/signalstats 由 metadata 写 stdout
ANALYSIS_VF = "cropdetect=limit=24:round=2:reset=0,idet,signalstats,metadata=print:file=-"


def load_schemes():
    with SCHEME_LOCK:
        try:
            with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            return d if isinstance(d, dict) else {}
        except Exception:
            return {}


def save_schemes(d):
    with SCHEME_LOCK:
        try:
            with open(SCHEMES_FILE, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False


def _analyze_segment(ff, path, ss):
    """取一小段做画面统计。返回每帧的 signalstats/idet 标签与 cropdetect 建议。"""
    cmd = [ff, "-hide_banner", "-loglevel", "info",
           "-ss", "%.3f" % ss, "-i", path, "-frames:v", "12", "-an",
           "-vf", ANALYSIS_VF, "-f", "null", "-"]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=90, **UTF8_KW)
    except Exception as e:
        return {"frames": [], "crop": None, "err": str(e)}
    frames, cur = [], {}
    for line in (r.stdout or "").splitlines():
        if line.startswith("frame:"):
            if cur:
                frames.append(cur)
            cur = {}
        elif line.startswith("lavfi.") and "=" in line:
            k, _, v = line.partition("=")
            cur[k.strip()] = v.strip()
    if cur:
        frames.append(cur)
    crop = None
    for m in re.finditer(r"crop=(\d+):(\d+):(\d+):(\d+)", r.stderr or ""):
        crop = [int(x) for x in m.groups()]
    return {"frames": frames, "crop": crop}


def _avg(nums):
    return round(sum(nums) / len(nums), 2) if nums else None


def analyze_media(ff, fp, path, samples=3):
    """采样分析一个视频, 返回可解释的媒体指标 + 一键推荐参数。"""
    info = probe_streams(fp, path)
    if not info.get("width") or not ff or not os.path.isfile(path):
        return {"ok": False, "err": "无法解析视频流或文件不存在", "info": info}
    dur = float(info.get("duration") or 0.0)
    if dur <= 0:
        positions = [0.0]
    elif dur < 3:
        positions = [0.0, max(0.0, dur * 0.5)]
    else:
        positions = [max(0.0, dur * c - 0.25) for c in (0.12, 0.5, 0.88)]
    positions = positions[:max(1, min(3, int(samples or 3)))] or [0.0]
    try:
        with ThreadPoolExecutor(max_workers=len(positions)) as ex:
            parts = list(ex.map(lambda s: _analyze_segment(ff, path, s), positions))
    except Exception as e:
        return {"ok": False, "err": str(e), "info": info}

    def _vals(key):
        out = []
        for p in parts:
            for fr in p.get("frames", []):
                try:
                    out.append(float(fr.get("lavfi.signalstats." + key, "")))
                except Exception:
                    pass
        return out

    yavg, ymin, ymax = _avg(_vals("YAVG")), _avg(_vals("YMIN")), _avg(_vals("YMAX"))
    ydif, satavg = _avg(_vals("YDIF")), _avg(_vals("SATAVG"))
    # 注意: idet 的 multiple.* 输出的是「累计帧计数」而不是 0-1 比例,
    # 必须自己除以总和归一化, 否则会得到 13.0 这种离谱值并误开去隔行。
    # 各采样段各自独立累计, 取每段末帧的最大值作为该段结果。
    idet = {}
    for p in parts:
        for fr in p.get("frames", []):
            for k in ("progressive", "tff", "bff", "undetermined"):
                key = "lavfi.idet.multiple." + k
                if key in fr:
                    try:
                        idet[k] = max(idet.get(k, 0.0), float(fr[key]))
                    except Exception:
                        pass
    idet_total = sum(idet.get(k, 0.0) for k in ("progressive", "tff", "bff", "undetermined"))
    if idet_total >= 4:
        interlaced = round((idet.get("tff", 0.0) + idet.get("bff", 0.0)) / idet_total, 3)
        undet = round(idet.get("undetermined", 0.0) / idet_total, 3)
    else:
        interlaced, undet, idet_total = 0.0, 1.0, 0

    crops = [p["crop"] for p in parts if p.get("crop")]
    crop = max(crops, key=lambda c: c[0] * c[1]) if crops else None
    w, h = info.get("width", 0), info.get("height", 0)
    if crop and w and h and crop[0] * crop[1] >= w * h * 0.98:
        crop = None  # 裁掉不到 2%, 多半是检测抖动, 不值得改画面
    crop_str = ":".join(str(x) for x in crop) if crop else ""

    bitrate = int(info.get("bitrate") or 0)
    kbps = bitrate / 1000.0 if bitrate else (info.get("size", 0) * 8.0 / max(dur, 0.1) / 1000.0)
    fps = float(info.get("fps") or 25.0) or 25.0
    bpp = kbps * 1000.0 / max(1.0, w * h * fps)
    stats = {
        "yavg": yavg, "ymin": ymin, "ymax": ymax,
        "dynamic": round((ymax or 0) - (ymin or 0), 1),
        "ydif": ydif, "satavg": satavg, "interlaced": interlaced,
        "undet": undet, "idet_total": int(idet_total),
        "kbps": round(kbps, 1), "bpp": round(bpp, 3),
        "crop": crop, "crop_str": crop_str,
    }
    return {"ok": True, "info": info, "stats": stats, "samples": len(parts),
            "recommend": recommend_from_analysis(info, stats)}


def recommend_from_analysis(info, s):
    """把分析指标翻译成一套可解释的压缩/增强参数 (前端可一键采用)。"""
    w, h = info.get("width", 0), info.get("height", 0)
    dur = float(info.get("duration") or 0)
    size = int(info.get("size") or 0)
    kbps, bpp = s.get("kbps", 0), s.get("bpp", 0)
    yavg, ydif, satavg = s.get("yavg"), s.get("ydif"), s.get("satavg")
    reasons, warns = [], []

    rec = {
        "mode": "crf", "codec": "hevc", "pix": "10", "crf": 24,
        "preset": "fast", "tune": "none", "engine": "auto", "workers": 2,
        "streams": "all" if (info.get("audio", 0) > 1 or info.get("subtitle", 0) > 0
                             or info.get("chapters", 0) > 0) else "single",
        "max_height": 0, "smart_copy": False, "keep_smaller": True,
        "verify": "quick", "target_mb": max(1, round(size * 0.3 / 1048576, 1)),
        "enh_on": False, "enh_denoise": "off", "enh_dn_method": "fast",
        "enh_deblock": False, "enh_deband": False, "enh_sharpen": "off",
        "enh_deinterlace": False, "enh_crop": "",
        "enh_brightness": 0.0, "enh_contrast": 1.0, "enh_saturation": 1.0,
        "enh_gamma": 1.0, "enh_upscale": "off", "enh_interp": "off",
        "reasons": reasons, "warnings": warns,
    }

    # 源码率 / 每像素码率: 判断还有多少压缩空间, 以及是否噪声过多
    if kbps and kbps < 800:
        rec["smart_copy"] = True
        rec["crf"] = 22
        reasons.append("源码率仅 %.0fkbps, 已接近压缩下限 → 开智能直传并放宽 CRF, 避免越压越差" % kbps)
        warns.append("压缩空间有限, 建议先试压单个文件")
    elif bpp and bpp > 0.30:
        rec["crf"] = 26
        rec["enh_on"] = True
        rec["enh_denoise"] = "medium"
        rec["enh_deblock"] = True
        reasons.append("每像素码率 %.3f 偏高(噪点/压缩伪影多) → 先降噪去块, 再用 CRF26 压得更狠" % bpp)
    elif bpp and bpp < 0.05:
        rec["crf"] = 21
        reasons.append("每像素码率 %.3f 很低 → 用 CRF21 保住细节, 别再压" % bpp)
    else:
        reasons.append("码率密度正常 (%.0fkbps / %.3f bpp) → 走标准 CRF24 平衡体积与画质" % (kbps, bpp))

    # 分辨率与码率的组合
    if h >= 1440 and kbps > 9000:
        rec["max_height"] = 1080
        reasons.append("%dp 且 %.0fkbps 偏重 → 限高 1080p, 省下的码率给画面" % (h, kbps))
    elif h >= 1080 and kbps < 2500:
        rec["crf"] = min(rec["crf"], 22)
        reasons.append("高分辨率但码率不高 → 保守 CRF, 防止放大块效应")

    # 运动量: 帧间差大需要更多码率
    if ydif is not None and ydif > 8:
        rec["crf"] = max(18, rec["crf"] - 2)
        reasons.append("帧间差 %.1f(运动/噪点偏多) → CRF 调低 2 档保动态画面" % ydif)
    elif ydif is not None and ydif < 1.5:
        rec["preset"] = "medium"
        reasons.append("画面以静态为主 → 用 medium 预设多榨一点体积, 耗时增加不多")

    # 亮度 / 色彩: 只在明显偏差时建议, 避免"自动调色"翻车
    if yavg is not None and yavg < 55:
        rec["enh_on"] = True
        rec["enh_brightness"] = 0.03
        rec["enh_contrast"] = 1.04
        reasons.append("平均亮度 %.0f 偏暗 → 建议亮度 +0.03 / 对比 1.04" % yavg)
    if satavg is not None and satavg < 25 and satavg > 0:
        rec["enh_on"] = True
        rec["enh_saturation"] = 1.10
        reasons.append("平均饱和度 %.0f 偏灰 → 建议饱和度 1.10" % satavg)
    if s.get("dynamic") is not None and s["dynamic"] < 90:
        rec["enh_on"] = True
        rec["enh_deband"] = True
        reasons.append("动态范围仅 %.0f(发灰/色带风险) → 建议去色带" % s["dynamic"])

    # 隔行与黑边。idet 对静态合成图案/横条纹会误判, 所以要求「高置信 + 画面有运动」
    # 才自动开启 yadif; 否则只提示, 避免把逐行视频去隔行糊掉。
    ir = s.get("interlaced", 0.0)
    undet = s.get("undet", 1.0)
    moving = (ydif is None or ydif >= 3.0)
    if ir >= 0.75 and undet < 0.5 and moving:
        rec["enh_on"] = True
        rec["enh_deinterlace"] = True
        reasons.append("检测到隔行扫描(置信 %.0f%%, 有效样本 %d 帧) → 建议去隔行"
                       % (ir * 100, s.get("idet_total", 0)))
    elif ir >= 0.75 and undet < 0.5:
        warns.append("疑似隔行(置信 %.0f%%)但画面近乎静止, 可能是检测误判; 未自动启用去隔行, 请用增强预览确认"
                     % (ir * 100))
    elif ir >= 0.35 and undet < 0.5:
        warns.append("疑似隔行(置信 %.0f%%), 未自动启用去隔行, 请用增强预览确认" % (ir * 100))
    if s.get("crop_str"):
        rec["enh_on"] = True
        rec["enh_crop"] = s["crop_str"]
        reasons.append("检测到黑边 → 建议自动裁剪 crop=%s (少编码无用像素)" % s["crop_str"])

    # 容器里的额外内容与 HDR
    if info.get("audio", 0) > 1 or info.get("subtitle", 0) > 0 or info.get("chapters", 0) > 0:
        reasons.append("含 %d 音轨 / %d 字幕 / %d 章节 → 已选全部流保留, 不丢内容"
                       % (info.get("audio", 0), info.get("subtitle", 0), info.get("chapters", 0)))
    if info.get("hdr"):
        rec["pix"] = "10"
        rec["streams"] = "all"
        warns.append("HDR 源 ( primaries=%s / trc=%s ) → 固定 10bit + 全流保留"
                     % (info.get("color_primaries", ""), info.get("color_transfer", "")))
    if info.get("codec") in ("hevc", "av1", "vp9") and kbps and kbps < 1500:
        warns.append("已是 %s 且码率不高, 压缩收益可能有限" % info.get("codec"))
    if info.get("fps", 0) > 50:
        rec["preset"] = "fast"
        reasons.append("高帧率 %.0ffps → 保持 fast 预设控制耗时" % info["fps"])
    if dur and size:
        rec["target_mb"] = max(1, round(min(size * 0.5, kbps * 1000 * 0.42 * dur / 8)
                                        / 1048576, 1))
    return rec


def verify_output(ff, fp, src, out, src_info, level, opts=None):
    """对刚编码出的文件做验收: 容器/时长/流数量/解码完整性。"""
    opts = opts or {}
    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})

    oi = probe_streams(fp, out)
    parsed = oi.get("width", 0) > 0 and oi.get("height", 0) > 0
    add("容器可解析", parsed, "%dx%d · %s · %.1fs"
        % (oi.get("width", 0), oi.get("height", 0), oi.get("codec", "?"), oi.get("duration", 0)))
    sd = float(src_info.get("duration") or 0)
    od = float(oi.get("duration") or 0)
    dev = abs(od - sd) / max(sd, 0.1) if sd else 0.0
    add("时长一致", dev <= 0.04, "%.2fs → %.2fs (偏差 %.1f%%)" % (sd, od, dev * 100))

    am = opts.get("audio", "reencode")
    sa = int(src_info.get("audio", 0) or 0)
    exp_a = 0 if am == "strip" else (sa if opts.get("streams") in ("all", "allaudio") else min(1, sa))
    add("音轨保留", oi.get("audio", 0) >= exp_a,
        "期望 %d / 实际 %d" % (exp_a, oi.get("audio", 0)))
    if opts.get("streams") == "all":
        exp_s = int(src_info.get("subtitle", 0) or 0)
        add("字幕保留", oi.get("subtitle", 0) >= exp_s,
            "期望 %d / 实际 %d" % (exp_s, oi.get("subtitle", 0)))

    dec_ok, dec_detail = True, ""
    if level in ("quick", "full") and parsed:
        if level == "full":
            spans = [(0.0, 0.0)]
        else:
            spans = [(max(0.0, sd * 0.05), 0.5), (sd * 0.5, 0.5),
                     (max(0.0, sd - 0.7), 0.5)]
        for ss, seglen in spans:
            cmd = [ff, "-hide_banner", "-v", "error", "-xerror"]
            if level == "quick":
                cmd += ["-ss", "%.3f" % ss, "-i", out, "-t", "%.3f" % seglen]
            else:
                cmd += ["-i", out]
            cmd += ["-an", "-f", "null", "-"]
            try:
                r = subprocess.run(cmd, capture_output=True, timeout=900, **UTF8_KW)
            except Exception as e:
                dec_ok, dec_detail = False, str(e)
                break
            err = (r.stderr or "").strip()
            if r.returncode != 0 or re.search(r"(?i)\b(error|invalid|corrupt|failed)\b", err):
                dec_ok, dec_detail = False, err[-300:]
                break
        add("解码校验" + ("(整片)" if level == "full" else "(抽3段)"),
            dec_ok, dec_detail or "无解码错误")
    elif level == "off":
        add("解码校验", True, "未开启")

    ok = all(c["ok"] for c in checks)
    fatal = (not parsed) or (not dec_ok)
    if ok:
        label = "✓ 通过"
    elif fatal:
        label = "✗ 输出损坏"
    else:
        label = "⚠ %d 项异常" % sum(1 for c in checks if not c["ok"])
    return {"ok": ok, "fatal": fatal, "label": label, "level": level,
            "checks": checks, "out_info": oi}


def make_opts(payload):
    """统一构造任务参数: Web /api/start 与 CLI 模式共用, 避免两边规则漂移。"""
    _streams = payload.get("streams", "single")
    opts = {
        "codec": payload.get("codec", "hevc"),
        "crf": int(_num(payload.get("crf", 24), 0, 51, 24)),
        # 缺省值与 v8 /api/start 保持一致, 避免漏传字段时行为漂移;
        # CLI 在 cli_main 的 base 里显式给出自己的提速默认值。
        "preset": payload.get("preset", "slow"),
        "tune": payload.get("tune", "animation"),
        "pix": payload.get("pix", "10"),
        "audio": payload.get("audio", "strip"),
        # v11 编码格式: 允许 hevc/h264/av1/vp9 (后两者需本机 ffmpeg 支持)
        "codec": payload.get("codec", "hevc") if payload.get("codec") in
                 ("hevc", "h264", "av1", "vp9") else "hevc",
        "engine": payload.get("engine", "software"),
        "mode": payload.get("mode", "crf"),
        "ratio": payload.get("ratio", 0.3),
        "target_mb": payload.get("target_mb", 50),
        # v7 提速 / 保护
        "workers": int(_num(payload.get("workers", 2), 1, 4, 2)),
        "smart_copy": _bool(payload.get("smart_copy", False)),
        "smart_copy_kbps": _num(payload.get("smart_copy_kbps", 1200), 100, 20000, 1200),
        "keep_smaller": _bool(payload.get("keep_smaller", True)),
        "auto_open": _bool(payload.get("auto_open", False)),
        "max_height": int(_num(payload.get("max_height", 0), 0, 4096, 0)),
        # v8 精准体积 / 流保留 / 续跑
        "streams": _streams if _streams in ("single", "allaudio", "all") else "single",
        "resume": _bool(payload.get("resume", True)),
        "smart_refine": _bool(payload.get("smart_refine", True)),
        # v9 输出验收
        "verify": payload.get("verify", "off") if payload.get("verify") in
                  ("off", "quick", "full") else "off",
        # v10 画质目标 / 失败自愈
        "quality_target": float(_num(payload.get("quality_target", 0.99),
                                     0.80, 0.9999, 0.99)),
        "auto_fallback": _bool(payload.get("auto_fallback", True)),
        # v11 音频增强
        "audio_bitrate": int(_num(payload.get("audio_bitrate", 128), 32, 512, 128)),
        "audio_samplerate": int(_num(payload.get("audio_samplerate", 0), 0, 192000, 0)),
        "audio_channels": int(_num(payload.get("audio_channels", 0), 0, 8, 0)),
        "audio_normalize": payload.get("audio_normalize", "off")
                          if payload.get("audio_normalize") in ("off", "-14", "-16") else "off",
        "audio_denoise": payload.get("audio_denoise", "off")
                        if payload.get("audio_denoise") in ("off", "light", "strong") else "off",
        # v11 水印与字幕烧录
        "wm_type": payload.get("wm_type", "off") if payload.get("wm_type") in
                   ("off", "text", "image") else "off",
        "wm_text": payload.get("wm_text", "") or "",
        "wm_image": payload.get("wm_image", "") or "",
        "wm_pos": payload.get("wm_pos", "br") if payload.get("wm_pos") in
                  ("br", "bl", "tr", "tl", "cc") else "br",
        "wm_size": int(_num(payload.get("wm_size", 36), 4, 200, 36)),
        "wm_opacity": float(_num(payload.get("wm_opacity", 0.6), 0.05, 1.0, 0.6)),
        "wm_sub": payload.get("wm_sub", "off") if payload.get("wm_sub") in
                  ("off", "embedded", "external") else "off",
        "wm_sub_index": int(_num(payload.get("wm_sub_index", 0), 0, 31, 0)),
        "wm_sub_file": payload.get("wm_sub_file", "") or "",
        # v12 画幅转换 (竖屏/方形等)
        "aspect": payload.get("aspect", "keep") if payload.get("aspect") in
                  ASPECT_PRESETS else "keep",
        "aspect_mode": payload.get("aspect_mode", "crop") if payload.get("aspect_mode") in
                       ASPECT_MODES else "crop",
        "aspect_color": payload.get("aspect_color", "black") if payload.get("aspect_color") in
                        ("black", "white", "gray", "red", "green", "blue", "yellow") else "black",
        "aspect_blur": int(_num(payload.get("aspect_blur", 20), 2, 60, 20)),
        # v12 输出文件名模板 (仅在输出到子文件夹时生效)
        "name_template": str(payload.get("name_template", "") or "").strip(),
    }
    # 只合并增强参数, 避免 parse_enh 的默认值反向覆盖上面的提速/流保留选项
    opts.update({k: v for k, v in parse_enh(payload).items() if k.startswith("enh_")})
    return opts


def _is_video(n):
    if ".vcpart." in n.lower():
        return False
    return os.path.splitext(n)[1].lower() in VIDEO_EXTS


def list_videos(folder, recursive, exclude_dir=None):
    files = []
    if not folder or not os.path.isdir(folder):
        return files
    if recursive:
        for root, _, names in os.walk(folder):
            if exclude_dir and os.path.abspath(root).startswith(exclude_dir):
                continue
            for n in names:
                if _is_video(n):
                    files.append(os.path.join(root, n))
    else:
        for n in sorted(os.listdir(folder)):
            p = os.path.join(folder, n)
            if os.path.isfile(p) and _is_video(n):
                files.append(p)
    return files


def get_hw(ff):
    global HW
    if HW["probed"] or not ff:
        return HW
    cands = {
        "hevc": ["hevc_nvenc", "hevc_qsv", "hevc_amf", "hevc_d3d12va", "hevc_mf", "hevc_vaapi", "hevc_vulkan"],
        "h264": ["h264_nvenc", "h264_qsv", "h264_amf", "h264_mf"],
    }
    labels = []
    for kind in ("hevc", "h264"):
        for enc in cands[kind]:
            if _test_enc(ff, enc):
                HW[kind] = enc
                for k, v in HW_FRIENDLY.items():
                    if k in enc and v not in labels:
                        labels.append(v)
                break
    HW["label"] = " / ".join(labels)
    HW["probed"] = True
    return HW


def _test_enc(ff, name):
    try:
        r = subprocess.run(
            [ff, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
             "-i", "color=c=black:s=128x128:d=0.1", "-c:v", name, "-f", "null", "-"],
            capture_output=True, timeout=15)
        return r.returncode == 0
    except Exception:
        return False


def mux_args(out):
    """movflags 只对 MP4/MOV 系列有效, 写 MKV 时必须省略, 否则 ffmpeg 直接报错。"""
    ext = os.path.splitext(out)[1].lower()
    return ["-movflags", "+faststart"] if ext in (".mp4", ".m4v", ".mov") else []


def audio_args(opts):
    """音频输出参数。strip=移除, copy=原样, 其余按重编码 (可自定义码率/采样率/声道)。"""
    am = opts.get("audio", "reencode")
    if am == "strip":
        return ["-an"]
    if am == "copy":
        return ["-c:a", "copy"]
    br = int(_num(opts.get("audio_bitrate", 128), 32, 512, 128))
    args = ["-c:a", "aac", "-b:a", "%dk" % br]
    sr = int(_num(opts.get("audio_samplerate", 0), 0, 192000, 0))
    if sr:
        args += ["-ar", str(sr)]
    ch = int(_num(opts.get("audio_channels", 0), 0, 8, 0))
    if ch:
        args += ["-ac", str(ch)]
    return args


def audio_filter_args(opts):
    """v11 音频滤镜: 音量归一化 + 降噪。任一启用都会强制重编码 (无法与原样复制共存)。"""
    af = []
    n = str(opts.get("audio_normalize", "off") or "off")
    if n in ("-14", "-16"):
        af.append("loudnorm=I=%s:TP=-1.5:LRA=11" % n)
    d = str(opts.get("audio_denoise", "off") or "off")
    if d == "light":
        af.append("afftdn=nr=12")
    elif d == "strong":
        af.append("afftdn=nr=20")
    return af


def _audio_chain(opts):
    """返回 (音频输出参数, 音频滤镜参数或 None)。当音频滤镜启用时强制重编码。"""
    am = opts.get("audio", "reencode")
    af = audio_filter_args(opts)
    if am == "strip":
        return ["-an"], None
    if af:
        # 归一化/降噪必须重编码, 忽略 copy 选择
        return audio_args(opts), af
    if am == "copy":
        return ["-c:a", "copy"], None
    return audio_args(opts), None


def encoder_args(opts, out=None):
    """只返回编码器部分的参数。正式编码与智能体积的采样试压共用, 确保两次刻度一致。
    out 用于判断封装容器 (MP4/MOV 需要写 tag, MKV/WebM 不需要)。"""
    codec = opts.get("codec", "hevc")
    crf = int(opts.get("crf", 24))
    preset = opts.get("preset", "fast")
    tune = opts.get("tune", "animation")
    pix = opts.get("pix", "8")
    engine = opts.get("engine", "software")
    hw = opts.get("hw")
    ext = os.path.splitext(out or "")[1].lower()
    is_mp4 = ext in (".mp4", ".m4v", ".mov")
    cmd = []
    fast = preset in ("ultrafast", "superfast", "veryfast", "faster", "fast")

    # ---- v11: AV1 / VP9 软件编码器 (体积更小但更慢, 默认关、自动探测) ----
    if codec == "av1":
        enc = VIDEO_CODECS_AVAIL.get("av1", "libaom-av1")
        cmd += ["-c:v", enc]
        if is_mp4:
            cmd += ["-tag:v", "av01"]
        # SVT-AV1 用 -preset (0-13, 越大越快), libaom 用 -cpu-used (0-8)
        if enc == "libsvtav1":
            svt = {"ultrafast": 13, "superfast": 12, "veryfast": 10, "faster": 9,
                   "fast": 8, "medium": 6, "slow": 4, "slower": 2, "veryslow": 1}.get(preset, 8)
            cmd += ["-preset", str(svt), "-crf", str(crf), "-b:v", "0"]
        else:
            cpu = {"ultrafast": 8, "superfast": 7, "veryfast": 6, "faster": 5,
                   "fast": 4, "medium": 3, "slow": 2, "slower": 1, "veryslow": 0}.get(preset, 4)
            cmd += ["-cpu-used", str(cpu), "-crf", str(crf), "-b:v", "0"]
        if pix == "10":
            cmd += ["-pix_fmt", "yuv420p10le"]
        return cmd
    if codec == "vp9":
        cmd += ["-c:v", "libvpx-vp9"]
        if is_mp4:
            cmd += ["-tag:v", "vp09"]
        dline = "realtime" if fast else "good"
        cpu = {"ultrafast": 8, "superfast": 7, "veryfast": 6, "faster": 5,
               "fast": 4, "medium": 3, "slow": 2, "slower": 1, "veryslow": 0}.get(preset, 4)
        cmd += ["-b:v", "0", "-crf", str(crf), "-deadline", dline, "-cpu-used", str(cpu)]
        if pix == "10":
            cmd += ["-pix_fmt", "yuv420p10le"]
        return cmd

    if engine == "hardware" and hw:
        # 硬件编码器的质量刻度与 x265 的 CRF 不同: 实测同数值下 QSV 会明显偏大,
        # 校准 +3(QSV)/+2(NVENC) 后体积才和软件 CRF 大致对齐, 滑杆含义才一致。
        hq = max(1, min(51, crf + (3 if "qsv" in hw else (2 if "nvenc" in hw else 0))))
        cmd += ["-c:v", hw]
        if "nvenc" in hw:
            cmd += ["-preset", "p1" if fast else "p4", "-rc", "vbr", "-cq", str(hq), "-b:v", "0"]
        elif "qsv" in hw:
            cmd += ["-preset", "veryfast" if fast else "medium", "-global_quality", str(hq)]
        elif "amf" in hw:
            cmd += ["-rc", "cqp", "-qp_i", str(hq), "-qp_p", str(hq + 2)]
        else:
            cmd += ["-rc", "vbr", "-b:v", "0", "-cq", str(hq)]
        cmd += ["-tag:v", "hvc1" if "hevc" in hw else "avc1"]
    else:
        if codec == "hevc":
            cmd += ["-c:v", "libx265", "-tag:v", "hvc1"]
            if pix == "10":
                cmd += ["-pix_fmt", "yuv420p10le"]
        else:
            cmd += ["-c:v", "libx264", "-tag:v", "avc1"]
        cmd += ["-crf", str(crf), "-preset", preset]
        if tune and tune != "none":
            cmd += ["-tune", tune]
    return cmd


def stream_map_args(opts, out):
    """流保留策略。single = 保持 v7 及以前的默认行为(不显式 -map, 完全兼容)。"""
    mode = opts.get("streams", "single")
    if mode == "single":
        return []
    ext = os.path.splitext(out)[1].lower()
    args = ["-map", "0:v:0"]
    if mode == "all":
        args += ["-map", "0:a?", "-map", "0:s?"]
        if ext in (".mkv", ".webm"):
            args += ["-map", "0:t?"]      # 封面/附件只有 Matroska 能安全承载
    else:
        args += ["-map", "0:a?"]
    args += ["-map_metadata", "0", "-map_chapters", "0"]
    return args


def stream_extra_args(opts, info, out):
    args = []
    ext = os.path.splitext(out)[1].lower()
    if opts.get("streams") == "all" and (info or {}).get("subtitle", 0) > 0:
        # MP4 只支持 mov_text 字幕, 直接 copy ass/ssa 会失败; MKV 可原样复制
        args += ["-c:s", "mov_text" if ext in (".mp4", ".m4v", ".mov") else "copy"]
    if opts.get("streams") != "single" and opts.get("pix") == "10":
        for key, flag in (("color_primaries", "-color_primaries"),
                          ("color_transfer", "-color_trc"),
                          ("color_space", "-colorspace"),
                          ("color_range", "-color_range")):
            v = (info or {}).get(key, "")
            if v and v not in ("unknown", "unspecified"):
                args += [flag, str(v)]
    return args


def build_cmd(ffmpeg, inp, out, opts, vf="", info=None):
    cmd = [ffmpeg, "-y", "-i", inp]
    fc = bool(vf) and vf.startswith(FC_MARK)
    if fc:
        body = vf[len(FC_MARK):]
        lbl, _, graph = body.partition("\n")
        cmd += ["-filter_complex", graph]
    elif vf:
        cmd += ["-vf", vf]
    smap = stream_map_args(opts, out)
    if fc:
        # filter_complex 模式下视频来自滤镜图, 不能与 -map 0:v:0 并存 (会绕过滤镜)
        smap = [x for x in smap if x != "0:v:0"]
        cmd += ["-map", lbl]
        if not smap and opts.get("audio", "strip") != "strip":
            smap = ["-map", "0:a:0?"]
    cmd += smap
    cmd += encoder_args(opts, out)
    aargs, af = _audio_chain(opts)
    cmd += aargs
    if af:
        cmd += ["-af", ",".join(af)]
    cmd += stream_extra_args(opts, info, out)
    cmd += mux_args(out) + [out]
    return cmd


def vf_args(vf):
    """把滤镜描述转成 ffmpeg 参数: 普通链用 -vf; filter_complex 图需额外指定输出映射。"""
    if not vf:
        return []
    if vf.startswith(FC_MARK):
        body = vf[len(FC_MARK):]
        lbl, _, graph = body.partition("\n")
        return ["-filter_complex", graph, "-map", lbl]
    return ["-vf", vf]


def fc_extend(vf, expr):
    """在 filter_complex 图的末节点后追加一段无标签滤镜表达式, 末标签仍是 [vout]。"""
    if not vf or not vf.startswith(FC_MARK):
        return vf
    body = vf[len(FC_MARK):]
    _lbl, _, graph = body.partition("\n")
    head, sep, tail = graph.rpartition("[vout]")
    if not sep:
        return vf
    return FC_MARK + "[vout]" + "\n" + head + "[vmid]" + tail + ";[vmid]" + expr + "[vout]"


def _run_with_progress(cmd, dur, on_pct, cwd=None):
    """返回 (ffmpeg 退出码, stderr 尾部若干行)。中文文件名也不会再触发 GBK 解码异常。"""
    tail = []
    try:
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                cwd=cwd, **UTF8_KW)
        try:
            for line in proc.stderr:
                s = line.strip()
                if s:
                    tail.append(s[-300:])
                    if len(tail) > 12:
                        del tail[:-12]
                if "time=" in line:
                    m = re.search(r"time=(\d+:\d+:\d+\.\d+)", line)
                    if m and dur > 0:
                        on_pct(min(100.0, hms_to_sec(m.group(1)) / dur * 100))
                with state_lock:
                    if state["stop"]:
                        proc.terminate()
                        break
        except (UnicodeDecodeError, OSError, ValueError) as e:
            tail.append("读取 ffmpeg 输出异常: " + str(e))
        try:
            proc.wait(timeout=60)
        except Exception:
            proc.kill()
            proc.wait()
        return proc.returncode, tail
    except Exception as e:
        tail.append("启动 ffmpeg 失败: " + str(e))
        return -2, tail


def _smart_copy_bitrate(opts, before, dur, vf):
    """源码率已经足够低时, 重编码只会更慢且可能更大 → 直接无损封装。"""
    if not opts.get("smart_copy") or vf or opts.get("enh_on"):
        return None
    # 音频滤镜(归一化/降噪)必须重编码音频, 不能走无损直传
    if audio_filter_args(opts):
        return None
    if opts.get("mode") in ("ratio", "size", "smart") or not dur or dur <= 0:
        return None
    kbps = before * 8.0 / dur / 1000.0
    limit = float(opts.get("smart_copy_kbps", 1200) or 1200)
    return kbps if kbps <= limit else None


def _trial_segment(ff, inp, tmp, opts, vf, crf, ss, seg):
    """按正式编码的同一套参数试压一小段, 返回该段字节数 (失败返回 0)。"""
    o = dict(opts)
    o["crf"] = int(crf)
    o["audio"] = "strip"
    cmd = [ff, "-y", "-ss", "%.3f" % ss, "-i", inp, "-t", "%.3f" % seg]
    fc = bool(vf) and vf.startswith(FC_MARK)
    if fc:
        body = vf[len(FC_MARK):]
        lbl, _, graph = body.partition("\n")
        cmd += ["-filter_complex", graph, "-map", lbl]
    else:
        cmd += ["-map", "0:v:0"]
        if vf:
            cmd += ["-vf", vf]
    cmd += encoder_args(o) + ["-an"] + mux_args(tmp) + [tmp]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=240, **UTF8_KW)
        if r.returncode == 0 and os.path.isfile(tmp):
            return os.path.getsize(tmp)
    except Exception:
        pass
    try:
        if os.path.isfile(tmp):
            os.remove(tmp)
    except Exception:
        pass
    return 0


def smart_crf(ff, inp, opts, vf, dur, target_bytes, tmpdir):
    """片头/片中/片尾各抽一小段, 用两档 CRF 试压; log(体积) 对 CRF 近似线性,
    由此反推命中目标体积的 CRF。只编码约 10% 的素材, 比两遍全片编码快得多。
    返回 (crf, slope, 说明); 失败时 crf 为 None。"""
    if dur <= 0.5:
        return None, 0.0, "视频太短, 无法采样"
    # 长片: 4 个均匀分布的点; 短片: 2 个点且更短, 否则试压成本会超过全片编码
    if dur < 8:
        seg = min(0.8, dur / 5.0)
        centers = (0.28, 0.72)
    else:
        seg = min(1.5, max(0.8, dur / 12.0), dur / 5.0)
        centers = (0.2, 0.5, 0.8)
    positions = [max(0.0, min(dur - seg, dur * c - seg / 2)) for c in centers]
    base = int(opts.get("crf", 24))
    c1, c2 = max(14, base - 4), min(38, base + 4)
    if c2 <= c1:
        c1, c2 = 14, 20
    ext = os.path.splitext(inp)[1].lower()
    if ext not in (".mp4", ".m4v", ".mov", ".mkv", ".webm"):
        ext = ".mp4"
    sizes = {}
    for crf in (c1, c2):
        total = 0
        for i, ss in enumerate(positions):
            tmp = os.path.join(tmpdir, "trial_%d_%d%s" % (crf, i, ext))
            total += _trial_segment(ff, inp, tmp, opts, vf, crf, ss, seg)
            try:
                if os.path.isfile(tmp):
                    os.remove(tmp)
            except Exception:
                pass
        sizes[crf] = total
    if sizes[c1] < 1024 or sizes[c2] < 1024:
        return None, 0.0, "试压未产出有效数据(可能是硬件编码器或特殊片源)"
    sample_dur = seg * len(positions)
    rate1 = sizes[c1] / sample_dur * dur
    rate2 = sizes[c2] / sample_dur * dur
    if rate1 <= rate2 * 1.001:
        # 体积未随 CRF 单调下降, 用经验斜率兜底
        rate2 = rate1 * 0.62
        c2 = c1 + 6
    slope = (math.log(max(1.0, rate2)) - math.log(max(1.0, rate1))) / float(c2 - c1)
    if slope >= -1e-4:
        slope = -0.075
    ab = 0.0 if opts.get("audio") == "strip" else 128000 * dur / 8.0
    tv = max(64 * 1024, target_bytes - ab)
    crf = c1 + (math.log(tv) - math.log(max(1.0, rate1))) / slope
    # 短采样段里 GOP / lookahead 结构不如整片充分, 同 CRF 下压缩率偏高,
    # 直接外推会系统性低估整片体积 (实测首轮可偏大 ~40%)。补一点保守余量,
    # 让首轮就落在目标附近, 尽量避免触发「再编码一遍」的精修。
    crf = max(12.0, min(40.0, crf + 1.2))
    note = ("采样 %d×%.1fs · CRF%d≈%.1fMB / CRF%d≈%.1fMB · 推算 CRF %.1f"
            % (len(positions), seg, c1, rate1 / 1048576, c2, rate2 / 1048576, crf))
    return crf, slope, note


# ==================== v10: 画质目标 (按 SSIM 反推 CRF) ====================
def _quality_point(ff, inp, tmp, opts, vf, crf, ss, seg):
    """试压一小段并与原片同段算 SSIM。返回 (ssim, 该段字节数)。"""
    size = _trial_segment(ff, inp, tmp, opts, vf, crf, ss, seg)
    if size <= 0 or not os.path.isfile(tmp):
        return None, size
    # 参考帧也要走同一条滤镜链, 否则量到的是「增强效果」而不是「压缩损伤」;
    # setpts 让两个输入都从 0 开始对齐, 避免 B 帧时间戳导致帧错位。
    # ssim 要求两路像素格式完全一致; 源可能是 8bit、10bit 输出是 yuv420p10le,
    # 统一转成 yuv420p 再比, 否则默认 10bit 设置下试压会直接失败。
    if vf and vf.startswith(FC_MARK):
        body = vf[len(FC_MARK):]
        _lbl, _, graph = body.partition("\n")
        # filter_complex 图的末节点是 [vout], 接着做时间戳/格式对齐再与原片比 SSIM
        fc = (graph + ";[vout]setpts=PTS-STARTPTS,format=yuv420p[ref];"
              "[1:v]setpts=PTS-STARTPTS,format=yuv420p[dist];[ref][dist]ssim")
    else:
        chain = ((vf + ",") if vf else "") + "setpts=PTS-STARTPTS,format=yuv420p"
        fc = ("[0:v]" + chain + "[ref];"
              "[1:v]setpts=PTS-STARTPTS,format=yuv420p[dist];[ref][dist]ssim")
    cmd = [ff, "-hide_banner", "-ss", "%.3f" % ss, "-t", "%.3f" % seg,
           "-i", inp, "-i", tmp, "-filter_complex", fc, "-an", "-f", "null", "-"]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=240, **UTF8_KW)
        if r.returncode == 0:
            m = re.search(r"All:\s*([0-9.]+)", r.stderr or "")
            if m:
                return max(0.0, min(1.0, float(m.group(1)))), size
    except Exception:
        pass
    return None, size


def fit_quality_crf(points, target, lo=12.0, hi=38.0, max_extrap=4.0):
    """由 (CRF, SSIM) 采样点反推满足目标 SSIM 的最大 CRF (体积最小)。
    局部把 SSIM~CRF 当作单调递减的折线, 分段线性插值。
    关键点: SSIM 在 0.99 以上会饱和(简单片源三档都接近 1), 若按斜率无限外推会
    冲到 CRF40 把整片压坏; 因此越界外推最多比实测范围多走 max_extrap 档。"""
    pts = []
    for p in points or []:
        try:
            c, s = float(p["crf"]), float(p["ssim"])
            if s > 0 and c > 0:
                pts.append((c, s))
        except Exception:
            pass
    pts.sort()
    if len(pts) < 2:
        return None
    # 去掉重复的 CRF, 并保证 SSIM 随 CRF 单调不增(试压偶有抖动)
    clean = []
    for c, s in pts:
        if clean and abs(c - clean[-1][0]) < 1e-6:
            continue
        if clean and s > clean[-1][1]:
            s = clean[-1][1]
        clean.append((c, s))
    if len(clean) < 2:
        return None

    def slope_of(a, b):
        d = (b[1] - a[1]) / (b[0] - a[0]) if b[0] != a[0] else -0.002
        return d if d < -1e-6 else -0.002

    if clean[-1][1] >= target:
        sl = slope_of(clean[-2], clean[-1])
        crf = clean[-1][0] + (clean[-1][1] - target) / (-sl) * 0.8
        crf = min(crf, clean[-1][0] + max_extrap)
    elif clean[0][1] <= target:
        sl = slope_of(clean[0], clean[1])
        crf = clean[0][0] - (target - clean[0][1]) / (-sl) * 0.8
        crf = max(crf, clean[0][0] - max_extrap)
    else:
        crf = clean[0][0]
        for a, b in zip(clean, clean[1:]):
            if a[1] >= target >= b[1]:
                crf = a[0] + (a[1] - target) / (a[1] - b[1]) * (b[0] - a[0])
                break
    return max(lo, min(hi, round(crf, 1)))


def quality_crf(ff, inp, opts, vf, dur, target, tmpdir):
    """抽 1-2 段试压 3 档 CRF, 每段算 SSIM, 拟合出满足目标画质的最小体积 CRF。
    返回 dict: {ok, crf, note, points, est_mb}。失败时 ok=False, 调用方回退固定 CRF。"""
    res = {"ok": False, "crf": None, "note": "", "points": [],
           "est_mb": 0.0, "target": target, "err": ""}
    if dur <= 0.5:
        res["err"] = "视频太短, 无法采样"
        return res
    # 短片只抽 1 段(试压成本不能超过全片编码), 其余一律片头+片尾 2 段,
    # 单段容易碰到纯色/静止画面导致 SSIM 虚高。
    short = dur < 3
    seg = min(0.6, dur / 5.0) if short else min(1.0, max(0.6, dur / 16.0), dur / 6.0)
    centers = (0.4,) if short else (0.28, 0.72)
    positions = [max(0.0, min(dur - seg, dur * c - seg / 2)) for c in centers]
    base = int(opts.get("crf", 24))
    crfs = sorted({max(14, min(38, int(c))) for c in (base - 4, base, base + 4)})
    if len(crfs) < 2:
        crfs = sorted({max(14, base - 2), min(38, base + 2)})
    sample_mb = {}
    for crf in crfs:
        vals, total = [], 0
        for i, ss in enumerate(positions):
            tmp = os.path.join(tmpdir, "qp_%d_%d.mp4" % (crf, i))
            s, sz = _quality_point(ff, inp, tmp, opts, vf, crf, ss, seg)
            if s is not None:
                vals.append(s)
            total += sz
            try:
                if os.path.isfile(tmp):
                    os.remove(tmp)
            except Exception:
                pass
        if vals:
            res["points"].append({"crf": crf, "ssim": round(sum(vals) / len(vals), 5),
                                  "sample_kb": round(total / 1024.0, 1)})
            sample_mb[crf] = total / 1048576.0
    if len(res["points"]) < 2:
        res["err"] = "试压未取得有效 SSIM 数据 (片源损坏 / 滤镜不被支持 / 编码器异常)"
        return res
    crf = fit_quality_crf(res["points"], target)
    if crf is None:
        res["err"] = "画质曲线拟合失败"
        return res
    res["ok"], res["crf"] = True, crf
    # 采样段 GOP 效率高于整片, 外推体积仅供参考, 不当作承诺值
    mid = min(sample_mb, key=lambda c: abs(c - crf))
    res["est_mb"] = round(sample_mb[mid] / (seg * len(positions)) * dur, 2)
    res["note"] = ("采样 %d×%.1fs · 目标 SSIM %.4f · "
                   % (len(positions), seg, target)
                   + " / ".join("CRF%d=%.4f" % (p["crf"], p["ssim"]) for p in res["points"])
                   + " · 推荐 CRF %.1f" % crf)
    return res


def encode_file(ff, inp, out, opts, before, dur, pct_cb=None, info=None):
    """返回 (ffmpeg 退出码, stderr 尾部, 是否走无损直传)。"""
    on_pct = pct_cb or set_cur
    mode = opts.get("mode", "crf")
    codec = opts.get("codec", "hevc")
    preset = opts.get("preset", "fast")
    tune = opts.get("tune", "animation")
    pix = opts.get("pix", "8")
    vf, _, _ = build_vf(opts, ff=ff, src=inp)

    kbps = _smart_copy_bitrate(opts, before, dur, vf)
    if kbps is not None:
        log("   智能直传: 源码率 %.0fkbps ≤ 阈值 %.0fkbps, 直接无损封装 (秒级完成)"
            % (kbps, float(opts.get("smart_copy_kbps", 1200) or 1200)))
        cmd = [ff, "-y", "-i", inp]
        cmd += stream_map_args(opts, out) or ["-map", "0:v:0", "-map", "0:a:0?"]
        cmd += ["-c:v", "copy"] + _audio_chain(opts)[0]
        cmd += stream_extra_args(opts, info, out)
        cmd += mux_args(out) + [out]
        rc, tail = _run_with_progress(cmd, dur, on_pct)
        if rc == 0:
            return 0, tail, True
        log("   直传失败, 回退正常重编码: " + (tail[-1] if tail else "未知原因"))
        try:
            if os.path.exists(out):
                os.remove(out)
        except Exception:
            pass

    # ---- v10 画质目标: 采样试压算 SSIM, 反推满足目标画质的最小体积 CRF ----
    if mode == "quality" and dur and dur > 0:
        target = float(_num(opts.get("quality_target", 0.99), 0.80, 0.9999, 0.99))
        tmpdir = tempfile.mkdtemp(prefix="vc_quality_")
        try:
            with state_lock:
                if state["stop"]:
                    return -1, [], False
            q = quality_crf(ff, inp, opts, vf, dur, target, tmpdir)
            o = dict(opts)
            o["mode"] = "crf"
            if q["ok"]:
                log("   画质目标: " + q["note"])
                o["crf"] = int(round(q["crf"]))
            else:
                log("   画质目标: " + (q["err"] or q["note"])
                    + " → 回退固定 CRF " + str(opts.get("crf")))
            rc, tail = _run_with_progress(build_cmd(ff, inp, out, o, vf, info), dur, on_pct)
            return rc, tail, False
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    # ---- v8 智能体积: 采样试压推算 CRF, 只编码一遍全片 (两遍模式要跑两遍) ----
    if mode == "smart" and dur and dur > 0:
        target = max(60 * 1024, float(opts.get("target_mb", 50)) * 1024 * 1024)
        tmpdir = tempfile.mkdtemp(prefix="vc_smart_")
        try:
            with state_lock:
                if state["stop"]:
                    return -1, [], False
            crf, slope, note = smart_crf(ff, inp, opts, vf, dur, target, tmpdir)
            if crf is None:
                log("   智能体积: " + note + " → 回退固定 CRF " + str(opts.get("crf")))
                o = dict(opts)
                o["mode"] = "crf"
                rc, tail = _run_with_progress(build_cmd(ff, inp, out, o, vf, info), dur, on_pct)
                return rc, tail, False
            log("   智能体积: 目标 %.1fMB · %s" % (target / 1048576, note))
            o = dict(opts)
            o["mode"], o["crf"] = "crf", int(round(crf))
            rc, tail = _run_with_progress(build_cmd(ff, inp, out, o, vf, info), dur, on_pct)

            # 偏差 >15% 时自动精修。关键点: 采样段得到的斜率通常比全片真实斜率平缓,
            # 直接用它会调过头; 因此首轮用保守收缩的斜率, 之后用两轮全片实测点重估斜率。
            if rc == 0 and os.path.isfile(out) and opts.get("smart_refine", True) and slope < -1e-4:
                best_crf, best_sz = float(o["crf"]), os.path.getsize(out)
                trials = [(best_crf, best_sz)]
                for _attempt in range(2):
                    err = abs(best_sz - target) / float(target)
                    if err <= 0.15:
                        break
                    if len(trials) >= 2:
                        (ca, sa), (cb, sb) = trials[-2], trials[-1]
                        sl = ((math.log(sb) - math.log(sa)) / (cb - ca)
                              if cb != ca and sa > 0 and sb > 0 else slope)
                        if sl >= -1e-3:
                            sl = slope
                    else:
                        sl = slope * 1.5
                    crf_n = max(12.0, min(40.0,
                                best_crf + math.log(best_sz / float(target)) / (-sl)))
                    if (abs(crf_n - best_crf) < 0.4
                            or int(round(crf_n)) == int(round(best_crf))):
                        break
                    stem, ext = os.path.splitext(out)
                    tmp2 = stem + ".vcpart.refine" + ext
                    o2 = dict(o)
                    o2["crf"] = int(round(crf_n))
                    log("   智能体积: 第%d轮 %.1fMB 偏差 %.0f%%, 精修 CRF %.1f → %.1f"
                        % (len(trials), best_sz / 1048576, err * 100, best_crf, crf_n))
                    rc2, tail2 = _run_with_progress(
                        build_cmd(ff, inp, tmp2, o2, vf, info), dur, on_pct)
                    try:
                        if rc2 == 0 and os.path.isfile(tmp2):
                            s2 = os.path.getsize(tmp2)
                            trials.append((float(o2["crf"]), s2))
                            if abs(s2 - target) < abs(best_sz - target):
                                os.replace(tmp2, out)
                                best_crf, best_sz = float(o2["crf"]), s2
                                tail = tail2
                                log("   智能体积: 精修后 %.1fMB (目标 %.1fMB)"
                                    % (s2 / 1048576, target / 1048576))
                            else:
                                log("   智能体积: 精修未更接近目标, 保留上一轮结果")
                        if os.path.isfile(tmp2):
                            os.remove(tmp2)
                    except Exception as e:
                        log("   智能体积: 精修结果处理失败 " + str(e))
            if rc == 0 and os.path.isfile(out):
                final_sz = os.path.getsize(out)
                log("   智能体积: 最终 %.2fMB / 目标 %.2fMB (偏差 %+.1f%%)"
                    % (final_sz / 1048576, target / 1048576,
                       (final_sz - target) / float(target) * 100))
            return rc, tail, False
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    if mode in ("ratio", "size") and dur and dur > 0:
        if mode == "ratio":
            target = before * float(opts.get("ratio", 0.3))
        else:
            target = float(opts.get("target_mb", 50)) * 1024 * 1024
        target = max(60 * 1024, target)
        abr = 0 if opts.get("audio") == "strip" else 128000
        vbr = int(max(100000, target * 8 / dur * 0.98 - abr))
        log(f"   目标体积模式: 目标≈{target/1024/1024:.1f}MB, 视频码率≈{vbr//1000}kbps, 两遍编码")
        tmp = tempfile.mkdtemp(prefix="vc_")
        try:
            def base(passno):
                c = [ff, "-y", "-i", inp]
                if vf:
                    c += ["-vf", vf]
                c += ["-c:v", "libx265" if codec == "hevc" else "libx264",
                      "-b:v", str(vbr), "-preset", preset]
                if codec == "hevc":
                    if pix == "10":
                        c += ["-pix_fmt", "yuv420p10le"]
                    xp = f"pass={passno}:stats=x265stats.log"
                    if passno == 1:
                        xp += ":fast-firstpass=1"   # 首遍只做统计, 用快速配置省一半时间
                    c += ["-x265-params", xp]
                else:
                    c += ["-pass", str(passno), "-passlogfile", "x264pass"]
                if tune and tune != "none":
                    c += ["-tune", tune]
                return c

            c1 = base(1) + ["-an", "-f", "null", "-"]
            rc1, tail1 = _run_with_progress(c1, dur, lambda p: on_pct(p * 0.5), cwd=tmp)
            with state_lock:
                stopped = state["stop"]
            if stopped:
                return -1, tail1, False
            if rc1 != 0:
                return rc1, tail1, False
            c2 = base(2) + stream_map_args(opts, out) + ["-tag:v", "hvc1" if codec == "hevc" else "avc1"]
            aargs2, af2 = _audio_chain(opts)
            c2 += aargs2
            if af2:
                c2 += ["-af", ",".join(af2)]
            c2 += stream_extra_args(opts, info, out)
            c2 += mux_args(out) + [out]
            rc2, tail2 = _run_with_progress(c2, dur, lambda p: on_pct(50 + p * 0.5), cwd=tmp)
            return rc2, tail2, False
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        cmd = build_cmd(ff, inp, out, opts, vf, info)
        rc, tail = _run_with_progress(cmd, dur, on_pct)
        return rc, tail, False


# ---- v11: 视频工具箱 (独立小工具, 不进入压缩流水线) ----
def _concat_reencode(ff, srcs, out, fp):
    """统一重编码拼接: 各段缩放到第一段的分辨率/帧率, 音轨统一为立体声 48k, 缺音轨补静音。"""
    infos = [probe_streams(fp, s) if fp else {} for s in srcs]
    W = int(infos[0].get("width") or 0) or 1280
    H = int(infos[0].get("height") or 0) or 720
    FPS = infos[0].get("fps") or 30
    hasa = [bool(i.get("audio")) for i in infos]
    any_a = any(hasa)
    cmd = [ff, "-y"]
    for s in srcs:
        cmd += ["-i", s]
    parts = []
    for i in range(len(srcs)):
        parts.append("[%d:v]scale=%d:%d,setsar=1,fps=%s,format=yuv420p[v%d]"
                     % (i, W, H, FPS, i))
        if any_a:
            if hasa[i]:
                parts.append("[%d:a]aresample=48000,aformat=sample_fmts=fltp:"
                             "channel_layouts=stereo[a%d]" % (i, i))
            else:
                dur = float(infos[i].get("duration") or 0.0) or 1.0
                parts.append("anullsrc=r=48000:cl=stereo,atrim=0:%.3f[a%d]" % (dur, i))
    vlabels = "".join("[v%d]" % i for i in range(len(srcs)))
    if any_a:
        alabels = "".join("[a%d]" % i for i in range(len(srcs)))
        fc = ";".join(parts) + ";%s%sconcat=n=%d:v=1:a=1[vout][aout]" % (
            vlabels, alabels, len(srcs))
    else:
        fc = ";".join(parts) + ";%sconcat=n=%d:v=1:a=0[vout]" % (vlabels, len(srcs))
    cmd += ["-filter_complex", fc, "-map", "[vout]"]
    if any_a:
        cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-crf", "20", "-preset", "fast"] + mux_args(out) + [out]
    return subprocess.run(cmd, capture_output=True, timeout=3600, **UTF8_KW)


def run_tool(ff, action, src, out, opts):
    """执行一个工具箱动作, 返回 (rc, 日志行列表, 信息字典)。非流式, 适合单文件快速处理。"""
    lines = []
    info = {"action": action, "src": src, "out": out}
    if not ff:
        return -1, ["未找到 ffmpeg"], info
    if action != "concat" and (not src or not os.path.isfile(src)):
        return -1, ["源文件不存在: " + str(src)], info
    if not out:
        return -1, ["未指定输出路径"], info
    try:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    except Exception:
        pass
    try:
        if action == "gif":
            ss = float(_num(opts.get("ss", 0), 0, 1e9, 0))
            dur = float(_num(opts.get("duration", 0), 0, 1e9, 0))
            fps = int(_num(opts.get("gif_fps", 15), 1, 50, 15))
            w = int(_num(opts.get("gif_w", 480), 32, 4096, 480))
            pref = ["-ss", "%.3f" % ss] if ss else []
            targ = ["-t", "%.3f" % dur] if dur else []
            pal = os.path.join(tempfile.gettempdir(), "vc_palette_%d.png"
                              % (int(time.time() * 1000) % 1000000))
            c1 = [ff, "-y"] + pref + ["-i", src] + targ + [
                "-vf", "fps=%d,scale=%d:-1:flags=lanczos,palettegen" % (fps, w), pal]
            lines.append("生成调色板…")
            r1 = subprocess.run(c1, capture_output=True, timeout=300, **UTF8_KW)
            if r1.returncode != 0:
                return r1.returncode, [r1.stderr.decode("utf-8", "replace")[-500:]
                                       if r1.stderr else "palettegen 失败"], info
            c2 = [ff, "-y"] + pref + ["-i", src, "-i", pal] + targ + [
                "-lavfi", "fps=%d,scale=%d:-1:flags=lanczos[x];[x][1:v]paletteuse" % (fps, w),
                "-loop", "0", out]
            lines.append("合成 GIF…")
            r2 = subprocess.run(c2, capture_output=True, timeout=600, **UTF8_KW)
            try:
                if os.path.isfile(pal):
                    os.remove(pal)
            except Exception:
                pass
            if r2.returncode == 0 and os.path.isfile(out):
                info["size"] = os.path.getsize(out)
                return 0, lines + ["完成: " + out], info
            return r2.returncode, [r2.stderr.decode("utf-8", "replace")[-500:]
                                  if r2.stderr else "合成失败"], info

        if action == "clip":
            ss = float(_num(opts.get("ss", 0), 0, 1e9, 0))
            dur = float(_num(opts.get("duration", 0), 0, 1e9, 0))
            pref = ["-ss", "%.3f" % ss] if ss else []
            targ = ["-t", "%.3f" % dur] if dur else []
            c = [ff, "-y"] + pref + ["-i", src] + targ + ["-c", "copy", out]
            lines.append("截取片段 (流拷贝)…")
            r = subprocess.run(c, capture_output=True, timeout=600, **UTF8_KW)
            if r.returncode != 0:
                # 流拷贝失败 (如跨格式/需重编码) 回退重编码
                lines.append("流拷贝失败, 回退重编码…")
                c2 = [ff, "-y"] + pref + ["-i", src] + targ + [
                    "-c:v", "libx264", "-crf", "20", "-preset", "fast",
                    "-c:a", "aac", "-b:a", "128k", out]
                r = subprocess.run(c2, capture_output=True, timeout=600, **UTF8_KW)
            if r.returncode == 0 and os.path.isfile(out):
                info["size"] = os.path.getsize(out)
                return 0, lines + ["完成: " + out], info
            return r.returncode, [r.stderr.decode("utf-8", "replace")[-500:]
                                 if r.stderr else "截取失败"], info

        if action == "deshake":
            c = [ff, "-y", "-i", src, "-vf", "deshake", "-c:v", "libx264",
                 "-crf", "20", "-preset", "fast", "-c:a", "copy", out]
            lines.append("防抖处理 (deshake)…")
            r = subprocess.run(c, capture_output=True, timeout=900, **UTF8_KW)
            if r.returncode == 0 and os.path.isfile(out):
                info["size"] = os.path.getsize(out)
                return 0, lines + ["完成: " + out], info
            return r.returncode, [r.stderr.decode("utf-8", "replace")[-500:]
                                 if r.stderr else "防抖失败"], info

        if action == "rotate":
            fp = find_ffprobe()
            rot = probe_streams(fp, src).get("rotation", 0) if fp else 0
            rot = int(round(rot / 90.0)) * 90 % 360
            info["rotation"] = rot
            if rot == 0:
                # 无需旋转, 仅重封装 (清空可能的旋转元数据)
                c = [ff, "-y", "-i", src, "-c", "copy", "-metadata:s:v:0",
                     "rotate=0", out]
                lines.append("无需旋转, 仅重封装并清除旋转元数据…")
            else:
                m = {90: "transpose=1", 180: "transpose=1,transpose=1",
                     270: "transpose=2"}[rot]
                c = [ff, "-y", "-i", src, "-vf", m, "-c:v", "libx264", "-crf", "20",
                     "-preset", "fast", "-c:a", "copy", "-metadata:s:v:0",
                     "rotate=0", out]
                lines.append("按旋转 %d° 自动转正…" % rot)
            r = subprocess.run(c, capture_output=True, timeout=900, **UTF8_KW)
            if r.returncode == 0 and os.path.isfile(out):
                info["size"] = os.path.getsize(out)
                return 0, lines + ["完成: " + out], info
            return r.returncode, [r.stderr.decode("utf-8", "replace")[-500:]
                                 if r.stderr else "旋转失败"], info

        if action == "concat":
            srcs = [s for s in (opts.get("sources") or []) if s and os.path.isfile(s)]
            if len(srcs) < 2:
                return -1, ["拼接至少需要 2 个有效源文件"], info
            fp = find_ffprobe()
            listf = os.path.join(tempfile.gettempdir(),
                                 "vc_concat_%d.txt" % (int(time.time() * 1000) % 1000000))
            try:
                with open(listf, "w", encoding="utf-8") as f:
                    for s in srcs:
                        f.write("file '%s'\n" % s.replace("\\", "/").replace("'", "'\\''"))
                lines.append("拼接 %d 个片段…" % len(srcs))
                c = [ff, "-y", "-f", "concat", "-safe", "0", "-i", listf, "-c", "copy", out]
                r = subprocess.run(c, capture_output=True, timeout=3600, **UTF8_KW)
                if r.returncode != 0:
                    lines.append("无损拼接失败 (编码参数不一致), 改为统一重编码…")
                    r = _concat_reencode(ff, srcs, out, fp)
            finally:
                try:
                    if os.path.isfile(listf):
                        os.remove(listf)
                except Exception:
                    pass
            if r.returncode == 0 and os.path.isfile(out):
                info["size"] = os.path.getsize(out)
                info["count"] = len(srcs)
                return 0, lines + ["完成: " + out], info
            err = r.stderr or ""
            tail = [l for l in err.splitlines() if l.strip()][-2:]
            return r.returncode, lines + (["拼接失败: " + tail[-1][:200]] if tail else ["拼接失败"]), info

        if action == "frame":
            ss = float(_num(opts.get("ss", 0), 0, 1e9, 0))
            c = [ff, "-y", "-ss", "%.3f" % ss, "-i", src, "-frames:v", "1", out]
            lines.append("提取第 %.1fs 帧…" % ss)
            r = subprocess.run(c, capture_output=True, timeout=120, **UTF8_KW)
            if r.returncode == 0 and os.path.isfile(out):
                info["size"] = os.path.getsize(out)
                return 0, lines + ["完成: " + out], info
            return r.returncode, [r.stderr.decode("utf-8", "replace")[-500:]
                                 if r.stderr else "抽帧失败"], info

        return -1, ["未知工具动作: " + str(action)], info
    except Exception as e:
        return -2, [str(e)], info


# ---- v12: 输出文件名模板可用变量 ----
NAME_TOKENS = {
    "name": "原文件名(不含扩展名)",
    "full": "完整原文件名(含扩展名)",
    "ext": "扩展名",
    "crf": "CRF 值",
    "size": "目标体积 MB",
    "codec": "编码格式",
    "mode": "压缩模式",
    "aspect": "画幅",
    "date": "日期(20261108)",
    "time": "时间(172530)",
    "index": "序号(001)",
}


def apply_name_template(tpl, src_path, opts, index=0):
    """按模板生成输出文件名。模板为空时返回原文件名 (保持默认行为)。
    模板里没写扩展名会自动补上源文件的扩展名。"""
    base = os.path.basename(src_path)
    stem, ext = os.path.splitext(base)
    if not tpl or not str(tpl).strip():
        return base
    vals = {
        "name": stem,
        "full": base,
        "ext": ext.lstrip("."),
        "crf": str(opts.get("crf", "")),
        "size": str(opts.get("target_mb", "")),
        "codec": str(opts.get("codec", "")),
        "mode": str(opts.get("mode", "")),
        "aspect": str(opts.get("aspect", "keep")),
        "date": time.strftime("%Y%m%d"),
        "time": time.strftime("%H%M%S"),
        "index": "%03d" % (int(index) + 1),
    }
    out = str(tpl).strip()
    for k, v in vals.items():
        out = out.replace("{%s}" % k, v)
    # 清理 Windows 文件名非法字符, 并去掉结尾的点/空格
    out = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", out).strip(" .")
    if not out:
        out = stem or "output"
    if not os.path.splitext(out)[1]:
        out += ext
    return out


def run_job(files, opts, out_mode, out_sub, force, overrides=None):
    overrides = overrides if isinstance(overrides, dict) else {}
    global FILE_PCT, DURS, ACTIVE, RESULTS_BUF
    ff = find_ffmpeg()
    fp = find_ffprobe()
    with state_lock:
        state.update({
            "running": True, "stop": False, "results": [], "log": [], "error": None,
            "overall_pct": 0, "current_index": -1, "current_pct": 0, "finished": 0,
            "total_duration": 0.0, "processed_dur": 0.0, "effective_dur": 0.0,
            "job_start": time.time(), "speed": 0.0, "active_names": [], "workers": 1,
            "eta": "", "out_folder": "", "log_file": "",
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "enhance_label": "",
        })

    if not ff:
        with state_lock:
            state["error"] = "未找到 ffmpeg, 请在界面中指定 ffmpeg.exe 路径"
            state["running"] = False
        return

    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        lf = os.path.join(LOGS_DIR, "job_" + time.strftime("%Y%m%d_%H%M%S") + ".log")
        JOB["log_file"] = lf
        with state_lock:
            state["log_file"] = lf
    except Exception:
        lf = ""
        JOB["log_file"] = ""

    log("=== 任务开始 " + time.strftime("%Y-%m-%d %H:%M:%S") + " ===")

    if opts.get("enh_on") and opts.get("enh_only"):
        opts["mode"] = "crf"
        opts["crf"] = opts.get("enh_crf", 16)
        opts["audio"] = "copy"
        opts["engine"] = "software"
        log("仅增强模式: 不压缩, CRF %s + 原音轨复制 (体积可能变大)" % opts["crf"])

    # auto = 检测到显卡就用硬件编码, 没有则静默回退软件
    hw = get_hw(ff)
    if opts.get("mode") in ("ratio", "size"):
        if opts.get("engine") != "software":
            log("目标体积模式使用两遍软件编码(硬件不支持两遍), 已忽略硬件加速")
        opts["engine"] = "software"
        opts["hw"] = None
    else:
        eng = opts.get("engine", "software")
        # v11: AV1/VP9 仅软件编码 (硬件编码器罕见且刻度漂移大), 且需本机 ffmpeg 支持
        if opts.get("codec") in ("av1", "vp9"):
            avail = get_video_codecs(ff)
            if opts.get("codec") not in avail:
                log("编码格式 %s 本机 ffmpeg 不支持, 已回退为 H.265" % opts.get("codec"))
                opts["codec"] = "hevc"
            else:
                opts["engine"], opts["hw"] = "software", None
                if opts.get("mode") in ("smart", "quality"):
                    log("%s 模式 + %s: 软件编码以保证试压曲线稳定 (AV1/VP9 编码较慢, 适合归档)"
                        % ("智能体积" if opts.get("mode") == "smart" else "画质目标",
                           opts.get("codec").upper()))
                else:
                    log("编码格式: %s (软件编码, 比 H.265 更慢但体积更小)" % opts.get("codec").upper())
        # 智能体积/画质目标都靠「CRF → 体积或画质」的稳定曲线反推,
        # 硬件编码器刻度漂移大, 自动引擎下统一用软件编码保证拟合精度;
        # 用户显式强制硬件时仍尊重选择。
        if opts.get("codec") not in ("av1", "vp9"):
            if opts.get("mode") in ("smart", "quality") and eng == "auto":
                eng = "software"
                log("%s: 自动引擎改用软件编码以保证试压曲线稳定 (可手动强制硬件)"
                    % ("智能体积" if opts.get("mode") == "smart" else "画质目标"))
            chosen = None
            if eng in ("auto", "hardware"):
                chosen = hw["h264"] if opts.get("codec") == "h264" else hw["hevc"]
            if chosen:
                opts["engine"], opts["hw"] = "hardware", chosen
            else:
                opts["engine"], opts["hw"] = "software", None
                if eng != "software":
                    log("未检测到可用硬件编码器, 回退为软件编码")

    workers = int(_num(opts.get("workers", 2), 1, 4, 2))
    keep_smaller = bool(opts.get("keep_smaller", True))
    smart_copy = bool(opts.get("smart_copy", False))
    max_height = int(_num(opts.get("max_height", 0), 0, 4096, 0))

    log("ffmpeg: " + ff)
    log("参数: mode=%s codec=%s crf=%s preset=%s tune=%s pix=%s audio=%s out=%s/%s" % (
        opts.get("mode"), opts.get("codec"), opts.get("crf"), opts.get("preset"),
        opts.get("tune"), opts.get("pix"), opts.get("audio"), out_mode, out_sub))
    log("提速: %d 并发 | 引擎=%s%s | 智能直传=%s | 限高=%s | 变大留原片=%s" % (
        workers, opts["engine"],
        ("(" + str(opts.get("hw")) + ")") if opts.get("hw") else "",
        "开" if smart_copy else "关",
        ("%dp" % max_height) if max_height else "不限",
        "开" if keep_smaller else "关"))
    _stream_label = {"single": "标准 (单视频轨 + 单音轨)",
                     "allaudio": "全部音轨 + 元数据/章节",
                     "all": "全部流 (音轨/字幕/章节/元数据/HDR 标记)"}
    log("流保留: %s | 断点续跑=%s | 智能体积精修=%s | 输出验收=%s" % (
        _stream_label.get(opts.get("streams", "single"), "标准"),
        "开" if opts.get("resume", True) else "关",
        "开" if opts.get("smart_refine", True) else "关",
        {"off": "关", "quick": "抽3段解码", "full": "整片解码"}.get(opts.get("verify", "off"), "关")))
    log("v11: 画质目标 SSIM=%s | 失败自愈=%s | 逐文件微调=%d 项 | 音频=%s%s%s"
        % (opts.get("quality_target", 0.99),
           "开" if opts.get("auto_fallback", True) else "关", len(overrides),
           opts.get("audio"),
           (" 归一化%s" % opts.get("audio_normalize")) if opts.get("audio_normalize", "off") != "off" else "",
           (" 降噪%s" % opts.get("audio_denoise")) if opts.get("audio_denoise", "off") != "off" else ""))
    if opts.get("wm_type", "off") != "off" or opts.get("wm_sub", "off") != "off":
        log("v11: 水印=%s | 字幕烧录=%s" % (opts.get("wm_type"), opts.get("wm_sub")))
    if opts.get("engine") == "hardware" and opts.get("hw"):
        h = str(opts.get("hw"))
        off = 3 if "qsv" in h else (2 if "nvenc" in h else 0)
        cal = f" · 质量校准 CRF{opts.get('crf')}→{int(opts.get('crf') or 24) + off}" if off else ""
        log("引擎: 硬件加速 " + h + cal)
    else:
        log("引擎: 软件编码(x265/x264)" + (" · 两遍" if opts.get("mode") in ("ratio", "size") else ""))

    vf, enh_labels, enh_skipped = build_vf(opts, ff=ff, src=files[0] if files else None)
    label = " + ".join(enh_labels)
    with state_lock:
        state["enhance_label"] = label if opts.get("enh_on") else ""
    if opts.get("enh_on") or vf:
        log("滤镜: " + (label if label else "无"))
        if vf:
            log("滤镜链: " + vf)
        for s in enh_skipped:
            log("  [跳过] " + s)

    files = [f for f in files if f and os.path.isfile(f) and _is_video(os.path.basename(f))]
    if not files:
        log("没有可处理的视频文件")
        with state_lock:
            state["running"] = False
        JOB["log_file"] = ""
        return

    n = len(files)
    if out_mode == "sub":
        with state_lock:
            state["out_folder"] = os.path.join(os.path.dirname(files[0]), out_sub or "已压缩")

    log(f"共 {n} 个文件待处理")

    def _probe(f):
        return probe_streams(fp, f) if fp else {}

    if fp and n > 1:
        with ThreadPoolExecutor(max_workers=min(8, n)) as ex:
            infos = list(ex.map(_probe, files))
    else:
        infos = [_probe(f) for f in files]
    durations = [float(i.get("duration", 0.0) or 0.0) for i in infos]
    total_dur = sum(durations)

    FILE_PCT = {i: 0.0 for i in range(n)}
    DURS = list(durations)
    ACTIVE = {}
    RESULTS_BUF = [None] * n
    with state_lock:
        state.update({"total": n, "total_duration": total_dur, "workers": workers,
                      "results": [], "finished": 0, "current_index": 0})

    tasks = []
    tpl = opts.get("name_template", "") or ""
    for idx, f in enumerate(files):
        name = os.path.basename(f)
        if out_mode == "sub":
            out_dir = os.path.join(os.path.dirname(f), out_sub or "已压缩")
            os.makedirs(out_dir, exist_ok=True)
            # 输出到子文件夹时可用文件名模板改名 (覆盖原文件模式保持原名)
            out_name = apply_name_template(tpl, f, opts, idx) if tpl else name
            out_path = os.path.join(out_dir, out_name)
        else:
            out_path = f
        tasks.append((idx, f, name, os.path.getsize(f), durations[idx], out_path, infos[idx]))

    task_word = ("增强" if (opts.get("enh_on") and opts.get("enh_only"))
                 else ("增强+压缩" if opts.get("enh_on") and vf
                       else ("限高+压缩" if vf else "压缩")))

    def _rm(p):
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass

    def fail_result(name, before, f, status):
        return {"name": name, "before": before, "after": 0, "pct": 0,
                "status": status, "src": f, "out": ""}

    def process_one(t):
        idx, f, name, before, cur_dur, out_path, finfo = t
        try:
            with state_lock:
                stopped = state["stop"]
            if stopped:
                return
            set_active(idx, name)
            set_file_pct(idx, 0)

            # v10 逐文件微调: 只合并白名单字段, 其余仍用全局参数
            o = merge_opts(opts, overrides.get(f) or overrides.get(name))
            if o.get("_ov_keys"):
                log("  [%s] 逐文件微调: %s" % (name, ", ".join(o["_ov_keys"])))

            # 断点续跑: 输出已存在时直接算成功; 关掉开关则重新编码覆盖它
            if (out_mode != "overwrite" and os.path.exists(out_path)
                    and not force and o.get("resume", True)):
                try:
                    fresh = os.path.getmtime(out_path) >= os.path.getmtime(f)
                except Exception:
                    fresh = True
                st = "已完成(续跑跳过)" if fresh else "已存在(跳过)"
                log(f"[跳过] {st}: {name}")
                after = os.path.getsize(out_path)
                push_result(idx, {"name": name, "before": before, "after": after,
                                  "pct": round(after / before * 100, 1) if before else 0,
                                  "status": st, "src": f, "out": out_path})
                return

            stem, ext = os.path.splitext(out_path)
            tmp_path = stem + ".vcpart" + ext
            log(f"[{idx+1}/{n}] {task_word}: {name}  ({before//1024//1024} MB)")
            t0 = time.time()
            fallback_note = ""

            def attempt(cur_o):
                return encode_file(
                    ff, f, tmp_path, cur_o, before, cur_dur,
                    pct_cb=lambda p, i=idx: set_file_pct(i, p), info=finfo)

            try:
                rc, tail, copied = attempt(o)
                # v10 失败自愈: 硬件编码器与增强滤镜是两类最常见的失败源。
                # 第一次失败后自动降级为软件编码 + 去掉滤镜/限高再试一次,
                # 避免整批任务因为单个特殊片源全部卡住。
                if rc != 0 and o.get("auto_fallback", True) and not o.get("enh_only"):
                    fb = dict(o)
                    changes = []
                    if fb.get("engine") == "hardware":
                        fb["engine"], fb["hw"] = "software", None
                        changes.append("硬件→软件编码")
                    if build_vf(fb, ff=ff)[0]:
                        fb["enh_on"] = False
                        fb["enh_crop"] = ""
                        fb["max_height"] = 0
                        fb["enh_denoise"] = "off"
                        fb["enh_sharpen"] = "off"
                        fb["enh_upscale"] = "off"
                        fb["enh_interp"] = "off"
                        fb["enh_deblock"] = fb["enh_deband"] = False
                        fb["enh_deinterlace"] = False
                        changes.append("关闭滤镜/限高")
                    if changes:
                        log("  -> 编码失败, 自动降级重试: " + " + ".join(changes))
                        _rm(tmp_path)
                        set_file_pct(idx, 0)
                        rc2, tail2, copied2 = attempt(fb)
                        # 无论成败都采用第二次的返回码, 但只有成功才记录降级说明
                        rc, tail, copied = rc2, tail2, copied2
                        if rc2 == 0:
                            fallback_note = " · 自动降级(" + "、".join(changes) + ")"
                            log("  -> 降级重试成功" + fallback_note)
            except Exception as e:
                log("编码异常: " + str(e))
                _rm(tmp_path)
                push_result(idx, fail_result(name, before, f, "失败:" + str(e)))
                return

            with state_lock:
                aborted = state["stop"]
            if aborted:
                _rm(tmp_path)
                log("  已中止, 丢弃未完成的输出(原文件未受影响)")
                push_result(idx, fail_result(name, before, f, "已中止"))
                return

            if rc != 0:
                log("  -> 编码失败 (ffmpeg 退出码 %s), 已丢弃输出, 原文件未受影响" % rc)
                for l in tail[-6:]:
                    log("     " + l)
                _rm(tmp_path)
                push_result(idx, fail_result(name, before, f, "失败:ffmpeg %s" % rc))
                return

            if not (os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0):
                log("  -> 输出缺失(可能中断)")
                push_result(idx, fail_result(name, before, f, "失败:无输出"))
                return

            # 压缩后反而变大: 丢掉重编码结果, 保留原片 (不再产出 119% 体积的文件)
            new_size = os.path.getsize(tmp_path)
            cur_vf = build_vf(o, ff=ff, src=f)[0]
            if (o.get("keep_smaller", keep_smaller) and not cur_vf
                    and not o.get("enh_only") and not copied and new_size >= before):
                _rm(tmp_path)
                if out_mode == "sub":
                    try:
                        shutil.copy2(f, out_path)
                    except Exception as e:
                        log("  复制原文件失败: " + str(e))
                log(f"  -> 重编码后 {new_size/1048576:.1f}MB ≥ 原片 {before/1048576:.1f}MB, 已保留原片")
                push_result(idx, {"name": name, "before": before, "after": before, "pct": 100.0,
                                  "status": "完成 (原文件更小, 已保留)", "src": f, "out": out_path,
                                  "verify": None})
                return

            # v9 输出验收: 先检验临时文件, 确认没被编码坏再落盘, 避免产出"看起来成功"的损坏视频
            verify = None
            vlvl = o.get("verify", "off")
            if vlvl in ("quick", "full"):
                try:
                    verify = verify_output(ff, fp, f, tmp_path, finfo, vlvl, o)
                except Exception as e:
                    verify = {"ok": False, "fatal": False, "label": "⚠ 校验异常", "level": vlvl,
                              "checks": [{"name": "校验执行", "ok": False, "detail": str(e)}]}
                if verify.get("fatal"):
                    log("  -> 输出验收未通过, 已丢弃损坏输出: " + verify.get("label", ""))
                    for c in verify.get("checks", []):
                        if not c.get("ok"):
                            log("     [%s] %s" % (c.get("name", ""), str(c.get("detail", ""))[:160]))
                    _rm(tmp_path)
                    push_result(idx, dict(fail_result(name, before, f, "失败:输出验收"), verify=verify))
                    return
                log("  -> 输出验收: " + verify.get("label", ""))

            try:
                os.replace(tmp_path, out_path)
            except Exception:
                try:
                    shutil.move(tmp_path, out_path)
                except Exception:
                    pass
            after = os.path.getsize(out_path)
            pctv = round(after / before * 100, 1) if before else 0
            try:
                st = os.stat(f)
                os.utime(out_path, (st.st_atime, st.st_mtime))
            except Exception:
                pass
            note = (" · 无损直传" if copied else "") + fallback_note
            log(f"  -> {after/1048576:.1f} MB  ({pctv}% 体积, 耗时 {time.time()-t0:.1f}s){note}")
            if copied:
                st_text = "完成 (无损直传)"
            elif pctv > 100:
                st_text = f"完成 (体积增大 {pctv-100:.0f}%)"
            else:
                st_text = f"完成 ({100-pctv:.0f}%↓)"
            if fallback_note:
                st_text += " · 已自动降级"
            push_result(idx, {"name": name, "before": before, "after": after, "pct": pctv,
                              "status": st_text, "src": f, "out": out_path, "verify": verify,
                              "fallback": fallback_note, "mode": o.get("mode", "crf"),
                              "quality_target": o.get("quality_target", 0.99)})
        except Exception as e:
            log(f"[{idx+1}/{n}] 处理异常: {name}: {e}")
            push_result(idx, fail_result(name, before, f, "失败:" + str(e)))
        finally:
            clear_active(idx)
            mark_done(idx)
            with state_lock:
                state["processed_dur"] += cur_dur
                state["finished"] += 1
                state["current_index"] = state["finished"]

    if workers > 1 and n > 1:
        with ThreadPoolExecutor(max_workers=min(workers, n)) as ex:
            futs = [ex.submit(process_one, t) for t in tasks]
            for _ in as_completed(futs):
                pass
    else:
        for t in tasks:
            process_one(t)

    with state_lock:
        res = list(state["results"])
        was_stopped = state["stop"]
        job_start = state["job_start"]
    ok_res = [r for r in res if r.get("after", 0) > 0]
    bad_n = len(res) - len(ok_res)
    tb = sum(r["before"] for r in ok_res)
    ta = sum(r["after"] for r in ok_res)
    save_pct = (100 - ta / tb * 100) if tb else 0
    elapsed = max(0.1, time.time() - job_start)
    spd = total_dur / elapsed if elapsed > 0 else 0
    log(f"--- 汇总: 成功 {len(ok_res)} 个, {tb/1048576:.1f}MB -> {ta/1048576:.1f}MB, 节省 {save_pct:.1f}%"
        + (f" · 失败/中止 {bad_n} 个" if bad_n else ""))
    log(f"--- 总耗时 {elapsed:.1f}s · 平均 {spd:.2f}× 实时 · {min(workers, n)} 并发")
    log("任务已中止。" if was_stopped else "全部处理完成。")
    if lf:
        log("日志已保存: " + lf)

    # v10 任务历史: 追加一行 JSON, 供界面统计与导出; 写失败不影响任务结果
    try:
        append_history({
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total": n, "ok": len(ok_res), "failed": bad_n,
            "before": tb, "after": ta, "saved_bytes": max(0, tb - ta),
            "saved_pct": round(save_pct, 1), "elapsed": round(elapsed, 1),
            "speed": round(spd, 2), "stopped": bool(was_stopped),
            "mode": opts.get("mode", "crf"), "codec": opts.get("codec", ""),
            "crf": opts.get("crf", 0), "workers": min(workers, n),
            "verify": opts.get("verify", "off"), "quality_target": opts.get("quality_target", 0.99),
            "files": [{"name": r.get("name", ""), "before": r.get("before", 0),
                       "after": r.get("after", 0), "status": r.get("status", "")}
                      for r in res],
        })
    except Exception as e:
        log("历史记录写入失败(不影响任务): " + str(e))

    if opts.get("auto_open"):
        with state_lock:
            out_folder = state["out_folder"]
        if out_folder and os.path.isdir(out_folder):
            try:
                os.startfile(out_folder)
            except Exception:
                pass

    with state_lock:
        state["running"] = False
        state["current_name"] = ""
        state["current_pct"] = 0
        state["eta"] = ""
        state["active_names"] = []
    JOB["log_file"] = ""


def extract_frame(ff, fp, path, t=None, width=720):
    if t is None:
        dur = probe_file(fp, path).get("duration", 0.0) if fp else 0.0
        t = dur / 2 if dur else 0
    try:
        w = max(160, min(4096, int(width)))
    except Exception:
        w = 720
    cmd = [ff, "-ss", str(t), "-i", path, "-frames:v", "1",
           "-vf", "scale=%d:-2" % w, "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "3", "-"]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        if r.returncode == 0 and r.stdout:
            return r.stdout
    except Exception:
        pass
    return None


def _run_metric(ff, first, second, flt, limit):
    """用参考滤镜比较两个视频, 返回 ffmpeg 的 stderr 文本。"""
    cmd = [ff, "-hide_banner"]
    if limit and limit > 0:
        cmd += ["-t", str(limit)]
    cmd += ["-i", first]
    if limit and limit > 0:
        cmd += ["-t", str(limit)]
    cmd += ["-i", second, "-lavfi", flt, "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, timeout=900, **UTF8_KW)
    return (r.stderr or ""), r.returncode


def quality_metrics(ff, src, out, limit=10):
    res = {"ok": False, "ssim": None, "ssim_db": None, "psnr": None, "limit": limit, "err": ""}
    err1, rc1 = _run_metric(ff, out, src, "[0:v][1:v]ssim", limit)
    if rc1 != 0:
        tail = [l for l in err1.strip().splitlines() if l.strip()]
        res["err"] = "SSIM 计算失败: " + (tail[-1][:200] if tail else str(rc1))
        return res
    m = re.search(r"All:\s*([0-9.]+)", err1)
    if m:
        res["ssim"] = float(m.group(1))
    m2 = re.search(r"All:[0-9.]+\s*\(([0-9.]+)\)", err1)
    if m2:
        res["ssim_db"] = float(m2.group(1))

    err2, rc2 = _run_metric(ff, out, src, "[0:v][1:v]psnr", limit)
    if rc2 == 0:
        m3 = re.search(r"average:\s*([0-9.]+|inf)", err2)
        if m3:
            v = m3.group(1)
            res["psnr"] = 99.0 if v == "inf" else float(v)
    res["ok"] = res["ssim"] is not None
    if res["ok"]:
        res["verdict"] = quality_verdict(res["ssim"])
    return res


def quality_verdict(ssim):
    if ssim is None:
        return ""
    if ssim >= 0.995:
        return "肉眼完全无法分辨"
    if ssim >= 0.99:
        return "几乎无差异 (推荐范围)"
    if ssim >= 0.98:
        return "需放大对比才能看出"
    if ssim >= 0.95:
        return "轻微损失, 静态观看不易发现"
    if ssim >= 0.90:
        return "可察觉损失, 建议降低 CRF"
    return "损失明显, 建议降低 CRF 或提高压缩比"


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.handle_api("GET")
        else:
            self._send(200, INDEX_HTML, "text/html; charset=utf-8")

    def do_POST(self):
        self.handle_api("POST")

    def handle_api(self, method):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            payload = {}

        if path == "/api/config":
            ff = find_ffmpeg()
            hw = get_hw(ff)
            vc = get_video_codecs(ff)
            caps = get_filter_names(ff)
            self._send(200, json.dumps({
                "ffmpeg_ok": bool(ff), "ffmpeg_path": ff or "",
                "default_folder": DEFAULT_FOLDER,
                "hw_hevc": hw["hevc"], "hw_h264": hw["h264"], "hw_label": hw["label"],
                "portable": bool(ff and os.path.abspath(ff).startswith(os.path.abspath(BASE_DIR))),
                "logs_dir": LOGS_DIR,
                "cpu_count": os.cpu_count() or 4,
                "version": "v12",
                "schemes_file": SCHEMES_FILE,
                "history_file": HISTORY_FILE,
                "quality_levels": QUALITY_LEVELS,
                "video_codecs": vc,   # {"av1": "libsvtav1", "vp9": "libvpx-vp9"} 仅本机支持的项
                "enhance_caps": {n: (n in caps) for n in ENH_FILTER_NAMES},
                "audio_caps": {n: (n in caps) for n in
                               ("loudnorm", "afftdn", "drawtext", "overlay", "movie", "subtitles")},
                "font_found": bool(find_font()),
            }, ensure_ascii=False))
            return

        if path == "/api/tool":
            action = str(payload.get("action", "") or "")
            src = payload.get("src", "") or ""
            out = payload.get("out", "") or ""
            opts = payload.get("opts", {}) or {}
            ff = find_ffmpeg()
            ext_map = {"gif": ".gif", "clip": os.path.splitext(src or "x.mp4")[1] or ".mp4",
                       "deshake": ".mp4", "rotate": ".mp4", "frame": ".png",
                       "concat": ".mp4"}
            if action == "concat":
                srcs = list(opts.get("sources") or payload.get("sources") or [])
                if not srcs and src:
                    srcs = [x for x in re.split(r"[|;]", src) if x.strip()]
                opts["sources"] = [os.path.abspath(x) for x in srcs if x]
                if not out and opts["sources"]:
                    out = os.path.join(os.path.dirname(opts["sources"][0]), "拼接输出.mp4")
            elif out:
                out = os.path.abspath(out)
            elif src:
                # 未指定输出: 在源文件旁生成「原名_动作」, 与 CLI 行为一致
                stem = os.path.splitext(src)[0]
                out = stem + "_" + action + ext_map.get(action, ".mp4")
            if not out or (action != "concat" and (not src or not os.path.isfile(src))):
                self._send(200, json.dumps({
                    "ok": False, "rc": -1, "lines": ["请填写源文件与输出路径"],
                    "info": {}, "out": "",
                }, ensure_ascii=False))
                return
            rc, lines, info = run_tool(ff, action, src, out, opts)
            self._send(200, json.dumps({
                "ok": rc == 0,
                "rc": rc,
                "lines": lines,
                "info": info,
                "out": out if rc == 0 else "",
            }, ensure_ascii=False))
            return

        if path == "/api/setffmpeg":
            p = payload.get("path", "")
            if os.path.isfile(p):
                USER_FFMPEG["path"] = p
                d = os.path.dirname(p)
                cand = os.path.join(d, "ffprobe.exe")
                if os.path.isfile(cand):
                    USER_FFPROBE["path"] = cand
                HW["probed"] = False
                FILTERS["probed"] = False
                self._send(200, json.dumps({"ok": True, "ffmpeg_ok": True}, ensure_ascii=False))
            else:
                self._send(200, json.dumps({"ok": False, "error": "文件不存在"}, ensure_ascii=False))
            return

        if path == "/api/portable":
            ff = find_ffmpeg()
            fp = find_ffprobe()
            if not ff:
                self._send(200, json.dumps({"ok": False, "error": "未找到 ffmpeg"}, ensure_ascii=False))
                return
            items = []
            try:
                for sp in (ff, fp):
                    if not sp:
                        continue
                    dst = os.path.join(BASE_DIR, os.path.basename(sp))
                    if os.path.abspath(sp) == os.path.abspath(dst):
                        items.append(os.path.basename(dst) + " · 已在本目录")
                        continue
                    if os.path.exists(dst):
                        items.append(os.path.basename(dst) + " · 已存在")
                        continue
                    try:
                        os.link(sp, dst)  # 同盘硬链接: 瞬间完成且不占额外空间
                        items.append(os.path.basename(dst) + " · 硬链接完成(不占额外空间)")
                    except Exception:
                        shutil.copy2(sp, dst)
                        items.append(os.path.basename(dst) + " · 已复制")
                HW["probed"] = False
                FILTERS["probed"] = False
                ff2 = find_ffmpeg()
                self._send(200, json.dumps({"ok": True, "items": items,
                                            "ffmpeg_path": ff2 or ""}, ensure_ascii=False))
            except Exception as e:
                self._send(200, json.dumps({"ok": False, "error": str(e), "items": items}, ensure_ascii=False))
            return

        if path == "/api/pickfolder":
            ok, out = False, ""
            try:
                ps = ("Add-Type -AssemblyName System.Windows.Forms;"
                      "$f=New-Object System.Windows.Forms.FolderBrowserDialog;"
                      "$f.Description='Select video folder';$f.ShowNewFolderButton=$false;"
                      "if($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK){Write-Output $f.SelectedPath}")
                r = subprocess.run(["powershell", "-NoProfile", "-STA", "-Command", ps],
                                   capture_output=True, text=True, errors="replace", timeout=600)
                out = (r.stdout or "").strip()
                ok = bool(out)
            except Exception as e:
                out = str(e)
            self._send(200, json.dumps({"ok": ok, "path": out}, ensure_ascii=False))
            return

        if path == "/api/pickfile":
            """Windows 原生单文件对话框, 返回完整路径 (水印图片/字幕/工具箱源文件用)。"""
            ok, out = False, ""
            try:
                ps = ("Add-Type -AssemblyName System.Windows.Forms;"
                      "$d=New-Object System.Windows.Forms.OpenFileDialog;"
                      "$d.Title='选择文件';$d.CheckFileExists=$true;"
                      "$d.Filter='所有文件|*.*';"
                      "if($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK){Write-Output $d.FileName}")
                r = subprocess.run(["powershell", "-NoProfile", "-STA", "-Command", ps],
                                   capture_output=True, text=True, errors="replace", timeout=600)
                out = (r.stdout or "").strip()
                ok = bool(out)
            except Exception as e:
                out = str(e)
            self._send(200, json.dumps({"ok": ok, "path": out}, ensure_ascii=False))
            return

        if path == "/api/frame":
            p = qs.get("path", [""])[0]
            t = qs.get("t", [None])[0]
            w = qs.get("w", [720])[0]
            try:
                t = float(t) if t not in (None, "") else None
            except Exception:
                t = None
            ff = find_ffmpeg()
            fp = find_ffprobe()
            if not ff or not p or not os.path.isfile(p):
                self._send(404, b"not found", "text/plain")
                return
            img = extract_frame(ff, fp, p, t, w)
            if not img:
                self._send(404, b"frame fail", "text/plain")
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(img)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(img)
            return

        if path == "/api/quality":
            src = qs.get("src", [""])[0] or payload.get("src", "")
            out = qs.get("out", [""])[0] or payload.get("out", "")
            try:
                limit = float(qs.get("limit", [payload.get("limit", 10)])[0])
            except Exception:
                limit = 10
            ff = find_ffmpeg()
            if not ff or not os.path.isfile(src) or not os.path.isfile(out):
                self._send(200, json.dumps({"ok": False, "err": "文件不存在"}, ensure_ascii=False))
                return
            self._send(200, json.dumps(quality_metrics(ff, src, out, limit), ensure_ascii=False))
            return

        if path == "/api/quality/probe":
            """v10 画质目标试算: 抽段试压 3 档 CRF, 返回 SSIM 曲线与推荐 CRF。"""
            p = payload.get("path", "")
            ff, fp = find_ffmpeg(), find_ffprobe()
            if not ff or not p or not os.path.isfile(p):
                self._send(200, json.dumps({"ok": False, "err": "文件不存在或 ffmpeg 未找到"},
                                           ensure_ascii=False))
                return
            try:
                o = make_opts(payload.get("opts") or {})
                # 试压必须与正式编码的刻度一致: 曲线统一用软件编码器拟合
                o["engine"], o["hw"] = "software", None
                target = float(_num(payload.get("quality_target",
                                               o.get("quality_target", 0.99)),
                                    0.80, 0.9999, 0.99))
                vf = build_vf(o, ff=ff)[0]
                dur = probe_file(fp, p).get("duration", 0.0) if fp else 0.0
                tmpdir = tempfile.mkdtemp(prefix="vc_qprobe_")
                try:
                    q = quality_crf(ff, p, o, vf, dur, target, tmpdir)
                finally:
                    shutil.rmtree(tmpdir, ignore_errors=True)
                q["vf"], q["duration"] = vf, dur
                q["level"] = quality_verdict(target)
            except Exception as e:
                q = {"ok": False, "err": str(e), "points": []}
            self._send(200, json.dumps(q, ensure_ascii=False))
            return

        if path == "/api/history":
            """v10 任务历史: 最近任务 + 累计统计, 支持清空 / 导出。"""
            if method == "POST" and payload.get("action") == "clear":
                ok = clear_history()
                self._send(200, json.dumps({"ok": ok, "items": [],
                                            "stats": history_stats([])}, ensure_ascii=False))
                return
            try:
                limit = int(_num(payload.get("limit", 60), 1, 500, 60))
            except Exception:
                limit = 60
            items = load_history(limit)
            self._send(200, json.dumps({"ok": True, "items": items,
                                        "stats": history_stats(items),
                                        "file": HISTORY_FILE}, ensure_ascii=False))
            return

        if path == "/api/enhpreview":
            """同一帧: 左边原帧, 右边套用当前增强参数后的帧。"""
            p = payload.get("path", "")
            ff = find_ffmpeg()
            fp = find_ffprobe()
            if not ff or not p or not os.path.isfile(p):
                self._send(200, json.dumps({"ok": False, "err": "文件不存在或 ffmpeg 未找到"}, ensure_ascii=False))
                return
            popts = payload.get("opts") or {}
            eh = parse_enh(popts)
            # 画幅转换会明显改变画面, 预览里一并体现
            for k in ("aspect", "aspect_mode", "aspect_color", "aspect_blur"):
                if k in popts:
                    eh[k] = popts[k]
            vf, labels, skipped = build_vf(eh, ff=ff, preview=True)
            if payload.get("t") in (None, ""):
                d = probe_file(fp, p).get("duration", 0.0) if fp else 0.0
                t = d / 2 if d else 0.0
            else:
                try:
                    t = max(0.0, float(payload.get("t")))
                except Exception:
                    t = 0.0

            def _one(vfs):
                if vfs.startswith(FC_MARK):
                    args = vf_args(fc_extend(vfs, "scale=720:-2"))
                    cmd = [ff, "-ss", "%.3f" % t, "-i", p, "-frames:v", "1"] + args + \
                          ["-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "3", "-"]
                else:
                    chain = (vfs + ",scale=720:-2") if vfs else "scale=720:-2"
                    cmd = [ff, "-ss", "%.3f" % t, "-i", p, "-frames:v", "1", "-vf", chain,
                           "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "3", "-"]
                try:
                    r = subprocess.run(cmd, capture_output=True, timeout=180)
                    if r.returncode == 0 and r.stdout:
                        return "data:image/jpeg;base64," + base64.b64encode(r.stdout).decode("ascii")
                except Exception:
                    pass
                return ""

            a, b = _one("scale=720:-2"), _one(vf)
            if not a or not b:
                self._send(200, json.dumps({
                    "ok": False, "err": "抽帧失败 (可能时间点超出时长, 或滤镜参数不被支持)",
                    "vf": vf, "labels": labels, "skipped": skipped,
                }, ensure_ascii=False))
                return
            self._send(200, json.dumps({
                "ok": True, "before": a, "after": b, "vf": vf,
                "labels": labels, "skipped": skipped, "t": t,
            }, ensure_ascii=False))
            return

        if path == "/api/analyze":
            """智能分析: 采样检测黑边/隔行/亮度/饱和度/运动量, 返回可解释的推荐参数。"""
            p = qs.get("path", [""])[0] or payload.get("path", "")
            if not p or not os.path.isfile(p):
                self._send(200, json.dumps({"ok": False, "err": "文件不存在"}, ensure_ascii=False))
                return
            try:
                r = analyze_media(find_ffmpeg(), find_ffprobe(), p,
                                  samples=int(_num(qs.get("samples", ["3"])[0], 1, 3, 3)))
            except Exception as e:
                r = {"ok": False, "err": str(e)}
            self._send(200, json.dumps(r, ensure_ascii=False))
            return

        if path == "/api/analyze/batch":
            """批量分析 (最多 3 并发), 用于「分析整个队列」。"""
            paths = [x for x in (payload.get("paths") or []) if x and os.path.isfile(x)]
            ff, fp = find_ffmpeg(), find_ffprobe()
            out = [None] * len(paths)

            def _one(i):
                try:
                    return i, analyze_media(ff, fp, paths[i], samples=2)
                except Exception as e:
                    return i, {"ok": False, "err": str(e), "path": paths[i]}

            if paths:
                with ThreadPoolExecutor(max_workers=min(3, len(paths))) as ex:
                    for i, r in ex.map(_one, range(len(paths))):
                        r["path"] = paths[i]
                        r["name"] = os.path.basename(paths[i])
                        out[i] = r
            self._send(200, json.dumps({"ok": True, "items": out}, ensure_ascii=False))
            return

        if path == "/api/schemes":
            schemes = load_schemes()
            if method == "POST" and payload.get("action") in ("save", "delete"):
                name = str(payload.get("name", "") or "").strip()[:40]
                if not name:
                    self._send(200, json.dumps({"ok": False, "error": "方案名不能为空"}, ensure_ascii=False))
                    return
                if payload["action"] == "delete":
                    schemes.pop(name, None)
                else:
                    schemes[name] = {"settings": payload.get("settings") or {},
                                     "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")}
                ok = save_schemes(schemes)
                self._send(200, json.dumps({"ok": ok, "schemes": schemes,
                                            "error": "" if ok else "方案文件写入失败"}, ensure_ascii=False))
                return
            self._send(200, json.dumps({"ok": True, "schemes": schemes,
                                        "file": SCHEMES_FILE}, ensure_ascii=False))
            return

        if path == "/api/queue/import":
            """导入队列 JSON 里的绝对路径: 逐个校验存在性并重新探测媒体信息。"""
            fp = find_ffprobe()
            items, missing = [], []
            for p in (payload.get("files") or []):
                if not isinstance(p, str) or not os.path.isfile(p):
                    missing.append(str(p))
                    continue
                if not _is_video(os.path.basename(p)):
                    continue
                i = probe_streams(fp, p)
                items.append({"path": os.path.abspath(p), "name": os.path.basename(p),
                              "size": i.get("size", 0) or os.path.getsize(p),
                              "duration": i.get("duration", 0),
                              "width": i.get("width", 0), "height": i.get("height", 0),
                              "codec": i.get("codec", ""), "audio": i.get("audio", 0),
                              "subtitle": i.get("subtitle", 0),
                              "fps": i.get("fps", 0), "bitrate": i.get("bitrate", 0)})
            self._send(200, json.dumps({"ok": True, "files": items,
                                        "missing": missing}, ensure_ascii=False))
            return

        if path == "/api/verify":
            """对已完成的结果手动复验一次 (前端结果表校验列可点开)。"""
            src = payload.get("src", "")
            out = payload.get("out", "")
            if not os.path.isfile(out):
                self._send(200, json.dumps({"ok": False, "err": "输出文件不存在"}, ensure_ascii=False))
                return
            lv = payload.get("level", "quick")
            lv = lv if lv in ("off", "quick", "full") else "quick"
            r = verify_output(find_ffmpeg(), find_ffprobe(), src, out,
                              probe_streams(find_ffprobe(), src), lv, make_opts(payload.get("opts") or {}))
            self._send(200, json.dumps(r, ensure_ascii=False))
            return

        if path == "/api/probe":
            """单文件完整流信息, 用于「压缩前后参数对比」弹窗。"""
            p = qs.get("path", [""])[0] or payload.get("path", "")
            if not p or not os.path.isfile(p):
                self._send(200, json.dumps({"ok": False, "err": "文件不存在"}, ensure_ascii=False))
                return
            self._send(200, json.dumps({"ok": True, "info": probe_streams(find_ffprobe(), p)},
                                       ensure_ascii=False))
            return

        if path == "/api/disk":
            """查询若干目录所在磁盘的可用空间, 界面上实时显示。"""
            out = []
            for d in (payload.get("dirs") or []):
                q = os.path.abspath(d)
                while not os.path.isdir(q) and os.path.dirname(q) != q:
                    q = os.path.dirname(q)
                try:
                    du = shutil.disk_usage(q)
                    out.append({"dir": d, "free": du.free, "total": du.total,
                                "used_pct": round(du.used / du.total * 100, 1) if du.total else 0})
                except Exception as e:
                    out.append({"dir": d, "err": str(e)})
            self._send(200, json.dumps({"ok": True, "disks": out}, ensure_ascii=False))
            return

        if path == "/api/pickfiles":
            """Windows 原生多选文件对话框, 返回完整路径 (浏览器 file input 拿不到绝对路径)。"""
            ps = ("Add-Type -AssemblyName System.Windows.Forms;"
                  "$d=New-Object System.Windows.Forms.OpenFileDialog;"
                  "$d.Multiselect=$true;$d.Title='选择视频文件';"
                  "$d.Filter='视频文件|*.mp4;*.mkv;*.mov;*.avi;*.webm;*.flv;*.wmv;*.m4v;*.ts|所有文件|*.*';"
                  "if($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK){"
                  "foreach($f in $d.FileNames){Write-Output $f}}")
            paths = []
            try:
                r = subprocess.run(["powershell", "-NoProfile", "-STA", "-Command", ps],
                                   capture_output=True, text=True, errors="replace", timeout=600)
                paths = [x.strip() for x in (r.stdout or "").splitlines() if x.strip()]
            except Exception:
                pass
            fp = find_ffprobe()
            items = []
            for p in paths:
                if not os.path.isfile(p):
                    continue
                i = probe_streams(fp, p)
                items.append({"path": os.path.abspath(p), "name": os.path.basename(p),
                              "size": i.get("size", 0), "duration": i.get("duration", 0),
                              "width": i.get("width", 0), "height": i.get("height", 0),
                              "codec": i.get("codec", ""), "audio": i.get("audio", 0),
                              "subtitle": i.get("subtitle", 0)})
            self._send(200, json.dumps({"ok": bool(items), "files": items}, ensure_ascii=False))
            return

        if path == "/api/scan":
            folder = payload.get("folder", "")
            recursive = bool(payload.get("recursive", False))
            out_sub = payload.get("out_sub", "已压缩")
            ff = find_ffmpeg()
            fp = find_ffprobe()
            out_dir = os.path.abspath(os.path.join(folder, out_sub)) if folder else None
            files = list_videos(folder, recursive, exclude_dir=out_dir)
            items = []
            for f in files:
                info = probe_streams(fp, f) if fp else {}
                items.append({
                    "path": os.path.abspath(f),
                    "name": os.path.basename(f), "size": os.path.getsize(f),
                    "duration": info.get("duration", 0),
                    "width": info.get("width", 0), "height": info.get("height", 0),
                    "codec": info.get("codec", ""),
                    "audio": info.get("audio", 0), "subtitle": info.get("subtitle", 0),
                    "fps": info.get("fps", 0), "bitrate": info.get("bitrate", 0),
                })
            self._send(200, json.dumps({
                "ffmpeg_ok": bool(ff), "files": items,
                "total_size": sum(i["size"] for i in items), "count": len(items),
            }, ensure_ascii=False))
            return

        if path == "/api/start":
            with state_lock:
                if state["running"]:
                    self._send(200, json.dumps({"ok": False, "error": "已有任务在运行"}, ensure_ascii=False))
                    return
            files = payload.get("files") or []
            if not files:
                folder = payload.get("folder", "")
                recursive = bool(payload.get("recursive", False))
                files = list_videos(folder, recursive)
            out_mode = payload.get("out_mode", "sub")
            out_sub = payload.get("out_sub", "已压缩")
            force = bool(payload.get("force", False))
            if not _bool(payload.get("ignore_disk", False)):
                dk = check_disk(files, out_mode, out_sub)
                if not dk["ok"]:
                    worst = min(dk["checks"], key=lambda x: x["free"] - x["need"])
                    msg = ("磁盘空间可能不足: %s 可用 %.1fGB, 预计需要 %.1fGB。"
                           "建议清理空间或更换输出目录。"
                           % (worst["dir"], worst["free"] / 1073741824,
                              worst["need"] / 1073741824))
                    self._send(200, json.dumps({"ok": False, "error": msg, "disk": dk},
                                               ensure_ascii=False))
                    return
            opts = make_opts(payload)
            ov = payload.get("overrides") or {}
            t = threading.Thread(target=run_job,
                                 args=(files, opts, out_mode, out_sub, force, ov), daemon=True)
            t.start()
            self._send(200, json.dumps({"ok": True}, ensure_ascii=False))
            return

        if path == "/api/stop":
            with state_lock:
                state["stop"] = True
            self._send(200, json.dumps({"ok": True}, ensure_ascii=False))
            return

        if path == "/api/openoutput":
            p = payload.get("path", "")
            ok = False
            try:
                if p and os.path.isdir(p):
                    os.startfile(p)
                    ok = True
            except Exception:
                pass
            self._send(200, json.dumps({"ok": ok}, ensure_ascii=False))
            return

        if path == "/api/openlogs":
            ok = False
            try:
                os.makedirs(LOGS_DIR, exist_ok=True)
                os.startfile(LOGS_DIR)
                ok = True
            except Exception:
                pass
            self._send(200, json.dumps({"ok": ok}, ensure_ascii=False))
            return

        if path == "/api/export":
            with state_lock:
                res = list(state["results"])
            lines = ["文件名,原大小(字节),压缩后(字节),比例(%),节省(%),状态,输出路径"]
            tb = ta = 0
            for r in res:
                tb += r["before"]
                ta += r["after"]
                save = round(100 - r["pct"], 1) if r["pct"] else ""
                nm = str(r["name"]).replace('"', '""')
                op = str(r.get("out", "")).replace('"', '""')
                lines.append(f'"{nm}",{r["before"]},{r["after"]},{r["pct"]},{save},"{r["status"]}","{op}"')
            tp = round(ta / tb * 100, 1) if tb else ""
            ts = round(100 - ta / tb * 100, 1) if tb else ""
            lines.append(f'"合计",{tb},{ta},{tp},{ts},"",""')
            data = ("\ufeff" + "\n".join(lines)).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=compress_report.csv")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path == "/api/status":
            with state_lock:
                snap = dict(state)
            eta = ""
            speed = 0.0
            elapsed = time.time() - snap["job_start"] if snap["job_start"] > 0 else 0
            # 并行时用「等效已处理时长」(各文件进度加权) 算 ETA, 比只看已完成文件准得多
            eff = snap.get("effective_dur", snap["processed_dur"])
            if elapsed > 0.2:
                speed = eff / elapsed
            snap["speed"] = round(speed, 2)
            if snap["running"] and snap["total_duration"] > 0 and speed > 0.01:
                remain_s = max(0.0, snap["total_duration"] - eff) / speed
                eta = f"约 {int(remain_s//60)}分{int(remain_s%60)}秒"
            snap["eta"] = eta
            self._send(200, json.dumps(snap, ensure_ascii=False))
            return

        self._send(404, json.dumps({"error": "not found"}, ensure_ascii=False))

    def log_message(self, *args):
        pass


INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>视频压缩工具</title>
<style>
  * { box-sizing: border-box; }
  body { margin:0; font-family: -apple-system,"Microsoft YaHei",sans-serif; background:#f4f6fb; color:#1f2533; }
  .wrap { max-width: 1020px; margin: 0 auto; padding: 20px; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  .sub { color:#7a8499; font-size:13px; margin-bottom:16px; }
  .card { background:#fff; border-radius:12px; padding:18px; box-shadow:0 2px 10px rgba(20,30,60,.06); margin-bottom:16px; }
  label { font-size:13px; font-weight:600; display:block; margin:12px 0 6px; }
  input[type=text], input[type=number], select { width:100%; padding:9px 10px; border:1px solid #d7dce8; border-radius:8px; font-size:14px; background:#fff; }
  .row { display:flex; gap:12px; flex-wrap:wrap; }
  .row > div { flex:1; min-width:170px; }
  .folder-row { display:flex; gap:8px; }
  .folder-row input { flex:1; }
  button { cursor:pointer; border:none; border-radius:8px; padding:10px 18px; font-size:14px; font-weight:600; }
  .btn-primary { background:#3b6cff; color:#fff; }
  .btn-primary:disabled { background:#aab8e0; cursor:not-allowed; }
  .btn-ghost { background:#eef1f8; color:#3b6cff; }
  .btn-danger { background:#ffe3e3; color:#d23b3b; }
  .btn-mini { padding:5px 10px; font-size:12px; border-radius:6px; background:#eef1f8; color:#3b6cff; font-weight:600; }
  .btn-mini:disabled { opacity:.5; cursor:not-allowed; }
  input[type=range] { width:100%; }
  .crfval { font-weight:700; color:#3b6cff; }
  .chk { display:flex; align-items:center; gap:8px; font-size:13px; font-weight:500; margin-top:12px; }
  .bar { height:14px; background:#e9edf6; border-radius:8px; overflow:hidden; margin-top:6px; }
  .bar > i { display:block; height:100%; width:0; background:linear-gradient(90deg,#3b6cff,#5b8bff); transition:width .3s; }
  .status-line { font-size:13px; color:#555; margin-top:8px; min-height:18px; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th,td { text-align:left; padding:7px 8px; border-bottom:1px solid #eef1f8; }
  th { color:#7a8499; font-weight:600; }
  .ok { color:#1a9e55; } .bad { color:#d23b3b; }
  #log { background:#0f1422; color:#cfe3ff; font-family:Consolas,monospace; font-size:12px; padding:10px; border-radius:8px; height:160px; overflow:auto; white-space:pre-wrap; }
  .ffwarn { color:#d23b3b; font-size:13px; display:none; }
  .pill { display:inline-block; background:#eef1f8; border-radius:20px; padding:2px 10px; font-size:12px; color:#3b6cff; margin-left:6px;}
  .hint { font-size:12px; color:#7a8499; }
  .hide { display:none; }
  .qbar { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin:10px 0; font-size:13px; color:#555; }
  .qtable-wrap { max-height:260px; overflow:auto; border:1px solid #eef1f8; border-radius:8px; }
  .qtable-wrap table { font-size:12px; }
  .modal { position:fixed; inset:0; background:rgba(10,15,30,.72); display:none; align-items:center; justify-content:center; z-index:50; }
  .modal-box { background:#fff; border-radius:12px; padding:14px; max-width:96vw; max-height:94vh; overflow:auto; }
  .cmp-grid { display:flex; gap:12px; }
  .cmp-grid figure { margin:0; }
  .cmp-grid img { max-width:46vw; max-height:70vh; border-radius:8px; background:#eee; display:block; }
  .cmp-grid figcaption { font-size:12px; color:#555; margin-top:6px; text-align:center; }
  /* v12: A/B 滑动对比台 (擦除式) */
  .cmp-stage { position:relative; overflow:hidden; border-radius:8px; background:#10141d;
    user-select:none; -webkit-user-select:none; touch-action:none; cursor:ew-resize; }
  .cmp-stage > img { display:block; width:100%; }
  .cmp-clip { position:absolute; top:0; bottom:0; right:0; left:50%; overflow:hidden; }
  .cmp-clip img { position:absolute; top:0; left:0; height:100%; width:auto; max-width:none; display:block; }
  .cmp-handle { position:absolute; top:0; bottom:0; left:50%; width:2px; margin-left:-1px;
    background:#fff; box-shadow:0 0 8px rgba(0,0,0,.65); pointer-events:none; }
  .cmp-handle::after { content:''; position:absolute; top:50%; left:50%; width:26px; height:26px;
    margin:-13px 0 0 -13px; border-radius:50%; background:rgba(255,255,255,.92);
    box-shadow:0 2px 8px rgba(0,0,0,.5); }
  .cmp-tag { position:absolute; top:8px; font-size:12px; background:rgba(0,0,0,.55);
    color:#fff; padding:2px 9px; border-radius:10px; pointer-events:none; }
  .cmp-tag-l { left:8px; } .cmp-tag-r { right:8px; }
  .presets { display:flex; gap:8px; flex-wrap:wrap; }
  .preset { flex:1; min-width:150px; background:#eef1f8; color:#3b6cff; border-radius:10px; padding:9px 11px; font-size:13px; text-align:left; line-height:1.35; }
  .preset span { display:block; font-size:11px; color:#7a8499; font-weight:500; margin-top:3px; }
  .preset.active { background:#3b6cff; color:#fff; }
  .preset.active span { color:#dbe5ff; }
  .qm-big { font-size:15px; }
  .qm-big b { font-size:26px; color:#3b6cff; }
  .qm-row { display:flex; gap:24px; margin:10px 0 6px; }
  .qm-row > div { flex:1; background:#f7f9ff; border-radius:10px; padding:12px 14px; }
  .qm-lbl { font-size:12px; color:#7a8499; }
  .toolbar { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin:12px 0 4px; }
  .sumline { font-size:13px; font-weight:600; color:#3b6cff; }
  .epill { display:inline-block; background:#f2eefe; color:#7a52d8; border-radius:20px; padding:2px 10px; font-size:12px; margin-left:6px; }
  .epreset { flex:1; min-width:150px; background:#f2eefe; color:#6f45d6; border-radius:10px; padding:9px 11px; font-size:13px; text-align:left; line-height:1.35; }
  .epreset span { display:block; font-size:11px; color:#8a80a8; font-weight:500; margin-top:3px; }
  .epreset.active { background:#7a52d8; color:#fff; }
  .epreset.active span { color:#e8ddff; }
  .enh-off { opacity:.45; pointer-events:none; }
  .enh-note { background:#f8f5ff; border:1px solid #e7dcff; border-radius:8px; padding:9px 11px; font-size:12px; color:#5d5380; margin-top:10px; word-break:break-all; }
  .slider-row { display:flex; gap:12px; flex-wrap:wrap; }
  .slider-row > div { flex:1; min-width:155px; }
  .slider-row .v { float:right; font-weight:700; color:#7a52d8; }
  .enh-accent { border-left:4px solid #7a52d8; }
  .spd-accent { border-left:4px solid #00a88f; }
  .spd-note { background:#effbf8; border:1px solid #c9efe7; border-radius:8px; padding:9px 11px; font-size:12px; color:#256b60; margin-top:10px; }
  .spd-pill { display:inline-block; background:#e3f8f3; color:#008f78; border-radius:20px; padding:2px 10px; font-size:12px; }
  .preset.turbo { background:#fff1e2; color:#d9751a; }
  .preset.turbo span { color:#b8895c; }
  .preset.turbo.active { background:#e8801c; color:#fff; }
  .preset.turbo.active span { color:#ffe6c9; }
  /* ---- v8 ---- */
  .v8-accent { border-left:4px solid #2f7de1; }
  .v8-pill { display:inline-block; background:#e8f1ff; color:#2563c9; border-radius:20px; padding:2px 10px; font-size:12px; }
  .v8-note { background:#f2f7ff; border:1px solid #d8e6ff; border-radius:8px; padding:9px 11px; font-size:12px; color:#31517d; margin-top:10px; line-height:1.6; }
  .info-tbl { width:100%; font-size:13px; border-collapse:collapse; }
  .info-tbl th, .info-tbl td { padding:7px 10px; border-bottom:1px solid #eef1f8; text-align:left; }
  .info-tbl thead th { color:#7a8499; font-weight:600; }
  .info-tbl tbody th { width:26%; color:#7a8499; font-weight:600; }
  .theme-btn { position:fixed; top:16px; right:18px; z-index:60; background:#eef1f8; color:#3b6cff; padding:7px 13px; font-size:12px; box-shadow:0 2px 8px rgba(20,30,60,.12); }
  .linkish { cursor:pointer; text-decoration:underline dotted #9aa6c0; }
  /* 深色主题: 只覆盖配色, 不改布局 */
  body[data-theme=dark] { background:#12151d; color:#e4e9f4; }
  body[data-theme=dark] .sub, body[data-theme=dark] .hint, body[data-theme=dark] th,
  body[data-theme=dark] .qm-lbl, body[data-theme=dark] .info-tbl tbody th { color:#98a3ba; }
  body[data-theme=dark] .card { background:#1b2130; box-shadow:0 2px 12px rgba(0,0,0,.35); }
  body[data-theme=dark] input[type=text], body[data-theme=dark] input[type=number],
  body[data-theme=dark] select { background:#232b3d; color:#e4e9f4; border-color:#39435a; }
  body[data-theme=dark] .btn-ghost, body[data-theme=dark] .btn-mini,
  body[data-theme=dark] .preset, body[data-theme=dark] .pill,
  body[data-theme=dark] .theme-btn { background:#2a3348; color:#a9c4ff; }
  body[data-theme=dark] .preset span, body[data-theme=dark] .preset.turbo span,
  body[data-theme=dark] .epreset span { color:#98a3ba; }
  body[data-theme=dark] .bar, body[data-theme=dark] .diskbar { background:#2a3348; }
  body[data-theme=dark] th, body[data-theme=dark] td { border-bottom-color:#2a3348; }
  body[data-theme=dark] .qtable-wrap { border-color:#2a3348; }
  body[data-theme=dark] .spd-note { background:#16302c; border-color:#245248; color:#9fd9c9; }
  body[data-theme=dark] .enh-note { background:#262138; border-color:#3a3058; color:#c3b4e8; }
  body[data-theme=dark] .v8-note { background:#1a2942; border-color:#2c4670; color:#a9c4e8; }
  body[data-theme=dark] .qm-row > div { background:#232b3d; }
  body[data-theme=dark] .modal-box { background:#1b2130; color:#e4e9f4; }
  body[data-theme=dark] .status-line, body[data-theme=dark] .cmp-grid figcaption { color:#c4ccdb; }
  body[data-theme=dark] .epreset { background:#262138; color:#c3b4e8; }
  body[data-theme=dark] .preset.turbo { background:#3a2a1c; color:#f0b478; }
  body[data-theme=dark] .preset.active, body[data-theme=dark] .preset.turbo.active { background:#3b6cff; color:#fff; }
  body[data-theme=dark] .epreset.active { background:#7a52d8; color:#fff; }
  body[data-theme=dark] .preset.turbo.active { background:#e8801c; }
  body[data-theme=dark] .btn-danger { background:#4a2430; color:#ff9a9a; }
  body[data-theme=dark] .ffwarn, body[data-theme=dark] .bad { color:#ff9a9a; }
  body[data-theme=dark] .ok { color:#57d99a; }
  body[data-theme=dark] .cmp-grid img { background:#232b3d; }
  body[data-theme=dark] .sumline, body[data-theme=dark] .crfval { color:#8ab0ff; }
  /* ---- v9: 智能分析 / 自动化 ---- */
  .v9-accent { border-left:4px solid #d97706; }
  .v9-pill { display:inline-block; background:#fff0dc; color:#b45309; border-radius:20px; padding:2px 10px; font-size:12px; }
  .v9-note { background:#fff8ed; border:1px solid #f6dfb8; border-radius:8px; padding:9px 11px; font-size:12px; color:#7a5218; margin-top:10px; line-height:1.65; }
  .v9-sep { height:1px; background:#eef1f8; margin:14px 0 6px; }
  .an-tbl { width:100%; font-size:12px; border-collapse:collapse; margin-top:6px; }
  .an-tbl th, .an-tbl td { padding:5px 8px; border-bottom:1px solid #eef1f8; text-align:left; }
  .an-tbl thead th { color:#7a8499; font-weight:600; }
  .an-badge { display:inline-block; background:#fff0dc; color:#b45309; border-radius:6px; padding:1px 7px; margin:2px 4px 2px 0; font-size:11px; }
  .vchk { cursor:pointer; text-decoration:underline dotted #9aa6c0; }
  body[data-theme=dark] .v9-note { background:#332715; border-color:#54401f; color:#e2c48d; }
  body[data-theme=dark] .v9-pill { background:#3b2c16; color:#f0b96a; }
  body[data-theme=dark] .v9-sep, body[data-theme=dark] .an-tbl th,
  body[data-theme=dark] .an-tbl td { border-color:#2a3348; }
  body[data-theme=dark] .an-badge { background:#3b2c16; color:#f0b96a; }
  /* ---- v10: 画质目标 / 逐文件微调 / 历史统计 ---- */
  .v10-accent { border-left:4px solid #7c3aed; }
  .v10-pill { display:inline-block; background:#f1e9ff; color:#6d28d9; border-radius:20px; padding:2px 10px; font-size:12px; }
  .v11-accent { border-left:4px solid #d946a6; }
  .wm-accent { border-left:4px solid #0ea5a4; }
  .tb-accent { border-left:4px solid #f59e0b; }
  .v11-pill { display:inline-block; background:#fde7f4; color:#be185d; border-radius:20px; padding:2px 10px; font-size:12px; }
  .v12-accent { border-left:4px solid #0891b2; }
  .v12-pill { display:inline-block; background:#e0f2fe; color:#0e7490; border-radius:20px; padding:2px 10px; font-size:12px; }
  .v10-note { background:#f8f5ff; border:1px solid #e6d9ff; border-radius:8px; padding:9px 11px; font-size:12px; color:#4c3b7a; margin-top:10px; line-height:1.65; }
  .v10-sep { height:1px; background:#eef1f8; margin:14px 0 6px; }
  .ov-badge { display:inline-block; background:#ede4ff; color:#6d28d9; border-radius:6px; padding:1px 7px; font-size:11px; }
  .hist-kpis { display:flex; gap:10px; flex-wrap:wrap; margin-top:8px; }
  .hist-kpi { flex:1; min-width:120px; background:#f7f5ff; border-radius:9px; padding:9px 11px; }
  .hist-kpi b { display:block; font-size:19px; color:#6d28d9; margin-top:3px; }
  .hist-kpi span { font-size:11px; color:#7a8499; }
  .hist-bars { display:flex; align-items:flex-end; gap:5px; height:56px; margin:10px 0 4px; }
  .hist-bar { width:16px; min-height:2px; background:linear-gradient(180deg,#8b5cf6,#c4b5fd); border-radius:3px 3px 0 0; }
  body[data-theme=dark] .v10-note, body[data-theme=dark] .hist-kpi { background:#281f3d; border-color:#473368; color:#cbb6f5; }
  body[data-theme=dark] .v10-pill, body[data-theme=dark] .ov-badge { background:#332247; color:#d8b4fe; }
  body[data-theme=dark] .v11-pill { background:#3a1f33; color:#f0a8d4; }
  body[data-theme=dark] .v12-pill { background:#123a4a; color:#7dd3fc; }
  body[data-theme=dark] .v10-sep { background:#2a3348; }
  body[data-theme=dark] .hist-kpi b { color:#c4b5fd; }
</style>
</head>
<body>
<button class="btn-ghost theme-btn" id="themeBtn">切换深色</button>
<div class="wrap">
  <h1>视频压缩工具 <span class="pill">v12 · 竖屏画幅 · AB对比 · 文件名模板 · 视频拼接</span></h1>
  <div class="sub">可按目标 SSIM 自动挑最省体积的 CRF、给单个视频单独调参、查看历史压缩成效, 编码失败还会自动降级重试。建议输出到子文件夹, 原文件保留。</div>

  <div class="card">
    <label>添加视频文件夹 (可添加多个文件夹, 累加到待处理列表)</label>
    <div class="folder-row">
      <input type="text" id="folder" placeholder="选择或输入文件夹路径">
      <button class="btn-ghost" id="pick">选择文件夹</button>
      <button class="btn-ghost" id="pickfiles">添加文件</button>
      <button class="btn-primary" id="scan">扫描加入</button>
    </div>
    <div class="chk"><input type="checkbox" id="recursive"><label style="margin:0;font-weight:500" for="recursive">包含子文件夹</label></div>

    <div class="qbar">
      <span id="qsummary">待处理列表为空</span>
      <span id="diskInfo" class="hint"></span>
      <span style="flex:1"></span>
      <button class="btn-mini" id="selall">全选</button>
      <button class="btn-mini" id="selnone">全不选</button>
      <button class="btn-mini" id="qclear">清空列表</button>
    </div>
    <div class="qtable-wrap" id="qwrap" style="display:none">
      <table>
        <thead><tr><th style="width:34px"></th><th>文件</th><th>分辨率</th><th>流</th><th>时长</th><th>原大小</th><th>预估压缩后</th><th style="width:56px">微调</th><th style="width:60px"></th></tr></thead>
        <tbody id="qbody"></tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <label>快速预设 (一键套用推荐参数)</label>
    <div class="presets" id="presets">
      <button class="preset" data-p="wallpaper">壁纸极省<span>H.265・10bit・去音轨・CRF26</span></button>
      <button class="preset" data-p="balanced">平衡<span>H.265・10bit・AAC・CRF24</span></button>
      <button class="preset" data-p="quality">高画质<span>H.265・10bit・原音轨・CRF20</span></button>
      <button class="preset" data-p="compat">兼容优先<span>H.264・8bit・通用・CRF22</span></button>
      <button class="preset turbo" data-p="turbo">极速方案<span>veryfast・8bit・自动硬件・直传・2并发</span></button>
    </div>

    <div class="row" style="margin-top:6px">
      <div>
        <label>压缩模式</label>
        <select id="mode">
          <option value="crf">画质优先 (CRF, 推荐)</option>
          <option value="quality">画质目标 (按 SSIM 自动挑最小体积 CRF, v10)</option>
          <option value="smart">智能体积 (精准命中 MB, 只编码一遍)</option>
          <option value="ratio">目标压缩比 (压缩到原来的百分之几)</option>
          <option value="size">目标体积 (两遍编码, 固定码率)</option>
        </select>
      </div>
      <div id="ratioWrap" class="hide">
        <label>目标压缩比 (%)</label>
        <input type="number" id="ratio_pct" value="30" min="5" max="95" step="5">
      </div>
      <div id="sizeWrap" class="hide">
        <label id="sizeLbl">目标体积 (MB)</label>
        <input type="number" id="target_mb" value="50" min="5" step="5">
      </div>
      <div id="crfWrap">
        <label>画质 CRF (越小质量越高、体积越大)</label>
        <input type="range" id="crf" min="16" max="32" value="24" step="1">
        <div>当前: <span class="crfval" id="crfval">24</span> <span class="hint">(20-24 接近无损)</span></div>
      </div>
      <div id="qualityWrap" class="hide">
        <label>画质目标 SSIM (越接近 1 越像原片)</label>
        <select id="quality_preset">
          <option value="lossless">视觉无损 · 0.995</option>
          <option value="high" selected>高画质 · 0.990 (推荐)</option>
          <option value="balanced">均衡 · 0.980</option>
          <option value="compact">小体积 · 0.950</option>
          <option value="custom">自定义数值…</option>
        </select>
        <input type="number" id="quality_target" value="0.990" min="0.80" max="0.9999" step="0.001" style="margin-top:6px">
      </div>
    </div>

    <div class="row">
      <div>
        <label>编码格式</label>
        <select id="codec">
          <option value="hevc">H.265 / HEVC (压缩率最高, 推荐)</option>
          <option value="h264">H.264 (兼容性最好)</option>
        </select>
      </div>
      <div>
        <label>编码引擎</label>
        <select id="engine"></select>
      </div>
      <div>
        <label>色彩深度</label>
        <select id="pix">
          <option value="10">10-bit (动画更干净/更小, H.265 推荐)</option>
          <option value="8">8-bit (兼容性最好)</option>
        </select>
      </div>
      <div>
        <label>音轨</label>
        <select id="audio">
          <option value="reencode">保留并重编码 AAC 128k</option>
          <option value="copy">原样复制 (无损)</option>
          <option value="strip">移除音轨 (壁纸推荐, 更省空间)</option>
        </select>
      </div>
    </div>

    <div class="row audio-adv hide" id="audioAdv">
      <div>
        <label>音量归一化</label>
        <select id="audio_normalize">
          <option value="off">关闭</option>
          <option value="-14">-14 LUFS (流媒体/youtube)</option>
          <option value="-16">-16 LUFS (语音/播客)</option>
        </select>
      </div>
      <div>
        <label>音频降噪</label>
        <select id="audio_denoise">
          <option value="off">关闭</option>
          <option value="light">轻度</option>
          <option value="strong">强力</option>
        </select>
      </div>
      <div>
        <label>音频码率 (kbps)</label>
        <input type="number" id="audio_bitrate" value="128" min="32" max="512" step="16">
      </div>
      <div>
        <label>采样率 (Hz, 0=保持)</label>
        <input type="number" id="audio_samplerate" value="0" min="0" step="1000">
      </div>
      <div>
        <label>声道 (0=保持)</label>
        <input type="number" id="audio_channels" value="0" min="0" max="8" step="1">
      </div>
    </div>
    <div class="hint audio-adv hide" id="audioAdvHint" style="margin:-4px 0 6px">
      归一化 / 降噪需要重编码音频, 仅在「保留并重编码」时生效。
    </div>
    <div class="hint" id="codecNote" style="display:none;margin:2px 0 6px"></div>

    <div class="row">
      <div>
        <label>预设 (压缩速度/效率)</label>
        <select id="preset">
          <option value="ultrafast">ultrafast</option><option value="superfast">superfast</option>
          <option value="veryfast">veryfast</option><option value="faster">faster</option>
          <option value="fast" selected>fast (推荐, 速度与画质平衡)</option><option value="medium">medium</option>
          <option value="slow">slow</option><option value="slower">slower</option>
          <option value="veryslow">veryslow</option>
        </select>
      </div>
      <div>
        <label>内容类型优化</label>
        <select id="tune">
          <option value="animation">动画/二次元 (推荐)</option>
          <option value="none">通用</option>
          <option value="film">电影/实拍</option>
          <option value="grain">保留颗粒感</option>
        </select>
      </div>
      <div>
        <label>输出方式</label>
        <select id="out_mode">
          <option value="sub">新建子文件夹 (推荐, 保留原文件)</option>
          <option value="overwrite">覆盖原文件 (不可恢复)</option>
        </select>
      </div>
      <div>
        <label>子文件夹名</label>
        <input type="text" id="out_sub" value="已压缩">
      </div>
    </div>
    <div class="chk"><input type="checkbox" id="force"><label style="margin:0;font-weight:500" for="force">强制重编码 (忽略已存在的输出)</label></div>

    <div class="row" style="margin-top:8px;align-items:flex-end">
      <div style="flex:1;min-width:280px">
        <label>输出文件名模板 <span class="v12-pill">v12</span></label>
        <input type="text" id="name_template" placeholder="留空=保持原文件名 (仅输出到子文件夹时生效)">
      </div>
    </div>
    <div class="hint" id="tplHint" style="margin-top:4px">
      可用变量: {name} 原名 · {crf} · {size} 目标MB · {codec} · {mode} · {aspect} · {date} · {time} · {index} · {ext}
      <br>例: <b>{date}_{index}_{name}_c{crf}</b> → 20261108_001_我的视频_c26.mp4
    </div>

    <div class="ffwarn" id="ffwarn">未找到 ffmpeg! 请在下方指定 ffmpeg.exe 路径。</div>
    <div style="margin-top:14px; display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
      <button class="btn-primary" id="start">开始压缩</button>
      <button class="btn-danger" id="stop" style="display:none">中止</button>
      <button class="btn-ghost" id="openout" style="display:none">打开输出文件夹</button>
      <button class="btn-ghost" id="export" style="display:none">导出报告(CSV)</button>
      <span id="ffpath" style="font-size:12px;color:#7a8499"></span>
    </div>
    <div style="margin-top:10px; display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
      <input type="text" id="ffset" placeholder="若未自动找到, 在此粘贴 ffmpeg.exe 路径后点设置" style="flex:1;min-width:260px">
      <button class="btn-ghost" id="ffsetbtn">设置 ffmpeg</button>
      <button class="btn-ghost" id="portablebtn">制作便携版</button>
      <span id="ptext" class="hint"></span>
    </div>
  </div>

  <div class="card spd-accent" id="speedCard">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <label style="margin:0;font-size:15px">速度与保护 <span class="spd-pill">v7 新增</span></label>
      <span style="flex:1"></span>
      <span class="hint" id="cpuHint"></span>
    </div>

    <div class="row" style="margin-top:6px">
      <div>
        <label>并行任务数 (批量短视频提速最明显)</label>
        <select id="workers">
          <option value="1">1 · 串行 (最省资源)</option>
          <option value="2" selected>2 · 推荐</option>
          <option value="3">3 · 激进</option>
          <option value="4">4 · 高配 CPU</option>
        </select>
      </div>
      <div>
        <label>最大高度 (只降不升)</label>
        <select id="max_height">
          <option value="0">不限 (保持原分辨率)</option>
          <option value="1080">1080p 上限</option>
          <option value="720">720p 上限 (明显提速)</option>
          <option value="540">540p 上限</option>
        </select>
      </div>
      <div>
        <label>智能直传阈值 (kbps)</label>
        <input type="number" id="smart_copy_kbps" value="1200" min="100" max="20000" step="100">
      </div>
    </div>

    <div class="row" style="margin-top:10px;align-items:flex-end">
      <div>
        <label>画幅转换 <span class="v12-pill">v12</span></label>
        <select id="aspect">
          <option value="keep">保持原比例</option>
          <option value="9:16">9:16 竖屏 (抖音/视频号)</option>
          <option value="1:1">1:1 方形 (朋友圈)</option>
          <option value="3:4">3:4 竖版海报</option>
          <option value="4:3">4:3 传统</option>
          <option value="16:10">16:10 宽屏</option>
          <option value="16:9">16:9 标准横屏</option>
        </select>
      </div>
      <div id="aspectModeWrap" class="hide">
        <label>填充方式</label>
        <select id="aspect_mode">
          <option value="crop">裁切填满 (裁掉超出部分)</option>
          <option value="pad">纯色边框 (主体完整)</option>
          <option value="blur">模糊填充 (主体完整, 背景模糊)</option>
        </select>
      </div>
      <div id="aspectColorWrap" class="hide">
        <label>边框颜色</label>
        <select id="aspect_color">
          <option value="black">黑色</option>
          <option value="white">白色</option>
          <option value="gray">灰色</option>
          <option value="red">红色</option>
          <option value="green">绿色</option>
          <option value="blue">蓝色</option>
          <option value="yellow">黄色</option>
        </select>
      </div>
      <div id="aspectBlurWrap" class="hide">
        <label>模糊强度</label>
        <input type="number" id="aspect_blur" value="20" min="2" max="60" step="2">
      </div>
    </div>
    <div class="hint" id="aspectHint" style="margin-top:4px">
      画幅转换放在画质增强之后, 决定最终输出比例; 与「限高」同时使用时以画幅为准。
    </div>

    <div class="chk"><input type="checkbox" id="smart_copy"><label style="margin:0;font-weight:600" for="smart_copy">智能直传: 源码率已低于阈值时不重编码, 直接无损封装</label></div>
    <div class="chk"><input type="checkbox" id="keep_smaller" checked><label style="margin:0;font-weight:600" for="keep_smaller">压缩后反而变大时保留原文件 (不再产出体积变大的结果)</label></div>
    <div class="chk"><input type="checkbox" id="auto_open"><label style="margin:0;font-weight:500" for="auto_open">任务完成后自动打开输出文件夹</label></div>
    <div class="chk"><input type="checkbox" id="auto_fallback" checked><label style="margin:0;font-weight:600" for="auto_fallback">v10 失败自愈: 编码失败时自动改用软件编码 / 去掉滤镜重试一次</label></div>

    <div class="spd-note" id="speedNote">默认已启用 2 并发 + fast 预设 + 自动硬件引擎。点上方「极速方案」可一键套用全部提速项。智能直传与「变大保留原片」在开启画质增强时自动让位, 避免把增强结果丢掉。</div>
  </div>

  <div class="card v8-accent" id="v8Card">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <label style="margin:0;font-size:15px">精准体积与完整保留 <span class="v8-pill">v8 新增</span></label>
      <span style="flex:1"></span>
      <span class="hint" id="diskInfo2">磁盘: 检测中…</span>
    </div>

    <div class="row" style="margin-top:6px">
      <div>
        <label>流保留策略 (多音轨 / 字幕 / 章节 / HDR)</label>
        <select id="streams">
          <option value="single">标准 · 单视频轨 + 单音轨 (兼容旧行为)</option>
          <option value="allaudio">保留全部音轨 + 元数据 / 章节</option>
          <option value="all">完整保留 · 音轨 + 字幕 + 章节 + 色彩标记</option>
        </select>
      </div>
      <div>
        <label>智能体积精修</label>
        <div class="chk" style="margin-top:7px"><input type="checkbox" id="smart_refine" checked><label style="margin:0;font-weight:500" for="smart_refine">偏差 &gt;15% 时自动精修 (最多 2 次, 更准)</label></div>
      </div>
    </div>
    <div class="chk"><input type="checkbox" id="resume" checked><label style="margin:0;font-weight:600" for="resume">断点续跑: 输出已存在且比源文件新时跳过, 中断后重跑不重复压缩</label></div>
    <div class="v8-note" id="v8Note">
      <b>智能体积</b>: 从片头 / 片中 / 片尾各抽一小段, 用两档 CRF 试压后拟合「CRF → 体积」曲线, 反推命中目标 MB 的 CRF, 常规目标只编码一遍全片 —— 比旧的「目标体积」两遍编码快约 1.8 倍, 也不用固定码率, 画质更均匀。<br>
      注意: 目标体积低于源文件约 20% 属极限压缩, 可能触发多轮精修而慢于两遍编码; 这种场景建议改用「目标体积(两遍编码)」或关掉精修。<br>
      <b>完整保留</b>: 显式映射全部音轨与字幕, 复制章节、元数据与 HDR 色彩标记; MP4 里的 ASS/SSA 字幕会自动转成兼容的 mov_text。<br>
      结果表格里<b>点击文件名</b>可查看压缩前后的完整参数对比。
    </div>
  </div>

  <div class="card v9-accent" id="v9Card">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <label style="margin:0;font-size:15px">智能分析与自动化 <span class="v9-pill">v9 新增</span></label>
      <span style="flex:1"></span>
      <span class="hint">只抽取少量帧做检测, 不改动原文件</span>
    </div>

    <div class="row" style="margin-top:8px">
      <div>
        <label>分析对象 (来自待处理列表)</label>
        <select id="analyzeFile"></select>
      </div>
      <div>
        <label>输出验收 (编码后自动检查)</label>
        <select id="verify">
          <option value="off">关闭</option>
          <option value="quick" selected>快速 · 抽 3 段解码 (推荐)</option>
          <option value="full">完整 · 整片解码 (最可靠, 较慢)</option>
        </select>
      </div>
      <div>
        <label>裁黑边 W:H:X:Y (留空关闭)</label>
        <input type="text" id="enh_crop" placeholder="由智能分析自动填入, 也可手填">
      </div>
    </div>

    <div class="toolbar">
      <button class="btn-ghost" id="analyzeBtn">分析选中文件</button>
      <button class="btn-ghost" id="analyzeAllBtn">扫描整个队列</button>
      <button class="btn-primary" id="adoptBtn" disabled>一键采用推荐参数</button>
      <span class="hint" id="analyzeState"></span>
    </div>
    <div id="analyzeResult" class="v9-note" style="display:none"></div>

    <div class="v9-sep"></div>
    <label style="margin-top:2px">参数方案 <span class="hint" style="font-weight:500">(存到 schemes.json, 命令行用 --scheme 名称 加载)</span></label>
    <div class="toolbar" style="margin-top:4px">
      <select id="schemeSel" style="width:auto;flex:1;max-width:300px"></select>
      <button class="btn-ghost" id="schemeSave">保存当前</button>
      <button class="btn-ghost" id="schemeApply">应用方案</button>
      <button class="btn-mini" id="schemeDel" style="background:#ffe3e3;color:#d23b3b">删除</button>
    </div>
    <div class="toolbar" style="margin-top:2px">
      <button class="btn-mini" id="queueExport">导出队列</button>
      <button class="btn-mini" id="queueImport">导入队列</button>
      <input type="file" id="queueFile" accept=".json" style="display:none">
      <span class="hint" id="schemeState"></span>
    </div>

    <div class="v9-note">
      <b>智能分析</b>: 从片头 / 片中 / 片尾各抽 12 帧, 用 cropdetect 找黑边、idet 判隔行、signalstats 量亮度与色彩, 再结合码率密度推一套带理由的参数; 点「一键采用」即可套用, 不满意可手动改。<br>
      <b>输出验收</b>: 编码完成后核对容器、时长、音轨/字幕数量并实际解码, 判定损坏的输出会直接丢弃并标记失败, 不会污染输出目录。结果表「验收」列可点开看逐项明细。<br>
      <b>方案 / CLI</b>: 常用参数可命名保存, 也可导出队列下次导入; 命令行运行 <code>python video_compressor.py --cli --help</code> 可无人值守批处理。
    </div>
  </div>

  <div class="card v10-accent" id="v10Card">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <label style="margin:0;font-size:15px">画质目标与逐文件微调 <span class="v10-pill">v10 新增</span></label>
      <span style="flex:1"></span>
      <span class="hint">试算只抽几秒素材, 不会改动原文件</span>
    </div>

    <div class="row" style="margin-top:8px">
      <div>
        <label>试算对象 (来自待处理列表)</label>
        <select id="qualityFile"></select>
      </div>
      <div>
        <label>画质曲线试算 (3 档 CRF × 抽段 SSIM)</label>
        <div class="toolbar" style="margin-top:2px">
          <button class="btn-ghost" id="qprobeBtn">试算画质曲线</button>
          <span class="hint" id="qprobeState"></span>
        </div>
      </div>
    </div>
    <div id="qprobeResult" class="v10-note" style="display:none"></div>

    <div class="v10-sep"></div>
    <label style="margin-top:2px">逐文件微调 <span class="hint" style="font-weight:500">(在上方待处理列表点「微调」)</span></label>
    <div class="toolbar" style="margin-top:2px">
      <span class="hint" id="ovSummary">当前没有微调项</span>
      <button class="btn-mini" id="ovClearAll">清除全部微调</button>
    </div>

    <div class="v10-note">
      <b>画质目标</b>: 与「智能体积」相反 —— 先定画质下限 (SSIM), 再由试压曲线反推<b>满足该画质的最小体积 CRF</b>,
      只编码一遍全片。不同片源难度不同, 同样的 CRF 画质可能差很多; 这个模式让结果更可预期。
      点「试算画质曲线」可先看各档 CRF 的实测 SSIM 与采样体积, 再决定档位。
      试压范围内全部达标时只会保守外推 4 档 CRF, 避免简单片源被盲目压到画质崩坏。<br>
      <b>逐文件微调</b>: 队列里某个视频特别糊 / 特别大时, 单独给它设 CRF、目标体积、限高、裁黑边或增强开关;
      留空的项继续用全局参数, 不会互相影响。<br>
      <b>失败自愈</b>: 硬件编码器或增强滤镜导致 ffmpeg 失败时, 自动降级为软件编码并去掉滤镜重试一次,
      结果状态会标注「已自动降级」, 日志里可看具体原因。
    </div>
  </div>

  <div class="card enh-accent" id="enhCard">
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
      <label style="margin:0;font-size:15px">画质增强 <span class="epill">v6 新增</span></label>
      <div class="chk" style="margin:0"><input type="checkbox" id="enh_on"><label style="margin:0;font-weight:600" for="enh_on">启用画质增强</label></div>
      <span style="flex:1"></span>
      <span id="enhCaps" class="hint"></span>
    </div>

    <div id="enhBody" class="enh-off" style="margin-top:8px">
      <label>增强预设 (一键套用, 之后仍可逐项微调)</label>
      <div class="presets" id="enhPresets">
        <button class="epreset" data-e="mild">轻度修复<span>轻降噪 · 轻锐化 · 微提亮</span></button>
        <button class="epreset" data-e="standard">标准增强<span>降噪 · 去块 · 去色带 · 锐化 · 鲜艳</span></button>
        <button class="epreset" data-e="restore">老片 / 低清修复<span>强降噪 · 去隔行 · 去块 · 轻锐化</span></button>
        <button class="epreset" data-e="upscale">超清放大<span>2× Lanczos · CAS 自适应锐化</span></button>
      </div>

      <div class="row" style="margin-top:10px">
        <div>
          <label>降噪强度</label>
          <select id="enh_denoise">
            <option value="off">关闭</option>
            <option value="light">轻度 (轻微噪点)</option>
            <option value="medium">标准 (推荐)</option>
            <option value="strong">强力 (明显噪点)</option>
            <option value="ultra">极致 (颗粒很重, 会糊细节)</option>
          </select>
        </div>
        <div>
          <label>降噪算法</label>
          <select id="enh_dn_method">
            <option value="fast">快速 hqdn3d (推荐)</option>
            <option value="hq">高质量 nlmeans (非常慢)</option>
            <option value="temporal">时域 atadenoise (实拍/老片)</option>
          </select>
        </div>
        <div>
          <label>锐化</label>
          <select id="enh_sharpen">
            <option value="off">关闭</option>
            <option value="light">轻度</option>
            <option value="medium">标准 (推荐)</option>
            <option value="strong">强力</option>
            <option value="cas">CAS 自适应 (放大后推荐)</option>
          </select>
        </div>
        <div>
          <label>超分放大 (Lanczos)</label>
          <select id="enh_upscale">
            <option value="off">不放大 (保持原分辨率)</option>
            <option value="1.5">1.5 倍</option>
            <option value="2">2 倍 (体积/耗时显著增加)</option>
          </select>
        </div>
      </div>

      <label style="margin-top:12px">色彩微调 <span class="hint" style="font-weight:500">(保持默认值即为不改色)</span></label>
      <div class="slider-row">
        <div><label style="font-weight:500">亮度 <span class="v" id="enh_brightness_v">0.00</span></label><input type="range" id="enh_brightness" min="-0.15" max="0.15" step="0.01" value="0"></div>
        <div><label style="font-weight:500">对比度 <span class="v" id="enh_contrast_v">1.00</span></label><input type="range" id="enh_contrast" min="0.70" max="1.40" step="0.01" value="1"></div>
        <div><label style="font-weight:500">饱和度 <span class="v" id="enh_saturation_v">1.00</span></label><input type="range" id="enh_saturation" min="0.50" max="1.80" step="0.01" value="1"></div>
        <div><label style="font-weight:500">Gamma <span class="v" id="enh_gamma_v">1.00</span></label><input type="range" id="enh_gamma" min="0.70" max="1.40" step="0.01" value="1"></div>
      </div>

      <div class="row" style="margin-top:10px">
        <div>
          <label>运动补偿插帧 <span class="hint">(极慢, 只建议短视频)</span></label>
          <select id="enh_interp">
            <option value="off">不插帧</option>
            <option value="60">补到 60 fps</option>
            <option value="120">补到 120 fps</option>
          </select>
        </div>
        <div>
          <label>针对性修复</label>
          <div class="chk" style="margin-top:2px"><input type="checkbox" id="enh_deblock"><label style="margin:0;font-weight:500" for="enh_deblock">去除压缩块 (低码率片源)</label></div>
          <div class="chk" style="margin-top:4px"><input type="checkbox" id="enh_deband"><label style="margin:0;font-weight:500" for="enh_deband">去除色带 (渐变断层)</label></div>
          <div class="chk" style="margin-top:4px"><input type="checkbox" id="enh_deinterlace"><label style="margin:0;font-weight:500" for="enh_deinterlace">去隔行 (老片 / 电视录制)</label></div>
        </div>
      </div>

      <div class="chk" style="margin-top:12px">
        <input type="checkbox" id="enh_only"><label style="margin:0;font-weight:600" for="enh_only">仅增强不压缩 (高画质输出, 体积可能变大)</label>
        <span class="hint" style="margin-left:8px">输出 CRF</span>
        <input type="number" id="enh_crf" value="16" min="10" max="28" step="1" style="width:70px;margin-left:4px;padding:4px 6px;border:1px solid #d7dce8;border-radius:6px">
      </div>

      <div class="enh-note" id="enhChainNote">当前: 未启用增强</div>

      <div class="toolbar">
        <select id="enhPreviewFile" style="width:auto;flex:1;max-width:300px"></select>
        <span class="hint">位置</span>
        <input type="range" id="enhPreviewPos" min="0" max="100" value="50" style="width:auto;flex:0 0 130px">
        <span class="hint" id="enhPreviewPosV" style="min-width:34px">50%</span>
        <button class="btn-ghost" id="enhPreviewBtn">生成增强预览</button>
      </div>
      <div class="hint">预览会用当前参数抽取同一帧: 左为原帧、右为增强后。插帧属于帧间效果, 静帧预览中不体现。</div>
    </div>
  </div>

  <div class="card wm-accent" id="wmCard">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <label style="margin:0;font-size:15px">水印与字幕烧录 <span class="v11-pill">v11 新增</span></label>
      <span style="flex:1"></span>
      <span class="hint" id="wmCaps"></span>
    </div>
    <div class="row" style="margin-top:8px">
      <div>
        <label>水印类型</label>
        <select id="wm_type">
          <option value="off">关闭</option>
          <option value="text">文字水印</option>
          <option value="image">图片水印</option>
        </select>
      </div>
      <div id="wmTextWrap" class="hide">
        <label>水印文字</label>
        <input type="text" id="wm_text" value="Sample" style="min-width:160px">
      </div>
      <div id="wmImgWrap" class="hide">
        <label>图片路径</label>
        <div style="display:flex;gap:6px">
          <input type="text" id="wm_image" placeholder="logo.png 完整路径" style="min-width:200px">
          <button class="btn-ghost" id="wmImgPick">选择</button>
        </div>
      </div>
      <div id="wmPosWrap" class="hide">
        <label>位置</label>
        <select id="wm_pos">
          <option value="br">右下</option><option value="bl">左下</option>
          <option value="tr">右上</option><option value="tl">左上</option>
          <option value="cc">居中</option>
        </select>
      </div>
      <div id="wmSizeWrap" class="hide">
        <label id="wmSizeLbl">大小</label>
        <input type="number" id="wm_size" value="36" min="4" max="200" step="2">
      </div>
      <div id="wmOpWrap" class="hide">
        <label>不透明度</label>
        <input type="number" id="wm_opacity" value="0.6" min="0.05" max="1" step="0.05">
      </div>
    </div>
    <div class="row" style="margin-top:6px">
      <div>
        <label>字幕烧录</label>
        <select id="wm_sub">
          <option value="off">关闭</option>
          <option value="embedded">内嵌字幕 (烧入画面)</option>
          <option value="external">外挂字幕文件</option>
        </select>
      </div>
      <div id="wmSubIdxWrap" class="hide">
        <label>内嵌轨道序号</label>
        <input type="number" id="wm_sub_index" value="0" min="0" max="31" step="1">
      </div>
      <div id="wmSubFileWrap" class="hide">
        <label>字幕文件路径</label>
        <div style="display:flex;gap:6px">
          <input type="text" id="wm_sub_file" placeholder="sub.srt/.ass 完整路径" style="min-width:200px">
          <button class="btn-ghost" id="wmSubPick">选择</button>
        </div>
      </div>
    </div>
    <div class="hint" style="margin-top:6px">
      水印与字幕会和上面的「画质增强」滤镜链叠加到同一画面; 适合发短视频平台 (字幕烧进画面才显示)。
    </div>
  </div>

  <div class="card tb-accent" id="toolCard">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <label style="margin:0;font-size:15px">视频工具箱 <span class="v11-pill">v11 新增</span></label>
      <span style="flex:1"></span>
      <span class="hint">单文件小工具, 不进入压缩流水线</span>
    </div>
    <div class="row" style="margin-top:8px">
      <div>
        <label>动作</label>
        <select id="tb_action">
          <option value="gif">视频转 GIF</option>
          <option value="clip">截取片段</option>
          <option value="deshake">防抖</option>
          <option value="rotate">按旋转自动转正</option>
          <option value="frame">抽帧截图</option>
          <option value="concat">拼接多个视频 <span class="v12-pill">v12</span></option>
        </select>
      </div>
      <div id="tbSrcWrap">
        <label>源文件</label>
        <div style="display:flex;gap:6px">
          <input type="text" id="tb_src" placeholder="视频完整路径" style="min-width:200px">
          <button class="btn-ghost" id="tbSrcPick">选择</button>
        </div>
      </div>
      <div id="tbConcatWrap" class="hide">
        <label>拼接来源</label>
        <div class="hint" id="tbConcatInfo">使用「待处理列表」中的视频, 按列表顺序拼接</div>
      </div>
      <div>
        <label>输出文件</label>
        <input type="text" id="tb_out" placeholder="留空=源目录同名_动作" style="min-width:200px">
      </div>
      <div id="tbSsWrap">
        <label>起始 (秒)</label>
        <input type="number" id="tb_ss" value="0" min="0" step="0.5">
      </div>
      <div id="tbDurWrap" class="hide">
        <label>时长 (秒)</label>
        <input type="number" id="tb_dur" value="5" min="0.1" step="0.5">
      </div>
      <div id="tbGifWrap" class="hide">
        <label>GIF 帧率/宽度</label>
        <div style="display:flex;gap:6px">
          <input type="number" id="tb_gif_fps" value="15" min="1" max="50" step="1" style="width:64px">
          <input type="number" id="tb_gif_w" value="480" min="32" max="4096" step="16" style="width:74px">
        </div>
      </div>
    </div>
    <div style="margin-top:10px;display:flex;gap:10px;align-items:center;flex-wrap:wrap">
      <button class="btn-primary" id="tbRun">执行</button>
      <span id="tbResult" class="hint"></span>
    </div>
  </div>

  <div class="card" id="resultCard" style="display:none">
    <div class="status-line" id="overallText">准备中…</div>
    <div class="bar"><i id="overallBar"></i></div>
    <div class="status-line" id="curText"></div>
    <div class="bar"><i id="curBar"></i></div>
    <div class="status-line" id="etaText"></div>
    <div class="toolbar">
      <span class="sumline" id="resultSummary"></span>
      <span style="flex:1"></span>
      <button class="btn-mini" id="retrybtn" style="display:none;background:#ffe9e0;color:#c2511b">重试失败项</button>
      <button class="btn-mini" id="evalall">一键测画质 (SSIM/PSNR)</button>
    </div>
    <div class="hint" id="enhUsed" style="margin-top:2px"></div>
    <table style="margin-top:6px">
      <thead><tr><th>文件</th><th>原大小</th><th>压缩后</th><th>比例</th><th>状态</th><th style="width:70px">验收</th><th style="width:74px">画质</th><th style="width:64px">对比</th></tr></thead>
      <tbody id="resultBody"></tbody>
    </table>
  </div>

  <div class="card" id="historyCard">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <label style="margin:0;font-size:15px">任务历史与统计 <span class="v10-pill">v10 新增</span></label>
      <span style="flex:1"></span>
      <button class="btn-mini" id="histRefresh">刷新</button>
      <button class="btn-mini" id="histExport">导出 JSON</button>
      <button class="btn-mini" id="histClear" style="background:#ffe3e3;color:#d23b3b">清空历史</button>
    </div>
    <div id="histStats" class="hist-kpis"></div>
    <div id="histBars" class="hist-bars" title="近期任务节省率"></div>
    <div id="histBody"></div>
    <div class="hint" style="margin-top:6px">记录保存在工具目录的 history.jsonl, 只含文件名与体积统计, 不含视频内容。</div>
  </div>

  <div class="card">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <label style="margin:0">运行日志</label>
      <span style="flex:1"></span>
      <span id="logpath" class="hint"></span>
      <button class="btn-mini" id="openlogs">打开日志文件夹</button>
    </div>
    <div id="log" style="margin-top:8px"></div>
  </div>
</div>

<div class="modal" id="cmpModal">
  <div class="modal-box" style="min-width:640px">
    <div style="display:flex;align-items:center;margin-bottom:10px;gap:8px;flex-wrap:wrap;">
      <b id="cmpTitle" style="font-size:14px"></b>
      <span style="flex:1"></span>
      <span class="hint" id="cmpMetric"></span>
      <button class="btn-mini" id="cmpClose">关闭</button>
    </div>
    <div class="cmp-stage" id="cmpStage">
      <img id="imgA" alt="原图">
      <div class="cmp-clip" id="cmpClip"><img id="imgB" alt="压缩后"></div>
      <div class="cmp-handle" id="cmpHandle"></div>
      <div class="cmp-tag cmp-tag-l">原文件</div>
      <div class="cmp-tag cmp-tag-r">压缩后</div>
    </div>
    <div class="toolbar" style="margin-top:10px">
      <span class="hint">时间点</span>
      <input type="range" id="cmpT" min="0" max="1000" value="500" style="width:150px">
      <span class="hint" id="cmpTv">-</span>
      <span class="hint">放大</span>
      <select id="cmpZoom" style="width:auto">
        <option value="720">1×</option>
        <option value="1440">2×</option>
        <option value="2160">3×</option>
      </select>
      <button class="btn-mini" id="cmpReload">重新取帧</button>
    </div>
    <div class="hint" id="cmpNote" style="margin-top:8px">
      左右拖动中间滑块擦除对比 (左侧原文件 / 右侧压缩后)。压缩细节很细微, 建议放大到 2× 以上, 并拖动时间点逐帧查看。
    </div>
  </div>
</div>

<div class="modal" id="qmModal">
  <div class="modal-box" style="min-width:440px">
    <div style="display:flex;align-items:center;margin-bottom:6px;">
      <b id="qmTitle" style="font-size:14px"></b>
      <span style="flex:1"></span>
      <button class="btn-mini" id="qmClose">关闭</button>
    </div>
    <div id="qmBody"></div>
  </div>
</div>

<div class="modal" id="enhModal">
  <div class="modal-box">
    <div style="display:flex;align-items:center;margin-bottom:10px;">
      <b id="enhModalTitle" style="font-size:14px">增强预览</b>
      <span style="flex:1"></span>
      <button class="btn-mini" id="enhModalClose">关闭</button>
    </div>
    <div class="cmp-grid">
      <figure><img id="enhImgA" alt="原帧"><figcaption>原帧</figcaption></figure>
      <figure><img id="enhImgB" alt="增强后"><figcaption>增强后</figcaption></figure>
    </div>
    <div class="enh-note" id="enhModalInfo"></div>
  </div>
</div>

<div class="modal" id="infoModal">
  <div class="modal-box" style="min-width:520px;max-width:90vw">
    <div style="display:flex;align-items:center;margin-bottom:10px;">
      <b id="infoTitle" style="font-size:14px">压缩前后参数对比</b>
      <span style="flex:1"></span>
      <button class="btn-mini" id="infoClose">关闭</button>
    </div>
    <div id="infoBody"></div>
  </div>
</div>

<div class="modal" id="ovModal">
  <div class="modal-box" style="min-width:420px;max-width:92vw">
    <div style="display:flex;align-items:center;margin-bottom:10px;">
      <b id="ovTitle" style="font-size:14px">逐文件微调</b>
      <span style="flex:1"></span>
      <button class="btn-mini" id="ovClose">关闭</button>
    </div>
    <div class="hint" style="margin-bottom:8px">留空 = 跟随全局参数。仅对当前文件生效, 不改变其他视频。</div>
    <div class="row">
      <div><label>CRF</label><input type="number" id="ov_crf" min="0" max="51" step="1" placeholder="留空跟随全局"></div>
      <div><label>目标体积 (MB)</label><input type="number" id="ov_target_mb" min="0.1" step="1" placeholder="留空跟随全局"></div>
    </div>
    <div class="row">
      <div><label>限高 (0=不限)</label><input type="number" id="ov_max_height" min="0" max="4096" step="10" placeholder="留空跟随全局"></div>
      <div><label>画质目标 SSIM</label><input type="number" id="ov_quality_target" min="0.80" max="0.9999" step="0.001" placeholder="留空跟随全局"></div>
    </div>
    <div class="row">
      <div><label>裁黑边 W:H:X:Y</label><input type="text" id="ov_enh_crop" placeholder="如 640:360:40:40, 留空跟随"></div>
      <div><label>画质增强</label><select id="ov_enh_on">
        <option value="">跟随全局</option><option value="1">强制开启</option><option value="0">强制关闭</option>
      </select></div>
    </div>
    <div class="chk"><input type="checkbox" id="ov_crop_off"><label style="margin:0;font-weight:500" for="ov_crop_off">关闭该文件的裁黑边 (覆盖全局设置)</label></div>
    <div class="toolbar" style="margin-top:12px">
      <button class="btn-primary" id="ovSave">保存微调</button>
      <button class="btn-ghost" id="ovReset">清除此文件微调</button>
    </div>
  </div>
</div>

<script>
const $ = id => document.getElementById(id);
function fmtSize(b){ if(b===undefined||b===null||b==='') return '-'; if(b===0) return '0'; const u=['B','KB','MB','GB']; let i=0,x=b; while(x>=1024&&i<u.length-1){x/=1024;i++;} return (x.toFixed(x<10&&i>0?1:0))+' '+u[i]; }
function fmtDur(s){ if(!s) return '-'; const m=Math.floor(s/60), ss=Math.round(s%60); return (m?m+'分':'')+ss+'秒'; }
let HWLabel='';
let enhCaps={};
let queue=[];       // {path,name,size,duration,width,height,codec,checked}
let qmap={};        // out path -> quality result
let lastResults=[];
let lastPayload=null;   // 供「重试失败项」复用同一套参数
let ovIndex=-1;         // v10: 当前正在微调的队列索引
let lastHistory=[];     // v10: 最近任务历史
const QL={lossless:0.995, high:0.990, balanced:0.980, compact:0.950};

const PRESETS={
  wallpaper:{mode:'crf',codec:'hevc',pix:'10',audio:'strip',tune:'animation',crf:26,preset:'fast',engine:'auto',workers:2,max_height:0,smart_copy:false,keep_smaller:true},
  balanced:{mode:'crf',codec:'hevc',pix:'10',audio:'reencode',tune:'animation',crf:24,preset:'fast',engine:'auto',workers:2,max_height:0,smart_copy:false,keep_smaller:true},
  quality:{mode:'crf',codec:'hevc',pix:'10',audio:'copy',tune:'animation',crf:20,preset:'medium',engine:'software',workers:1,max_height:0,smart_copy:false,keep_smaller:false},
  compat:{mode:'crf',codec:'h264',pix:'8',audio:'reencode',tune:'none',crf:22,preset:'fast',engine:'software',workers:2,max_height:0,smart_copy:false,keep_smaller:true},
  turbo:{mode:'crf',codec:'hevc',pix:'8',audio:'strip',tune:'none',crf:26,preset:'veryfast',engine:'auto',
         workers:2,max_height:0,smart_copy:true,smart_copy_kbps:1200,keep_smaller:true}
};
function markPreset(name){
  document.querySelectorAll('#presets .preset').forEach(b=>b.classList.toggle('active', b.dataset.p===name));
  try{ if(name) localStorage.setItem('vc_preset',name); }catch(e){}
}

const ENH_PRESETS={
  mild:{enh_denoise:'light',enh_dn_method:'fast',enh_sharpen:'light',enh_upscale:'off',
        enh_deblock:false,enh_deband:false,enh_deinterlace:false,enh_interp:'off',
        enh_brightness:0.01,enh_contrast:1.03,enh_saturation:1.05,enh_gamma:1.0},
  standard:{enh_denoise:'medium',enh_dn_method:'fast',enh_sharpen:'medium',enh_upscale:'off',
        enh_deblock:true,enh_deband:true,enh_deinterlace:false,enh_interp:'off',
        enh_brightness:0.01,enh_contrast:1.06,enh_saturation:1.12,enh_gamma:1.0},
  restore:{enh_denoise:'strong',enh_dn_method:'temporal',enh_sharpen:'light',enh_upscale:'off',
        enh_deblock:true,enh_deband:true,enh_deinterlace:true,enh_interp:'off',
        enh_brightness:0.02,enh_contrast:1.08,enh_saturation:1.10,enh_gamma:0.98},
  upscale:{enh_denoise:'light',enh_dn_method:'fast',enh_sharpen:'cas',enh_upscale:'2',
        enh_deblock:true,enh_deband:false,enh_deinterlace:false,enh_interp:'off',
        enh_brightness:0,enh_contrast:1.04,enh_saturation:1.08,enh_gamma:1.0}
};
function markEnhPreset(name){
  document.querySelectorAll('#enhPresets .epreset').forEach(b=>b.classList.toggle('active', b.dataset.e===name));
  try{ if(name) localStorage.setItem('vc_enh_preset',name); else localStorage.removeItem('vc_enh_preset'); }catch(e){}
}
function applyEnhPreset(name){
  const p=ENH_PRESETS[name]; if(!p) return;
  $('enh_on').checked=true;
  for(const k in p){ const el=$(k); if(!el) continue; if(el.type==='checkbox') el.checked=!!p[k]; else el.value=p[k]; }
  updateEnhUI(); saveSettings(); renderQueue(); markEnhPreset(name);
}
$('enhPresets').addEventListener('click', e=>{
  const b=e.target.closest('.epreset'); if(!b) return;
  applyEnhPreset(b.dataset.e);
});
function gatherEnh(){
  return {
    enh_on:$('enh_on').checked,
    enh_denoise:$('enh_denoise').value,
    enh_dn_method:$('enh_dn_method').value,
    enh_deblock:$('enh_deblock').checked,
    enh_deband:$('enh_deband').checked,
    enh_sharpen:$('enh_sharpen').value,
    enh_upscale:$('enh_upscale').value,
    enh_brightness:parseFloat($('enh_brightness').value),
    enh_contrast:parseFloat($('enh_contrast').value),
    enh_saturation:parseFloat($('enh_saturation').value),
    enh_gamma:parseFloat($('enh_gamma').value),
    enh_deinterlace:$('enh_deinterlace').checked,
    enh_interp:$('enh_interp').value,
    enh_only:$('enh_only').checked,
    enh_crf:parseInt($('enh_crf').value)||16,
    enh_crop:$('enh_crop').value.trim()
  };
}
function gatherAudio(){
  return {
    audio_normalize:$('audio_normalize').value,
    audio_denoise:$('audio_denoise').value,
    audio_bitrate:parseInt($('audio_bitrate').value)||128,
    audio_samplerate:parseInt($('audio_samplerate').value)||0,
    audio_channels:parseInt($('audio_channels').value)||0,
  };
}
function gatherWM(){
  return {
    wm_type:$('wm_type').value,
    wm_text:$('wm_text').value,
    wm_image:$('wm_image').value.trim(),
    wm_pos:$('wm_pos').value,
    wm_size:parseInt($('wm_size').value)||36,
    wm_opacity:parseFloat($('wm_opacity').value)||0.6,
    wm_sub:$('wm_sub').value,
    wm_sub_index:parseInt($('wm_sub_index').value)||0,
    wm_sub_file:$('wm_sub_file').value.trim(),
  };
}
function gatherAspect(){
  return {
    aspect:$('aspect').value,
    aspect_mode:$('aspect_mode').value,
    aspect_color:$('aspect_color').value,
    aspect_blur:parseInt($('aspect_blur').value)||20,
  };
}
function updateWMUI(){
  const t=$('wm_type').value;
  $('wmTextWrap').classList.toggle('hide', t!=='text');
  $('wmImgWrap').classList.toggle('hide', t!=='image');
  $('wmPosWrap').classList.toggle('hide', t==='off');
  $('wmSizeWrap').classList.toggle('hide', t==='off');
  $('wmOpWrap').classList.toggle('hide', t==='off');
  $('wmSizeLbl').textContent = t==='image' ? '大小(%)' : '大小(px)';
  const s=$('wm_sub').value;
  $('wmSubIdxWrap').classList.toggle('hide', s!=='embedded');
  $('wmSubFileWrap').classList.toggle('hide', s!=='external');
  const caps=window.__audioCaps||{};
  const f=window.__fontFound;
  let msg=[];
  if(t==='text' && !f) msg.push('未找到系统字体, 文字水印将不可用');
  if(t==='image' && !caps.overlay) msg.push('overlay 滤镜不可用, 图片水印将失败');
  if(s!=='off' && !caps.subtitles) msg.push('subtitles 滤镜不可用, 字幕烧录将失败');
  $('wmCaps').textContent=msg.join('；')||'';
}
function updateToolUI(){
  const a=$('tb_action').value;
  const hasDur = a==='gif'||a==='clip';
  $('tbDurWrap').classList.toggle('hide', !hasDur);
  $('tbGifWrap').classList.toggle('hide', a!=='gif');
  const isConcat = a==='concat';
  $('tbSrcWrap').classList.toggle('hide', isConcat);
  $('tbConcatWrap').classList.toggle('hide', !isConcat);
  if(isConcat){
    const n=(queue||[]).length;
    $('tbConcatInfo').textContent = n>=2
      ? ('将拼接待处理列表中的 '+n+' 个视频 (按列表顺序)')
      : '待处理列表中至少需要 2 个视频, 请先添加文件';
  }
}
function updateAspectUI(){
  const a=$('aspect').value;
  const on = a && a!=='keep';
  $('aspectModeWrap').classList.toggle('hide', !on);
  const mode=$('aspect_mode').value;
  $('aspectColorWrap').classList.toggle('hide', !on || mode!=='pad');
  $('aspectBlurWrap').classList.toggle('hide', !on || mode!=='blur');
}
function updateEnhUI(){
  const on=$('enh_on').checked;
  $('enhBody').classList.toggle('enh-off', !on);
  ['enh_brightness','enh_contrast','enh_saturation','enh_gamma'].forEach(id=>{
    const v=$(id+'_v'); if(v) v.textContent=parseFloat($(id).value).toFixed(2);
  });
  $('enhPreviewPosV').textContent=$('enhPreviewPos').value+'%';
  const e=gatherEnh(), L=[];
  if(on){
    if(e.enh_denoise!=='off') L.push('降噪·'+e.enh_denoise+'('+e.enh_dn_method+')');
    if(e.enh_deblock) L.push('去压缩块');
    if(e.enh_deband) L.push('去色带');
    if(e.enh_sharpen!=='off') L.push('锐化·'+e.enh_sharpen);
    if(e.enh_upscale!=='off') L.push('放大'+e.enh_upscale+'×');
    if(e.enh_deinterlace) L.push('去隔行');
    if(e.enh_interp!=='off') L.push('插帧'+e.enh_interp+'fps');
    if(e.enh_brightness||e.enh_contrast!==1||e.enh_saturation!==1||e.enh_gamma!==1) L.push('色彩微调');
    if(e.enh_only) L.push('仅增强 CRF'+e.enh_crf);
  }
  $('enhChainNote').textContent = on ? ('当前增强链: '+(L.length?L.join(' + '):'无 (原样编码)')) : '当前: 未启用增强';
}
function refreshPreviewFiles(){
  const sel=$('enhPreviewFile'); if(!sel) return;
  const prev=sel.value;
  sel.innerHTML='';
  if(queue.length===0){ const o=document.createElement('option'); o.value=''; o.textContent='(请先扫描加入视频)'; sel.appendChild(o); return; }
  queue.forEach(it=>{ const o=document.createElement('option'); o.value=it.path; o.textContent=it.name; sel.appendChild(o); });
  if(prev && queue.some(x=>x.path===prev)) sel.value=prev;
}
const ENH_IDS=['enh_on','enh_denoise','enh_dn_method','enh_deblock','enh_deband','enh_sharpen','enh_upscale','enh_deinterlace','enh_interp','enh_only','enh_crf'];
ENH_IDS.forEach(id=>{ const el=$(id); if(el) el.addEventListener('change',()=>{ updateEnhUI(); saveSettings(); renderQueue(); markEnhPreset(''); }); });
['enh_brightness','enh_contrast','enh_saturation','enh_gamma'].forEach(id=>{
  const el=$(id); if(el) el.addEventListener('input',()=>{ updateEnhUI(); saveSettings(); markEnhPreset(''); });
});
$('enhPreviewPos').addEventListener('input', ()=>{ $('enhPreviewPosV').textContent=$('enhPreviewPos').value+'%'; });
$('enhModalClose').addEventListener('click', ()=>{ $('enhModal').style.display='none'; });
$('enhModal').addEventListener('click', e=>{ if(e.target===$('enhModal')) $('enhModal').style.display='none'; });
$('enhPreviewBtn').addEventListener('click', async ()=>{
  const p=$('enhPreviewFile').value;
  if(!p){ alert('请先扫描加入视频, 再选择要预览的文件'); return; }
  const it=queue.find(x=>x.path===p);
  const b=$('enhPreviewBtn'); b.disabled=true; b.textContent='生成中…';
  const dur=(it&&it.duration)?it.duration:0;
  const t=Math.max(0,Math.min(dur?dur-0.08:0, dur*parseFloat($('enhPreviewPos').value)/100));
  try{
    const r=await fetch('/api/enhpreview',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({path:p,t:t,opts:{...gatherEnh(),max_height:parseInt($('max_height').value)||0}})});
    const j=await r.json();
    if(!j.ok){ alert(j.err||'预览生成失败'); }
    else{
      $('enhImgA').src=j.before; $('enhImgB').src=j.after;
      $('enhModalTitle').textContent='增强预览 · '+(it?it.name:p);
      $('enhModalInfo').textContent='取样 '+t.toFixed(1)+'s · 滤镜链: '+(j.vf||'无')
        +(j.skipped&&j.skipped.length?(' · 当前 ffmpeg 不支持已跳过: '+j.skipped.join('、')):'');
      $('enhModal').style.display='flex';
    }
  }catch(e){ alert('预览请求失败: '+e); }
  b.disabled=false; b.textContent='生成增强预览';
});
function applyPreset(name){
  const p=PRESETS[name]; if(!p) return;
  for(const k in p){ const el=$(k); if(!el) continue; if(el.type==='checkbox') el.checked=!!p[k]; else el.value=p[k]; }
  $('crfval').textContent=$('crf').value;
  updateModeUI(); saveSettings(); markPreset(name);
}
$('presets').addEventListener('click', e=>{
  const b=e.target.closest('.preset'); if(!b) return;
  applyPreset(b.dataset.p);
});

function gather(){
  return { folder:$('folder').value, recursive:$('recursive').checked, force:$('force').checked,
    mode:$('mode').value, ratio_pct:$('ratio_pct').value, target_mb:$('target_mb').value,
    codec:$('codec').value, engine:$('engine').value, pix:$('pix').value, audio:$('audio').value,
    crf:$('crf').value, preset:$('preset').value, tune:$('tune').value,
    out_mode:$('out_mode').value, out_sub:$('out_sub').value,
    workers:$('workers').value, max_height:$('max_height').value,
    smart_copy:$('smart_copy').checked, smart_copy_kbps:parseFloat($('smart_copy_kbps').value)||1200,
    keep_smaller:$('keep_smaller').checked, auto_open:$('auto_open').checked,
    streams:$('streams').value, resume:$('resume').checked, smart_refine:$('smart_refine').checked,
    verify:$('verify').value,
    auto_fallback:$('auto_fallback').checked,
    quality_preset:$('quality_preset').value,
    quality_target:parseFloat($('quality_target').value)||0.99,
    name_template:$('name_template').value,
    ...gatherEnh(), ...gatherAudio(), ...gatherWM(), ...gatherAspect() };
}
function saveSettings(){ try{ localStorage.setItem('vc_settings', JSON.stringify(gather())); }catch(e){} }
function loadSettings(){
  try{ const s=JSON.parse(localStorage.getItem('vc_settings')||'{}');
    for(const k in s){ const el=$(k); if(!el) continue; if(el.type==='checkbox') el.checked=!!s[k]; else el.value=s[k]; }
  }catch(e){}
  $('crfval').textContent=$('crf').value;
}
function updateModeUI(){
  const m=$('mode').value;
  $('crfWrap').classList.toggle('hide', m!=='crf');
  $('qualityWrap').classList.toggle('hide', m!=='quality');
  $('ratioWrap').classList.toggle('hide', m!=='ratio');
  $('sizeWrap').classList.toggle('hide', m!=='size' && m!=='smart');
  $('sizeLbl').textContent = m==='smart' ? '目标体积 (MB, 智能体积精准命中)' : '目标体积 (MB)';
  renderQueue();
}

function updateAudioUI(){
  const a=$('audio').value;
  const show = a==='reencode';
  $('audioAdv').classList.toggle('hide', !show);
  $('audioAdvHint').classList.toggle('hide', !show);
  // v11: AV1/VP9 仅软件编码且较慢, 给出提示
  const codec=$('codec').value;
  const note=$('codecNote');
  if(codec==='av1' || codec==='vp9'){
    note.style.display='block';
    note.textContent='注意: '+(codec==='av1'?'AV1':'VP9')+' 比 H.265 体积更小但编码明显更慢, 适合归档/网页, 不适合批量急用。';
  } else {
    note.style.display='none';
  }
}

function estSize(it){
  const enhOn=$('enh_on').checked;
  const up=enhOn?$('enh_upscale').value:'off';
  const upF= up==='2'?2.5:(up==='1.5'?1.65:1);
  const mh=parseInt($('max_height').value)||0;
  const hF= (mh&&it.height&&it.height>mh) ? Math.max(0.15,Math.pow(mh/it.height,1.5)) : 1;
  if(enhOn && $('enh_only').checked) return it.size*1.6*upF*hF;
  const mode=$('mode').value;
  if(mode==='quality'){
    const q=(it.ov&&it.ov.quality_target!==undefined)?parseFloat(it.ov.quality_target):(parseFloat($('quality_target').value)||0.99);
    const qr = q>=0.995?0.62:(q>=0.99?0.44:(q>=0.98?0.33:0.23));
    return Math.min(it.size, it.size*qr*upF*hF);
  }
  if(mode==='smart') return Math.min(it.size,(parseFloat($('target_mb').value)||50)*1024*1024);
  if(mode==='ratio') return it.size*((parseFloat($('ratio_pct').value)||30)/100)*upF*hF;
  if(mode==='size') return Math.min(it.size,(parseFloat($('target_mb').value)||50)*1024*1024)*upF*hF;
  const codec=$('codec').value, pix=$('pix').value;
  let r = codec==='h264' ? 0.42 : (pix==='10'?0.28:0.33);
  const crf=(it.ov&&it.ov.crf!==undefined)?parseFloat(it.ov.crf):(parseInt($('crf').value)||24);
  if(crf>=28) r*=1.45; else if(crf>26) r*=1.25; else if(crf>24) r*=1.12; else if(crf<20) r*=0.72; else if(crf<22) r*=0.85;
  if(enhOn){
    const dn=$('enh_denoise').value;
    r*= dn==='off'?1.02:(dn==='strong'||dn==='ultra'?0.85:0.93);
    if($('enh_interp').value!=='off') r*=1.5;
  }
  return it.size*r*upF*hF;
}

function renderQueue(){
  refreshPreviewFiles();
  refreshAnalyzeFiles();
  refreshQualityFiles();
  const wrap=$('qwrap'), body=$('qbody');
  if(queue.length===0){ wrap.style.display='none'; $('qsummary').textContent='待处理列表为空'; return; }
  wrap.style.display='block'; body.innerHTML='';
  let totS=0, totE=0, chk=0;
  queue.forEach((it,i)=>{
    totS+=it.size; totE+=estSize(it); if(it.checked) chk++;
    const tr=document.createElement('tr');
    const cb=document.createElement('input'); cb.type='checkbox'; cb.checked=!!it.checked; cb.setAttribute('data-i', i);
    const td0=document.createElement('td'); td0.appendChild(cb);
    const td1=document.createElement('td'); td1.textContent=it.name; td1.title=it.path;
    const td2=document.createElement('td'); td2.textContent= it.width? it.width+'×'+it.height : '-';
    const tdStream=document.createElement('td');
    tdStream.textContent = (it.audio||0)+'音'+(it.subtitle? ' · '+it.subtitle+'字幕':'');
    tdStream.title = '音轨 / 字幕数量 · 在下方「流保留策略」中可选择完整保留';
    const td3=document.createElement('td'); td3.textContent=fmtDur(it.duration);
    const td4=document.createElement('td'); td4.textContent=fmtSize(it.size);
    const td5=document.createElement('td'); td5.textContent=fmtSize(estSize(it));
    const tdOv=document.createElement('td');
    if(it.ov && Object.keys(it.ov).length){
      const badge=document.createElement('button'); badge.className='btn-mini';
      badge.textContent='已微调'; badge.title='点击修改或清除该文件的独立参数';
      badge.setAttribute('data-ov', i); tdOv.appendChild(badge);
    }else{
      const ob=document.createElement('button'); ob.className='btn-mini';
      ob.textContent='微调'; ob.title='给这个文件单独设置参数';
      ob.setAttribute('data-ov', i); tdOv.appendChild(ob);
    }
    const td6=document.createElement('td');
    const rm=document.createElement('button'); rm.className='btn-mini'; rm.textContent='移除'; rm.setAttribute('data-rm', i);
    td6.appendChild(rm);
    [td0,td1,td2,tdStream,td3,td4,td5,tdOv,td6].forEach(td=>tr.appendChild(td));
    body.appendChild(tr);
  });
  $('qsummary').textContent=`共 ${queue.length} 个, 已选 ${chk} 个 · 原总大小 ${fmtSize(totS)} · 预估压缩后 ${fmtSize(totE)}`;
  updateToolUI();   // 拼接来源提示里要显示当前待处理数量
  const nOv=queue.filter(x=>x.ov && Object.keys(x.ov).length).length;
  $('ovSummary').textContent = nOv ? (`${nOv} 个文件已设置独立参数 (仅对勾选文件生效)`) : '当前没有微调项';
}
$('qbody').addEventListener('click', e=>{
  const rm=e.target.getAttribute('data-rm'); if(rm!==null){ queue.splice(parseInt(rm),1); renderQueue(); return; }
  const ov=e.target.getAttribute('data-ov'); if(ov!==null){ openOv(parseInt(ov)); }
});
$('qbody').addEventListener('change', e=>{
  const i=e.target.getAttribute('data-i'); if(i!==null){ queue[parseInt(i)].checked=e.target.checked; renderQueue(); }
});
$('selall').addEventListener('click', ()=>{ queue.forEach(x=>x.checked=true); renderQueue(); });
$('selnone').addEventListener('click', ()=>{ queue.forEach(x=>x.checked=false); renderQueue(); });
$('qclear').addEventListener('click', ()=>{ queue=[]; renderQueue(); });

/* ---------- v8: 主题 / 磁盘 / 多选文件 / 参数对比 ---------- */
function applyTheme(t){
  const d = t==='dark' ? 'dark' : 'light';
  document.body.setAttribute('data-theme', d);
  $('themeBtn').textContent = d==='dark' ? '切换浅色' : '切换深色';
  try{ localStorage.setItem('vc_theme', d); }catch(e){}
}
$('themeBtn').addEventListener('click', ()=>
  applyTheme(document.body.getAttribute('data-theme')==='dark' ? 'light' : 'dark'));

function dirnameOf(p){
  const s=String(p), bs=String.fromCharCode(92);
  const i=Math.max(s.lastIndexOf(bs), s.lastIndexOf('/'));
  return i>0 ? s.slice(0,i) : s;
}
async function refreshDisk(){
  const dirs=[...new Set(queue.filter(x=>x.checked && x.path).map(x=>dirnameOf(x.path)))];
  if(!dirs.length) dirs.push($('folder').value.trim() || '.');
  try{
    const r=await fetch('/api/disk',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({dirs})});
    const j=await r.json();
    const d=(j.disks||[]).filter(x=>x.free!==undefined);
    if(!d.length) return;
    const minFree=Math.min(...d.map(x=>x.free));
    const txt='输出磁盘可用 '+(minFree/1073741824).toFixed(1)+' GB · 已用 '+d[0].used_pct+'%';
    $('diskInfo').textContent=txt; $('diskInfo2').textContent=txt;
  }catch(e){}
}

$('pickfiles').addEventListener('click', async ()=>{
  const b=$('pickfiles'); b.disabled=true; b.textContent='选择中…';
  try{
    const r=await fetch('/api/pickfiles',{method:'POST'}); const j=await r.json();
    if(j.files && j.files.length){
      const have=new Set(queue.map(x=>x.path));
      j.files.forEach(f=>{ if(!have.has(f.path)) queue.push({...f, checked:true}); });
      renderQueue(); refreshDisk();
    }
  }catch(e){ alert('打开文件选择框失败'); }
  b.disabled=false; b.textContent='添加文件';
});

function infoRows(a,b){
  const rows=[
    ['文件大小', fmtSize(a.size), fmtSize(b.size)],
    ['时长', fmtDur(a.duration), fmtDur(b.duration)],
    ['分辨率', a.width? a.width+'×'+a.height:'-', b.width? b.width+'×'+b.height:'-'],
    ['视频编码', (a.codec||'-').toUpperCase(), (b.codec||'-').toUpperCase()],
    ['像素格式', a.pix_fmt||'-', b.pix_fmt||'-'],
    ['帧率', a.fps? a.fps+' fps':'-', b.fps? b.fps+' fps':'-'],
    ['总码率', a.bitrate? Math.round(a.bitrate/1000)+' kbps':'-', b.bitrate? Math.round(b.bitrate/1000)+' kbps':'-'],
    ['音轨数', a.audio, b.audio], ['字幕数', a.subtitle, b.subtitle],
    ['章节数', a.chapters, b.chapters], ['容器', a.format||'-', b.format||'-'],
    ['色彩', (a.hdr?'HDR · ':'')+(a.color_transfer||a.color_space||'SDR/未标注'),
             (b.hdr?'HDR · ':'')+(b.color_transfer||b.color_space||'SDR/未标注')]
  ];
  return '<table class="info-tbl"><thead><tr><th>项目</th><th>原文件</th><th>输出</th></tr></thead><tbody>'
    + rows.map(r=>'<tr><th>'+r[0]+'</th><td>'+r[1]+'</td><td>'+r[2]+'</td></tr>').join('')
    + '</tbody></table>';
}
async function showInfo(src,out,name){
  $('infoTitle').textContent='参数对比 · '+(name||'');
  $('infoBody').innerHTML='<div class="hint">读取媒体信息中…</div>';
  $('infoModal').style.display='flex';
  try{
    const [ra,rb]=await Promise.all([
      fetch('/api/probe?path='+encodeURIComponent(src)),
      fetch('/api/probe?path='+encodeURIComponent(out))]);
    const [ja,jb]=await Promise.all([ra.json(),rb.json()]);
    if(!ja.ok||!jb.ok){
      $('infoBody').innerHTML='<div class="bad" style="font-size:13px">读取失败: '+(ja.err||jb.err||'文件不可用')+'</div>';
      return;
    }
    $('infoBody').innerHTML=infoRows(ja.info,jb.info)
      +'<div class="hint" style="margin-top:10px">若音轨 / 字幕数减少, 把「流保留策略」改成「完整保留」后重跑即可。</div>';
  }catch(e){ $('infoBody').innerHTML='<div class="bad">请求失败</div>'; }
}
$('infoClose').addEventListener('click', ()=>{ $('infoModal').style.display='none'; });
$('infoModal').addEventListener('click', e=>{ if(e.target===$('infoModal')) $('infoModal').style.display='none'; });

async function loadConfig(){
  try{ applyTheme(localStorage.getItem('vc_theme')||'light'); }catch(e){ applyTheme('light'); }
  const r=await fetch('/api/config'); const c=await r.json();
  HWLabel=c.hw_label||'';
  enhCaps=c.enhance_caps||{};
  const miss=Object.keys(enhCaps).filter(k=>enhCaps[k]===false);
  $('enhCaps').textContent = miss.length ? ('部分滤镜不可用: '+miss.join(', ')) : '增强滤镜: 全部可用';
  $('ffpath').textContent = c.ffmpeg_ok ? ('ffmpeg: '+c.ffmpeg_path) : 'ffmpeg 未找到';
  if(!c.ffmpeg_ok) $('ffwarn').style.display='block';
  const eng=$('engine'); const prev=eng.value; eng.innerHTML='';
  const o0=document.createElement('option'); o0.value='auto'; o0.textContent='自动 (有显卡用硬件, 否则软件, 推荐)'; eng.appendChild(o0);
  const o1=document.createElement('option'); o1.value='software'; o1.textContent='软件编码 (质量优先, 慢)'; eng.appendChild(o1);
  if(c.hw_hevc||c.hw_h264){ const o2=document.createElement('option'); o2.value='hardware'; o2.textContent='强制硬件加速 ('+(HWLabel||'GPU')+')'; eng.appendChild(o2); }
  if(prev) eng.value=prev;
  // v11: 根据可用编码器动态补充 AV1 / VP9 选项
  const codecSel=$('codec'); const codecPrev=codecSel.value;
  if(c.video_codecs && c.video_codecs.av1){
    if(![...codecSel.options].some(o=>o.value==='av1')){
      const o=document.createElement('option'); o.value='av1';
      o.textContent='AV1 (体积更小, 慢, 适合归档)'; codecSel.appendChild(o);
    }
  }
  if(c.video_codecs && c.video_codecs.vp9){
    if(![...codecSel.options].some(o=>o.value==='vp9')){
      const o=document.createElement('option'); o.value='vp9';
      o.textContent='VP9 (体积更小, 慢)'; codecSel.appendChild(o);
    }
  }
  if(codecPrev) codecSel.value=codecPrev;
  window.__audioCaps=c.audio_caps||{};
  window.__fontFound=c.font_found;
  $('cpuHint').textContent = 'CPU: '+(c.cpu_count||'?')+' 逻辑核心 · 检测到硬件: '+(HWLabel||'无');
  $('ptext').textContent = c.portable ? '已便携化 (工具目录内含 ffmpeg)' : '';
  if(c.default_folder && !localStorage.getItem('vc_settings')) $('folder').value=c.default_folder;
  loadSettings();
  // v7 一次性迁移: 老配置里 slow/slower/veryslow 是最大的速度瓶颈, 自动切到提速组合
  if(!localStorage.getItem('vc_v7')){
    if(['slow','slower','veryslow'].includes($('preset').value)) $('preset').value='fast';
    $('engine').value='auto'; $('workers').value='2';
    $('smart_copy').checked=false; $('keep_smaller').checked=true;
    localStorage.setItem('vc_v7','1');
    $('speedNote').textContent='已从旧的慢速预设自动切换到 fast + 2 并发 + 自动硬件引擎。想完全提速请点上方「极速方案」, 想恢复画质可手动改回 slow。';
    saveSettings();
  }
  if(!$('engine').value) $('engine').value='auto';
  if(!$('workers').value) $('workers').value='2';
  if(!$('max_height').value) $('max_height').value='0';
  updateEnhUI(); updateModeUI(); updateAudioUI(); updateWMUI(); updateToolUI(); updateAspectUI();
  const savedPreset=localStorage.getItem('vc_preset'); if(savedPreset && PRESETS[savedPreset]) markPreset(savedPreset);
  const savedEnh=localStorage.getItem('vc_enh_preset'); if(savedEnh && ENH_PRESETS[savedEnh]) markEnhPreset(savedEnh);
  refreshAnalyzeFiles(); loadSchemes(); refreshDisk(); loadHistory();
}

$('mode').addEventListener('change', ()=>{ updateModeUI(); saveSettings(); });
$('crf').addEventListener('input', e=>{ $('crfval').textContent=e.target.value; saveSettings(); renderQueue(); markPreset(''); });
['folder','recursive','force','ratio_pct','target_mb','codec','engine','pix','audio','preset','tune','out_mode','out_sub',
 'workers','max_height','smart_copy_kbps','smart_copy','keep_smaller','auto_open',
 'streams','resume','smart_refine','verify','enh_crop',
 'auto_fallback','quality_target','quality_preset',
 'aspect','aspect_mode','aspect_color','aspect_blur','name_template'].forEach(id=>{
  const el=$(id); if(el){ el.addEventListener('change', ()=>{ saveSettings(); renderQueue(); markPreset(''); }); }
});
$('aspect').addEventListener('change', ()=>{ updateAspectUI(); saveSettings(); renderQueue(); });
$('aspect_mode').addEventListener('change', ()=>{ updateAspectUI(); saveSettings(); renderQueue(); });
$('folder').addEventListener('input', saveSettings);
$('audio').addEventListener('change', ()=>{ updateAudioUI(); });
$('codec').addEventListener('change', ()=>{ updateAudioUI(); renderQueue(); });

// v11 水印与字幕 UI 联动
['wm_type','wm_sub'].forEach(id=>{ const el=$(id); if(el) el.addEventListener('change', updateWMUI); });
// v11 工具箱 UI 联动
$('tb_action').addEventListener('change', updateToolUI);
async function pickFile(inputId){
  try{ const r=await fetch('/api/pickfile',{method:'POST'}); const j=await r.json();
    if(j.ok&&j.path){ $(inputId).value=j.path; } }
  catch(e){ alert('打开选择框失败'); }
}
$('wmImgPick').addEventListener('click', ()=>pickFile('wm_image'));
$('wmSubPick').addEventListener('click', ()=>pickFile('wm_sub_file'));
$('tbSrcPick').addEventListener('click', ()=>pickFile('tb_src'));
$('tbRun').addEventListener('click', async ()=>{
  const act=$('tb_action').value;
  const src=$('tb_src').value.trim();
  let srcs=[];
  if(act==='concat'){
    srcs=(queue||[]).map(x=>x.path).filter(Boolean);
    if(srcs.length<2){ alert('待处理列表中至少需要 2 个视频才能拼接'); return; }
  } else if(!src){ alert('请先选择或填写源文件'); return; }
  const opts={ ss:parseFloat($('tb_ss').value)||0, duration:parseFloat($('tb_dur').value)||0,
    gif_fps:parseInt($('tb_gif_fps').value)||15, gif_w:parseInt($('tb_gif_w').value)||480 };
  $('tbRun').disabled=true; $('tbResult').textContent='处理中…';
  try{
    const r=await fetch('/api/tool',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:act, src, out:$('tb_out').value.trim(), opts, sources:srcs})});
    const j=await r.json();
    if(j.ok){ $('tbResult').textContent='完成: '+j.out+'  ('+((j.info&&j.info.size||0)/1024).toFixed(0)+' KB)'; }
    else { $('tbResult').textContent='失败 (rc='+j.rc+') '+(j.lines&&j.lines[j.lines.length-1]||''); console.log(j.lines); }
  }catch(e){ $('tbResult').textContent='请求失败: '+e.message; }
  $('tbRun').disabled=false;
});

$('pick').addEventListener('click', async ()=>{
  $('pick').textContent='选择中…';
  try{ const r=await fetch('/api/pickfolder',{method:'POST'}); const j=await r.json();
    if(j.ok&&j.path){ $('folder').value=j.path; saveSettings(); } }
  catch(e){ alert('打开选择框失败'); }
  $('pick').textContent='选择文件夹';
});

$('scan').addEventListener('click', async ()=>{
  const folder=$('folder').value.trim();
  if(!folder){ alert('请先选择文件夹'); return; }
  $('scan').disabled=true; $('scan').textContent='扫描中…';
  try{
    const r=await fetch('/api/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({folder,recursive:$('recursive').checked,out_sub:$('out_sub').value||'已压缩'})});
    const j=await r.json();
    if(!j.files || j.files.length===0){ alert('该文件夹未找到视频'); }
    else{
      const have=new Set(queue.map(x=>x.path));
      j.files.forEach(f=>{ if(!have.has(f.path)) queue.push({...f, checked:true}); });
      renderQueue(); refreshDisk();
    }
  }catch(e){ alert('扫描失败'); }
  $('scan').disabled=false; $('scan').textContent='扫描加入';
});

$('ffsetbtn').addEventListener('click', async ()=>{
  const p=$('ffset').value.trim(); if(!p) return;
  const r=await fetch('/api/setffmpeg',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:p})});
  const j=await r.json();
  if(j.ok){ $('ffwarn').style.display='none'; $('ffpath').textContent='ffmpeg: '+p; loadConfig(); }
  else alert(j.error||'设置失败');
});

$('portablebtn').addEventListener('click', async ()=>{
  const b=$('portablebtn'); b.disabled=true; b.textContent='处理中…';
  try{
    const r=await fetch('/api/portable',{method:'POST'}); const j=await r.json();
    if(j.ok){
      $('ptext').textContent='便携化完成';
      $('ffwarn').style.display='none';
      $('ffpath').textContent='ffmpeg: '+(j.ffmpeg_path||'');
      alert('便携化完成:\\n'+(j.items||[]).join('\\n'));
    } else { alert('便携化失败: '+(j.error||'')); }
  }catch(e){ alert('便携化请求失败'); }
  b.disabled=false; b.textContent='制作便携版';
});

$('openlogs').addEventListener('click', async ()=>{ await fetch('/api/openlogs',{method:'POST'}); });

/* ---------- v9: 智能分析 / 参数方案 / 队列 / 输出验收 ---------- */
let lastRecommend=null;
let analyzeBusy=false;

function refreshAnalyzeFiles(){
  const sel=$('analyzeFile'); if(!sel) return;
  const prev=sel.value; sel.innerHTML='';
  if(queue.length===0){
    const o=document.createElement('option'); o.value=''; o.textContent='(请先扫描加入视频)'; sel.appendChild(o); return;
  }
  queue.forEach(it=>{ const o=document.createElement('option'); o.value=it.path; o.textContent=it.name; sel.appendChild(o); });
  if(prev && queue.some(x=>x.path===prev)) sel.value=prev;
}

function statBadges(s){
  const a=[];
  if(s.kbps!==undefined) a.push('码率 '+s.kbps+' kbps');
  if(s.bpp!==undefined) a.push('码率密度 '+s.bpp);
  if(s.yavg!==null&&s.yavg!==undefined) a.push('亮度 '+s.yavg);
  if(s.dynamic!==undefined) a.push('动态范围 '+s.dynamic);
  if(s.ydif!==null&&s.ydif!==undefined) a.push('帧间差 '+s.ydif);
  if(s.satavg!==null&&s.satavg!==undefined) a.push('饱和度 '+s.satavg);
  if(s.undet!==undefined && s.undet>0.5) a.push('隔行: 样本无法判定');
  else if(s.interlaced!==undefined) a.push('隔行置信 '+Math.round(s.interlaced*100)+'%');
  if(s.crop_str) a.push('黑边 '+s.crop_str);
  return a.map(x=>'<span class="an-badge">'+x+'</span>').join('');
}

function applySettings(s){
  if(!s||typeof s!=='object') return;
  for(const k in s){
    const el=$(k); if(!el) continue;
    if(el.type==='checkbox') el.checked=!!s[k]; else el.value=s[k];
  }
  $('crfval').textContent=$('crf').value;
  updateEnhUI(); updateModeUI(); saveSettings(); markPreset('');
}

function renderAnalysis(j){
  const box=$('analyzeResult'); box.style.display='block';
  if(!j.ok){ box.innerHTML='<div class="bad">分析失败: '+(j.err||'未知原因')+'</div>'; return; }
  const i=j.info||{}, s=j.stats||{}, r=j.recommend||{};
  lastRecommend=r; $('adoptBtn').disabled=false;
  $('analyzeState').textContent='分析完成 · '+(j.samples||1)+' 段采样';
  let h='<b>'+(i.width? i.width+'×'+i.height : '?')+' · '+String(i.codec||'?').toUpperCase()
       +' · '+fmtDur(i.duration)+' · '+fmtSize(i.size)+'</b>';
  h+='<div style="margin-top:6px">'+statBadges(s)+'</div>';
  h+='<div style="margin-top:8px"><b>推荐:</b> '+String(r.mode||'crf').toUpperCase()
     +' / '+String(r.codec||'hevc').toUpperCase()+' / CRF '+r.crf+' / '+r.preset+' / '+r.pix
     +'bit · '+r.workers+' 并发 · 验收 '+r.verify
     +((r.enh_on)?(' · 开启增强'+(r.enh_crop?('(裁黑边 '+r.enh_crop+')'):'')):' · 不增强')+'</div>';
  h+='<ul style="margin:6px 0 0 18px;padding:0">'
     +(r.reasons||[]).map(x=>'<li>'+x+'</li>').join('')+'</ul>';
  if((r.warnings||[]).length) h+='<div class="bad" style="margin-top:6px">注意: '+r.warnings.join(' / ')+'</div>';
  box.innerHTML=h;
}

$('analyzeBtn').addEventListener('click', async ()=>{
  const p=$('analyzeFile').value;
  if(!p){ alert('请先扫描加入视频'); return; }
  if(analyzeBusy) return;
  analyzeBusy=true; $('analyzeBtn').disabled=true; $('analyzeState').textContent='采样分析中…';
  try{
    const r=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:p})});
    renderAnalysis(await r.json());
  }catch(e){ $('analyzeState').textContent='分析请求失败'; }
  analyzeBusy=false; $('analyzeBtn').disabled=false;
});

$('analyzeAllBtn').addEventListener('click', async ()=>{
  const paths=queue.filter(x=>x.checked).map(x=>x.path);
  if(!paths.length){ alert('待处理列表为空或未勾选文件'); return; }
  if(analyzeBusy) return;
  analyzeBusy=true; $('analyzeAllBtn').disabled=true; $('analyzeState').textContent='批量分析 '+paths.length+' 个文件…';
  try{
    const r=await fetch('/api/analyze/batch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({paths})});
    const j=await r.json(); const items=j.items||[];
    let h='<b>队列扫描结果 ('+items.length+' 个)</b><table class="an-tbl"><thead><tr>'
         +'<th>文件</th><th>分辨率</th><th>kbps</th><th>黑边</th><th>隔行</th><th>建议 CRF</th><th>建议增强</th>'
         +'</tr></thead><tbody>';
    items.forEach(x=>{
      const nm=x.name||String(x.path||'').split('/').pop()||'-';
      if(!x.ok){ h+='<tr><td>'+nm+'</td><td colspan="6" class="bad">'+(x.err||'分析失败')+'</td></tr>'; return; }
      const i=x.info||{}, s=x.stats||{}, r=x.recommend||{};
      h+='<tr><td>'+nm+'</td><td>'+(i.width||'?')+'×'+(i.height||'?')+'</td><td>'+(s.kbps||'-')+'</td>'
        +'<td>'+(s.crop_str||'无')+'</td><td>'+Math.round((s.interlaced||0)*100)+'%</td>'
        +'<td>'+(r.crf||'-')+'</td><td>'+(r.enh_on? '是':'否')+'</td></tr>';
    });
    h+='</tbody></table><div class="hint" style="margin-top:6px">「一键采用」将套用第一个文件的推荐; 想针对单个文件精细调参请改用「分析选中文件」。</div>';
    const first=items.find(x=>x.ok&&x.recommend);
    if(first){ lastRecommend=first.recommend; $('adoptBtn').disabled=false; }
    $('analyzeResult').style.display='block'; $('analyzeResult').innerHTML=h;
    $('analyzeState').textContent='批量分析完成';
  }catch(e){ $('analyzeState').textContent='批量分析失败'; }
  analyzeBusy=false; $('analyzeAllBtn').disabled=false;
});

$('adoptBtn').addEventListener('click', ()=>{
  if(!lastRecommend) return;
  applySettings(lastRecommend);
  $('analyzeState').textContent='已采用推荐参数, 可直接开始压缩';
});

async function loadSchemes(){
  try{
    const j=await (await fetch('/api/schemes')).json();
    const all=j.schemes||{}; const sel=$('schemeSel'); const prev=sel.value;
    sel.innerHTML='';
    const o=document.createElement('option'); o.value='';
    o.textContent=Object.keys(all).length? '(选择一个已保存方案)' : '(暂无方案, 点「保存当前」新建)';
    sel.appendChild(o);
    Object.keys(all).forEach(k=>{
      const x=document.createElement('option'); x.value=k;
      x.textContent=k+' · '+((all[k]||{}).saved_at||''); sel.appendChild(x);
    });
    if(prev && all[prev]) sel.value=prev;
    return all;
  }catch(e){ return {}; }
}

$('schemeSave').addEventListener('click', async ()=>{
  const name=(prompt('给这套参数起个名字 (如: 壁纸方案 / 老片修复):', $('schemeSel').value||'')||'').trim();
  if(!name) return;
  try{
    const r=await fetch('/api/schemes',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'save',name,settings:gather()})});
    const j=await r.json();
    $('schemeState').textContent= j.ok? ('已保存方案: '+name) : ('保存失败: '+(j.error||''));
    await loadSchemes(); if(j.ok) $('schemeSel').value=name;
  }catch(e){ $('schemeState').textContent='保存请求失败'; }
});

$('schemeApply').addEventListener('click', async ()=>{
  const name=$('schemeSel').value; if(!name){ alert('请先选择一个方案'); return; }
  const all=await loadSchemes(); const s=(all[name]||{}).settings;
  if(!s){ alert('方案内容为空'); return; }
  applySettings(s); $('schemeState').textContent='已应用方案: '+name;
});

$('schemeDel').addEventListener('click', async ()=>{
  const name=$('schemeSel').value; if(!name) return;
  if(!confirm('确定删除方案「'+name+'」?')) return;
  try{
    await fetch('/api/schemes',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'delete',name})});
    $('schemeState').textContent='已删除: '+name; await loadSchemes();
  }catch(e){ $('schemeState').textContent='删除失败'; }
});

$('queueExport').addEventListener('click', ()=>{
  if(!queue.length){ alert('队列为空'); return; }
  const d={tool:'video_compressor',version:12,saved_at:new Date().toISOString(),files:queue.map(x=>x.path)};
  const b=new Blob([JSON.stringify(d,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='视频队列.json';
  document.body.appendChild(a); a.click(); a.remove();
  $('schemeState').textContent='已导出 '+queue.length+' 个文件路径';
});
$('queueImport').addEventListener('click', ()=>{ $('queueFile').click(); });
$('queueFile').addEventListener('change', async e=>{
  const f=e.target.files[0]; if(!f) return;
  try{
    const d=JSON.parse(await f.text());
    const paths=Array.isArray(d)? d : (d.files||[]);
    const r=await fetch('/api/queue/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({files:paths})});
    const j=await r.json();
    const have=new Set(queue.map(x=>x.path)); let add=0;
    (j.files||[]).forEach(x=>{ if(!have.has(x.path)){ queue.push({...x,checked:true}); have.add(x.path); add++; } });
    renderQueue(); refreshDisk();
    $('schemeState').textContent='导入 '+add+' 个'
      +((j.missing||[]).length? (' · '+(j.missing||[]).length+' 个路径已失效'):'');
  }catch(err){ alert('导入失败: 不是有效的队列 JSON'); }
  e.target.value='';
});

function showVerify(x){
  const v=x.verify;
  $('infoTitle').textContent='输出验收 · '+(x.name||'');
  if(!v){
    $('infoBody').innerHTML='<div class="hint">本次未开启输出验收, 或该文件属于跳过 / 保留原片。</div>';
  }else{
    let h='<div style="font-size:15px;margin-bottom:8px" class="'+(v.ok?'ok':'bad')+'">'+v.label
         +' <span class="hint">('+(v.level||'')+')</span></div>';
    h+='<table class="info-tbl"><thead><tr><th>检查项</th><th>结果</th><th>详情</th></tr></thead><tbody>';
    (v.checks||[]).forEach(c=>{
      h+='<tr><th>'+c.name+'</th><td class="'+(c.ok?'ok':'bad')+'">'+(c.ok?'通过':'异常')+'</td><td>'
        +String(c.detail||'').replace(/</g,'&lt;')+'</td></tr>';
    });
    h+='</tbody></table><div style="margin-top:10px"><button class="btn-mini" id="reverifyBtn">重新验收</button></div>';
    $('infoBody').innerHTML=h;
    const b=$('reverifyBtn');
    if(b) b.addEventListener('click', async ()=>{
      b.disabled=true; b.textContent='检查中…';
      try{
        const r=await fetch('/api/verify',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({src:x.src,out:x.out,level:$('verify').value,
            opts:{audio:$('audio').value,streams:$('streams').value}})});
        const nv=await r.json();
        const k=lastResults.findIndex(y=>y.src===x.src&&y.out===x.out);
        if(k>=0) lastResults[k].verify=nv;
        showVerify({...x,verify:nv}); renderResults();
      }catch(e){ alert('复验失败'); b.disabled=false; b.textContent='重新验收'; }
    });
  }
  $('infoModal').style.display='flex';
}


let timer=null;
async function beginJob(payload){
  const post = p => fetch('/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
  let j = await (await post(payload)).json();
  if(!j.ok && j.disk){
    if(!confirm(j.error+String.fromCharCode(10)+'仍要忽略空间检查继续吗? (磁盘写满可能导致部分文件失败)')) return false;
    j = await (await post({...payload, ignore_disk:true})).json();
  }
  if(!j.ok){ alert(j.error||'启动失败'); return false; }
  lastPayload=payload; qmap={}; lastResults=[];
  $('resultCard').style.display='block';
  $('start').disabled=true; $('stop').style.display='inline-block';
  $('openout').style.display='none'; $('export').style.display='none';
  $('retrybtn').style.display='none'; $('resultSummary').textContent='';
  if(timer) clearInterval(timer); timer=setInterval(poll,800);
  return true;
}
$('start').addEventListener('click', async ()=>{
  const files=queue.filter(x=>x.checked).map(x=>x.path);
  if(files.length===0){ alert('待处理列表为空或未勾选文件, 请先扫描加入'); return; }
  const payload = {
    files, recursive:$('recursive').checked, force:$('force').checked,
    mode:$('mode').value, ratio:(parseFloat($('ratio_pct').value)||30)/100, target_mb:parseFloat($('target_mb').value)||50,
    codec:$('codec').value, engine:$('engine').value, pix:$('pix').value, audio:$('audio').value,
    preset:$('preset').value, crf:parseInt($('crf').value), tune:$('tune').value,
    out_mode:$('out_mode').value, out_sub:$('out_sub').value,
    workers:parseInt($('workers').value)||2, max_height:parseInt($('max_height').value)||0,
    smart_copy:$('smart_copy').checked, smart_copy_kbps:parseFloat($('smart_copy_kbps').value)||1200,
    keep_smaller:$('keep_smaller').checked, auto_open:$('auto_open').checked,
    streams:$('streams').value, resume:$('resume').checked, smart_refine:$('smart_refine').checked,
    verify:$('verify').value,
    auto_fallback:$('auto_fallback').checked,
    quality_target:parseFloat($('quality_target').value)||0.99,
    name_template:$('name_template').value.trim(),
    ...gatherEnh(), ...gatherAudio(), ...gatherWM(), ...gatherAspect()
  };
  const overrides={};
  queue.filter(x=>x.checked).forEach(x=>{ if(x.ov && Object.keys(x.ov).length) overrides[x.path]=x.ov; });
  payload.overrides=overrides;
  await beginJob(payload);
});
$('retrybtn').addEventListener('click', async ()=>{
  if(!lastPayload) return;
  const failed=(lastResults||[]).filter(x=>x.src && (!x.after || (x.status||'').indexOf('失败')===0)).map(x=>x.src);
  if(!failed.length){ alert('没有失败项'); return; }
  if(!confirm('用相同参数重试 '+failed.length+' 个失败文件?')) return;
  await beginJob({...lastPayload, files:failed, force:true});
});
$('stop').addEventListener('click', async ()=>{ await fetch('/api/stop',{method:'POST'}); });
$('openout').addEventListener('click', async ()=>{
  const r=await fetch('/api/status'); const s=await r.json();
  if(s.out_folder) await fetch('/api/openoutput',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:s.out_folder})});
});
$('export').addEventListener('click', async ()=>{
  const r=await fetch('/api/export'); const b=await r.blob();
  const a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='压缩报告.csv'; document.body.appendChild(a); a.click(); a.remove();
});

let cmpState={src:'',out:'',dur:0};
function cmpSetSplit(pct){
  pct=Math.max(0,Math.min(100,pct));
  const st=$('cmpStage');
  if(st){ $('cmpClip').style.left=pct+'%'; $('cmpHandle').style.left=pct+'%'; }
}
function cmpTime(){
  const dur=cmpState.dur||0;
  const r=parseInt($('cmpT').value||'500',10)/1000;
  return dur>0? dur*r : 0;
}
async function cmpLoadFrames(){
  if(!cmpState.src||!cmpState.out) return;
  const w=$('cmpZoom').value||'720';
  const t=cmpTime();
  $('cmpTv').textContent=cmpState.dur>0? t.toFixed(2)+'s / '+cmpState.dur.toFixed(2)+'s' : t.toFixed(2)+'s';
  $('imgA').src='/api/frame?path='+encodeURIComponent(cmpState.src)+'&t='+t+'&w='+w+'&_='+Date.now();
  $('imgB').src='/api/frame?path='+encodeURIComponent(cmpState.out)+'&t='+t+'&w='+w+'&_='+Date.now();
}
async function showCompare(src,out,title){
  cmpState.src=src; cmpState.out=out; cmpState.dur=0;
  $('cmpTitle').textContent=title||'画质对比';
  $('cmpMetric').textContent='正在评估画质…';
  $('cmpModal').style.display='flex';
  cmpSetSplit(50);
  try{
    const r=await fetch('/api/probe?path='+encodeURIComponent(src));
    const info=await r.json();
    cmpState.dur=(info&&info.duration)||0;
  }catch(e){}
  cmpLoadFrames();
  try{
    const q=await calcQuality(src,out);
    if(q&&q.ok){
      $('cmpMetric').innerHTML='SSIM <b>'+q.ssim.toFixed(5)+'</b> · PSNR <b>'+(q.psnr===null?'-':q.psnr.toFixed(2))+'</b> dB · '+(q.verdict||verdictOf(q.ssim));
    } else { $('cmpMetric').textContent=(q&&q.err)||'画质评估失败'; }
  }catch(e){ $('cmpMetric').textContent=''; }
}
(function(){
  const st=$('cmpStage');
  let dragging=false;
  function fromEvent(e){
    const r=st.getBoundingClientRect();
    const x=(e.touches&&e.touches[0]? e.touches[0].clientX : e.clientX);
    return (x-r.left)/r.width*100;
  }
  st.addEventListener('mousedown', e=>{ dragging=true; cmpSetSplit(fromEvent(e)); e.preventDefault(); });
  window.addEventListener('mousemove', e=>{ if(dragging) cmpSetSplit(fromEvent(e)); });
  window.addEventListener('mouseup', ()=>{ dragging=false; });
  st.addEventListener('touchstart', e=>{ dragging=true; cmpSetSplit(fromEvent(e)); }, {passive:true});
  st.addEventListener('touchmove', e=>{ if(dragging){ cmpSetSplit(fromEvent(e)); e.preventDefault(); } }, {passive:false});
  st.addEventListener('touchend', ()=>{ dragging=false; });
})();
$('cmpT').addEventListener('input', ()=>{ cmpLoadFrames(); });
$('cmpZoom').addEventListener('change', ()=>{ cmpLoadFrames(); });
$('cmpReload').addEventListener('click', ()=>{ cmpLoadFrames(); });
$('cmpClose').addEventListener('click', ()=>{ $('cmpModal').style.display='none'; });
$('cmpModal').addEventListener('click', e=>{ if(e.target===$('cmpModal')) $('cmpModal').style.display='none'; });
$('qmClose').addEventListener('click', ()=>{ $('qmModal').style.display='none'; });
$('qmModal').addEventListener('click', e=>{ if(e.target===$('qmModal')) $('qmModal').style.display='none'; });

function verdictOf(s){
  if(s===null||s===undefined) return '';
  if(s>=0.995) return '肉眼完全无法分辨';
  if(s>=0.99) return '几乎无差异 (推荐范围)';
  if(s>=0.98) return '需放大对比才能看出';
  if(s>=0.95) return '轻微损失, 静态观看不易发现';
  if(s>=0.90) return '可察觉损失, 建议降低 CRF';
  return '损失明显, 建议降低 CRF 或提高压缩比';
}
async function calcQuality(src,out,limit){
  const r=await fetch('/api/quality?src='+encodeURIComponent(src)+'&out='+encodeURIComponent(out)+'&limit='+(limit||10));
  return await r.json();
}
function showQuality(name, q){
  $('qmTitle').textContent='画质评估 · '+(name||'');
  if(!q || !q.ok){
    $('qmBody').innerHTML='<div class="bad" style="font-size:13px">'+(q&&q.err? q.err : '评估失败')+'</div>';
  } else {
    const s=q.ssim, p=q.psnr;
    $('qmBody').innerHTML=
      '<div class="qm-row">'+
        '<div><div class="qm-lbl">SSIM 结构相似度 (1 为完全一致)</div><div class="qm-big"><b>'+s.toFixed(5)+'</b></div></div>'+
        '<div><div class="qm-lbl">PSNR 峰值信噪比 (越高越好, >40dB 优秀)</div><div class="qm-big"><b>'+(p===null?'-':p.toFixed(2))+'</b> <span class="hint">dB</span></div></div>'+
      '</div>'+
      '<div style="font-size:13px;margin-top:6px">评价: <b class="ok">'+(q.verdict||verdictOf(s))+'</b></div>'+
      '<div class="hint" style="margin-top:10px">比较范围: 前 '+(q.limit||10)+' 秒 · 原生分辨率逐帧比对。SSIM 0.99 以上视觉无损。</div>';
  }
  $('qmModal').style.display='flex';
}

function renderResults(){
  const tb=$('resultBody'); tb.innerHTML='';
  let sumB=0,sumA=0,n=0,nok=0;
  (lastResults||[]).forEach(x=>{
    const ok=x.status&&x.status.indexOf('完成')===0;
    n++;
    if(x.after>0){ nok++; sumB+=x.before||0; sumA+=x.after||0; }
    const tr=document.createElement('tr');
    const tdName=document.createElement('td'); tdName.textContent=x.name;
    if(x.src && x.out){
      tdName.className='linkish'; tdName.title='点击查看压缩前后的完整参数对比';
      tdName.addEventListener('click', ()=> showInfo(x.src,x.out,x.name));
    }
    const tdB=document.createElement('td'); tdB.textContent=fmtSize(x.before);
    const tdA=document.createElement('td'); tdA.textContent=fmtSize(x.after);
    const tdP=document.createElement('td'); tdP.textContent= x.pct? x.pct+'%' : '';
    const tdS=document.createElement('td'); tdS.textContent=x.status||''; tdS.className= ok?'ok':'bad';
    tdS.title=[x.fallback||'', (x.mode==='quality'?('画质目标 SSIM≥'+(x.quality_target||0.99)):'')]
      .filter(Boolean).join(' · ');
    const tdV=document.createElement('td');
    if(x.verify){
      const sp=document.createElement('span'); sp.className='vchk '+(x.verify.ok?'ok':'bad');
      sp.textContent=x.verify.label; sp.title='点击查看逐项验收结果';
      sp.addEventListener('click', ()=> showVerify(x));
      tdV.appendChild(sp);
    }else if(ok && x.src && x.out){
      const vb=document.createElement('button'); vb.className='btn-mini'; vb.textContent='验收';
      vb.addEventListener('click', async ()=>{
        vb.disabled=true; vb.textContent='检查中…';
        const lv=$('verify').value==='off'? 'quick' : $('verify').value;
        try{
          const r=await fetch('/api/verify',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({src:x.src,out:x.out,level:lv,
              opts:{audio:$('audio').value,streams:$('streams').value}})});
          const nv=await r.json();
          const k=lastResults.findIndex(y=>y.src===x.src&&y.out===x.out);
          if(k>=0) lastResults[k].verify=nv;
          renderResults(); showVerify({...x,verify:nv});
        }catch(e){ vb.disabled=false; vb.textContent='验收'; alert('验收请求失败'); }
      });
      tdV.appendChild(vb);
    }
    const tdQ=document.createElement('td'), tdC=document.createElement('td');
    if(ok && x.src && x.out){
      const q=qmap[x.out];
      if(q && q.ok){
        const sp=document.createElement('span'); sp.className='ok'; sp.textContent='SSIM '+q.ssim.toFixed(4);
        sp.title='PSNR '+(q.psnr===null?'-':q.psnr)+' dB · '+(q.verdict||'');
        sp.style.cursor='pointer';
        sp.addEventListener('click', ()=> showQuality(x.name,q));
        tdQ.appendChild(sp);
      } else {
        const b=document.createElement('button'); b.className='btn-mini'; b.textContent='测画质';
        b.addEventListener('click', async ()=>{
          b.disabled=true; b.textContent='计算中…';
          try{ const q2=await calcQuality(x.src,x.out); if(q2.ok){ qmap[x.out]=q2; renderResults(); showQuality(x.name,q2); } else { b.disabled=false; b.textContent='测画质'; alert(q2.err||'评估失败'); } }
          catch(e){ b.disabled=false; b.textContent='测画质'; alert('评估请求失败'); }
        });
        tdQ.appendChild(b);
      }
      const cb=document.createElement('button'); cb.className='btn-mini'; cb.textContent='对比';
      cb.addEventListener('click', ()=> showCompare(x.src,x.out,x.name));
      tdC.appendChild(cb);
    }
    [tdName,tdB,tdA,tdP,tdS,tdV,tdQ,tdC].forEach(td=>tr.appendChild(td));
    tb.appendChild(tr);
  });
  if(n){
    const save = sumB? (100-sumA/sumB*100) : 0;
    const badTxt = (n-nok)>0 ? ` · 失败/中止 ${n-nok} 个` : '';
    $('resultSummary').textContent=`成功 ${nok} 个 · 原 ${fmtSize(sumB)} → 压缩后 ${fmtSize(sumA)} · 节省 ${save.toFixed(1)}%${badTxt}`;
  }
}

$('evalall').addEventListener('click', async ()=>{
  const items=(lastResults||[]).filter(x=>x.status&&x.status.indexOf('完成')===0&&x.src&&x.out&&!qmap[x.out]);
  if(!items.length){ alert('没有需要评估的文件(可能已全部评估)'); return; }
  const b=$('evalall'); b.disabled=true;
  for(let i=0;i<items.length;i++){
    b.textContent=`评估中 ${i+1}/${items.length}`;
    try{ const q=await calcQuality(items[i].src,items[i].out); if(q.ok) qmap[items[i].out]=q; }catch(e){}
    renderResults();
  }
  b.disabled=false; b.textContent='一键测画质 (SSIM/PSNR)';
});

async function poll(){
  const r=await fetch('/api/status'); const s=await r.json();
  $('overallBar').style.width=(s.overall_pct||0)+'%';
  $('overallText').textContent = s.running ? ('总进度: '+s.overall_pct+'%  ('+(s.finished||0)+'/'+s.total+') · '+(s.workers||1)+' 并发') : (s.total?'已完成 100%':'空闲');
  const names=s.active_names||[];
  $('curText').textContent = names.length ? ('并行 '+names.length+' 个: '+names.slice(0,2).join(' / ')+(names.length>2?' …':'')+' · 单任务 '+s.current_pct+'%') : '';
  $('curBar').style.width=(s.current_pct||0)+'%';
  $('etaText').textContent = (s.eta?('预计剩余: '+s.eta):'')+(s.speed?(' · 平均 '+s.speed+'× 实时'):'');
  $('enhUsed').textContent = s.enhance_label ? ('本次增强: '+s.enhance_label) : '';
  const lg=$('log'); lg.textContent=(s.log||[]).join('\\n'); lg.scrollTop=lg.scrollHeight;
  $('logpath').textContent = s.log_file ? ('日志: '+s.log_file.split(/[\\\\\\/]/).pop()) : '';
  lastResults = s.results||[];
  const nfailed=lastResults.filter(x=>!x.after||(x.status||'').indexOf('失败')===0).length;
  $('retrybtn').style.display = (!s.running && nfailed) ? 'inline-block' : 'none';
  renderResults();
  if(!s.running && s.total){ $('start').disabled=false; $('stop').style.display='none'; if(timer){clearInterval(timer);timer=null;} if(s.out_folder) $('openout').style.display='inline-block'; $('export').style.display='inline-block'; loadHistory(); }
}
/* ---------- v10: 画质目标 / 逐文件微调 / 任务历史 ---------- */
function refreshQualityFiles(){
  const sel=$('qualityFile'); if(!sel) return;
  const prev=sel.value; sel.innerHTML='';
  if(queue.length===0){ const o=document.createElement('option'); o.value=''; o.textContent='(请先扫描加入视频)'; sel.appendChild(o); return; }
  queue.forEach(it=>{ const o=document.createElement('option'); o.value=it.path; o.textContent=it.name; sel.appendChild(o); });
  if(prev && queue.some(x=>x.path===prev)) sel.value=prev;
}
$('quality_preset').addEventListener('change', ()=>{
  const v=QL[$('quality_preset').value];
  if(v) $('quality_target').value=v.toFixed(3);
  saveSettings(); renderQueue();
});
$('quality_target').addEventListener('input', ()=>{
  $('quality_preset').value='custom'; saveSettings(); renderQueue();
});
$('qprobeBtn').addEventListener('click', async ()=>{
  const p=$('qualityFile').value;
  if(!p){ alert('请先扫描加入视频, 再选择要试算的文件'); return; }
  const b=$('qprobeBtn'); b.disabled=true; b.textContent='试算中…';
  $('qprobeState').textContent='抽段试压 3 档 CRF 并计算 SSIM…';
  const box=$('qprobeResult'); box.style.display='block';
  try{
    const r=await fetch('/api/quality/probe',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({path:p,
        opts:{...gather(), max_height:parseInt($('max_height').value)||0},
        quality_target:parseFloat($('quality_target').value)||0.99})});
    const j=await r.json();
    if(!j.ok){
      box.innerHTML='<div class="bad">试算失败: '+String(j.err||'未知原因').replace(/</g,'&lt;')+'</div>';
      $('qprobeState').textContent='试算失败';
    }else{
      const t=parseFloat($('quality_target').value)||0.99;
      let h='<b>画质曲线</b> · 目标 SSIM '+t.toFixed(4)+' · 采样 '+(j.points||[]).length+' 档'
            +' · 采样外推全片约 '+(j.est_mb||0)+' MB <span class="hint">(仅供参考)</span>';
      h+='<table class="an-tbl" style="margin-top:6px"><thead><tr><th>CRF</th><th>实测 SSIM</th><th>采样体积</th><th>是否达标</th></tr></thead><tbody>';
      (j.points||[]).forEach(pt=>{
        const good=Number(pt.ssim)>=t;
        h+='<tr><td>'+pt.crf+'</td><td>'+Number(pt.ssim).toFixed(5)+'</td><td>'+fmtSize((pt.sample_kb||0)*1024)+'</td>'
          +'<td class="'+(good?'ok':'bad')+'">'+(good?'达标':'不足')+'</td></tr>';
      });
      h+='</tbody></table>';
      h+='<div style="margin-top:8px"><b>推荐 CRF '+j.crf+'</b> <span class="hint">'+(j.level||'')+'</span> '
        +'<button class="btn-mini" id="qAdoptBtn">切到 CRF 模式并采用</button></div>';
      h+='<div class="hint" style="margin-top:6px">保持「画质目标」模式时, 正式压缩会重新试压一遍以适配当前片源; '
        +'想跳过试压直接用这个 CRF 可点上面的按钮。</div>';
      if(j.vf) h+='<div class="hint" style="margin-top:4px">当前滤镜链: '+String(j.vf).replace(/</g,'&lt;')+'</div>';
      box.innerHTML=h;
      const ab=$('qAdoptBtn');
      if(ab) ab.addEventListener('click', ()=>{
        $('mode').value='crf'; $('crf').value=Math.max(16,Math.min(32,Math.round(j.crf)));
        $('crfval').textContent=$('crf').value;
        updateModeUI(); saveSettings(); markPreset('');
        $('qprobeState').textContent='已采用 CRF '+$('crf').value;
      });
      $('qprobeState').textContent='试算完成';
    }
  }catch(e){
    box.innerHTML='<div class="bad">试算请求失败: '+String(e).replace(/</g,'&lt;')+'</div>';
    $('qprobeState').textContent='试算请求失败';
  }
  b.disabled=false; b.textContent='试算画质曲线';
});

function openOv(i){
  if(!queue[i]) return;
  ovIndex=i; const it=queue[i], ov=it.ov||{};
  $('ovTitle').textContent='逐文件微调 · '+it.name;
  const put=(id,key)=>{ $(id).value = (ov[key]===undefined||ov[key]===null)?'':ov[key]; };
  put('ov_crf','crf'); put('ov_target_mb','target_mb'); put('ov_max_height','max_height');
  put('ov_quality_target','quality_target'); put('ov_enh_crop','enh_crop');
  $('ov_enh_on').value = ov.enh_on===undefined? '' : (ov.enh_on?'1':'0');
  $('ov_crop_off').checked = Object.prototype.hasOwnProperty.call(ov,'enh_crop') && ov.enh_crop==='';
  $('ovModal').style.display='flex';
}
$('ovClose').addEventListener('click', ()=>{ $('ovModal').style.display='none'; });
$('ovModal').addEventListener('click', e=>{ if(e.target===$('ovModal')) $('ovModal').style.display='none'; });
$('ovSave').addEventListener('click', ()=>{
  if(ovIndex<0 || !queue[ovIndex]) return;
  const ov={};
  const num=(id,k)=>{ const v=String($(id).value||'').trim(); if(v!==''){ const x=parseFloat(v); if(!isNaN(x)) ov[k]=x; } };
  num('ov_crf','crf'); num('ov_target_mb','target_mb'); num('ov_max_height','max_height');
  num('ov_quality_target','quality_target');
  const crop=String($('ov_enh_crop').value||'').trim();
  if($('ov_crop_off').checked) ov.enh_crop='';
  else if(crop){
    const parts=crop.split(':');
    const ok=parts.length===4 && parts.every(x=>x!=='' && !isNaN(Number(x)) && Number(x)>=0);
    if(!ok){ alert('裁黑边格式应为 W:H:X:Y (四个非负整数)'); return; }
    ov.enh_crop=crop;
  }
  const e=$('ov_enh_on').value;
  if(e!=='') ov.enh_on = (e==='1');
  if(Object.keys(ov).length) queue[ovIndex].ov=ov; else delete queue[ovIndex].ov;
  $('ovModal').style.display='none'; renderQueue();
});
$('ovReset').addEventListener('click', ()=>{
  if(ovIndex<0 || !queue[ovIndex]) return;
  delete queue[ovIndex].ov; $('ovModal').style.display='none'; renderQueue();
});
$('ovClearAll').addEventListener('click', ()=>{
  if(!queue.some(x=>x.ov)){ alert('没有微调项'); return; }
  if(!confirm('清除所有文件的独立参数?')) return;
  queue.forEach(x=>{ delete x.ov; }); renderQueue();
});

async function loadHistory(){
  try{
    const j=await (await fetch('/api/history',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({limit:60})})).json();
    lastHistory=j.items||[]; renderHistory(j.stats||{});
  }catch(e){}
}
function renderHistory(s){
  const k=(label,val)=>'<div class="hist-kpi"><span>'+label+'</span><b>'+val+'</b></div>';
  $('histStats').innerHTML = k('累计任务',s.jobs||0)+k('处理文件',s.files||0)
    +k('成功 / 失败',(s.ok||0)+' / '+(s.failed||0))
    +k('累计节省',fmtSize(s.saved_bytes||0))
    +k('平均节省率',(s.saved_pct||0)+'%')
    +k('平均倍速',(s.avg_speed||0)+'×');
  const bars=$('histBars'); bars.innerHTML='';
  if(!lastHistory.length){ $('histBody').innerHTML='<div class="hint">暂无历史记录, 完成一次任务后会自动出现。</div>'; return; }
  lastHistory.slice(0,20).reverse().forEach(h=>{
    const d=document.createElement('div'); d.className='hist-bar';
    const p=Math.max(2,Math.min(100,Number(h.saved_pct)||0));
    d.style.height=(p/100*54)+'px';
    d.title=(h.ts||'')+' · 节省 '+(h.saved_pct||0)+'% · '+(h.ok||0)+'/'+(h.total||0)+' 成功';
    bars.appendChild(d);
  });
  let h='<table class="an-tbl"><thead><tr><th>时间</th><th>模式</th><th>文件</th><th>成功</th><th>原始 → 结果</th><th>节省</th><th>耗时</th></tr></thead><tbody>';
  lastHistory.slice(0,10).forEach(x=>{
    h+='<tr><td>'+(x.ts||'-')+'</td><td>'+String(x.mode||'-').toUpperCase()
      +(x.mode==='quality'?(' (SSIM '+(x.quality_target||0.99)+')'):'')+'</td>'
      +'<td>'+(x.total||0)+'</td><td>'+(x.ok||0)+'</td>'
      +'<td>'+fmtSize(x.before)+' → '+fmtSize(x.after)+'</td>'
      +'<td class="ok">'+(x.saved_pct||0)+'%</td><td>'+(x.elapsed||0)+'s</td></tr>';
  });
  h+='</tbody></table>';
  $('histBody').innerHTML=h;
}
$('histRefresh').addEventListener('click', loadHistory);
$('histExport').addEventListener('click', ()=>{
  if(!lastHistory.length){ alert('暂无历史可导出'); return; }
  const d={tool:'video_compressor',version:12,exported_at:new Date().toISOString(),jobs:lastHistory};
  const b=new Blob([JSON.stringify(d,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='压缩历史.json';
  document.body.appendChild(a); a.click(); a.remove();
});
$('histClear').addEventListener('click', async ()=>{
  if(!confirm('确定清空全部任务历史? (不影响已压缩的视频文件)')) return;
  try{
    await fetch('/api/history',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'clear'})});
    await loadHistory();
  }catch(e){ alert('清空失败'); }
});

loadConfig();
</script>
</body>
</html>"""


def cli_main(argv=None):
    """无界面批处理: 不启浏览器、不弹窗, 适合定时任务 / 脚本 / 服务器。"""
    import argparse
    import sys as _sys
    CLI_MODE["on"] = True
    ap = argparse.ArgumentParser(
        prog="video_compressor.py --cli",
        description="视频压缩工具 v12 命令行模式 (与网页界面共用同一套编码逻辑)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python video_compressor.py --cli -i \"D:\\videos\" --recursive --scheme 壁纸方案\n"
               "  python video_compressor.py --cli -i a.mp4 b.mp4 --crf 26 --workers 3 --verify full\n"
               "  python video_compressor.py --cli -i a.mp4 --mode quality --quality-target 0.99\n"
               "  python video_compressor.py --cli -i a.mp4 --audio reencode --audio-normalize -16 --audio-denoise light\n"
               "  python video_compressor.py --cli -i a.mp4 --codec av1 --crf 30\n"
               "  python video_compressor.py --cli --tool gif --tool-src a.mp4 --tool-ss 3 --tool-duration 5 --tool-gif-w 480\n"
               "  python video_compressor.py --cli --list-schemes")
    ap.add_argument("-i", "--input", nargs="+", default=[], help="视频文件或目录 (可多个)")
    ap.add_argument("--recursive", action="store_true", help="目录输入时包含子文件夹")
    ap.add_argument("--out-mode", choices=["sub", "overwrite"], default="sub",
                    help="输出到子文件夹 / 覆盖原文件 (默认 sub)")
    ap.add_argument("--out-sub", default="已压缩", help="输出子文件夹名")
    ap.add_argument("--scheme", default="", help="加载网页里保存的命名参数方案")
    ap.add_argument("--list-schemes", action="store_true", help="列出已保存方案后退出")
    ap.add_argument("--mode", choices=["crf", "ratio", "size", "smart", "quality"],
                    help="压缩模式 (quality=按目标 SSIM 自动选 CRF)")
    ap.add_argument("--quality-target", type=float,
                    help="画质目标 SSIM 0.80-0.9999 (仅 --mode quality, 默认 0.99)")
    ap.add_argument("--no-fallback", action="store_true", help="关闭编码失败自动降级重试")
    ap.add_argument("--crf", type=int, help="CRF 值 (0-51, 越大越小)")
    ap.add_argument("--codec", choices=["hevc", "h264", "av1", "vp9"],
                    help="视频编码 (av1/vp9 体积更小但更慢, 需本机 ffmpeg 支持)")
    ap.add_argument("--pix", choices=["8", "10"], help="位深")
    ap.add_argument("--audio", choices=["copy", "strip", "reencode"], help="音轨处理")
    # v11 音频增强
    ap.add_argument("--audio-bitrate", type=int, help="音频码率 kbps (reencode 时, 32-512)")
    ap.add_argument("--audio-samplerate", type=int, help="音频采样率 Hz (如 44100/48000, 0=保持)")
    ap.add_argument("--audio-channels", type=int, help="音频声道数 (1=单声道, 2=立体声, 0=保持)")
    ap.add_argument("--audio-normalize", choices=["off", "-14", "-16"],
                    help="音量归一化目标响度 (-14 流媒体 / -16 语音)")
    ap.add_argument("--audio-denoise", choices=["off", "light", "strong"], help="音频降噪")
    ap.add_argument("--preset", help="编码预设, 如 ultrafast/fast/medium/slow")
    ap.add_argument("--tune", help="x264/x265 tune, 如 animation/none")
    ap.add_argument("--engine", choices=["auto", "software", "hardware"], help="编码引擎")
    ap.add_argument("--target-mb", type=float, help="目标体积 MB (size/smart 模式)")
    ap.add_argument("--ratio-pct", type=float, help="目标压缩比 %% (ratio 模式)")
    ap.add_argument("--workers", type=int, help="并行数 1-4")
    ap.add_argument("--max-height", type=int, help="限高像素 (0=不限)")
    ap.add_argument("--streams", choices=["single", "allaudio", "all"], help="流保留策略")
    ap.add_argument("--verify", choices=["off", "quick", "full"],
                    help="输出验收: 关 / 抽3段解码 / 整片解码")
    ap.add_argument("--force", action="store_true", help="强制覆盖已存在的输出")
    ap.add_argument("--no-resume", action="store_true", help="关闭断点续跑")
    ap.add_argument("--no-keep-smaller", action="store_true", help="关闭「变大保留原片」")
    ap.add_argument("--smart-copy", action="store_true", help="开启低码率无损直传")
    ap.add_argument("--enh-on", action="store_true", help="开启画质增强滤镜链")
    ap.add_argument("--denoise", choices=["off", "light", "medium", "strong", "ultra"],
                    help="降噪强度 (隐含 --enh-on)")
    ap.add_argument("--crop", default="", help="裁剪黑边 W:H:X:Y (隐含 --enh-on)")
    ap.add_argument("--upscale", choices=["off", "1.5", "2"], help="超清放大倍数")
    ap.add_argument("--enh-only", action="store_true", help="仅增强不压缩")
    # v11 水印与字幕烧录
    ap.add_argument("--wm-type", choices=["off", "text", "image"], help="水印类型")
    ap.add_argument("--wm-text", default="", help="文字水印内容")
    ap.add_argument("--wm-image", default="", help="图片水印路径")
    ap.add_argument("--wm-pos", choices=["br", "bl", "tr", "tl", "cc"], help="水印位置")
    ap.add_argument("--wm-size", type=int, help="文字大小(px) / 图片占视频宽百分比")
    ap.add_argument("--wm-opacity", type=float, help="水印不透明度 0.05-1.0")
    ap.add_argument("--wm-sub", choices=["off", "embedded", "external"], help="字幕烧录来源")
    ap.add_argument("--wm-sub-index", type=int, help="内嵌字幕轨道序号 (0 起)")
    ap.add_argument("--wm-sub-file", default="", help="外挂字幕文件路径")
    # v12 画幅转换 / 文件名模板
    ap.add_argument("--aspect", choices=["keep", "9:16", "1:1", "3:4", "4:3", "16:10", "16:9"],
                    help="画幅转换 (keep=保持原比例)")
    ap.add_argument("--aspect-mode", choices=["crop", "pad", "blur"],
                    help="画幅填充方式: crop=裁切填满 / pad=纯色边框 / blur=模糊填充")
    ap.add_argument("--aspect-color", choices=["black", "white", "gray", "red", "green", "blue", "yellow"],
                    help="纯色边框颜色 (--aspect-mode pad 时生效)")
    ap.add_argument("--name-template", default="",
                    help="输出文件名模板, 如 {date}_{index}_{name}_c{crf}")
    # v11 视频工具箱 (独立单文件工具, 不进入压缩流水线)
    ap.add_argument("--tool", choices=["gif", "clip", "deshake", "rotate", "frame", "concat"],
                    help="工具箱动作 (单独使用, 配合 --tool-src/--tool-out)")
    ap.add_argument("--tool-src", default="", help="工具箱源文件")
    ap.add_argument("--tool-out", default="", help="工具箱输出文件")
    ap.add_argument("--tool-sources", default="",
                    help="拼接用的多个源文件 (用 | 或 ; 分隔, 顺序即拼接顺序)")
    ap.add_argument("--tool-ss", type=float, help="工具箱起始时间(秒)")
    ap.add_argument("--tool-duration", type=float, help="工具箱时长(秒, gif/clip)")
    ap.add_argument("--tool-gif-fps", type=int, help="GIF 帧率")
    ap.add_argument("--tool-gif-w", type=int, help="GIF 宽度(px)")
    ap.add_argument("--json", action="store_true", help="末尾额外打印一行 JSON 汇总, 便于脚本解析")
    raw = list(argv if argv is not None else _sys.argv[1:])
    a = ap.parse_args([x for x in raw if x != "--cli"])

    if a.list_schemes:
        sc = load_schemes()
        if not sc:
            print("(暂无已保存方案)  方案文件: " + SCHEMES_FILE)
        for k, v in sc.items():
            print("  %-20s  %s" % (k, (v or {}).get("saved_at", "")))
        return 0

    ff = find_ffmpeg()
    if not ff:
        print("错误: 未找到 ffmpeg.exe (可放在工具目录内)")
        return 2

    # v11 视频工具箱: 独立单文件动作, 不走压缩流水线 (无需 -i/--input)
    if a.tool:
        src = os.path.abspath(a.tool_src) if a.tool_src else ""
        out = os.path.abspath(a.tool_out) if a.tool_out else ""
        if a.tool == "concat":
            srcs = [os.path.abspath(x) for x in re.split(r"[|;]", a.tool_sources or "") if x.strip()]
            if len(srcs) < 2:
                print("错误: --tool concat 需要 --tool-sources 提供至少 2 个源文件 (用 | 分隔)")
                return 2
            if not out:
                out = os.path.join(os.path.dirname(srcs[0]), "拼接输出.mp4")
            opts = {"sources": srcs}
            print("工具箱: concat %d 个片段 -> %s" % (len(srcs), out))
            rc, lines, info = run_tool(ff, a.tool, "", out, opts)
            for ln in lines:
                print("  " + ln)
            if rc == 0:
                print("完成: " + out + ("  (%.1f KB)" % (info.get("size", 0) / 1024)))
                return 0
            return 1
        if not src or not os.path.isfile(src):
            print("错误: --tool 需要有效的 --tool-src 源文件")
            return 2
        if not out:
            base, ext = os.path.splitext(src)
            ext_map = {"gif": ".gif", "clip": os.path.splitext(src)[1] or ".mp4",
                       "deshake": ".mp4", "rotate": ".mp4", "frame": ".png"}
            out = base + "_" + a.tool + (ext_map.get(a.tool, ".mp4"))
        opts = {"ss": a.tool_ss or 0, "duration": a.tool_duration or 0,
                "gif_fps": a.tool_gif_fps or 15, "gif_w": a.tool_gif_w or 480}
        print("工具箱: %s %s -> %s" % (a.tool, src, out))
        rc, lines, info = run_tool(ff, a.tool, src, out, opts)
        for ln in lines:
            print("  " + ln)
        if rc == 0:
            print("完成: " + out + ("  (%.1f KB)" % (info.get("size", 0) / 1024)))
            return 0
        return 1

    if not a.input:
        ap.error("请用 -i/--input 指定至少一个视频文件或目录 "
                 "(或用 --list-schemes / --tool 工具箱模式)")

    base = {
        "codec": "hevc", "crf": 24, "preset": "fast", "tune": "none",
        "pix": "10", "audio": "strip", "engine": "auto", "mode": "crf",
        "ratio": 0.3, "target_mb": 50, "workers": min(2, os.cpu_count() or 2),
        "smart_copy": False, "smart_copy_kbps": 1200,
        "keep_smaller": True, "auto_open": False, "max_height": 0,
        "streams": "single", "resume": True, "smart_refine": True, "verify": "quick",
        "quality_target": 0.99, "auto_fallback": True,
    }
    if a.scheme:
        sc = load_schemes()
        if a.scheme not in sc:
            print("错误: 方案 '%s' 不存在。已有: %s" % (a.scheme, ", ".join(sc) or "(空)"))
            return 2
        s = sc[a.scheme].get("settings") or {}
        base.update({k: v for k, v in s.items() if k not in ("folder", "recursive", "force")})
        # 网页里压缩比用百分数, 内部用 0-1 小数
        if "ratio_pct" in s:
            try:
                base["ratio"] = float(s["ratio_pct"]) / 100.0
            except Exception:
                pass
        print("已加载参数方案: %s (%s)" % (a.scheme, sc[a.scheme].get("saved_at", "")))

    over = {
        "mode": a.mode, "crf": a.crf, "codec": a.codec, "pix": a.pix,
        "audio": a.audio, "preset": a.preset, "tune": a.tune, "engine": a.engine,
        "target_mb": a.target_mb, "workers": a.workers, "max_height": a.max_height,
        "streams": a.streams, "verify": a.verify, "quality_target": a.quality_target,
        # v11 音频增强
        "audio_bitrate": a.audio_bitrate, "audio_samplerate": a.audio_samplerate,
        "audio_channels": a.audio_channels, "audio_normalize": a.audio_normalize,
        "audio_denoise": a.audio_denoise,
        # v11 水印与字幕
        "wm_type": a.wm_type, "wm_text": a.wm_text, "wm_image": a.wm_image,
        "wm_pos": a.wm_pos, "wm_size": a.wm_size, "wm_opacity": a.wm_opacity,
        "wm_sub": a.wm_sub, "wm_sub_index": a.wm_sub_index, "wm_sub_file": a.wm_sub_file,
        # v12
        "aspect": a.aspect, "aspect_mode": a.aspect_mode, "aspect_color": a.aspect_color,
        "name_template": a.name_template,
    }
    for k, v in over.items():
        if v is not None:
            base[k] = v
    if a.no_fallback:
        base["auto_fallback"] = False
    if a.ratio_pct is not None:
        base["ratio"] = a.ratio_pct / 100.0
        if not a.mode:
            base["mode"] = "ratio"
    if a.force:
        base["resume"] = False
    if a.no_resume:
        base["resume"] = False
    if a.no_keep_smaller:
        base["keep_smaller"] = False
    if a.smart_copy:
        base["smart_copy"] = True
    if a.enh_on or a.denoise or a.crop or a.upscale or a.enh_only:
        base["enh_on"] = True
    if a.denoise:
        base["enh_denoise"] = a.denoise
    if a.crop:
        base["enh_crop"] = a.crop
    if a.upscale:
        base["enh_upscale"] = a.upscale
    if a.enh_only:
        base["enh_only"] = True

    files, seen = [], set()
    for p in a.input:
        q = os.path.abspath(p)
        if os.path.isdir(q):
            excl = os.path.abspath(os.path.join(q, a.out_sub)) if a.out_mode == "sub" else None
            for f in list_videos(q, a.recursive, exclude_dir=excl):
                if f not in seen:
                    seen.add(f)
                    files.append(f)
        elif os.path.isfile(q) and _is_video(os.path.basename(q)):
            if q not in seen:
                seen.add(q)
                files.append(q)
        else:
            print("警告: 跳过不存在的路径或非视频文件: " + p)
    if not files:
        print("错误: 没有找到可处理的视频文件")
        return 2

    opts = make_opts(base)
    qinfo = (" · 目标 SSIM %.4f" % opts.get("quality_target", 0.99)) \
        if opts.get("mode") == "quality" else ""
    print("CLI 模式 | %d 个文件 | %s %s CRF%s %s%s | %d 并发 | 验收=%s | 输出=%s"
          % (len(files), opts.get("codec"), opts.get("mode"), opts.get("crf"),
             opts.get("preset"), qinfo, opts.get("workers"), opts.get("verify"),
             (a.out_sub if a.out_mode == "sub" else "覆盖原文件")))
    run_job(files, opts, a.out_mode, a.out_sub, a.force)
    with state_lock:
        res = list(state["results"])
    okn = sum(1 for r in res if r.get("after", 0) > 0)
    tb = sum(r.get("before", 0) for r in res if r.get("after", 0) > 0)
    ta = sum(r.get("after", 0) for r in res if r.get("after", 0) > 0)
    summary = {"total": len(files), "ok": okn, "failed": len(res) - okn,
               "before": tb, "after": ta,
               "saved_pct": round(100 - ta / tb * 100, 1) if tb else 0.0,
               "results": res}
    print("=== CLI 汇总: 成功 %d / %d, %.1fMB → %.1fMB, 节省 %.1f%% ==="
          % (okn, len(files), tb / 1048576, ta / 1048576, summary["saved_pct"]))
    if a.json:
        print("VC_JSON " + json.dumps(summary, ensure_ascii=False))
    return 0 if (okn == len(files) and okn > 0) else 1


def main():
    import sys
    if any(x in ("--cli", "--list-schemes", "-i", "--input", "-h", "--help")
           for x in sys.argv[1:]):
        sys.exit(cli_main())
    os.chdir(BASE_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}/"
    print("视频压缩工具已启动: " + url)
    print("按 Ctrl+C 退出")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("已停止")
        httpd.shutdown()


if __name__ == "__main__":
    main()
