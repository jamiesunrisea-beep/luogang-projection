Projection Output — 使用说明

目标：生成可直接投影的最终视觉效果（基于论文内容：远航 / 共生 / 脉动 三章）。

文件：
- projection_output.html  —— 可直接在浏览器打开用于投影。

运行方式：
1. 直接在文件管理器中双击 `projection_output.html`，或在浏览器中打开该文件。
2. 建议使用 Chrome 或 Edge，设置浏览器为全屏（F11），并关闭缩放（100%）。
3. 可使用 Live Server（VS Code）或直接打开文件：

   在项目根目录运行（可选）：

   ```powershell
   # 如果安装了 node 的 live-server
   live-server . --entry-file=projection_output.html
   ```

快捷键：
- 1：远航（冷蓝矢量线）
- 2：共生（有机分支）
- 3：脉动（响应鼠标的粒子场）
- 空格：暂停/继续
- 鼠标移动：在“脉动”章节中模拟人群密度与交互

投影建议：
- 将投影比例设为投影机分辨率（例如 1920x1080）并选择浏览器窗口无边框（或使用专用播放器/Chromium命令行启动）
- 若需要纯视频，可以屏幕录制 `projection_output.html` 后导出为 mp4 用投影播放

如需我把某一章改为特定内容（例如：把“共生”改用 L-System 生成器，或把“脉动”替换为大颗粒无人机点阵样式），告诉我具体要求，我会修改代码并给出新文件。