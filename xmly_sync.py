import os
import re
import sys
import time
import hashlib
import requests

# 配置区：从 GitHub Secrets 读取
APP_KEY = os.getenv('XMLY_APP_KEY')
APP_SECRET = os.getenv('XMLY_APP_SECRET')

def get_xmly_status():
    """获取喜马拉雅最近播放记录"""
    params = {
        "app_key": APP_KEY,
        "device_id": "github_action_bot",
        "timestamp": int(time.time() * 1000)
    }
    # 喜马拉雅官方签名逻辑：参数排序拼接 + Secret 后 MD5
    sig_str = "".join([f"{k}{v}" for k, v in sorted(params.items())])
    params["sig"] = hashlib.md5((sig_str + APP_SECRET).encode('utf-8')).hexdigest()
    
    # 获取历史记录 API 路径（请确认你申请的接口权限包）
    url = "https://api.ximalaya.com/revision/user/track/history"
    
    try:
        res = requests.get(url, params=params, timeout=15)
        data = res.json()
        if data.get('ret') == 0:
            tracks = data.get('data', {}).get('trackHistoryList', [])
            if tracks:
                track = tracks[0]
                return f"📻 最近在听：[{track['trackTitle']}](https://www.ximalaya.com{track['trackUrl']}) —— *{track['albumTitle']}*"
        return "📻 喜马拉雅：暂时没发现播放记录"
    except Exception as e:
        print(f"API Error: {e}")
        return "📻 喜马拉雅：数据获取异常"

def update_readme(new_status):
    """安全地更新 README 文件"""
    # 确认文件路径
    readme_path = os.path.join(os.getcwd(), "README.md")
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 如果 README 里没有标签，直接报错退出，不执行写入
    start_tag = ""
    end_tag = ""
    
    if start_tag not in content or end_tag not in content:
        print("❌ 错误：在 README 中找不到喜马拉雅标签，请先添加标签。")
        sys.exit(1)

    # 正则替换：使用非贪婪匹配
    # [\s\S]*? 确保能匹配包含换行符在内的所有字符
    pattern = rf"{start_tag}[\s\S]*?{end_tag}"
    replacement = f"{start_tag}\n{new_status}\n{end_tag}"
    
    new_content = re.sub(pattern, replacement, content)

    # 覆盖写入（'w' 模式保证不会在末尾追加）
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ README 更新成功！")

if __name__ == "__main__":
    if not APP_KEY or not APP_SECRET:
        print("❌ 错误：GitHub Secrets 中缺少 XMLY_APP_KEY 或 XMLY_APP_SECRET")
        sys.exit(1)
        
    status = get_xmly_status()
    update_readme(status)
