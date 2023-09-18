import math
import sys
import time

import numpy as np
import readdata

_bid_, _req_, _delta_, _re_, eBW, cBW, _sigma_ = readdata.get_data()

"""数据生成，资源数据的最后一维是带宽资源"""
# ecs_cap = np.array([[40, 40, 200, 3], [40, 40, 200, 3]])
# user_deploy = np.array([[1, 0], [1, 1], [1, 1], [0, 1]])
# user_req = np.array([[4, 4, 3, 3], [3, 3, 2, 3], [3, 4, 3, 3], [2, 2, 2, 2]])
# user_sigma = np.array([0.15, 0.44, 0.53, 0.6], dtype=np.float64)
# user_bid = np.array([14, 10, 15, 8], dtype=np.float64)

ecs_cap = np.array(_re_)
user_deploy = np.array(_delta_)
user_req = np.array(_req_)
user_sigma = np.array(_sigma_, dtype=np.float64)
user_bid = np.array(_bid_, dtype=np.float64)

"""变量初始化"""
ECS_SIZE = len(_re_)
USER_SIZE = len(_bid_)

if ECS_SIZE > 0:
    RES_SIZE = len(_re_[0])
else:
    RES_SIZE = 0

ClOUD_BW = cBW
MAX_BID = 0
"""epsilon"""
step = 0.1
"""云端带宽单价"""
unit_price_cloudBW = 0
"""记录每轮的活跃用户集合，初始全为1"""
all_active_user = np.ones(USER_SIZE, dtype=np.int64)
"""记录分配和支付的变量"""
winner = np.zeros((USER_SIZE, ECS_SIZE))
deploy_type = np.zeros(USER_SIZE)  # 1 表示处理在边缘端 ,2 表示处理在云端, 0 表示未分配
payment = np.zeros((USER_SIZE, ECS_SIZE), dtype=np.float64)
totalpay = 0


class ECS:
    ####### initializa ECS ###############
    def __init__(self, id, cap):
        self.id = id
        self.cap = cap
        self.unit_price = np.array([0 for _ in range(RES_SIZE)], dtype=np.float64)
        self.active_user = np.array([0 for _ in range(USER_SIZE)])
        self.p_cloud = np.array([MAX_BID for _ in range(USER_SIZE)], dtype=np.float64)
        self.p_edge = np.array([MAX_BID for _ in range(USER_SIZE)], dtype=np.float64)

    #### update unit price of this ECS
    def update_unit_price(self):
        for r in range(RES_SIZE):
            total_res = 0
            for i in range(USER_SIZE):
                if self.active_user[i] != 0:
                    total_res += USERs[i].req[r]
            exp = max((total_res - self.cap[r]) / self.cap[r], 0)
            # exp = max((total_res - self.cap[r]) / self.cap[r], 1)

            # lamda = math.pow(math.e, exp)
            # self.unit_price[r] += lamda * step
            self.unit_price[r] += exp * step


class USER:
    def __init__(self, id, req, deploy, sigma, bid):
        self.id = id
        self.req = req
        self.deploy = deploy
        self.sigma = sigma
        self.bid = bid
        self.norm = self.get_norm()

    ##  get norm of the user
    def get_norm(self):
        res = 0
        r_cap = [0 for _ in range(RES_SIZE)]
        for r in range(RES_SIZE):
            for j in range(ECS_SIZE):
                r_cap[r] += ECSs[j].cap[r]
        for r in range(RES_SIZE):
            res += pow(self.req[r] / r_cap[r], 2)
        return math.sqrt(res)


###### get active user of this ECS
def get_active_user(users, ecss):
    for user in users:
        for ecs in ecss:
            if user_deploy[user.id][ecs.id] == 1:
                ##  the cost of processing in edge
                cost = ecs.unit_price[0] * user.req[0] + ecs.unit_price[1] * user.req[1] + ecs.unit_price[2] * user.req[
                    2] + ecs.unit_price[3] * user.req[3] + unit_price_cloudBW * user.sigma * user.req[3]
                ##  the cost of processing in cloud
                cost1 = (unit_price_cloudBW + ecs.unit_price[3]) * user.req[3]
                if cost1 > user.bid or cost > user.bid:
                    all_active_user[user.id] = 0
                    for js in ecss:
                        js.active_user[user.id] = 0
                    break
                else:
                    ecs.active_user[user.id] = 1


