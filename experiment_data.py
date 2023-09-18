import random

import numpy as np

if __name__ == '__main__':

    # Cplex求解时需要用到的变量
    user_size, res_size, server_size, delta_links = 100, 4, 10, 6
    bids, caps, S = {}, {}, {}
    delta = {}
    R_rate = 1.0 # 1.55==100%  1.0==65% 0.4==25% 0.78==50% 1.17==75%
    edge_BW = 10
    cloud_BW = 100

    # 从huawei_data.txt读入数据并放入到res和user变量中
    res, user = [], []

    with open('data/huawei_data.txt', 'r', encoding='utf8') as data:
        data.readline()
        res = list(map(int, data.readline().strip('\n').split()))
        n = int(data.readline().strip('\n'))
        for i in range(n):
            user.append(list(map(int, data.readline().strip('\n').split())))

    random.shuffle(user)
    # 生成用户的出价(均匀分布)
    user_bid = [0] * user_size
    unit_price = [43.5, 15.2, 0.35, 20]  # 元/每月
    times = [0] * user_size  # 用户估值为单价的倍数
    coins = []
    while True:
        for i in range(user_size):
            coin = np.random.randint(0, 2)
            if coin:  # 从0.2 - 1中生成一个倍数
                times[i] = np.random.randint(2, 11) / 10
            else:  # 从1 - 5中生成一个倍数
                times[i] = np.random.randint(10, 51) / 10
            coins.append(coin)

        # if res_size == 1:   # 单资源，期望为300的均匀分布
        #     user_bid = np.random.uniform(100, 501, size=(1, user_size))
        # else:               # 多资源，期望为600的均匀分布
        #     user_bid = np.random.uniform(200, 1001, size=(1, user_size))

        # # 生成用户的出价(正态分布)
        # flag = True
        # while flag:
        #     flag = False
        #     if res_size == 1:
        #         user_bid = np.random.normal(loc=300, scale=150, size=(1, user_size))
        #     else:
        #         user_bid = np.random.normal(loc=600, scale=300, size=(1, user_size))
        #
        #     for i in range(user_size):
        #         if user_bid[0][i] < 10:
        #             flag = True

        # user_bid = user_bid.tolist()[0]
        # for i in range(user_size):
        #     user_bid[i] = round(user_bid[i], 1)
        # print(user_bid)

        # 将res和user变量中的数据按照一定格式写入到data2.txt中供C++算法调用
        # with open('./data', 'w+', encoding='utf8') as f:
        # 写入用户数量以及资源种类数
        # f.write('p %d %d\n' % (user_size, res_size))

        # 写入用户需求(res_size种资源)
        for i in range(user_size):
            for j in range(res_size):
                if j < 3:
                    num = user[i][j]
                    # f.write('d %d %d %d\n' % (i + 1, j + 1, num))
                    S[(i + 1, j + 1)] = num
                elif j == 3:
                    S[(i + 1, j + 1)] = random.randint(1, 2)

        # print(coins)
        print(sum(coins) / len(coins))  # 均值为0.5左右
        # print(times)
        print(sum(times) / len(times))  # 0.6和3的均值, 1.8左右

        for i in range(user_size):
            bid_i = 0
            for j in range(res_size):
                bid_i += times[i] * unit_price[j] * S[(i + 1, j + 1)]
            user_bid[i] = round(bid_i)

        if 4450 <= max(user_bid) <= 4550:  # 限制bmaxh
            break

        # break

    print(user_bid)
    print('--------------------------------------------------------------------\n')
    print(max(user_bid))

    # 写入用户报价
    for i in range(user_size):
        # f.write('b %d %f\n' % (i + 1, user_bid[i]))
        bids[i + 1] = user_bid[i]

    # 写入服务器容量
    # cr = np.random.normal(loc=)
    s = 'r'
    r_cpu, r_ram, r_harware = [], [], []
    cpuf = True
    while cpuf:
        cpuf = False
        r_cpu = np.random.normal(loc=92, scale=0.5, size=server_size)
        # r_cpu = [r_cpu[i] * R_rate for i in range(server_size)]
        for indx in r_cpu:
            if indx < 0:
                cpuf = True
    ramf = True
    while ramf:
        ramf = False
        r_ram = np.random.normal(loc=160, scale=1.0, size=server_size)
        # r_ram = [r_ram[i] * R_rate for i in range(server_size)]
        for indx in r_ram:
            if indx < 0:
                ramf = True
    hdf = True
    while hdf:
        hdf = False
        r_harware = np.random.normal(loc=1536, scale=2.0, size=server_size)
        # r_harware = [r_harware[i] * R_rate for i in range(server_size)]
        for indx in r_harware:
            if indx < 0:
                hdf = True

    for j in range(server_size):
        for r in range(res_size):
            # s += ' %d' % res[r]
            if r == 0:
                caps[(j + 1, r + 1)] = round(r_cpu[j] * R_rate)
            if r == 1:
                caps[(j + 1, r + 1)] = round(r_ram[j] * R_rate)
                # caps[(j + 1, r + 1)] = round(r_ram[j] * 0.5)
            if r == 2:
                caps[(j + 1, r + 1)] = round(r_harware[j])
                # caps[(j + 1, r + 1)] = round(r_harware[j] * 0.5)
            if r == 3:
                # caps[(j + 1, r + 1)] = edge_BW
                caps[(j + 1, r + 1)] = round(edge_BW * R_rate)
    # f.write(s + '\n')
    # print('各种资源种类的容量为: ' + s.lstrip("r "))

    # 写入部署约束
    _delta_ = []
    for indxs in range(user_size):
        del_s = np.random.randint(low=0, high=2, size=server_size, dtype='int')
        while sum(del_s) == 0:
            del_s = np.random.randint(low=0, high=2, size=server_size, dtype='int')
        _delta_.append(del_s)
    while sum(sum(_delta_)) > (user_size * delta_links):
        ind_i = np.random.randint(low=0, high=user_size)
        ind_j = np.random.randint(low=0, high=server_size)
        if sum(_delta_[ind_i]) > 1:
            _delta_[ind_i][ind_j] = 0

    while sum(sum(_delta_)) < (user_size * delta_links):
        ind_i = np.random.randint(low=0, high=user_size)
        ind_j = np.random.randint(low=0, high=server_size)
        _delta_[ind_i][ind_j] = 1

    print(sum(sum(_delta_)))
    for i in range(user_size):
        for j in range(server_size):
            delta[(i + 1, j + 1)] = _delta_[i][j]

    print("data generated again...")
    print(caps)

    '''create sigma'''
    sigma = []
    for i in range(user_size):
        sigma.append(random.uniform(0.01, 0.2))

    bi = list(bids.values())
    si = list(S.values())
    si = np.array(si)
    si = si.reshape(user_size, res_size)
    # delta = _delta_
    c_ = list(caps.values())
    c_ = np.array(c_)
    c_ = c_.reshape(server_size, res_size)

    np.savetxt("data/data_bi.txt", bi, fmt="%.2f")
    np.savetxt("data/data_si.txt", si, fmt="%d")
    np.savetxt("data/data_delta.txt", _delta_, fmt="%d")
    np.savetxt("data/data_cr.txt", c_, fmt="%d")
    np.savetxt("data/data_eBW.txt", [edge_BW], fmt="%d")
    np.savetxt("data/data_cBW.txt", [cloud_BW], fmt="%d")
    np.savetxt("data/data_sigma.txt", sigma, fmt="%.2f")
    print("数据生成成功")
