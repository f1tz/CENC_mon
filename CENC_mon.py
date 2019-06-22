# -*- coding: utf-8 -*-
import re, requests, time

phonenum = '17127290868'  # 接收通知的手机号
print_flag = True  # 是否打印详细信息 True / False
notify_level = 4  # 预设震级
notify_location = '四川'  # 预设监控地区
interval = 5  # 监控间隔 秒


def monitor():  # 监控模块
    global notify_level, notify_location

    source = 'http://www.ceic.ac.cn/speedsearch'
    pattern = re.compile('<tr.*?>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>'
                         '.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?><a href="(.*?)">(.*?)</a></td>.*?</tr>',
                         re.S)
    latestID = logger()

    while True:
        try:
            r = requests.get(source)
            result = re.findall(pattern, r.text)
            if len(result):  # 如果24小时内有地震才继续
                result = result[0]
                # Index 0=震级,1=发震时刻,2=纬度,3=经度,4=深度,5=URL,6=参考位置
                level = result[0]
                location = result[6]
                url = result[5]
                logid = url[23:-5]
                if print_flag:
                    msg = '[+]最新地震信息如下：\n    [-]震级：%s	\n    [-]发震时刻(UTC+8)：%s	' \
                          '\n    [-]纬度(°)：%s	\n    [-]经度(°)：%s	' \
                          '\n    [-]深度(千米)：%s	\n    [-]参考位置：%s \n    [-]详细信息：%s \n' % \
                          (level, result[1], result[2], result[3], result[4], location, url)
                    print(msg)
                if logid == latestID:
                    print('[*]地震信息未发生变化，持续监控中...\n')
                else:
                    print('    [+]信息已更新')
                    latestID = logid
                    logger(latestID)
                    if round(float(level)) >= notify_level:
                        print('    [+]已达到预设震级')
                        if notify_location in location:
                            print('    [+]地震发生在%s，正在尝试发送通知... \n' % notify_location)
                            sender()  # 发通知

            else:
                print('[*]最近24小时内没有发生地震\n')

        except Exception as e:
            print('[!]获取信息失败 \n', e)

        # 休眠时间
        time.sleep(interval)


def sender():  # 通知模块
    global phonenum
    api_url = 'http://47.97.77.195:8083/training/user/smsSend?' \
              'accessToken=null&account=%s&accountType=1&channel=4' % phonenum
    try:
        r = requests.post(api_url)
        if r.status_code == 200:
            if '成功' in r.text:
                print('    [+]%s 短信通知已发送\n' % phonenum)
            else:
                print('    [+]短信接口似乎出现问题了，通知没有发送\n')
        else:
            print('    [!]短信通知发送失败\n')
    except:
        print('    [!]短信通知发送失败\n')


def logger(logid=''):  # 日志模块
    if logid == '':
        try:
            with open('CENC_log.txt', 'r') as f:
                logid = f.readline()
                return logid
        except FileNotFoundError:
            with open('CENC_log.txt', 'w') as f:
                print('[!]首次运行监控，日志文件不存在，已创建\n')
                return ''
    else:
        try:
            with open('CENC_log.txt', 'w') as f:
                f.write(logid)
        except Exception:
            with open('CENC_log.txt', 'w') as f:
                print('[!]写日志未知错误\n')


if __name__ == '__main__':
    monitor()
