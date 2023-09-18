import copy
import math
import time

import cplex
import numpy as np
import readdata

_bid_, _req_, _delta_, _re_, eBW, cBW, _sigma_ = readdata.get_data()

########   dataset the last is bandwidth ###############

Ecs_cap = np.array(_re_, dtype=np.float64)
User_deploy = np.array(_delta_, dtype=np.float64)
User_req = np.array(_req_, dtype=np.float64)
User_sigma = np.array(_sigma_, dtype=np.float64)
User_bid = np.array(_bid_, dtype=np.float64)
User_req_BW = np.array([_req_[i][3] for i in range(len(_bid_))], dtype=np.float64)
ClOUD_BW = cBW
user_p = [0] * len(User_bid)


def fCplex(ecs_cap, user_req, user_req_BW, user_deploy, user_bid, user_sigma):
    # Create the modeler/solver.
    cpx = cplex.Cplex()
    cpx.objective.set_sense(cpx.objective.sense.maximize)
    # Create variables. We have variables
    # x[i][j]        if allocation to the edge.
    # y[i][j]        if allocation to the cloud.
    x_edge = [None] * len(user_bid)
    for i in range(len(user_bid)):
        x_edge[i] = list(cpx.variables.add(
            obj=[user_bid[i] * user_deploy[i][j] for j in range(len(ecs_cap))],
            ub=[1] * len(ecs_cap),
            lb=[0] * len(ecs_cap),
            types=["I"] * len(ecs_cap),
            names=["x[%d]" % i + "[%c]" % str(j) for j in range(len(ecs_cap))]
        ))

    y_cloud = [None] * len(user_bid)
    for i in range(len(user_bid)):
        y_cloud[i] = list(cpx.variables.add(
            obj=[user_bid[i] * user_deploy[i][j] for j in range(len(ecs_cap))],
            ub=[1] * len(ecs_cap),
            lb=[0] * len(ecs_cap),
            types=["I"] * len(ecs_cap),
            names=["y[%d]" % i + "[%c]" % str(j) for j in range(len(ecs_cap))]
        ))

    # Constraint 1
    for r in range(len(ecs_cap[0])):
        for j in range(len(ecs_cap)):
            ind = [x_edge[i][j] for i in range(len(user_bid))]
            val = [user_deploy[i][j] * user_req[i][r] for i in range(len(user_bid))]
            cpx.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=ind, val=val)],
                senses=["L"],
                rhs=[ecs_cap[j][r]]
            )

    # Constraint 2
    for j in range(len(ecs_cap)):
        ind = [x_edge[i][j] for i in range(len(user_bid))] + [y_cloud[i][j] for i in range(len(user_bid))]
        val = [user_deploy[i][j] * user_req_BW[i] for i in range(len(user_bid))] + [user_deploy[i][j] * user_req_BW[i]
                                                                                    for i in range(len(user_bid))]
        cpx.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=ind, val=val)],
            senses=["L"],
            rhs=[ecs_cap[j][len(ecs_cap[0]) - 1]]
        )

        # Constraint 3

        ind = [x_edge[i][j] for i in range(len(user_bid)) for j in range(len(ecs_cap))] + \
              [y_cloud[i][j] for i in range(len(user_bid)) for j in range(len(ecs_cap))]
        val = [user_deploy[i][j] * user_req_BW[i] * user_sigma[i] for i in range(len(user_bid)) for j in
               range(len(ecs_cap))] + \
              [user_deploy[i][j] * user_req_BW[i] for i in range(len(user_bid)) for j in range(len(ecs_cap))]
        cpx.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=ind, val=val)],
            senses=["L"],
            rhs=[ClOUD_BW]
        )

    # Constraint 4
    for i in range(len(user_bid)):
        ind = [x_edge[i][j] for j in range(len(ecs_cap))] + [y_cloud[i][j] for j in range(len(ecs_cap))]
        val = [1.0] * len(ecs_cap) + [1.0] * len(ecs_cap)
        cpx.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=ind, val=val)],
            senses=["L"],
            rhs=[1.0]
        )

    cpx.solve()
    print("Solution status =", cpx.solution.get_status_string())
    print("Optimal value:", cpx.solution.get_objective_value())
    # print('x: ', cpx.solution.get_values())
    # cmax = cpx.solution.get_values()
    cval = cpx.solution.get_objective_value()
    x_ij = cpx.solution.get_values("x[0][0]", "x[%d][%d]" % (len(user_bid) - 1, len(ecs_cap) - 1))
    y_ij = cpx.solution.get_values("y[0][0]", "y[%d][%d]" % (len(user_bid) - 1, len(ecs_cap) - 1))
    cpx.end()
    return x_ij, y_ij, cval


