#%%
# from ssl import VERIFY_ALLOW_PROXY_CERTS
import sys
from turtle import forward
sys.path.append('..')
import torch.nn as nn
import torch
import math
import loader

    
class resnet50(nn.Module):
    """
    block: A sub module
    """

    def __init__(self, layers=[3, 4, 6, 3], planes=144, model_path=None):
        super(resnet50, self).__init__()
        self.inplanes = 64
        self.modelPath = model_path
        self.conv1 = nn.Conv2d(6, 64, kernel_size=7, stride=2, padding=3,
                               bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.stack1 = self.make_stack(64, layers[0])
        self.stack2 = self.make_stack(128, layers[1], stride=2)
        self.stack3 = self.make_stack(256, layers[2], stride=2)
        self.stack4 = self.make_stack(512, layers[3], stride=2)
        self.avgpool = nn.AvgPool2d(4, stride=1)
        self.fc = nn.Linear(512 * Bottleneck.expansion, planes)

        self.cla_fea = nn.Linear(512 * Bottleneck.expansion, 512 * Bottleneck.expansion)  #分类
        self.cla_term = nn.Linear(512 * Bottleneck.expansion, planes)  # 分类

        self.reg_fea = nn.Linear(512 * Bottleneck.expansion, 512 * Bottleneck.expansion)            #回归
        self.reg_term = nn.Linear(512 * Bottleneck.expansion, 1)  # 回归
        # initialize parameters
        self.init_param()

    def init_param(self):
        # The following is initialization
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                n = m.weight.shape[0] * m.weight.shape[1]
                m.weight.data.normal_(0, math.sqrt(2. / n))
                m.bias.data.zero_()

    def make_stack(self, planes, blocks, stride=1):
        downsample = None
        layers = []

        if stride != 1 or self.inplanes != planes * Bottleneck.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * Bottleneck.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * Bottleneck.expansion),
            )

        layers.append(Bottleneck(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * Bottleneck.expansion
        for i in range(1, blocks):
            layers.append(Bottleneck(self.inplanes, planes))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)

        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.stack1(x)
        # print(x.size)

        x = self.stack2(x)
        # print(x.size)

        x = self.stack3(x)
        # print(x.size)

        x = self.stack4(x)
        # print(x.size)


        avg_x = self.avgpool(x)

        # print(avg_x.size())
        avg_x = avg_x.view(avg_x.size(0), -1)

        # print("avg_x.view 后：", avg_x.size())
        # reg_fea = self.reg_fea(avg_x)
        cla_fea = self.cla_fea(avg_x)
        # print(cla_fea.size())
        # x = self.fc(x)
        cla = self.cla_term(cla_fea)

        # reg = self.reg_term(reg_fea)

        return cla





class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(Bottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out



# %%
class tkdsresnet50size120(nn.Module):
    def __init__(self,encoder=resnet50,planes=144*8,max_len=16,n_class=2):
        super(tkdsresnet50size120,self).__init__()
        self.planes=planes
        self.n_class=n_class
        self.max_len=max_len
        self.encoder=encoder(planes=planes)
        self.relu = nn.ReLU(inplace=True)
        self.hand=nn.Sequential(
            nn.Conv1d(in_channels=144*8,out_channels = 144*8, kernel_size = 3,padding=1),
            nn.ReLU(inplace=True),
            nn.Conv1d(in_channels=144*8,out_channels = n_class, kernel_size = 3,padding=1),
            nn.ReLU(inplace=True)
        )
        # self.init_param()

    def init_param(self):
        # The following is initialization
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                n = m.weight.shape[0] * m.weight.shape[1]
                m.weight.data.normal_(0, math.sqrt(2. / n))
                
                m.bias.data.zero_()
    def forward(self,x):
        B,L,W,H=x.shape
        x=x.view(B,int(L/6),-1,W,H)
        B,L,C,W,H=x.shape
        x=x.view(-1,C,W,H)
        x=self.encoder(x)
        x=x.view(B,L,144*8).permute(0, 2, 1)#B,L,C
        # print(x.shape)
        x=self.hand(x)
        x=x.permute(0,2,1)

        return x

