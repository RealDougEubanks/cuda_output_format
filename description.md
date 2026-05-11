
Fork of [Josh5/unmanic.plugin.encoder_video_hevc_nvenc](https://github.com/Josh5/unmanic.plugin.encoder_video_hevc_nvenc) that adds `-hwaccel_output_format cuda` when NVDEC HW decoding is enabled. This keeps decoded frames in GPU memory for a full NVDEC → NVENC pipeline, cutting CPU usage per worker.

For information on the hevc_nvenc encoder settings:
 - [NVIDIA FFmpeg Transcoding Guide](https://developer.nvidia.com/blog/nvidia-ffmpeg-transcoding-guide/)
 - [FFmpeg - HWAccelIntro](https://trac.ffmpeg.org/wiki/HWAccelIntro#NVENC)

Check your GPU compatibility:
 - [GPU compatibility table](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new).


### Config description

#### <span style="color:blue">Enable NVDEC HW Accelerated Decoding?</span>
Decode the video stream using hardware-accelerated decoding. This sets `-hwaccel cuda -hwaccel_device {device}` in the ffmpeg generic options. Required for the GPU pipeline.

For 10-bit encodes that fall outside NVDEC's supported profiles, leave this off.


#### <span style="color:blue">Keep decoded frames in GPU memory</span>
When HW decoding is on, this also sets `-hwaccel_output_format cuda`. Without it, ffmpeg downloads each decoded frame from the GPU to system RAM and re-uploads it for NVENC — wasteful. Leave this on unless you have a specific reason to disable it (some filter chains require frames in system memory).


#### <span style="color:blue">NVENC Encoder Quality Preset</span>
A preset is a collection of options trading encoding speed for compression. A slower preset gives better quality at the same bitrate.

`Slow` and `Lossless` presets are pinned to a single FFmpeg thread to improve quality.


#### <span style="color:blue">Profile</span>
Main = 8-bit. Main10 = 10-bit. Range Extended = >10-bit / higher chroma subsampling. Hardware support varies by GPU.


#### <span style="color:blue">Max input stream packet buffer</span>
ffmpeg's `-max_muxing_queue_size`. Default 2048 is fine for most sources.


#### <span style="color:blue">Overwrite all options with custom input</span>
Advanced free-text FFmpeg params. Placement:

```
ffmpeg \
    -hide_banner \
    -loglevel info \
    <CUSTOM MAIN OPTIONS HERE> \
    -i /library/TEST_FILE.mkv \
    <CUSTOM ADVANCED OPTIONS HERE> \
    -map 0:v:0 \
    -c:v:0 hevc_nvenc \
    <CUSTOM VIDEO OPTIONS HERE> \
    -y /path/to/output/video.mkv
```
