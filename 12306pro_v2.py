from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config import Config  # 信息保存在config.py里
import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 增加车次平替功能
# Z，K，G 已测试可用，K于Z相似所以 K 测试较少

# check_available_tickets()函数用来判断是否有预订按钮是非常快的，自己尝试的其他方法都很慢~(^T^)~
# 判断是否有预订按钮非常影响速度，如果有人感觉自己写的代码慢，大概率是因为这个
def check_available_tickets():
    # 使用 JavaScript 直接获取符合条件的车次信息
    tickets_info = driver.execute_script("""
        const tickets = [];
        const rows = document.querySelectorAll('#queryLeftTable tr:not([style*="display: none"])');
        
        for (const row of rows) {
            const trainNumber = row.querySelector('.number')?.textContent;
            const bookingBtn = row.querySelector('.btn72');
            const ywStatus = row.querySelector('td:nth-child(8)')?.textContent;
            
            if (bookingBtn && trainNumber && ywStatus) {
                tickets.push({
                    trainNumber: trainNumber,
                    hasButton: true,
                    status: ywStatus
                });
            }
        }
        return tickets;
    """)
    return tickets_info


def get_ticket(conf, driver, url):
    # 过网站检测，没加这句的话，账号密码登录时滑动验证码过不了，但二维码登录不受影响
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined})"""})
    driver.maximize_window()
    driver.get(url)

    # 获取并点击右上角登录按钮
    time.sleep(1)
    login = driver.find_element(by=By.ID, value='J-btn-login')
    login.click()

    # 扫码登录
    scan_QR = driver.find_element(by=By.XPATH, value='//*[@id="toolbar_Div"]/div[2]/div[2]/ul/li[2]/a')
    scan_QR.click()
    driver.implicitly_wait(20)

    # 点击车票预订跳转到预订车票页面
    driver.find_element(by=By.XPATH, value='//*[@id="link_for_ticket"]').click()

    # 输入出发地和目的地信息
    # 出发地
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').click()
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').clear()
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').send_keys(conf.fromstation)
    time.sleep(1)
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').send_keys(Keys.ENTER)

    # 目的地
    destination_tag = driver.find_element(by=By.XPATH, value='//*[@id="toStationText"]')
    destination_tag.click()
    destination_tag.clear()
    destination_tag.send_keys(conf.destination)
    time.sleep(1)
    destination_tag.send_keys(Keys.ENTER)
    driver.implicitly_wait(5)

    # 出发日期
    date_tag = driver.find_element(by=By.XPATH, value='//*[@id="train_date"]')
    date_tag.click()
    date_tag.clear()
    date_tag.send_keys(conf.date)
    time.sleep(1)
    query_tag = driver.find_element(by=By.XPATH, value='//*[@id="query_ticket"]')


    while True:

        # 如果查询按钮可用，点击查询
        if query_tag.get_attribute('class') == "btn92s":
            driver.execute_script("arguments[0].click();", query_tag)

        # 使用新的车票查询方法
        available_tickets = check_available_tickets()

        if not available_tickets:
            print("未找到预订按钮，继续等待...")
            time.sleep(random.uniform(0.097, 0.345))
            continue

        print("12306出票！！")
        start = time.time()

        # 尝试按顺序购买多个车次
        for train_number in conf.trainnumber:
            target_ticket = next((ticket for ticket in available_tickets
                                  if ticket['trainNumber'] == train_number and "候补" not in ticket['status']), None)

            if target_ticket:
                print(f"找到可预订的车次：{train_number}")

                # 使用 JavaScript 直接点击对应车次的预订按钮
                driver.execute_script("""
                    const rows = document.querySelectorAll('#queryLeftTable tr:not([style*="display: none"])');
                    for (const row of rows) {
                        if (row.querySelector('.number')?.textContent === arguments[0]) {
                            row.querySelector('.btn72').click();
                            break;
                        }
                    }
                """, train_number)

                # 选择乘车人
                string = f'//*[@id="normalPassenger_{conf.passengernum}"]'
                driver.find_element(by=By.XPATH, value=string).click()
                
                # 学生票判断
                if conf.stu_seat:
                    driver.find_element(by=By.XPATH, value='//*[@id="dialog_xsertcj_ok"]').click()

                
                if train_number.startswith("Z") or train_number.startswith("K"):   # 判断是否为Z系列 或 K系列
                
                    # Z,K系列  没找到软座，应该没有软座
                    driver.find_element(by=By.XPATH, value='//*[@id="seatType_1"]').click()      
                                    
                    # Z,k 硬座 
                    if conf.Z_seat==1:               
                        # 依旧使用 JavaScript 来选择来加快速度   注意：选择型不能用简单的click点击
                        log = driver.execute_script("""
                            var selectElement = document.querySelector('#seatType_1');
                            var option = selectElement.querySelector('option[value="1"]');
                            if (option){
                                option.selected = true;
                                selectElement.dispatchEvent(new Event('change'));     // 触发选择
                                return "找到座位！";
                            } else {
                                return "没有硬座了，听从12306分配";                  
                            }
                        """)

                    # Z,k 硬卧
                    elif conf.Z_seat==3:
                        log = driver.execute_script("""
                            var selectElement = document.querySelector('#seatType_1');
                            var option = selectElement.querySelector('option[value="3"]');
                            if (option){
                                option.selected = true;
                                selectElement.dispatchEvent(new Event('change'));
                                return "找到座位！";
                            } else {
                                return "没有硬卧了，听从12306分配";                  
                            }
                        """)

                    
                    # Z,k 软卧
                    if conf.Z_seat==4:
                        log = driver.execute_script("""
                            var selectElement = document.querySelector('#seatType_1');
                            var option = selectElement.querySelector('option[value="4"]');
                            if (option){
                                option.selected = true;
                                selectElement.dispatchEvent(new Event('change'));
                                return "找到座位！";
                            } else {
                                return "没有软卧了，听从12306分配";                  
                            }
                        """)
                    # Z K如果没抢到要求座位，会抢12306默认座位
                    

                # 提交订单
                driver.find_element(by=By.XPATH, value='//*[@id="submitOrder_id"]').click()

                print(log)
                # # 选座 F座
                if train_number.startswith("G"):
                    driver.execute_script('''
                        var element = document.evaluate(
                            '/html/body/div[6]/div/div[5]/div[1]/div/div[2]/div[2]/div[3]/div[2]/div[2]/ul[2]/li[2]/a[@id="1F"]', 
                            document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
                        ).singleNodeValue;
                        if (element) { element.click(); }
                    ''')

                # 点击确认支付
                element = driver.find_element(by=By.XPATH,
                                              value='//*[@id="qr_submit_id" and @class="btn92s"]'
                                              )
                element.click()

                current_time = time.time()

                print(f"！！！{train_number}次列车抢票成功，总用时{current_time-start}秒，请尽快在10分钟内支付！")
                return
            else:
                print(f"{train_number}次车次未找到可预订票，继续尝试下一个车次。")
                continue

        # 极短暂延迟，避免CPU占用过高
        time.sleep(0.001)


if __name__ == '__main__':
    # 有关车票的配置信息保存在该类里
    # 请事先在config.py里填好相关信息
    conf = Config()

    url = 'https://www.12306.cn/index/'

    # 用chrome浏览器打开网页
    driver = webdriver.Chrome()                       
    get_ticket(conf, driver, url)
    time.sleep(10)
    driver.quit()
