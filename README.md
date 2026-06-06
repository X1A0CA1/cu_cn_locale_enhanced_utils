# zh-CN Enhanced 翻译构建工具

## 直接打包

```bash
git clone --recurse-submodules https://github.com/X1A0CA1/cu_cn_locale_enhanced_utils.git
python3 src/build.py
```

输出文件位于 `outputs/` 目录：

- `zh-CN_Enhanced.json` — 合并后的完整翻译文件
- `zh-CN_Enhanced_paratranz.json` — 用于上传至 Paratranz 的格式

---

## 从 Paratranz 更新翻译

1. 在 Paratranz 项目页面下载翻译压缩包，将解压后的 `.json` 文件放入 `translate/` 目录
2. 运行转换脚本：
   ```bash
   python3 translate/convert_paratranz_to_patch.py
   ```
3. 运行构建脚本：
   ```bash
   python3 src/build.py
   ```
