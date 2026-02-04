import requests
import re
import os

def 获取最新版本():
    基础地址 = "https://antigravity.google"
    下载页面 = f"{基础地址}/download"
    请求头 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # 1. 获取下载页面 HTML
        响应 = requests.get(下载页面, headers=请求头, timeout=15)
        响应.raise_for_status()
        网页内容 = 响应.text
        
        # 2. 寻找 main-*.js 文件
        js文件匹配 = re.search(r'src="(main-[^"]+\.js)"', 网页内容)
        if not js文件匹配:
            print("错误：未能找到 main.js 文件")
            return None
        
        js地址 = f"{基础地址}/{js文件匹配.group(1)}"
        print(f"正在解析 JS 文件: {js地址}")
        
        # 3. 获取 JS 内容并提取版本号
        js响应 = requests.get(js地址, headers=请求头, timeout=15)
        js响应.raise_for_status()
        js内容 = js响应.text
        
        # 匹配版本号规律：x.y.z-digits
        版本匹配 = re.search(r'(\d+\.\d+\.\d+)-(\d+)', js内容)
        if 版本匹配:
            主版本 = 版本匹配.group(1)
            完整版本 = f"{主版本}-{版本匹配.group(2)}"
            return 主版本, 完整版本
        else:
            print("错误：未能从 JS 文件中提取到版本号")
            return None, None
    except Exception as e:
        print(f"请求失败: {e}")
        return None, None

def 生成README内容(版本, 完整版本, 历史列表):
    import datetime
    当前时间 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    内容 = f"""# Google Antigravity 版本监控

> [!TIP]
> 本仓库由自动化脚本维护，每小时自动同步一次官网最新版本。

## 🌟 当前最新版本: `{版本}`
**更新时间**: `{当前时间}`

### 🚀 快速下载 (最新版)
| 平台 | 架构 | 下载链接 |
| :--- | :--- | :--- |
| **Windows** | x64 | [点击下载](https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{完整版本}/windows-x64/Antigravity.exe) |
| **Windows** | ARM64 | [点击下载](https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{完整版本}/windows-arm64/Antigravity.exe) |
| **MacOS** | Apple Silicon | [点击下载](https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{完整版本}/darwin-arm/Antigravity.dmg) |
| **MacOS** | Intel | [点击下载](https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{完整版本}/darwin-x64/Antigravity.dmg) |
| **Linux** | x64 | [点击下载](https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{完整版本}/linux-x64/Antigravity.tar.gz) \\| [官网](https://antigravity.google/download/linux) |

## 📜 历史版本记录
| 版本号 | Windows (x64) | MacOS (M系列) | MacOS (Intel) | Linux (x64) |
| :--- | :--- | :--- | :--- | :--- |
"""
    # 倒序排列历史版本，让较新的排在上面
    for 项 in reversed(历史列表):
        v = 项["version"]
        fv = 项["full_version"]
        内容 += f"| `{v}` | [下载](https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{fv}/windows-x64/Antigravity.exe) | [下载](https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{fv}/darwin-arm/Antigravity.dmg) | [下载](https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{fv}/darwin-x64/Antigravity.dmg) | [下载](https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{fv}/linux-x64/Antigravity.tar.gz) \\| [官网](https://antigravity.google/download/linux) |\n"

    内容 += "\n---\nAntigravity，反重力升天！\n"
    return 内容

