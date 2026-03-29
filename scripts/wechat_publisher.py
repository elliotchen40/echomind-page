#!/usr/bin/env python3
"""微信公众号发布脚本 v11 (完整版)"""

import subprocess
import json
import glob
import os
import re
import sys

def get_access_token():
    """获取access token"""
    appid = "wx0472455b30dcacfb"
    secret = "89b4a099fb727d2919a505779b116521"
    
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    result = subprocess.run(['curl', '-s', '-X', 'POST', url], capture_output=True, text=True)
    data = json.loads(result.stdout)
    return data.get('access_token', '')

def upload_article_image(access_token, image_path):
    """上传图文内图片，返回URL"""
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"
    result = subprocess.run(['curl', '-s', '-X', 'POST', url, '-F', f'media=@{image_path}'], 
                          capture_output=True, text=True)
    data = json.loads(result.stdout)
    return data.get('url', '')

def upload_thumb(access_token, image_path):
    """上传封面图(永久thumb)"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=thumb"
    result = subprocess.run(['curl', '-s', '-X', 'POST', url, '-F', f'media=@{image_path}'], 
                          capture_output=True, text=True)
    data = json.loads(result.stdout)
    return data.get('media_id', '')

def compress_image(src, dst, width=860, height=360):
    """压缩图片"""
    subprocess.run(['ffmpeg', '-i', src, '-vf', f'scale={width}:{height}', '-q:v', '8', dst], 
                  capture_output=True)

def create_draft(access_token, title, content, thumb_media_id):
    """创建草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    
    data = {
        "articles": [{
            "title": title,
            "author": "EchoMind",
            "digest": "让爱，不止于回忆",
            "content": content,
            "content_source_url": "",
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }]
    }
    
    json_str = json.dumps(data, ensure_ascii=False)
    
    # 写入临时文件
    with open('/tmp/draft.json', 'w', encoding='utf-8') as f:
        f.write(json_str)
    
    result = subprocess.run(['curl', '-s', '-X', 'POST', url, 
                           '-H', 'Content-Type: application/json; charset=utf-8',
                           '--data-binary', '@/tmp/draft.json'], 
                          capture_output=True, text=True)
    
    os.remove('/tmp/draft.json')
    return json.loads(result.stdout)