ECSs = [ECS(_, ecs_cap[_].copy()) for _ in range(ECS_SIZE)]
USERs = [USER(_, user_req[_].copy(), user_deploy[_].copy(), user_sigma[_].copy(), user_bid[_].copy()) for _ in
         range(USER_SIZE)]
cloud_BW = ClOUD_BW
edge_flag = None
index_j = -1
index_i = -1

"""MaxB"""
maxB = 46500

if __name__ == '__main__':
    start = time.perf_counter()
    round = 0
    while True:
        round += 1
        print("-----------------------round %d---------------------------------" % round)
        """更新活跃用户"""
        get_active_user(USERs, ECSs)
        # print("活跃用户为：", all_active_user)
        """更新服务器资源单价"""
        for j in ECSs:
            j.update_unit_price()
            # print("EDS %d 的资源单价为：" % j.id, j.unit_price)
        """计算云端带宽单价"""
        for j in ECSs:
            unit_price_cloudBW += j.unit_price[RES_SIZE - 1] * j.cap[RES_SIZE - 1]
        unit_price_cloudBW /= ClOUD_BW
        unit_price_cloudBW *= 30
        # print("云端带宽单价为：%.2f" % unit_price_cloudBW)
        """更新活跃用户"""
        get_active_user(USERs, ECSs)
        print("活跃用户为：", all_active_user)
        """用户依据模排序"""
        USERs.sort(key=lambda x: x.norm, reverse=True)
        print("排序后的用户列表为：", [USERs[i].id for i in range(USER_SIZE)])
        """-------------------------------------------------------------------"""
        """分配与定价"""
        for i in USERs:
            pi = 0
            flags = 1
            """更新活跃用户"""
            # get_active_user(USERs, ECSs)
            for j in ECSs:
                if j.active_user[i.id] != 0:
                    """计算云端支付"""
                    if (j.cap[3] - i.req[3] >= 0) and (cloud_BW - i.req[3] >= 0):
                        j.p_cloud[i.id] = (j.unit_price[3] + unit_price_cloudBW) * i.req[3]
                    """计算边缘端支付"""
                    if all(map(lambda x: x >= 0, j.cap - i.req)) and ((cloud_BW - i.req[3] * i.sigma) >= 0):
                        j.p_edge[i.id] = j.unit_price[0] * i.req[0] + j.unit_price[1] * i.req[1] + j.unit_price[2] * \
                                         i.req[2] + j.unit_price[3] * i.req[3] + unit_price_cloudBW * i.req[3] * i.sigma
                    """比较两边支付高低"""
                    p_ij = max(j.p_cloud[i.id], j.p_edge[i.id])
                    if pi < p_ij:
                        pi = p_ij
                        index_j = j.id
                        index_i = i.id
                        if pi == j.p_edge[i.id]:
                            edge_flag = 1
                        elif pi == j.p_cloud[i.id]:
                            edge_flag = 0
            if pi == 0 or flags == 0:
                continue
            """更新资源容量"""
            if edge_flag == 1:
                """分配在边缘"""
                ECSs[index_j].cap -= i.req
                cloud_BW -= i.req[RES_SIZE - 1] * i.sigma
                deploy_type[i.id] = 1
            elif edge_flag == 0:
                """分配在云端"""
                ECSs[index_j].cap[RES_SIZE - 1] -= i.req[RES_SIZE - 1]
                cloud_BW -= i.req[RES_SIZE - 1]
                deploy_type[i.id] = 2
            else:
                print("edge_flag 出错！")
            """更新判别矩阵x"""
            winner[i.id][index_j] = 1
            """记录总支付"""
            totalpay += pi
            payment[i.id][index_j] = float('%.2f' % pi)
            """更新活跃用户"""
            for j in ECSs:
                j.active_user[i.id] = 0
            all_active_user[i.id] = 0
        """退出循环条件"""
        if totalpay >= maxB:
            break
        """该轮分配失败，重置资源"""
        for j in ECSs:
            j.cap = ecs_cap[j.id].copy()
            j.p_cloud = [MAX_BID for _ in range(USER_SIZE)]
            j.p_edge = [MAX_BID for _ in range(USER_SIZE)]
        cloud_BW = ClOUD_BW
        unit_price_cloudBW = 0
        all_active_user = np.ones(USER_SIZE, dtype=np.int64)
        deploy_type = np.zeros(USER_SIZE, dtype=np.int64)
        payment = np.zeros((USER_SIZE, ECS_SIZE), dtype=np.float64)
        totalpay = 0
        USERs.sort(key=lambda x: x.id)
        edge_flag = None
        index_j = -1
    print('///////////////////////////////////////////////final/////////////////////////////')
    # print('winner is\n', winner)
    end = time.perf_counter()
    USERs.sort(key=lambda x: x.id)
    print('deploy type  is', deploy_type)
    for i in range(ECS_SIZE):
        print('ECS', i, 'resource unitprice is', ECSs[i].unit_price)
    print('cloud BW remain is', cloud_BW)
    # print('payment is\n', payment)
    print("总轮数：", round)
    sum_cap_user = [0] * RES_SIZE
    sum_sw = 0
    sum_user = 0
    user_edge = 0
    user_cloud = 0
    for i in range(len(deploy_type)):
        if deploy_type[i] == 1:
            for r in range(RES_SIZE - 1):
                sum_cap_user[r] += USERs[i].req[r]
            sum_cap_user[RES_SIZE - 1] += USERs[i].req[RES_SIZE - 1] * USERs[i].sigma + USERs[i].req[RES_SIZE - 1]
            sum_sw += USERs[i].bid
            sum_user += 1
            user_edge += 1
        if deploy_type[i] == 2:
            sum_cap_user[RES_SIZE - 1] += USERs[i].req[RES_SIZE - 1] * 2
            sum_sw += USERs[i].bid
            sum_user += 1
            user_cloud += 1
    sum_cap_ecs = np.sum(ecs_cap, axis=0)
    for i in range(USER_SIZE):
        paysuser = []
        paycloud = []
        if sum(payment[i]) != 0:
            print("用户%d支付为：" % i, sum(payment[i]))
            for j in range(ECS_SIZE):
                if payment[i][j] != 0:
                    print("分配在%d服务器上" % j)
                if _delta_[i][j] == 1:
                    paysuser.append(ECSs[j].unit_price[0] * USERs[i].req[0] + ECSs[j].unit_price[1] * USERs[i].req[1] + \
                                    ECSs[j].unit_price[2] * USERs[i].req[2] + ECSs[j].unit_price[3] * USERs[i].req[
                                        3] + unit_price_cloudBW * USERs[i].req[3] * USERs[i].sigma)
                    paycloud.append((ECSs[j].unit_price[3] + unit_price_cloudBW) * USERs[i].req[3])
            # print("用户需求：", USERs[i].req)
            # print("可分配服务器价格：", paysuser)
            # print("云端价格：", paycloud)
            break
    print("资源利用率：", [sum_cap_user[r] / sum_cap_ecs[r] for r in range(RES_SIZE - 1)])
    print("带宽资源利用率：", sum_cap_user[RES_SIZE - 1] / (sum_cap_ecs[RES_SIZE - 1] + cBW))
    # print("总出价：", sum(_bid_))
    print("社会福利为：", sum_sw)
    print('总支付为：', float('%.2f' % totalpay))
    print("胜出用户人数为：", sum_user)
    print("云端分配比例为：", user_cloud / sum_user)
    print('执行时间为：', end - start)
