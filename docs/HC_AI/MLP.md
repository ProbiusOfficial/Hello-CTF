# 我的第一个神经网络

神经网络是当前机器学习领域普遍所应用的，例如可利用神经网络进行图像识别、语音识别等，从而将其拓展应用于自动驾驶汽车。它是一种高度并行的信息处理系统，具有很强的自适应学习能力，不依赖于研究对象的数学模型，对被控对象的的系统参数变化及外界干扰有很好的鲁棒性，能处理复杂的多输入、多输出非线性系统，**神经网络要解决的基本问题是分类问题**。

我们的第一个神经网络选择**基于BP误差反向传播法的MLP神经网络模型**。

### MLP多层感知机

!!! question "图片的另一种形态"
    如果让你向一位视力障碍人来描述一幅图片，你会怎样去描述它？物体和他们的属性、风格、情感、布局
    如果是想计算机呢，你又该怎么去描述它？

这





![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\pixel-values.png)







<iframe src=".\assets\pixels-to-neurons.mp4" width="100%" height="700" frameborder="no" scrolling="no" allowfullscreen="allowfullscreen"> </iframe> 

一个

<iframe src=".\assets\network-propagation.mp4" width="100%" height="700" frameborder="no" scrolling="no" allowfullscreen="allowfullscreen"> </iframe> 







![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\v2-5a81c06789ad5e9323f93c6540263327_r.jpg)









### BP误差反向传播法



![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\v2-b84fee51daf26d27bd90420311d410a2_r-1701958087743-6.jpg)

上图形象的展示了BP算法的















### 代码解析

```python
import torch
import torch.nn as nn
from torch.optim import Adam
from torchvision import datasets,transforms
from torch.utils.data import DataLoader
import numpy as np

BATCH_SIZE = 64		#设置每一批的大小
EPOCHS = 5		#设置训练轮数
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")		#确定是否有可用的CUDA设备

#定义一个BPNet类，它继承于nn.Module类，nn.Module是pytorch给出的默认神经网络类
class BPNet(nn.Module):		
    def __init__(self):		#定义类对象实例化方法
        super().__init__()		#初始化神经网络
        #定义类的接口函数，使用nn.Sequential将操作合并到一起
        self.classifier = nn.Sequential(
            nn.Linear(28 * 28, 128),		#放入了一个全连接层，从28*28—>128，28*28是图像大小
            nn.ReLU(inplace=True),			#放入了一个ReLU激活函数，inplace=True节省显存
            nn.Linear(128, 64),				#放入了一个全连接层，从128—>64，128是上层大小
            nn.ReLU(inplace=True),			#放入了一个ReLU激活函数
            nn.Linear(64, 10)				#放入了一个全连接层，从64—>10，64是上层大小
        )
    #forward函数定义该神经如何处理数据，也就是数据如何在网络中前进
    def forward(self, x):
        x = torch.flatten(-1)		#首先将x展平为一维数组
        x = self.classifier(x)		#将x放入上面定义的函数中
        return x
    
def test(model):
    test_dataset = datasets.MNIST(root='data', 
                            train=False, 
                            transform=transforms.ToTensor(),
                            download=True)
    test_loader = DataLoader(dataset=test_dataset, 
                            batch_size=BATCH_SIZE, 
                            shuffle=False)
    total = 0
    correct = 0
    for index, (data, target) in enumerate(test_loader):
        data, target = data.to(DEVICE), target.to(DEVICE)

        pred = model(data)
        pred = torch.argmax(pred)
        correct += (pred == target).sum()
        total += pred.size(0)

    print("Correct : ",correct,'/',total,sep='')
    print('Accuracy : ',float(correct)/float(total) * 100. ,"%",sep='')
            
    

def train(model):
    train_dataset = datasets.MNIST(root=r'data', 
                                train=True, 
                                transform=transforms.ToTensor(),
                                download=True)
    train_loader = DataLoader(dataset=train_dataset, 
                            batch_size=BATCH_SIZE,
                            shuffle=True)
    
    optimizer = Adam(model.parameters(), lr=0.05)
    criterion = nn.CrossEntropyLoss()  
    model.train()

    for epoch in range(EPOCHS):
        for index, (data, target) in enumerate(train_loader):

            data, target = data.to(DEVICE), target.to(DEVICE)
            optimizer.zero_grad()

            pred = model(data)
            loss = criterion(pred, target)

            loss.backward()
            optimizer.step()

            if index % 100 == 0:
                print(f'Train Epoch: {epoch} [{index * len(data)}/{len(train_loader.dataset)} ({(100. * index / len(train_loader)):.0f}%)]\tLoss: {loss.data[0]:.6f}')


    model.eval()
    torch.save(model.state_dict(),"BPNet.pth")

if __name__ == "__main__":
    model = BPNet().to(DEVICE)

    train(model)
    test(model)


```