if __name__ == "__main__":
    start = time.perf_counter()
    xij, yij, max_v = fCplex(Ecs_cap, User_req, User_req_BW, User_deploy, User_bid, User_sigma)

    xij = np.array(xij)
    yij = np.array(yij)

    xij = xij.reshape(len(User_bid), len(Ecs_cap))
    yij = yij.reshape(len(User_bid), len(Ecs_cap))

    users = []
    sum_cap = [0] * len(Ecs_cap[0])
    sum_user = 0
    user_cloud = 0
    for i in range(len(User_bid)):
        if sum(xij[i]) == 1:
            users.append([i, User_bid[i]])
            for r in range(len(Ecs_cap[0]) - 1):
                sum_cap[r] += User_req[i][r]
            sum_cap[len(Ecs_cap[0]) - 1] += User_req[i][len(Ecs_cap[0]) - 1] + User_req[i][len(Ecs_cap[0]) - 1] * \
                                            User_sigma[i]
            sum_user += 1
        elif sum(yij[i]) == 1:
            users.append([i, User_bid[i]])
            sum_cap[len(Ecs_cap[0]) - 1] += User_req[i][len(Ecs_cap[0]) - 1] * 2
            sum_user += 1
            user_cloud += 1
        if sum(xij[i]) == 1 and sum(yij[i]) == 1:
            print("有错误！！！")

    user_bid = copy.deepcopy(User_bid)
    user_delta = copy.deepcopy(User_deploy)
    user_req = copy.deepcopy(User_req)
    user_req_bw = copy.deepcopy(User_req_BW)
    user_sigma = copy.deepcopy(User_sigma)
    for i in users:
        user_bid = np.delete(user_bid, i[0], 0)
        user_delta = np.delete(user_delta, i[0], 0)
        user_req = np.delete(user_req, i[0], 0)
        user_req_bw = np.delete(user_req_bw, i[0], 0)
        user_sigma = np.delete(user_sigma, i[0], 0)
        maxv = fCplex(Ecs_cap, user_req, user_req_bw, user_delta, user_bid, user_sigma)[2]
        user_p[i[0]] = round(maxv, 3) - (round(max_v, 3) - round(i[1], 3))
        print(user_p[i[0]], maxv, max_v, i[1])
        user_bid = copy.deepcopy(User_bid)
        user_delta = copy.deepcopy(User_deploy)
        user_req = copy.deepcopy(User_req)
        user_req_bw = copy.deepcopy(User_req_BW)
        user_sigma = copy.deepcopy(User_sigma)
    end = time.perf_counter()
    sum_cap_ecs = np.sum(Ecs_cap, axis=0)
    print("_________________________")
    print("xij=", len(xij))
    print("yij=", len(yij))
    print(sum_cap)
    print(sum_cap_ecs)
    print(np.sum(User_req, axis=0))
    print(sum_user)
    print('社会福利为：', max_v)
    print('用户支付为：', sum(user_p))
    print("资源利用率为：", [sum_cap[r] / sum_cap_ecs[r] for r in range(len(Ecs_cap[0]) - 1)])
    print("带宽利用率：", (sum_cap[len(Ecs_cap[0]) - 1] / (sum_cap_ecs[len(Ecs_cap[0]) - 1] + cBW)))
    print("云端分配比例为：", user_cloud / sum_user)
    print('执行时间为：', end - start)
