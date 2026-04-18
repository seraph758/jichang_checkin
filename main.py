import requests
import json
import os

# 从环境变量获取配置
URL = os.environ.get('URL', '').rstrip('/')
SCKEY = os.environ.get('SCKEY', '')
CONFIG = os.environ.get('CONFIG', '')

LOGIN_URL = f'{URL}/auth/login'
CHECKIN_URL = f'{URL}/user/checkin'

def sign(order: int, email: str, passwd: str):
    session = requests.session()
    headers = {
        'origin': URL,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }
    
    data = {'email': email.strip(), 'passwd': passwd.strip()}

    try:
        print(f'=== 账号 {order} 开始签到 ===')
        print(f'邮箱：{email}')

        # 登录
        resp = session.post(LOGIN_URL, headers=headers, data=data, timeout=30)
        print(f'登录响应: {resp.text}')
        result = resp.json()
        print(result.get('msg', '无 msg 字段'))

        # 签到
        resp2 = session.post(CHECKIN_URL, headers=headers, timeout=30)
        print(f'签到响应: {resp2.text}')
        result2 = resp2.json()
        content = result2.get('msg', '签到完成')

        print(f'签到结果：{content}')

        # Server酱推送
        if SCKEY:
            push_url = f'https://sctapi.ftqq.com/{SCKEY}.send?title=机场签到&desp={content}'
            requests.get(push_url, timeout=10)   # 用 GET 更稳定
            print('Server酱推送成功')

    except json.JSONDecodeError:
        print('返回内容不是有效 JSON')
        content = '签到失败：返回非 JSON'
    except requests.exceptions.RequestException as e:
        print(f'网络请求异常: {e}')
        content = f'签到失败：网络错误 {e}'
    except Exception as e:
        print(f'未知异常: {e}')
        content = f'签到失败：{e}'
    finally:
        if SCKEY and '失败' in content:
            try:
                push_url = f'https://sctapi.ftqq.com/{SCKEY}.send?title=机场签到&desp={content}'
                requests.get(push_url, timeout=10)
                print('失败推送已发送')
            except:
                print('推送失败')
        
        print(f'=== 账号 {order} 签到结束 ===\n')


if __name__ == '__main__':
    if not CONFIG:
        print('CONFIG 环境变量为空')
        exit(1)

    configs = [line.strip() for line in CONFIG.splitlines() if line.strip()]
    
    if len(configs) % 2 != 0 or len(configs) == 0:
        print('配置文件格式错误：必须是偶数行（邮箱+密码交替）')
        exit(1)

    user_quantity = len(configs) // 2
    print(f'共检测到 {user_quantity} 个账号')

    for i in range(user_quantity):
        email = configs[i * 2]
        pwd = configs[i * 2 + 1]
        sign(i + 1, email, pwd)   # 从 1 开始计数更友好
