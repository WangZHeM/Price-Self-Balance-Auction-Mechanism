# Price-Self-Balance-Auction-Mechanism
Price Self-Balance Auction Mechanism实验代码及数据集
#### Price Self-Balance Auction Mechanism实验包括以下文件：

1）data文件夹

2）analysis_huawei_data.py

3）experiment_data.py

4）G_PMRM.py

5）PSBnp.py

6）readdata.py

7）CPLEX.py

#### 文件说明

1）data文件夹用于存放实验数据以及数据集training-1.text

2）analysis_huawei_data.py ：可将数据集training-1.text中适合实验的虚拟机数据抽取保存在huawei_data.text中

3）experiment_data.py ：随机抽取huawei_data.text中的数据加以处理后分别保存在data_bi.txt（用户出价）、data_si.txt（用户需求）、data_delta.txt（部署约束）、data_cr.txt（边缘服务器容量）、data_eBW.txt（边缘服务器带宽）、data_cBW.txt（云服务器带宽）、data_sigma.txt（参数σ）

4）G_PMRM.py ：G_PMRM算法代码

5）PSBnp.py：Price Self-Balance Auction Mechanism算法代码

6）readdata.py：用于读取data数据

7）CPLEX.py：CPLEX算法代码
