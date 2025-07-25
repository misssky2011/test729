import requests

# DeepAI NSFW API endpoint
API_URL = 'https://api.deepai.org/api/nsfw-detector'

# 获取 DeepAI API 密钥（从DeepAI网站注册）
API_KEY = 'wc6UeFYRIBAbY6clz-gY7n_UAShNJMmzyjNlbei9VZL-PKDr-xIZmA'


# 读取图像并发送到DeepAI NSFW API
def check_nsfw(image_path):
    with open (image_path, 'rb') as image_file:
        response = requests.post (
            API_URL,
            files={'image': image_file},
            headers={'api-key': API_KEY}
        )

    if response.status_code == 200:
        # 输出API返回的结果
        data = response.json ()
        nsfw_score = data['output']['nsfw_score']

        print (f"NSFW score: {nsfw_score}")
        if nsfw_score > 0.5:
            print ("The image contains inappropriate content.")
        else:
            print ("The image does not contain inappropriate content.")
    else:
        print (f"Error: {response.status_code}, {response.text}")


# 使用示例
image_path = 'C:/Users/figo/Pictures/br/12.jpg'  # 替换为您的图像路径
check_nsfw (image_path)
