import copy
import math
import sys
import time

import numpy as np
import readdata

_bid_, _req_, _delta_, _re_, eBW, cBW, _sigma_ = readdata.get_data()

ECS_SIZE = len(_re_)
USER_SIZE = len(_bid_)

if ECS_SIZE > 0:
    RES_SIZE = len(_re_[0])
else:
    RES_SIZE = 0

ecs_cap = np.array(_re_)
user_deploy = np.array(_delta_)
user_req = np.array(_req_)
user_sigma = np.array(_sigma_, dtype=np.float64)
user_bid = np.array(_bid_, dtype=np.float64)


class USER:
    def __init__(self, id, req: list, deploy: list, bid: float, sigma: float):
        self.id = id
        self.deploy = deploy
        self.req = req
        self.bid = bid
        self.sigma = sigma
        self.allocated = False


class ECS:  # 服务器类
    def __init__(self, id, r_: list):
        self.id = id
        self.cap = r_


def is_feasible(User: USER, cpr):
    flag = True
    for r in range(RES_SIZE):
        if User.req[r] > cpr[r]:
            flag = False
            break
    return flag


def g_pmrm_win(users, Ecss):
    max_payment = 0
    obj_X = [[0] * USER_SIZE] * ECS_SIZE
    bw_cloud = cBW
    bw_cloud2 = cBW
    for ecs in Ecss:
        Users = []

        for i in users:
            if _delta_[i.id][ecs.id] == 1 and i.allocated is False:
                Users.append(i)
        """First phase"""
        cap = ecs.cap.copy()
        obj_x1 = [0] * USER_SIZE
        canallocatuser = []
        half_cap = np.array(cap)
        for user in Users:
            if is_feasible(user, cap):
                canallocatuser.append(user)
        max_pay = 0
        max_j = -1
        for user in canallocatuser:
            if user.bid > max_pay and all(map(lambda x: x >= 0, half_cap - user.req)) and bw_cloud - (
                    user.req[3] * user.sigma) > 0:
                max_pay = user.bid
                max_j = user.id
                bw_cloud -= user.req[3] * user.sigma
        if max_j != -1:
            obj_x1[max_j] = 1
        """Second phase"""
        canallocatuser2 = []
        obj_x2 = [0] * USER_SIZE
        for user in Users:
            if is_feasible(user, half_cap):
                canallocatuser2.append(user)
        if len(canallocatuser2) == 0:
            continue
        norm_di = []
        for user in canallocatuser2:
            sum_rec = 0
            for r in range(RES_SIZE):
                sum_rec += user.req[r] / cap[r]
            sum_rec = sum_rec ** 0.5
            norm_di.append([user.id, user.bid / sum_rec])
        norm_di.sort(key=lambda x: x[1], reverse=True)
        allocate_user = []
        cap_copy = [0] * RES_SIZE
        flag = True
        while (len(canallocatuser2) != 0) and flag:
            index_i = norm_di[0][0]
            for r in range(RES_SIZE):
                if half_cap[r] - users[index_i].req[r] < 0 or bw_cloud2 - (
                        users[index_i].req[3] * users[index_i].sigma) < 0:
                    flag = False
            if flag:
                copyi = 0
                for i in range(len(canallocatuser2)):
                    if canallocatuser2[i].id == index_i:
                        copyi = i
                        allocate_user.append(canallocatuser2[copyi])
                        del canallocatuser2[i]
                        del norm_di[0]
                        break
                obj_x2[index_i] = 1
                for r in range(RES_SIZE):
                    # cap_copy[r] += Users[copyi].req[r]
                    half_cap[r] -= Users[copyi].req[r]
                    bw_cloud2 -= Users[copyi].req[3]*Users[copyi].sigma
        max_pay2 = 0
        cap_alloc = [0] * RES_SIZE
        if len(allocate_user) != 0:
            for i in range(len(allocate_user) - 1):
                max_pay2 += allocate_user[i].bid
                for r in range(RES_SIZE):
                    cap_alloc[r] += allocate_user[i].req[r]
            last_user = allocate_user[len(allocate_user) - 1]
            for r in range(RES_SIZE):
                last_user.req[r] = cap[r] / 2 - cap_alloc[r]
            flag = True
            for r in range(RES_SIZE):
                if allocate_user[len(allocate_user) - 1].req[r] > last_user.req[r]:
                    flag = False
            if flag:
                for r in range(RES_SIZE):
                    last_user.req[r] = allocate_user[len(allocate_user) - 1].req[r]
            for d in range(len(norm_di)):
                if last_user.id == norm_di[d][0]:
                    sums = 0
                    for r in range(RES_SIZE):
                        sums += last_user.req[r] / cap[r]
                    sums = sums ** 0.5
                    last_user.bid = norm_di[d][1] * sums
            max_pay2 += last_user.bid
        """Third phase"""
        if max_pay >= max_pay2:
            payment_p = max_pay
            win_p = obj_x1
            for rr in range(RES_SIZE):
                half_cap[rr] -= users[max_j].req[rr]
            bw_cloud2 = bw_cloud
        else:
            payment_p = max_pay2
            win_p = obj_x2
            bw_cloud = bw_cloud2
        for winer in range(len(win_p)):
            if win_p[winer] == 1:
                users[winer].allocated = True
        max_payment += payment_p
        obj_X[ecs.id] = win_p
    return max_payment, obj_X


ECSs = [ECS(_, ecs_cap[_].copy()) for _ in range(ECS_SIZE)]
USERs = [USER(_, user_req[_].copy(), user_deploy[_].copy(), user_bid[_].copy(), user_sigma[_].copy()) for _ in
         range(USER_SIZE)]

if __name__ == '__main__':
    start = time.perf_counter()
    user_copy = copy.deepcopy(USERs)
    social_welfare, winners = g_pmrm_win(user_copy, ECSs)

    caps = [0] * RES_SIZE
    num_winner = 0
    cbw=0
    for j in ECSs:
        for i in USERs:
            if winners[j.id][i.id] == 1:
                for r in range(RES_SIZE - 1):
                    caps[r] += i.req[r]
                caps[RES_SIZE - 1] += i.req[RES_SIZE - 1] + i.req[RES_SIZE - 1] * i.sigma
                cbw += i.req[RES_SIZE - 1] * i.sigma
                num_winner += 1

    payment = [0] * USER_SIZE
    user_copy = copy.deepcopy(USERs)
    for user in user_copy:
        for j in winners:
            if j[user.id] == 1:
                lb = 0
                hb = user.bid
                while (hb - lb) >= 1:
                    temp_pay = (hb + lb) / 2
                    user_copy[user.id].bid = temp_pay
                    getwiner = g_pmrm_win(user_copy, ECSs)[1]
                    fail = True
                    for es in getwiner:
                        if es[user.id] == 1:
                            hb = temp_pay
                            fail = False
                    if fail:
                        lb = temp_pay
                    user_copy = copy.deepcopy(USERs)
                payment[user.id] = int(hb)
                print("用户%d支付确定" % user.id)
                break
    print("总支付：", sum(payment))
    print("社会福利：", social_welfare)

    print("胜出人数：", num_winner)
    sum_caps = np.sum(ecs_cap, axis=0)
    sum_caps[3] += cBW
    print("资源利用率：", [caps[r] / sum_caps[r] for r in range(RES_SIZE)])
    end = time.perf_counter()
    print("执行时间：", end - start)
