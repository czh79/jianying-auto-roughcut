# 🎞️ 剪映草稿自动生成 · JianYing Auto Roughcut

> 写一份分镜清单，脚本自动搜素材、按时长切片、排好时间轴，直接生成可编辑的剪映草稿工程。

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![JianYing](https://img.shields.io/badge/剪映-草稿工程-00c8ff)](https://www.capcut.cn/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**中文** | [English](#-english)

---

## 解决的问题

做解说类视频，最耗时的不是剪，是**找素材**：脑子里有画面，得去搜、下载、拖进时间轴、切成 8 秒、对齐顺序。十个镜头就是一小时。

这个脚本把"分镜表"变成"可编辑的时间轴"：

```
分镜清单 (Python 列表)
   ↓  yt-dlp 按关键词搜索 + 只下载指定时间段
   ↓  pyJianYingDraft 写入草稿数据结构
剪映草稿工程（打开即用，可继续精剪，可换素材）
```

**它不渲染视频**——它生成的是剪映的工程文件，所以你还是能在剪映里随意改、换素材、调色、加特效。这是它和"一键成片"工具最大的区别。

## 核心能力

| 能力 | 说明 |
|---|---|
| **按段下载** | `--download-sections` 只拉取需要的那 8 秒，不用把整条 4K 素材下下来 |
| **关键帧强制切点** | `--force-keyframes-at-cuts` 强制在切点重编码关键帧，**防止导入剪映黑屏**（这一步很关键） |
| **自动排轨** | 视频轨 + 音频轨自动创建，片段按清单顺序首尾相接 |
| **原声静音** | 素材轨音量置 0，把位置留给旁白 |
| **旁白自动挂载** | 检测到 `gungun_voiceover.mp3` 就自动挂到音频轨 |
| **断点缓存** | 已下载的切片跳过，改分镜表后不用重下前面的素材 |
| **分辨率可配** | 默认 1920×1080 横屏，改一行就是 1080×1920 竖屏 |

## 分镜清单长什么样

```python
SCENES = [
    {"id": "01_record", "query": "ytsearch1:陈淑桦 罗大佑 滚滚红尘 MV",
     "start": "00:00:10", "end": "00:00:18", "duration": "8s"},

    {"id": "02_window", "query": "ytsearch1:滚滚红尘 林青霞 电影片段",
     "start": "00:00:30", "end": "00:00:40", "duration": "10s"},
    ...
]
```

- `query` 支持 `ytsearch1:关键词`（YouTube 搜第一条，最稳）、`bv1xxxx` 这类具体链接，或本地文件路径
- `start` / `end` 决定切片区间，`duration` 是落到时间轴上的长度
- `id` 同时是缓存文件名，改了 id 就会重新下载

## 快速开始

```bash
git clone https://github.com/czh79/jianying-auto-roughcut.git
cd jianying-auto-roughcut
pip install -r requirements.txt
python roughcut.py
```

**前置条件**

1. 安装 [剪映专业版](https://www.capcut.cn/)（Windows / macOS）
2. FFmpeg 已加入 `PATH`
3. 找到草稿目录：剪映 → 右上角「全局设置」→「草稿位置」

脚本默认读 `%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft`，路径不同就设环境变量：

```bash
# Windows
set JIANYING_DRAFT_DIR=D:\JianyingPro\...\com.lveditor.draft
# macOS / Linux
export JIANYING_DRAFT_DIR="/path/to/com.lveditor.draft"
```

**运行后**打开剪映，首页第一个项目就是生成好的工程。

## 参数速查

| 变量 | 位置 | 说明 |
|---|---|---|
| `JIANYING_DRAFT_DIR` | 环境变量 | 草稿目录 |
| `PROJECT_NAME` | 代码常量 | 工程名，同时是剪映首页显示的名字 |
| `VOICEOVER_PATH` | 代码常量 | 旁白音频，不存在则只排画面轨 |
| `ASSET_DIR` | 代码常量 | 素材缓存目录 |
| `create_draft(..., 1920, 1080, ...)` | 代码 | 改成 `1080, 1920` 即竖屏 |

## 常见坑

**导入后黑屏？**
多半是切点没对齐关键帧。脚本已带 `--force-keyframes-at-cuts`，如果你改过下载参数，别把它删掉。

**草稿生成了但剪映里看不到？**
确认 `JIANYING_DRAFT_DIR` 指向的是**当前账号**的草稿目录（多账号会有多个子目录）。

---

## 🇬🇧 English

> Turn a shot list into an editable JianYing (CapCut CN) draft project: auto-search footage, download only the needed seconds, and lay it out on a timeline.

The slowest part of making a commentary video isn't editing — it's hunting for footage. This script turns a Python shot list into a real draft project you can keep editing in JianYing.

**It does not render a video.** It writes JianYing's draft format, so you keep full creative control afterwards — swap clips, grade, add effects.

### Highlights

- `--download-sections` pulls only the 8 seconds you need, not the whole 4K source.
- `--force-keyframes-at-cuts` re-encodes keyframes at cut points — this is what prevents the classic black-frame-on-import problem.
- Auto-creates a video track and an audio track, mutes source audio, and attaches a voiceover file if present.
- Cached by segment `id`, so editing the shot list doesn't re-download earlier footage.

### Usage

```bash
pip install -r requirements.txt
python roughcut.py     # requires JianYing + FFmpeg on PATH
```

Set `JIANYING_DRAFT_DIR` if your draft folder isn't the default. Switch to vertical by changing the `create_draft` dimensions to `1080, 1920`.

---

<div align="center">

做解说视频的朋友，**点个 Star** ⭐

</div>
