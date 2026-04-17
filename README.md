# 🎬 TMDB 电影数据爬虫

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个基于网页爬取的 TMDB 电影数据采集工具，支持自定义抓取页数，自动导出结构化 CSV 数据。本项目通过模拟浏览器请求，智能绕过基础反爬机制，稳定获取高质量电影信息。

> ⚠️ **重要提示**  
> 本项目仅用于学习交流，请遵守 [TMDB 使用条款](https://www.themoviedb.org/documentation/api/terms-of-use)  
> 请勿高频请求，程序已内置请求延迟和重试机制，请保持合理使用频率

---

## 🌟 核心功能
- ✅ **交互式页数控制**：运行时输入要抓取的页数
- ✅ **完整电影数据采集**（11个字段）：
  - 电影名
  - 上映年份
  - 上映时间
  - 电影类型
  - 电影时长
  - 评分
  - 语言
  - 导演
  - 编剧
  - 电影简介
  - 电影标语
- ✅ **智能反爬策略**：
  - 多 User-Agent 轮换
  - 随机请求延迟 (2-5秒)
  - 失败自动重试 (3次)
  - 页间额外延迟 (3-6秒)
- ✅ **数据自动清洗**：
  - 年份格式标准化
  - 日期格式提取
  - 特殊字符过滤
- ✅ **结构化存储**：自动创建 `csv_data/` 目录，保存 UTF-8 with BOM 编码的 CSV

---

## 📦 依赖安装
```bash
pip install requests lxml
