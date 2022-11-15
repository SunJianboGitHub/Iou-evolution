# <div align="center">IoU的演化历程🚀</div>
☘️🌟🚀
1. IoU的提出之前🌟
2. IoU的提出🌟
3. 各种IoU的改进🌟
4. 代码实现🌟


## <div align="center">IoU提出之前🚀</div>

目标检测任务的损失函数一般是由分类损失和回归损失组成。在IoU提出之前，我们针对候选框的回归通常采用坐标的回归损失，回归损失包括L1 Loss和L2 Loss两种，但是两者都存在一定的问题：

- L1 Loss的问题是：损失函数对x的导数是常数1，在训练后期，微调参数时，较大的导数会导致损失函数在稳定值附近波动，很难收敛到更高的精度。
- L2 Loss的问题是：损失函数对x的导数是2x，在训练初期，x很大，导致其导数很大，训练不稳定。
  
而且，基于L1/L2 Loss的坐标回归不具有尺度不变性，也没有将四个坐标之间的相关性考虑进去。因此，像L1/L2 Loss的直接坐标回归实际上很难描述两框之间的相对位置关系。

因此，在ACM2016的论文中提出了IoU Loss，它将四个坐标点看成一个整体进行计算，具有尺度不变性(也就是对尺度不敏感)。IoU Loss的定义是先求出预测框和真实框之间的交集和并集之比，再求负对数，但是在实际使用中我们常常将IoU Loss写成 1-IoU。如果两个框重合则交并比等于1，Loss为0说明完全重合。因此，IoU的取值范围是[0,1]。


## <div align="center">IoU的提出🚀</div>

IoU的全称是交并比(Intersection over Union)，是目标检测任务中使用的一个概念。IoU计算的是预测边界框与真实标注框的交叠率，也就是它们交集和并集的比值。最理想的情况是两个边界框完全重合，即IoU的值为1。

<div align="center">
    <a align="center"><img src=./images/iou-1.png width="50%" /></a>  
</div>

$$IoU = \frac{A \cap B}{A \cup B}$$


## <div align="center">各种IoU的改进🚀</div>

虽然IoU Loss解决了Smooth L1系列变量相互独立和不具有尺度不变性的两大问题，但是IoU它本身也存在两个问题：

<div align="center">
    <a align="center"><img src=./images/iou-2.png width="50%" /></a>  
</div>

- 1. 当预测框和标注框没有交集时，即IoU(A,B)=0，不能反应A、B距离的远近，此时损失函数不可导，IoU Loss无法优化两个框不相交的情况。
- 2. 如上图所示，假设预测框和标注框的大小是确定的，当两个框的相交值是确定的，即IoU值相同时，IoU值不能反映两个框是如何相交的，那么损失函数也就无法确定进一步的优化方向。(只是知道要降低IoU，但是不知道如何优化，只能慢慢搜索)。



### GIoU(CVPR-2019)

- [论文地址](https://arxiv.org/abs/1902.09630)
- [github地址](https://github.com/generalized-iou)
- $$GIoU = \frac{|A\cap B|}{|A\cup B|} - \frac{|C\backslash(A\cup B)|}{|C|} = IoU - \frac{|C\backslash(A\cup B)|}{|C|}$$
  
针对IoU无法反映两个框是如何相交的(不相交或者怎么相交)，GIoU通过引入预测框和标注框的最小外接矩形来获取预测框和标注框在闭包区域中的比重。因此，GIoU不仅可以关注重叠区域，还可以关注其它非重叠区域，能较好地反映两个框在闭包区域中的相交情况。

<div align="center">
    <a align="center"><img src=./images/giou-1.png width="50%" /></a>  
</div>
<div align="center">
    <a align="center"><img src=./images/giou-2.png width="50%" /></a>  
</div>

根据公式来看，GIoU的取值范围是(-1,1]。在两个框完全重合时取最大值1，在两个框没有交集时且无限远时，无限接近于最小值-1。因此，与IoU相比，GIoU是一个比较好的距离度量指标。



### DIoU(AAAI-2020)

- [论文地址](https://arxiv.org/abs/1911.08287)
- [github地址](https://github.com/Zzh-tju/DIoU)
- $$GIoU = IoU - \frac{\rho^{2}\left(\mathbf{b}, \mathbf{b}^{gt}\right)}{c^{2}}$$


虽然GIoU通过引入闭包区域缓解了预测框和标注框相交位置的衡量问题，但其仍然存在两个问题：

- 1. 针对每个预测框与真实标注框均要去计算最小外接矩形，计算速度受到限制
- 2. 当预测框与真实框是包含关系时，GIoU退化为IoU，也无法区分相对位置关系，不好进一步提供优化方向

<div align="center">
    <a align="center"><img src=./images/giou-1.png width="50%" /></a>  
</div>
<div align="center">
    <a align="center"><img src=./images/giou-2.png width="50%" /></a>  
</div>

根据公式来看，GIoU的取值范围是(-1,1]。在两个框完全重合时取最大值1，在两个框没有交集时且无限远时，无限接近于最小值-1。因此，与IoU相比，GIoU是一个比较好的距离度量指标。




## <div align="center">代码实现🚀</div>











    
