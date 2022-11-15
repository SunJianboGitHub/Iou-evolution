# Iou-evolution(彻底搞懂IoU及其发展历程)
    1. IoU的提出之前
    2. IoU的提出
    3. 各种IoU的改进
    4. 代码实现

## IoU提出之前
        目标检测任务的损失函数一般是由分类损失和回归损失组成。在IoU提出之前，我们针对候选框的回归通常采用坐标的回归损失，回归
    损失包括L1 Loss和L2 Loss两种，但是两者都存在一定的问题：

        1. L1 Loss的问题是：损失函数对x的导数是常数1，在训练后期，微调参数时，较大的导数会导致损失函数在稳定值附近波动，很难
           收敛到更高的精度。
        2. L2 Loss的问题是：损失函数对x的导数是2x，在训练初期，x很大，导致其导数很大，训练不稳定。

        而且，基于L1/L2 Loss的坐标回归不具有尺度不变性，也没有将四个坐标之间的相关性考虑进去。因此，像L1/L2 Loss的直接坐标回
    归实际上很难描述两框之间的相对位置关系。













    
