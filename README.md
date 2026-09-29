# Romaji Video Subtitles · 罗马音视频字幕

**中文** | [English](README.en.md)

为不熟悉平假名、片假名，但能看罗马音的人，给日语视频加上更容易跟读、跟唱的字幕。
适用于对白、学习片段、歌曲和 KTV 视频：保留原视频，根据语音节奏整理罗马音，按短语展示，并在核对过的停顿处留出间隔。

这是一个 **Codex skill + 本地辅助脚本**，由助手组织识别、校对、对齐和导出流程。
项目从歌曲 PV 制作起步，因此仓库名和调用名保留 `karaoke-pv-skill`、`$karaoke-pv`，用途已扩展到一般日语视频。

## 输入：先把视频下载好

请自行下载视频，再把本地文件或路径交给助手。**当前没有内置视频下载器，也不会仅凭链接自动下载。**
源视频会保留，字幕和导出视频写入单独目录。

## 两种文本模式

| 模式 | 你提供什么 | 助手如何处理 |
| --- | --- | --- |
| A：提供文本 | 本地视频 + 日文、罗马音或两者；支持粘贴文本、UTF-8 文本文件和已有字幕 | 整理文本，日文转罗马音草稿，按该视频的声音对齐并分段 |
| B：语音识别 | 本地视频，无需提供台词 | 提取音频，识别日文及词级时间戳，校对后生成罗马音草稿，再对齐分段 |

- **只有罗马音也能处理**，不会强行反推日文汉字。只有日文时，助手生成读音并检查歧义。
- 模式 A 可借助识别辅助定位，但不会直接用识别结果覆盖用户文本。
- 两种模式都可导出**纯罗马音**或**日文＋罗马音**。用户不需要写 JSON 或标时间。
- 默认保留原声音。需要 KTV 伴奏时再分离人声；对白无需先做伴奏分离。

## 使用示例

> 用 $karaoke-pv 处理这个本地视频。我提供罗马音台词，请保留原声，按实际停顿分段，只显示罗马音。

> 用 $karaoke-pv 给这个日语对白视频加罗马音。我没有台词，请先语音识别，做一小段预览。

> 用 $karaoke-pv 处理歌曲 PV。这是日文歌词，请加日文和罗马音，导出有原唱的练习版。

## 安装 skill

克隆后进入仓库：

```sh
git clone https://github.com/zjxx/karaoke-pv-skill.git
cd karaoke-pv-skill
```

Windows PowerShell：

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex/skills' }
$skillTarget = Join-Path $skillRoot 'karaoke-pv'
if (Test-Path $skillTarget) { throw '同名 skill 已存在，请先比较再更新。' }
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
Copy-Item -Recurse skills/karaoke-pv $skillTarget
```

macOS / Linux：

```sh
skill_root="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$skill_root"
if [ -e "$skill_root/karaoke-pv" ]; then
  echo '同名 skill 已存在，请先比较再更新。'
else
  cp -R skills/karaoke-pv "$skill_root/karaoke-pv"
fi
```

## 工具与输出

需要 Python 3.9+；视频导出需要 PATH 中带 `libass` 的 FFmpeg 和 ffprobe。
`faster-whisper` 是可选识别依赖，使用识别时才需要；首次使用可能下载模型。字幕导出只依赖 Python 标准库。

输出可包含原始识别 JSON、整理后的短语时间轴、SRT、ASS、时间轴检查报告和 MP4。
**没有提供原始台词到成品的全自动一键命令**：文本整理、罗马音读法、音频对齐与校对由助手组织完成。
下面是在仓库根目录独立调用辅助脚本的示例，路径需要替换成你的文件：

```sh
# 模式 B：先创建 work 目录，再提取音频并识别。
python -m pip install faster-whisper
ffmpeg -n -i video.mp4 -vn -c:a pcm_s16le work/source.wav
python skills/karaoke-pv/scripts/transcribe.py work/source.wav --output work/asr.json --cache-dir work/models

# 合成时间轴仅演示格式，不对应上面视频的真实台词。
python skills/karaoke-pv/scripts/subtitles.py examples/timeline.json --output-dir work/bilingual --draft
python skills/karaoke-pv/scripts/subtitles.py examples/romaji-only.json --output-dir work/romaji --display romaji --draft

# 对齐你的视频、生成自己的 ASS 后，导出预览。
python skills/karaoke-pv/scripts/render.py video.mp4 work/romaji/romaji.ass work/preview.mp4 --start 0 --duration 8
```

`--display bilingual`（默认）显示已有日文及罗马音，日文缺失时只显示罗马音。
`--display romaji` 始终只显示罗马音。脚本不会覆盖已有输出。模式 A 已有可用时间轴时可跳过识别。
见 [时间轴格式](skills/karaoke-pv/references/timeline.md) 和 [音频分析说明](skills/karaoke-pv/references/audio-analysis.md)。所有脚本支持 `--help`。

## 对齐准确度

识别时间戳是对齐线索，不等于精确强制对齐，也不保证文本正确。
每段时间记录来源：`asr`（识别）、`estimated`（估算）、`audio-reviewed`（已核对音频）。未核对的时间轴需用 `--draft` 导出。
单词间隙不一定是真实静音，截图只能检查排版，不能证明同步。长音、专名、特殊读法和多人重叠对白需要重点检查；当前导出脚本支持单组不重叠字幕，复杂重叠布局需要另行编辑。

## 开发验证

```sh
python -m unittest discover -s tests -v
```

## 依赖与协议

- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper)：本地识别。
- [FFmpeg ASS filter](https://ffmpeg.org/ffmpeg-filters.html#ass)：字幕烧录。
- [Audio Separator](https://github.com/nomadkaraoke/python-audio-separator)：可选的歌曲人声分离工具。

代码与原创文档采用 [MIT 协议](LICENSE)。第三方模型、工具和媒体各有其协议。
仓库仅发布通用代码、文档和原创合成示例；用户视频、台词、音轨、模型缓存和成品留在本地。
