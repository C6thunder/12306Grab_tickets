class Config:
    # 类不需要定义的太复杂，只需要定义一些属性即可
    # 12306
    fromstation = '北京'              # '无锡'
    destination = '无锡'
    date = '2025-01-17'  # 写成标准形式 2025-01-02 而不是 2025-1-2
    # 12306
    # trainnumber = ['G2812','G1826']  # 适用于 推荐使用12306pro_v2.py 如果第一个车次没抢到会抢第二个车次(T_T)  
    trainnumber = ['G7','G125']
    passengernum = '0'  # 第一个乘车人是 0  
    stu_seat = 1        # 0: 不用学生票  1：学生票


