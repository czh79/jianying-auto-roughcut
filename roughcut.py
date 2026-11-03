import os
import subprocess
import pyJianYingDraft as draft
from pyJianYingDraft import trange, tim

# ==================== 1. 基础路径配置 ====================
# 请修改为你本地【剪映专业版】的 Drafts 草稿文件夹路径
# 打开剪映 -> 右上角全局设置 -> 草稿位置 即可查看
JIANYING_DRAFT_DIR = os.environ.get(
    "JIANYING_DRAFT_DIR",
    os.path.expandvars(r"%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft"),
)

# 工程名称（运行后会直接出现在剪映首页）
PROJECT_NAME = "滚滚红尘_自动粗剪工程"

# 你在 ComfyUI 生成的旁白音频路径（若暂时没有，脚本也能单独排好视频轨道）
VOICEOVER_PATH = r"./gungun_voiceover.mp3"

# 本地素材缓存文件夹
ASSET_DIR = os.path.abspath("./gungun_assets")
os.makedirs(ASSET_DIR, exist_ok=True)

# ==================== 2. 五幕素材搜索与切片清单 ====================
# 提示：B站搜词偶有被拒，脚本默认使用 ytsearch1: (YouTube 搜索第一条结果，最稳定)
# 如果你有梯子，ytsearch1 速度极快；如果想直接喂指定B站/YT链接，把 query 换成具体网址即可
SCENES = [
    # 第一幕：引子 · 乱世回响
    {"id": "01_record", "query": "ytsearch1:陈淑桦 罗大佑 滚滚红尘 MV", "start": "00:00:10", "end": "00:00:18", "duration": "8s"},
    {"id": "02_window", "query": "ytsearch1:滚滚红尘 林青霞 电影片段", "start": "00:00:30", "end": "00:00:40", "duration": "10s"},
    
    # 第二幕：三毛写张爱玲 · 两个女人的泣血
    {"id": "03_sanmao", "query": "ytsearch1:三毛 滚滚红尘 纪录片 采访", "start": "00:00:20", "end": "00:00:32", "duration": "12s"},
    {"id": "04_zhang",  "query": "ytsearch1:张爱玲 历史影像 纪录片", "start": "00:00:15", "end": "00:00:25", "duration": "10s"},
    
    # 第三幕：林青霞与秦汉 · 十八年银幕绝唱
    {"id": "05_dance",  "query": "ytsearch1:滚滚红尘 林青霞 秦汉 跳舞", "start": "00:00:15", "end": "00:00:30", "duration": "15s"},
    {"id": "06_part",   "query": "ytsearch1:滚滚红尘 码头 离别 结局", "start": "00:00:40", "end": "00:00:55", "duration": "15s"},
    
    # 第四幕：金马奖落败 · 台下的强颜欢笑
    {"id": "07_award",  "query": "ytsearch1:1990 金马奖 滚滚红尘 三毛", "start": "00:00:20", "end": "00:00:35", "duration": "15s"},
    {"id": "08_lin_win","query": "ytsearch1:林青霞 金马奖 最佳女主角 滚滚红尘", "start": "00:00:10", "end": "00:00:22", "duration": "12s"},
    
    # 第五幕：终章 · 二十天后的绝响与散落天涯
    {"id": "09_snow",   "query": "ytsearch1:滚滚红尘 结局 林青霞 雪地", "start": "00:00:10", "end": "00:00:25", "duration": "15s"},
    {"id": "10_desert", "query": "ytsearch1:三毛 撒哈拉 纪录片", "start": "00:00:30", "end": "00:00:45", "duration": "15s"},
]

def download_and_slice():
    """利用 yt-dlp 自动搜索并只下载指定时间段的切片（节省大量下载时间）"""
    downloaded_files = []
    for item in SCENES:
        out_file = os.path.join(ASSET_DIR, f"{item['id']}.mp4")
        if os.path.exists(out_file):
            print(f"[已存在，跳过下载] {out_file}")
            downloaded_files.append((out_file, item["duration"]))
            continue

        print(f"正在检索并截取: {item['query']} ({item['start']} -> {item['end']})...")
        cmd = [
            "yt-dlp",
            item["query"],
            "--download-sections", f"*{item['start']}-{item['end']}",
            "--force-keyframes-at-cuts",  # 强制在切点重编码关键帧，防止导入剪映黑屏
            "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", out_file,
            "--no-playlist",
            "--quiet", "--progress"
        ]
        try:
            subprocess.run(cmd, check=True)
            if os.path.exists(out_file):
                downloaded_files.append((out_file, item["duration"]))
        except Exception as e:
            print(f"[警告] {item['id']} 下载失败，请检查网络或替换关键词: {e}")

    return downloaded_files

def build_jianying_project(video_clips):
    """创建剪映草稿工程并按顺序排入时间轴"""
    print("\n正在生成剪映工程文件...")
    folder = draft.DraftFolder(JIANYING_DRAFT_DIR)
    
    # 创建 1920x1080 横屏工程（若做抖音竖屏可改为 1080, 1920）
    script = folder.create_draft(PROJECT_NAME, 1920, 1080, allow_replace=True)
    
    # 添加一条主视频轨和一条音频轨
    script.add_track(draft.TrackType.video, "主画面轨")
    script.add_track(draft.TrackType.audio, "ComfyUI旁白轨")

    current_time = 0  # 时间轴游标（微秒）

    for file_path, duration_str in video_clips:
        dur = tim(duration_str)
        material = draft.VideoMaterial(file_path)
        
        # 将切片按顺序放置在时间轴上，并把原视频自带的声音静音（0.0），留给旁白
        seg = draft.VideoSegment(
            material,
            target_timerange=trange(current_time, dur),
            source_timerange=trange(0, dur),
            volume=0.0
        )
        script.add_segment(seg, "主画面轨")
        current_time += dur

    # 如果你已经生成了 ComfyUI 旁白音频，自动挂载到音频轨
    if os.path.exists(VOICEOVER_PATH):
        audio_mat = draft.AudioMaterial(os.path.abspath(VOICEOVER_PATH))
        audio_seg = draft.AudioSegment(
            audio_mat,
            target_timerange=trange(0, audio_mat.duration),
            volume=1.0
        )
        script.add_segment(audio_seg, "ComfyUI旁白轨")
        print(f"已自动挂载 ComfyUI 旁白音轨：{VOICEOVER_PATH}")
    else:
        print(f"未检测到 {VOICEOVER_PATH}，仅生成视频画面轨，你可在剪映内手动拖入旁白。")

    script.save()
    print(f"\n✅ 完成！现在打开【剪映专业版】，首页第一个项目就是《{PROJECT_NAME}》！")

if __name__ == "__main__":
    clips = download_and_slice()
    if clips:
        build_jianying_project(clips)
    else:
        print("未下载到任何有效片段，请检查网络或 FFmpeg 是否安装。")