import numpy as np
import math
import random

cpu, memory, disk = [], [], []

with open('training-1.txt', 'r', encoding='utf8') as data:
    m = int(data.readline().rstrip())
    for i in range(m):
        # st = data.readline().strip('\n').split(', ')
        # print(st)
        data.readline()
    n = int(data.readline().rstrip())
    print(n)
    for i in range(n):
        st = data.readline().strip('\n').split(', ')
        if int(st[1]) <= 25 and int(st[2]) <= 35:
            cpu.append(math.ceil(int(st[1])))
            memory.append(math.ceil(int(st[2])))
            disk.append(np.random.randint(40, 101))
    #     if 100 <= int(st[1]) < 250 and 100 <= int(st[2]) < 3500:
    #         cpu.append(math.ceil(int(int(st[1]) / 10)))
    #         memory.append(math.ceil(int(int(st[2]) / 10)))
    #         disk.append(np.random.randint(40, 101))
    # for i in range(1500):
    #     cpu.append(np.random.randint(1, 25))
    #     memory.append(np.random.randint(1, 35))
    #     disk.append(np.random.randint(40, 101))

    print(sum(cpu) / len(cpu))
    print(sum(memory) / len(memory))
    print(sum(disk) / len(disk))
    print(cpu)
    print(memory)
    print(disk)
    print(len(cpu))

print('######################################################################')
user = []
for i in range(len(cpu)):
    user.append([cpu[i], memory[i], disk[i]])
print(user)
# random.shuffle(user)
print(user)

with open('huawei_data.txt', 'w+', encoding='utf8') as f:
    f.write('1\n')
    # f.write('184 320 10240\n')  # 0.2
    # f.write('368 640 10240\n')  # 0.4
    # f.write('552 960 10240\n')  # 0.6
    # f.write('736 1280 10240\n')  # 0.8

    # f.write('230 400 10240\n')  # 0.25
    # f.write('460 800 10240\n')  # 0.5
    # f.write('690 1200 10240\n')  # 0.75
    f.write('920 1600 10240\n')  # 1.0  # 容量不卡硬盘，只卡CPU和内存!
    # f.write('1150 2000 10240\n')  # 1.25
    f.write('%d\n' % len(user))
    for l in user:
        f.write('%d %d %d\n' % (l[0], l[1], l[2]))
