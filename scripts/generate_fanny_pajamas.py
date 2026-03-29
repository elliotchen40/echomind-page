import requests
import base64
import json

# 读取图片并转base64
image_path = "/root/.openclaw/workspace/media/fanny/2026-03-28-avatar.jpg"
with open(image_path, "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode()

# API配置
api_key = "sk-cp-P8A3crJvBKzFjNHQDFnbooCd_1wvFDq0SSsESP2NRGTESjf3QURLdcj8bDnRf3HHm4Xocg8OACXK9-AozutDd2K4T20zIgoCNH0bcjd7yZLlIfF3H4BrycA"
url = "https://api.minimaxi.com/v1/image_generation"

# 用户提供的prompt
prompt = """Replace the clothing of the person with a delicate sheer lingerie set in soft peach pink color, consisting of a babydoll dress and a matching thong. The babydoll has a deep V-neckline with floral lace cups, thin spaghetti straps, a small bow at the center of the chest, and a short, flowy, semi-transparent mesh skirt. The matching thong features lace detailing and thin straps.

Keep the person's face, body shape, pose, hairstyle, and expression exactly the same.

Keep the original background, lighting, camera angle, composition, and image style unchanged.

Preserve skin tone, shadows, and all environmental details.

Only change the clothing, ensuring natural fit, realistic fabric behavior, and accurate lighting interaction.

The result should look photorealistic and seamless, with no distortion or artifacts.

Only modify the clothing. Do not change anything else.

Do not alter the face, identity, pose, body proportions, hands, or legs.

Do not change background, lighting, shadows, perspective, or composition.

Maintain exact pixel-level consistency for all non-clothing areas.

Ensure the new outfit fits naturally on the body with correct folds, transparency, and lighting.

No extra accessories, no additional elements, no style change."""

# 发送请求
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "image-01",
    "image_base64": img_base64,
    "prompt": prompt
}

print("正在发送请求...")
response = requests.post(url, headers=headers, json=payload)
print(f"状态码: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if "data" in result and "image_urls" in result["data"] and len(result["data"]["image_urls"]) > 0:
        image_url = result["data"]["image_urls"][0]
        print(f"\n生成的图片URL: {image_url}")
        # 保存结果到文件
        with open("/root/.openclaw/workspace/media/fanny/2026-03-28-pink-pajamas-v3.result.json", "w") as f:
            json.dump(result, f, indent=2)
else:
    print(f"错误响应: {response.text}")
