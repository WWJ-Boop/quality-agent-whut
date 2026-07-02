# Assets 资源文件夹

此文件夹用于存放项目资源文件，如架构图、图片等。

## 添加架构图

1. 将你的架构图文件（PNG、SVG 或 JPG 格式）放入此文件夹
2. 命名为 `architecture.png`（或修改代码中的文件名）
3. 修改 `app/cloud_main.py` 中的架构图代码：

```python
# 找到以下代码（约第840行），取消注释：
st.image("assets/architecture.png", use_container_width=True)
```

## 在线图片

如果使用在线图片，直接修改代码中的 URL：

```python
st.image("https://your-architecture-image-url.png", use_container_width=True)
```

## 图片建议

- 建议尺寸：宽度 1200px 以上
- 格式：PNG（推荐）或 SVG
- 内容：系统架构图、功能流程图等