def 加载历史记录():
    try:
        if os.path.exists("history.json"):
            with open("history.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"读取 history.json 失败: {e}")
    return []

def 保存历史记录(历史列表):
    try:
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(历史列表, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"保存 history.json 失败: {e}")

def 更新版本文件(新版本, 完整版本, 历史列表):
    版本文件路径 = "VERSION"
    README路径 = "README.md"
    旧版本 = ""
    README已存在 = os.path.exists(README路径)
    
    if os.path.exists(版本文件路径):
        with open(版本文件路径, "r", encoding="utf-8") as f:
            旧版本 = f.read().strip()
    
    # 检查是否是全新版本
    版本变化 = (新版本 != 旧版本)
    
    # 如果是新版本，且不在历史列表中，则添加到历史记录
    # 注意：这里我们维护一份完整的历史记录（包含当前最新）
    # 但为了避免重复，我们需要检查
    已知版本号集合 = {项["version"] for 项 in 历史列表}
    
    if 新版本 not in 已知版本号集合:
        print(f"发现全新版本 {新版本}，添加到历史记录...")
        历史列表.append({"version": 新版本, "full_version": 完整版本})
        保存历史记录(历史列表)
        # 重新排序或整理？目前列表是按时间顺序追加的，生成README时会倒序
    
    # 生成 README 内容
    # 传递给 README 生成器的历史列表应该排除当前最新版本（因为最新版本显示在顶部）
    # 或者生成器内部自己处理。查看生成器代码：
    # 它遍历历史列表生成表格。我们希望表格里只显示"旧版本"。
    # 所以这里筛选一下
    旧版本列表 = [项 for 项 in 历史列表 if 项["version"] != 新版本]
    README内容 = 生成README内容(新版本, 完整版本, 旧版本列表)
    
    # 检查 README 是否需要更新
    需要更新README = not README已存在
    if README已存在:
        with open(README路径, "r", encoding="utf-8") as f:
            if f.read() != README内容:
                需要更新README = True

    # 写入 README
    if 需要更新README:
        with open(README路径, "w", encoding="utf-8") as f:
            f.write(README内容)
    
    if 版本变化:
        print(f"检测到新版本: {旧版本} -> {新版本}")
        with open(版本文件路径, "w", encoding="utf-8") as f:
            f.write(新版本)
    elif 需要更新README:
        print("版本未变，但更新了 README.md (时间戳或内容变动)")
        
    return 版本变化, 需要更新README

def 下载安装包(版本, 完整版本):
    下载任务 = [
        {"名": "Antigravity-Windows-x64.exe", "地址": f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{完整版本}/windows-x64/Antigravity.exe"},
        {"名": "Antigravity-Windows-ARM64.exe", "地址": f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{完整版本}/windows-arm64/Antigravity.exe"},
        {"名": "Antigravity-MacOS-Silicon.dmg", "地址": f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{完整版本}/darwin-arm/Antigravity.dmg"},
        {"名": "Antigravity-MacOS-Intel.dmg", "地址": f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{完整版本}/darwin-x64/Antigravity.dmg"},
        {"名": "Antigravity-Linux-x64.tar.gz", "地址": f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{完整版本}/linux-x64/Antigravity.tar.gz"}
    ]
    
    已下载文件 = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    for 任务 in 下载任务:
        文件名 = 任务["名"]
        url = 任务["地址"]
        print(f"正在备份安装包: {文件名}...")
        try:
            with requests.get(url, headers=headers, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(文件名, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            已下载文件.append(文件名)
        except Exception as e:
            print(f"备份失败 ({文件名}): {e}")
            
    return 已下载文件

if __name__ == "__main__":
    import sys
    import json
    
    # 支持命令行参数直接下载指定版本 (用于历史版本备份)
    if len(sys.argv) > 3 and sys.argv[1] == "--download":
        版本 = sys.argv[2]
        完整版本 = sys.argv[3]
        下载安装包(版本, 完整版本)
        sys.exit(0)

    # 支持从 API 获取完整历史列表 (用于 GitHub Actions Matrix)
    if len(sys.argv) > 1 and sys.argv[1] == "--api-history":
        try:
            r = requests.get("https://antigravity-auto-updater-974169037036.us-central1.run.app/releases", timeout=15)
            r.raise_for_status()
            数据 = r.json()
            输出列表 = []
            for 项 in 数据:
                输出列表.append({
                    "version": 项["version"],
                    "full_version": f"{项['version']}-{项['execution_id']}"
                })
            
            # 按版本号升序排列 (最小版本最先执行)
            try:
                输出列表.sort(key=lambda x: tuple(map(int, x["version"].split('.'))))
            except Exception:
                pass # 如果版本号格式不符合预期，则保持原序或不处理

            print(json.dumps(输出列表))
        except Exception as e:
            print(f"API 请求失败: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    # 加载历史版本数据
    历史版本列表 = 加载历史记录()

    最新主版本, 最新完整版本 = 获取最新版本()
    
    # 检查是否需要初始化
    需要初始化 = not os.path.exists("VERSION")
    
    if 最新主版本:
        版本变化, 首页变化 = 更新版本文件(最新主版本, 最新完整版本, 历史版本列表)
        
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                if 需要初始化:
                    # 历史旧版本不包含当前最新版
                    历史旧版本 = [项 for 项 in 历史版本列表 if 项["version"] != 最新主版本]
                    f.write(f"init=true\n")
                    f.write(f"history={json.dumps(历史旧版本)}\n")
                
                # 信号输出
                f.write(f"version_changed={'true' if 版本变化 else 'false'}\n")
                f.write(f"readme_changed={'true' if 首页变化 else 'false'}\n")
                f.write(f"version={最新主版本}\n")
                f.write(f"full_version={最新完整版本}\n")

                # 只有版本真的变了，或者第一次初始化，才下载备份
                if 版本变化 or 需要初始化:
                    print(f"触发安装包备份 (原因: {'新版本' if 版本变化 else '初始化'})")
                    文件列表 = 下载安装包(最新主版本, 最新完整版本)
                    f.write(f"assets={' '.join(文件列表)}\n")
                    f.write(f"need_release=true\n")
                else:
                    f.write(f"need_release=false\n")
