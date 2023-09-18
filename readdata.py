import numpy as np


def get_data():
    with open("data/data_bi.txt", 'r') as f_bi:
        b_ = f_bi.readlines()
    data_bi = []
    for b in b_:
        b = b.strip("\n")  # 去除末尾的换行符
        data_split = b.split(",")
        temp = list(map(float, data_split))
        data_bi.append(temp[0])

    with open("data/data_si.txt", 'r') as f_si:
        si_ = f_si.readlines()
    data_si = []
    for s in si_:
        s = s.strip("\n")
        data_split = s.split(",")
        temp = list(data_split)
        ds = []
        for d in temp:
            d_sp = d.split(" ")
            ds = list(map(int, d_sp))
        data_si.append(ds)

    with open("data/data_delta.txt", 'r') as f_delta:
        delta_ = f_delta.readlines()
    data_delta = []
    for delta in delta_:
        delta = delta.strip("\n")
        data_split = delta.split(",")
        temp = list(data_split)
        delt = []
        for d in temp:
            d_sp = d.split(" ")
            delt = list(map(int, d_sp))
        data_delta.append(delt)

    with open("data/data_cr.txt", 'r') as f_cr:
        cr_ = f_cr.readlines()
    data_cr = []
    for c in cr_:
        c = c.strip("\n")
        data_split = c.split(",")
        temp = list(data_split)
        cr = []
        for d in temp:
            d_sp = d.split(" ")
            cr = list(map(int, d_sp))
        data_cr.append(cr)

    with open("data/data_eBW.txt", "r") as f_eBW:
        eBW = f_eBW.readline()
    data_eBW = int(eBW)

    with open("data/data_cBW.txt", "r") as f_cBW:
        cBW = f_cBW.readline()
    data_cBW = int(cBW)

    with open("data/data_sigma.txt", "r") as f_sigma:
        sigma = f_sigma.readlines()
    data_sigma = []
    for sig in sigma:
        sig = sig.strip("\n")
        data_sigma.append(float(sig))

    return data_bi, data_si, data_delta, data_cr, data_eBW, data_cBW, data_sigma
