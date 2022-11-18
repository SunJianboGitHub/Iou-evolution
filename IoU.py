#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   IoU.py
@Time    :   2022/11/18 16:48:48
@Author  :   JianBo Sun 
@Version :   1.0
@License :   (C)Copyright 2021-2022, ai-uav-cyy-cmii
@Desc    :    some tools
'''

import os
import torch
import math
import numpy as np



class BboxIoU(object):
    """
        ### 类说明
            - 计算个中IOU, 包括GIoU、CIoU、DIoU、EIoU
            - 通过 mode 参数选择哪种方式
        ### 参数
            - predict_bboxes: 维度是 [N, 4], [x, y, w, h]
            - gt_bboxes:      维度是 [N, 4], [x, y, w, h]
    """
    def __init__(self, predict_bboxes, gt_bboxes, eps=1e-16):
        self.eps = eps
        
        self.predict_bboxes = predict_bboxes
        self.gt_bboxes = gt_bboxes

        self.gt_xmin = gt_bboxes[:, 0] - (gt_bboxes[:, 2] - 1) / 2   
        self.gt_xmax = gt_bboxes[:, 0] + (gt_bboxes[:, 2] - 1) / 2
        self.gt_ymin = gt_bboxes[:, 1] - (gt_bboxes[:, 3] - 1) / 2
        self.gt_ymax = gt_bboxes[:, 1] + (gt_bboxes[:, 3] - 1) / 2

        self.pt_xmin = predict_bboxes[:, 0] - (predict_bboxes[:, 2] - 1) / 2
        self.pt_xmax = predict_bboxes[:, 0] + (predict_bboxes[:, 2] - 1) / 2
        self.pt_ymin = predict_bboxes[:, 1] - (predict_bboxes[:, 3] - 1) / 2
        self.pt_ymax = predict_bboxes[:, 1] + (predict_bboxes[:, 3] - 1) / 2

    def iou(self):
        """
            ### 函数说明
                - 计算交并比
                - 防止分母为0, 添加一个很小的数
        """
        gt_w, gt_h = (self.gt_xmax - self.gt_xmin + 1), (self.gt_ymax - self.gt_ymin + 1)
        pt_w, pt_h = (self.pt_xmax - self.pt_xmin + 1), (self.pt_ymax - self.pt_ymin + 1)

        inter_xmin, inter_ymin = torch.max(self.pt_xmin, self.gt_xmin), torch.max(self.pt_ymin, self.gt_ymin)
        inter_xmax, inter_ymax = torch.min(self.pt_xmax, self.gt_xmax), torch.min(self.pt_ymax, self.gt_ymax)

        inter_w = (inter_xmax - inter_xmin + 1).clamp(0)
        inter_h = (inter_ymax - inter_ymin + 1).clamp(0)

        self.inter_area = inter_w * inter_h
        self.union_area = (gt_w * gt_h) + (pt_w * pt_h) - self.inter_area

        return self.inter_area / (self.union_area + self.eps)


    def giou(self):
        """
            ### 函数说明
                - yolov5中在计算GIoU时, left = cx - width / 2
                - 我们通常采用, left = cx - (width - 1) / 2
                - 这里采用自己的方法, 未完全复现yolov5
            ### 计算公式
                - giou = iou - (C - AUB) / C
                - C表示最小包络矩形的面积
                - giou的阈值为 (-1, 1]
        """
    
        # 最小包络矩形 Minimum envelope rectangle
        C_w = torch.max(self.pt_xmax, self.gt_xmax) - torch.min(self.pt_xmin, self.gt_xmin) + 1
        C_h = torch.max(self.pt_ymax, self.gt_ymax) - torch.min(self.pt_ymin, self.gt_ymin) + 1
        
        iou = self.iou()
        C_area = C_w * C_h
        giou = iou - (C_area - self.union_area) / C_area

        return giou


    def diou(self):
        # DIoU Loss 最小化Bbox间的中心点距离,从而使得函数快速收敛
        """
            ### 函数说明
                - 将target中心与predict中心之间的距离, 重叠率以及尺度都考虑进去
                - 公式为: DIoU = IOU - L2(c1, c2) / c**2
                - 其中, c1, c2分别表示预测框与目标框的中心点, c表示最小包络框的对角线距离
        """
        # C_xmin = torch.min(self.pt_xmin, self.gt_xmin)
        # C_ymin = torch.min(self.pt_ymin, self.gt_ymin)
        # C_xmax = torch.max(self.pt_xmax, self.gt_xmax)
        # C_ymax = torch.max(self.pt_ymax, self.gt_ymax)

        C_w = torch.max(self.pt_xmax, self.gt_xmax) - torch.min(self.pt_xmin, self.gt_xmin) + 1
        C_h = torch.max(self.pt_ymax, self.gt_ymax) - torch.min(self.pt_ymin, self.gt_ymin) + 1

        pt_center = self.predict_bboxes[:, [0, 1]]
        gt_center = self.gt_bboxes[:, [0, 1]]
        
        
        iou = self.iou()
        L2_center = torch.sum(torch.pow(pt_center - gt_center, 2.0).sum(1), dim=0)
        C_square  = torch.pow(C_w, 2.0) + torch.pow(C_h, 2.0)
        diou = iou - L2_center / (C_square + self.eps)

        return diou




        pass


    def ciou(self):
        # 在中大型物体上CIOU效果较好,在小物体上性能有所下降,可能是由于长宽比对小物体检测的贡献不大,因此中心点距离比长宽比更重要
        # yolov5采用的是CIoU
        """
            ### 函数说明
                - ciou包括重叠区域、中心点距离、宽高比
                - 公式是: diou - alpha * v
                - v = (4/(math.pi ** 2)) * (arctan(pw/ph) - arctan(gw/gh))**2
                - s = 1 - iou
                - alpha = v / (s+v)
                - 这些计算不要计算梯度
        """
        with torch.no_grad():
            arctan = torch.atan(self.predict_bboxes[..., 2] / self.predict_bboxes[..., 3]) - torch.atan(self.gt_bboxes[..., 2] / self.gt_bboxes[..., 3])
        
            v = (4 / (math.pi ** 2)) * torch.pow(arctan, 2)
            s = 1 - self.iou()
            alpha = v / (s + v)
        
        ciou = self.diou() - alpha * v
        
        return ciou


    def eiou(self):
        # EIoU Loss包括重叠损失、中心距离损失、宽和高的损失
        
        """
            ### 函数说明
                - 直接回归宽高的真实值, 而不是宽高比, 收敛速度更快
                - 公式是: EIoU = IoU - L2(pc, gc)/c**2 - L2(pw,gw)/cw**2 - L2(ph,gh)/ch**2
                - c是最小外接矩形对角线长度
                - cw、ch分别是最小外接矩形的宽和高
        """
        
        C_w = torch.max(self.pt_xmax, self.gt_xmax) - torch.min(self.pt_xmin, self.gt_xmin) + 1
        C_h = torch.max(self.pt_ymax, self.gt_ymax) - torch.min(self.pt_ymin, self.gt_ymin) + 1

        pt_center = self.predict_bboxes[:, [0, 1]]
        gt_center = self.gt_bboxes[:, [0, 1]]
        
        
        iou = self.iou()
        L2_center = torch.sum(torch.pow(pt_center - gt_center, 2.0).sum(1), dim=0)
        L2_ww = torch.pow(self.predict_bboxes[:, 2] - self.gt_bboxes[:, 2], 2)
        L2_hh = torch.pow(self.predict_bboxes[:, 3] - self.gt_bboxes[:, 3], 2)
        C_square  = torch.pow(C_w, 2.0) + torch.pow(C_h, 2.0)
        
        cc = L2_center / (C_square + self.eps)
        ww = L2_ww / (torch.pow(C_w, 2.0) + self.eps)
        hh = L2_hh / (torch.pow(C_h, 2.0) + self.eps)
        
        eiou = iou - cc - ww - hh
        
        return eiou

    
    def siou(self, theta=4):
        # yolov6采用的损失函数,并不是它最先提出的
        """
            ### 函数说明
                - siou包括角度损失、距离损失、形状损失、重叠损失
        """
    
        # 最小外接矩形的宽度和高度
        C_w = torch.max(self.pt_xmax, self.gt_xmax) - torch.min(self.pt_xmin, self.gt_xmin) + 1
        C_h = torch.max(self.pt_ymax, self.gt_ymax) - torch.min(self.pt_ymin, self.gt_ymin) + 1
        
        
        # 预测框和目标框中心点在水平和垂直方向的距离
        s_cw = torch.max(self.predict_bboxes[:, 0], self.gt_bboxes[:, 0]) - torch.min(self.predict_bboxes[:, 0], self.gt_bboxes[:, 0])
        s_ch = torch.max(self.predict_bboxes[:, 1], self.gt_bboxes[:, 1]) - torch.min(self.predict_bboxes[:, 1], self.gt_bboxes[:, 1])
        sigma = torch.pow(s_cw ** 2 + s_ch **2, 0.5)                                    # 中心点之间的距离
        sin_alpha_1 = s_ch / (sigma + self.eps)
        sin_alpha_2 = s_cw / (sigma + self.eps)
        threshold = math.pow(2, 0.5) / 2                                               # 大于45度，选择beta，小于45度，选择alpha
        sin_alpha = torch.where(sin_alpha_1 > threshold, sin_alpha_2, sin_alpha_1)
        
        angle_cost = torch.cos(torch.arcsin(sin_alpha) * 2 - math.pi / 2)               # 角度损失
        
        rho_w = torch.pow(s_cw / C_w, 2)
        rho_h = torch.pow(s_ch / C_h, 2)
        gamma = 2 - angle_cost                                                                          # 距离损失的系数，平衡角度和距离
        distance_cost = (1 - torch.exp(-1 * gamma * rho_w)) + (1 - torch.exp(-1 * gamma * rho_h))       # 距离损失
        
        omiga_w = torch.abs(self.predict_bboxes[:, 2] - self.gt_bboxes[:, 2]) / torch.max(self.predict_bboxes[:, 2], self.gt_bboxes[:, 2])
        omiga_h = torch.abs(self.predict_bboxes[:, 3] - self.gt_bboxes[:, 3]) / torch.max(self.predict_bboxes[:, 3], self.gt_bboxes[:, 3])
        shape_cost = torch.pow(1 - torch.exp(-1 * omiga_w), theta) + torch.pow(1 - torch.exp(-1 * omiga_h), theta)

        siou = self.iou() - 0.5 * (distance_cost + shape_cost)
        
        return siou
        
        
        
    def cosiou(self):
        """
            ### 函数说明
                - 自己想法的实现
                - 根据来自diou与ciou的灵感
                - 设计对角线对齐的损失
        """
        C_xmin = torch.min(self.pt_xmin, self.gt_xmin)
        C_ymin = torch.min(self.pt_ymin, self.gt_ymin)
        C_xmax = torch.max(self.pt_xmax, self.gt_xmax)
        C_ymax = torch.max(self.pt_ymax, self.gt_ymax)

        C_w = torch.max(self.pt_xmax, self.gt_xmax) - torch.min(self.pt_xmin, self.gt_xmin) + 1
        C_h = torch.max(self.pt_ymax, self.gt_ymax) - torch.min(self.pt_ymin, self.gt_ymin) + 1

        pt_center = self.predict_bboxes[:, [0, 1]]
        gt_center = self.gt_bboxes[:, [0, 1]]

        L2_center = torch.sum(torch.pow(pt_center - gt_center, 2.0).sum(1), dim=0)
        C_square  = torch.pow(C_w, 2.0) + torch.pow(C_h, 2.0)

        # 计算两个向量的夹角余弦值, gt框的左上角、右下角与预测框中心形成的向量
        # 当向量夹角为0时,cosine_v=1, 当夹角为180时, cosine=-1
        # 我们将cosine_v值阈变换为[0, -2] ->[0, 180]
        # 
        tensor_1 = torch.stack((self.gt_xmax, self.gt_ymax), dim=1) - pt_center
        tensor_2 = pt_center - torch.stack((self.gt_xmin, self.gt_ymin), dim=1)
        cosine_v = self.cosine(tensor_1, tensor_2)                                      # 值阈是[1, -1]
        cosine_v = (cosine_v - 1.) / 2.0                                                # 变换范围为 [0, -1]
        cosine_v = cosine_v * 1.0
        

        # print(cosine_v, cosine_v.shape)
        
        iou = self.iou()
        # siou = iou - L2_center / (C_square + 1e-16) + L2_center * cosine_v
        # siou = iou - L2_center - L2_center * cosine_v
        siou = iou - L2_center * (1 - cosine_v) / (C_square + 1e-16)


        return siou


    def cosine(self, tensor_1, tensor_2):
        normalized_tensor_1 = tensor_1 / tensor_1.norm(dim=-1, keepdim=True)
        normalized_tensor_2 = tensor_2 / tensor_2.norm(dim=-1, keepdim=True)
        return (normalized_tensor_1 * normalized_tensor_2).sum(dim=-1)





    















