# <div align="center">IoU的演化历程🚀</div>
☘️🌟🚀🔥
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
    <a align="center"><img src=![图像](https://github.com/SunJianboGitHub/Iou-evolution/blob/main/images/iou-1.png) width="40%" /></a>  
</div>

![image](https://github.com/SunJianboGitHub/Iou-evolution/blob/main/images/iou-1.png)

$$IoU = \frac{A \cap B}{A \cup B}$$


## <div align="center">各种IoU的改进🚀</div>

虽然IoU Loss解决了Smooth L1系列变量相互独立和不具有尺度不变性的两大问题，但是IoU它本身也存在问题：

<div align="center">
    <a align="center"><img src=./images/iou-2.png width="40%" /></a>  
</div>


- 1. 当预测框和标注框没有交集时，即IoU(A,B)=0，不能反应A、B距离的远近，此时损失函数不可导，IoU Loss无法优化两个框不相交的情况。换句话说，IoU Loss 仅在边界框重叠时起作用，并且在非重叠情况下不会提供任何移动梯度。
- 2. 如上图所示，假设预测框和标注框的大小是确定的，当两个框的相交值是确定的，即IoU值相同时，IoU值不能反映两个框是如何相交的，那么损失函数也就无法确定进一步的优化方向。(只是知道要降低IoU，但是不知道如何优化，只能慢慢搜索)。



### GIoU(CVPR-2019)

- [论文地址](https://arxiv.org/abs/1902.09630)
- [github地址](https://github.com/generalized-iou)
- $$GIoU = \frac{|A\cap B|}{|A\cup B|} - \frac{|C\backslash(A\cup B)|}{|C|} = IoU - \frac{|C\backslash(A\cup B)|}{|C|}$$
  
针对IoU无法反映两个框是如何相交的(不相交或者怎么相交)，GIoU通过引入预测框和标注框的最小外接矩形来获取预测框和标注框在闭包区域中的比重。因此，GIoU不仅可以关注重叠区域，还可以关注其它非重叠区域，能较好地反映两个框在闭包区域中的相交情况。

<div align="center">
    <a align="center"><img src=./images/giou-1.png width="40%" /></a>  
</div>
<div align="center">
    <a align="center"><img src=./images/giou-2.png width="40%" /></a>  
</div>

根据公式来看，GIoU的取值范围是(-1,1]。在两个框完全重合时取最大值1，在两个框没有交集时且无限远时，无限接近于最小值-1。因此，与IoU相比，GIoU是一个比较好的距离度量指标。

**GIoU的特点如下：**

- 与IoU不同，当边界框与目标框不相交时，GIoU仍然可以为边界框提供移动方向，缓解非不相交时候的梯度消失问题。
- 当预测框与目标框存在包含关系时，GIoU退化为IoU，它的收敛速度较慢。
- GIoU收敛的很慢，因为它首先增加预测框的大小，使其与目标框重叠，然后最大化边界框的重叠区域。


### DIoU(AAAI-2020)

- [论文地址](https://arxiv.org/abs/1911.08287)
- [github地址](https://github.com/Zzh-tju/DIoU)
- $$DIoU = IoU - \frac{\rho^{2}\left(\mathbf{b}, \mathbf{b}^{gt}\right)}{c^{2}}$$


虽然GIoU通过引入闭包区域缓解了预测框和标注框相交位置的衡量问题，但其仍然存在两个问题：

- 1. 针对每个预测框与真实标注框均要去计算最小外接矩形，计算速度受到限制
- 2. 当预测框与真实框是包含关系时，GIoU退化为IoU，也无法区分相对位置关系，不好进一步提供优化方向

<div align="center">
    <a align="center"><img src=./images/diou-1.png width="40%" /></a>  
</div>
<div align="center">
    <a align="center"><img src=./images/diou-2.png width="40%" /></a>  
</div>

因此，考虑到GIoU的缺点，DIoU在IoU的基础上直接回归两个框中心点的欧氏距离，加速了收敛速度。DIoU的惩罚项基于中心点的距离和最小外接矩形的对角线的比值。这样避免了GIoU在预测框和标注框包含关系时，退化为IoU，梯度消失的问题。

<div align="center">
    <a align="center"><img src=./images/diou-3.png width="40%" /></a>  
</div>



**DIoU的特点如下：**
- DIoU Loss的回归与边界框尺度无关(尺度不变性)
- 与GIoU不同，当边界框与目标框存在包含关系时，DIoU仍然可以为边界框提供移动方向
- DIoU损失可以直接最小化检测框与目标框之间的距离，因此它比GIoU损失收敛快得多。



### CIoU(AAAI-2020)

- [论文地址](https://arxiv.org/abs/1911.08287)
- [github地址](https://github.com/Zzh-tju/DIoU)
- $$CIoU = IoU - \frac{\rho^{2}\left(\mathbf{b}, \mathbf{b}^{gt}\right)}{c^{2}} - \alpha v$$
- $$v = \frac{4}{\pi ^{2}}(\arctan{\frac{w ^ {gt}}{h ^ {gt}}} - \arctan{\frac{w}{h}}) ^ {2}$$
- $$\alpha = \frac{v}{(1 - IoU + v)}$$

虽然DIoU Loss通过中心点回归缓解了预测框和目标框距离较远时难以优化的问题，但是DIoU Loss仍然存在两框中心点重合，但是宽高比不同时，DIoU退化为IoU Loss的问题。因此，为了得到更加精准的预测框，CIOU在DIoU的基础上增加一个影响因子，即增加了预测框与目标框之间长宽比的一致性考量。

<div align="center">
    <a align="center"><img src=./images/ciou-1.png width="40%" /></a>  
</div>

当边界框回归出现上面三种情况时，即目标框包括预测框，本来DIoU可以起作用，但是预测框的中心点位置都一样，因此按照DIoU的公式，三者的值是相同的，无法更精确的提供下一步的优化方向。因此，提出了CIoU来解决此问题。


**CIoU的特点如下：**

- CIoU Loss不仅考虑了边界框回归的重叠面积、中心点距离以及长宽比。
- 与DIoU不同，CIoU将长宽比也作为回归目标
- 虽然CIoU引入了长宽比差异v，但是并不是预测框与目标框宽高的真实差异，所以有时候会阻碍模型的有效优化。
- CIoU存在的问题是宽和高不能同时增大或者减小。


### EIoU(arXiv-2021)

- [论文地址](https://arxiv.org/abs/2101.08158)
- [github地址](https://github.com/jacobi93/alpha-iou)

我们知道，CIoU损失在DIoU的基础上添加了衡量预测框和GT框的纵横比v，在一定程度上可以加快预测框的回归速度，但是仍然存在着很大的问题：

- 在预测框的回归过程中，一旦预测框和GT框的宽高纵横比呈现线性比例时，CIoU中添加的相对比例的惩罚项便不再起作用
- 根据预测框w和h的梯度公式可知，w和h在其中一个值增大时，另一个值必须减小，它俩不能保持同增同减。

为了解决这个问题，EIoU提出了直接对w和h的预测结果进行惩罚，EIoU的计算公式为:

- $$EIoU = IoU - \frac{\rho^{2}\left(\mathbf{b}, \mathbf{b}^{gt}\right)}{c^{2}} - \frac{\rho^2 (\mathbf{w, w ^{gt}})}{{C_w} ^ 2} - \frac{\rho^2 (\mathbf{h, h ^{gt}})}{{C_h} ^ 2}$$
- 其中，$C_w ^ 2$和$C_h ^ 2$分别是预测框和GT框最小外接矩形的宽和高。

<div align="center">
    <a align="center"><img src=./images/eiou-1.jpg width="40%" /></a>  
</div>


**EIoU的特点如下：**

- EIoU Loss包括重叠损失、中心距离损失、宽和高的损失。
- 与CIoU不同，EIoU的宽高损失直接使预测框与真实框的宽度和高度之差最小，使得收敛速度更快。
- GIoU的问题是使用最小外接矩形的面积减去并集的面积作为惩罚项，这导致了GIoU存在先扩大并集的面积，在优化IoU的弯路问题。




### $\alpha$IoU(arXiv-2021)

- [论文地址](https://arxiv.org/abs/2110.13675v2)
- [github地址](https://github.com/jacobi93/alpha-iou)

由于IoU Loss对于Bbox尺度的不变性，可以训练出更好的检测器，因此在目标检测中常用IoU Loss对预测框计算定位损失(在 yolov5中采用的是CIoU Loss)。而本文提出了Alpha-IoU Loss是基于现有的IoU Loss的统一幂化，即对所有的IoU Loss，增加$\alpha$幂，当$\alpha$等于1时，则回归到原始的各个Loss。

- $$\alpha IoU = {IoU} ^ {\alpha}$$
- $$\alpha GIoU = {IoU} ^ {\alpha} - (\frac{|C\backslash(A\cup B)|}{|C|}) ^ {\alpha}$$
- $$\alpha DIoU = IoU ^ {\alpha} - \frac{\rho^{2 \alpha}\left(\mathbf{b}, \mathbf{b}^{gt}\right)}{c^{2 \alpha}}$$
- $$\alpha CIoU = IoU ^ {\alpha} - \frac{\rho^{2 \alpha}\left(\mathbf{b}, \mathbf{b}^{gt}\right)}{c^{2 \alpha}} - (\beta v) ^ {\alpha}$$
- $$\alpha EIoU = IoU ^ \alpha - \frac{\rho^{2 \alpha}\left(\mathbf{b}, \mathbf{b}^{gt}\right)}{c^{2 \alpha}} - \frac{\rho^{2 \alpha} (\mathbf{w, w ^{gt}})}{{C_w} ^ {2 \alpha}} - \frac{\rho^ {2 \alpha} (\mathbf{h, h ^{gt}})}{{C_h} ^ {2 \alpha}}$$




### SIoU(arXiv-2022)

- [论文地址](https://arxiv.org/pdf/2205.12740.pdf)

就SIoU的总体设计来说，它相比于之前的设计，除了考虑了重叠区域，中心点距离、长度和宽度，还考虑了两个框之间的角度问题。SIoU Loss共包括四个部分，**角度损失、距离损失、形状损失、IoU损失**。接下来，看看SIoU具体是怎么设计的。


**1. 角度损失**

作者在SIoU中引入角度损失，主要是为了辅助两框之间的距离计算，因为在目标检测的一开始的训练中，大多数的预测框是跟真实框不相交的，所以如何快速的收敛两框之间的距离是值得考虑的。

<div align="center">
    <a align="center"><img src=./images/siou-1.png width="40%" /></a>  
</div>

上述角度损失化简之后，公式为$\sin(2 \alpha)$，取值范围为[0,90]度，当$\alpha=0$时，角度损失为0，达到最小值；当$\alpha=45$时，角度损失为1，达到最大值。其具体作用可以和距离损失一起结合来看。

**2. 距离损失**

就SIoU的距离损失来说，其基本上与CIoU的思想很接近，都是通过两框中心的距离和最小外接矩形来构建。但是这里多了一项系数$\gamma$，这一项其实就是将角度损失引入到距离损失。

<div align="center">
    <a align="center"><img src=./images/siou-2.png width="40%" /></a>  
</div>

具体来说：

- 与CIoU不同，这里的距离损失不是单存的距离之间的损失，还包括了角度损失。
- 从距离损失(距离+角度)来看角度损失，它是单调递增的，也就是当距离一定时，角度损失小，距离损失要小，角度损失大，距离损失大。
- 当$\alpha$趋近于0时，这样计算出来的角度损失是趋近于0的，此时$\gamma$的值趋近于2，那么两框之间的距离损失相对变大了。这也说明此时角度影响小，距离影响大。
- 当$\alpha$趋近于45时，这样计算出来的角度损失趋近于1，此时$\gamma$的值趋近于1，那么两框的距离损失相对变小了。这也说明此时，角度影响大，抑制一下距离的影响。
- 其实要深刻理解，距离损失中包含着角度损失。此消彼长，相互影响。





**3. 形状损失**

这里的形状损失其实就是宽高损失，与EIoU类似，采用的是真实宽高的回归，而不是宽高比例的回归。CIoU考虑的是两框整体形状的收敛，SIoU是以宽高两个边收敛来达到整体形状收敛的效果。

<div align="center">
    <a align="center"><img src=./images/siou-3.png width="40%" /></a>  
</div>

这里的可调参数$\theta$，用来表示网络需要对形状这个属性给予多少注意力，即占多少权重。实验中设置为4，一般范围为[2,6]






**4. 重叠损失**

重叠损失其实就是普通的IoU损失

<div align="center">
    <a align="center"><img src=./images/iou-1.png width="40%" /></a>  
</div>

**4. 总体损失**

总体损失 = 距离损失(距离、角度) + 形状损失 + IoU损失

<div align="center">
    <a align="center"><img src=./images/siou-4.png width="40%" /></a>  
</div>





## <div align="center">代码实现🚀</div>

[各种IoU代码实现](IoU.py)









    