def main():
    print("=========================================")
    print("  微信公众号发布脚本 v11 (完整版)")
    print("=========================================")
    
    # 获取token
    print("\n获取Access Token...")
    access_token = get_access_token()
    if not access_token:
        print("获取Token失败！")
        sys.exit(1)
    print(f"Token获取成功")
    
    # 路径设置
    base_dir = "/root/.openclaw/workspace/projects/echomind/gonzhonghao"
    latest_dir = sorted(glob.glob(f"{base_dir}/2026-*"))[-1]
    content_dir = f"{latest_dir}/mainpage"
    images_dir = f"{content_dir}/images"
    
    # 读取标题
    with open(f"{content_dir}/官网主页完整文案.md", 'r') as f:
        title = f.readline().strip().lstrip('# ')
    
    print(f"使用内容目录: {content_dir}")
    print(f"文章标题: {title}")
    
    # 上传8张图
    print("\nStep 1: 上传8张配图获取URL")
    image_urls = []
    for i in range(1, 9):
        pattern = f"{images_dir}/{i}_*.jpeg"
        files = glob.glob(pattern)
        if files:
            print(f"上传第{i}张... ", end='', flush=True)
            url = upload_article_image(access_token, files[0])
            if url:
                image_urls.append(url)
                print("OK")
            else:
                print("失败")
    
    if len(image_urls) != 8:
        print(f"错误：只成功上传了 {len(image_urls)} 张图片")
        sys.exit(1)
    
    print(f"\n成功获取 {len(image_urls)} 个图片URL")
    
    # 压缩并上传封面
    print("\nStep 2: 压缩并上传封面图")
    compress_image(f"{images_dir}/1_hero_visual.jpeg", "/tmp/cover_thumb.jpg")
    print("上传播封面... ", end='', flush=True)
    thumb_media_id = upload_thumb(access_token, "/tmp/cover_thumb.jpg")
    os.remove("/tmp/cover_thumb.jpg")
    
    if not thumb_media_id:
        print("失败")
        sys.exit(1)
    print(f"OK, media_id: {thumb_media_id}")
    
    # 构建HTML
    print("\nStep 3: 构建完整HTML内容")
    
    html = f"""<h1 style="text-align:center;">留声</h1>
<p style="text-align:center;font-size:18px;color:#666;">让思念不只是回忆</p>
<p>有些人离开了，但他们的声音、语气、习惯仍然留在我们的记忆里</p>
<p>留声，帮你把这些记忆整理、保存，并在需要的时候，重新"听见"</p>
<p style="text-align:center;"><img src="{image_urls[0]}" style="width:100%;max-width:600px;"/></p>

<hr/><h2>你有没有这样的时候——</h2>
<p>会反复翻以前的聊天记录，听一段语音，停很久</p>
<p>明明只是几句话，却舍不得删，也不敢再听太多</p>
<p>不是放不下，只是这些东西，没有地方可以好好安放</p>
<p style="text-align:center;"><img src="{image_urls[1]}" style="width:100%;max-width:600px;"/></p>

<hr/><h2>留声，不是去"还原一个人"</h2>
<p>而是把这些零散的记忆——聊天、语音、表达方式</p>
<p>重新整理成一种可以被轻轻触达的存在</p>
<p style="text-align:center;"><img src="{image_urls[2]}" style="width:100%;max-width:600px;"/></p>

<hr/><h2>它可以做什么</h2>
<ul>
<li>保存并整理重要的聊天记录与语音</li>
<li>还原熟悉的表达方式与说话习惯</li>
<li>在某些时刻，再次"听见"熟悉的声音</li>
<li>通过对话，触发那些被遗忘的细节</li>
</ul>
<p>不是一直对话，而是在需要的时候，有一个回应</p>
<p style="text-align:center;"><img src="{image_urls[3]}" style="width:100%;max-width:600px;"/></p>

<hr/><h2>边界说明</h2>
<p style="font-size:20px;font-weight:bold;color:#c00;">留声不会试图替代任何人</p>
<p>它不是复活，也不是复制</p>
<p>而是一种基于记忆生成的陪伴方式</p>
<p>我们刻意保留边界，是希望它成为一种纪念，而不是依赖</p>
<p style="text-align:center;"><img src="{image_urls[4]}" style="width:100%;max-width:600px;"/></p>

<hr/><h2>为什么要做这件事</h2>
<p>我们发现，真正难的不是忘记</p>
<p>而是——没有一个地方，可以安放这些记忆</p>
<p>留声存在的意义，就是给这些重要的东西一个可以停留的地方</p>
<p style="text-align:center;"><img src="{image_urls[5]}" style="width:100%;max-width:600px;"/></p>

<hr/><h2>使用流程</h2>
<p>只需要简单几步：</p>
<ol>
<li>提供聊天记录、语音等资料</li>
<li>我们帮你整理与构建记忆模型</li>
<li>完成后，你可以通过微信进行交互</li>
</ol>
<p>整个过程，我们会全程协助，不需要任何技术基础</p>
<p style="text-align:center;"><img src="{image_urls[6]}" style="width:100%;max-width:600px;"/></p>

<hr/><h2>有些人不会再回来</h2>
<p>但他们留下的东西，值得被好好对待</p>
<p style="text-align:center;font-size:24px;font-weight:bold;">留声，让思念不只是回忆</p>
<p style="text-align:center;"><img src="{image_urls[7]}" style="width:100%;max-width:600px;"/></p>"""
    
    print(f"HTML内容长度: {len(html)} 字符")
    
    # 创建草稿
    print("\nStep 4: 创建草稿")
    result = create_draft(access_token, title, html, thumb_media_id)
    
    media_id = result.get('media_id', '')
    errcode = result.get('errcode', 0)
    
    if errcode == 0 and media_id:
        print("")
        print("=========================================")
        print("  草稿创建成功！🎉")
        print("=========================================")
        print(f"media_id: {media_id}")
        print("")
        print("请到 mp.weixin.qq.com 草稿箱确认并发布")
    else:
        print(f"草稿创建失败: {result}")
        sys.exit(1)

if __name__ == "__main__":
    main()
