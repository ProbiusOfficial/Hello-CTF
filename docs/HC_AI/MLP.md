# 你的第一个神经网络

神经网络是当前机器学习领域普遍所应用的，例如可利用神经网络进行图像识别、语音识别等，从而将其拓展应用于自动驾驶汽车。它是一种高度并行的信息处理系统，具有很强的自适应学习能力，不依赖于研究对象的数学模型，对被控对象的的系统参数变化及外界干扰有很好的鲁棒性，能处理复杂的多输入、多输出非线性系统，**神经网络要解决的基本问题是分类问题**。

我们的第一个神经网络选择**基于BP误差反向传播法的MLP神经网络模型**。

![动图](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\v2-78685a273bd758c985c0d6c82068f88f_b-1702219237661-14.webp)

## 前置导引

### 朴素感知机

感知机是由美国学者FrankRosenblatt在1957年提出来的。感知机是作为神经网络（深度学习）的起源的算法。因此，学习感知机的构造也就是学习通向神经网络和深度学习的一种重要思想。
感知机接收多个输入信号，输出一个信号。这里所说的“信号”可以想象成电流或河流那样具备“流动性”的东西。像电流流过导线，向前方输送电子一样，感知机的信号也会形成流，向前方输送信息。但是，和实际的电流不同的是，感知机的信号只有“流/不流”（1/0）两种取值。这里我们认为0对应“不传递信号”， 1对应“传递信号”。

!!! attention "现在是数学时间！"

这里有很多的点，其中一部分的位置如图所示，你能找出一条直线，尽可能多的将所有的点（包括还没画出的）分开吗？对了，记得给我他的函数式。

​    <img src="C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\image-20231210220919065.png" alt="image-20231210220919065" style="zoom:50%;" />

让我们假设这条直线的方程是$f(x,y) = ax+by+c$，小学二年级学过的知识告诉我们，对于给出的每一个点$（x , y）$,代入直线方程后根据结果大小来判断他和直线的位置关系。因此，我们可以把这个过程抽象为下面的感知机：

<img src="C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\1702219744283.png" alt="1702219744283" style="zoom:50%;" />

我们还可以把整个感知机抽象为下面的数学模型。
$$
Output = \left\{\begin{matrix} 
  Red,  f(x,y)>0\\  
  Green,  f(x,y)<0\end{matrix}\right.
$$
如你所见，最简单的感知机就是将输入进行处理得到中间结果，再将结果经过非线性函数处理输出。一般的，我们也把上述的模型称为**神经元**。

### 神经网络

神经网络的灵感取自于生物上的神经元细胞，如下图所示：

![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\1.png)

这是人体神经元的基本构成，其中树突主要用于接收其他神经元的信号，轴突用于输出该神经元的信号，数以万计的神经元相互合作，使得我们人类能够进行高级的思考，能够不断地对新事物进行学习。因此，我们就希望仿照人类神经网络的结构，搭建一种人为的神经网络结构，从而使其能够完成一些计算任务，这也是神经网络名字的由来。

神经网络中计算的基本单元是**神经元**，一般称作「节点」（node）或者「单元」（unit）。每个节点可以从其他节点接收输入，或者从外部源接收输入，然后计算输出。每个输入都各自的「权重」（weight，即 w），用于调节该输入对输出影响的大小，节点的结构如图所示：

![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\3.png)

其中x1,x2作为该节点的输入，其权重分别为 w1 和 w2。同时，还有配有「偏置b」（bias）的输入 ，偏置的主要功能是为每一个节点提供可训练的常量值（在节点接收的正常输入以外）。

## 多层感知机

多层感知机（Multilayer Perceptron）缩写为MLP，也称作前馈神经网络（Feedforward Neural Network）。它是一种基于神经网络的机器学习模型，通过多层非线性变换对输入数据进行高级别的抽象和分类。

在上面的例子中，我们假定了直线的方程式为$f(x)=ax+by+c$，但如果是一些复杂的情况，我们可能无法通过简单的数学计算找到对应的函数。但与单层感知机相比，MLP有多个隐藏层，每个隐藏层由多个神经元组成，每个神经元通过对上一层的输入进行加权和处理，再通过激活函数进行非线性映射。这样我们便可以表达这个抽象的映射关系。

### 基本结构

下图显示了一个最典型的MLP，它包括包括三层：**输入层、隐层（全连接层）和输出层**（全连接的意思就是：上一层的任何一个神经元与下一层的所有神经元都有连接）。

![动图](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\v2-2110a4d62384a277ab700907e73e8721_b.gif)

 它的工作分为两部分:

- **前向传播**：输入数据被馈送到输入层，然后传递到隐藏层，并最终生成输出层的输出。每一层的每一个神经元都会计算其加权输入和非线性激活函数的输出。

- **反向传播**：在训练过程中，输出与期望的输出进行比较，产生一个误差值。这个误差随后被反向传播到网络中，权重得到相应的更新。

因为参与运算的各元素都是**矩阵**，我们可以使用Numpy来构造一个三层的MLP：

```python
import numpy as np

class BPNetwork_Numpy:
    def __init__(self):
        self.weights = {
            'fc1': np.random.randn(128, 28 * 28),
            'fc2': np.random.randn(64, 128),
            'fc3': np.random.randn(10, 64)
        }
        self.biases = {
            'fc1': np.random.randn(128),
            'fc2': np.random.randn(64),
            'fc3': np.random.randn(10)
        }
```

### **为什么需要引入隐藏层？**

1. **模型复杂性和表示能力**：隐藏层增加了网络的容量，使其能够学习并表示更复杂的函数。理论上，一个单隐藏层的神经网络可以近似任何连续函数，但在实践中，增加更多的隐藏层可以更容易（需要更少的神经元）地近似这些函数，并且可以更高效地学习。
2. **层次化特征学习**：深度网络（有多个隐藏层的网络）可以学习层次化的特征。例如，在图像识别中，第一层可能会学习边缘和纹理，第二层可能会学习更复杂的结构（如形状或模式），以此类推。这种层次化的表示使得网络能够更有效地捕捉数据的内在结构。
3. **非线性堆叠**：通过引入多个隐藏层并在每个层之后应用非线性激活函数，网络可以表示更复杂的非线性函数。这增加了模型对各种数据分布和关系的灵活性。
4. **降低参数数量**：与一个非常宽的单隐藏层相比，深度结构可以用较少的总参数来实现同样的模型容量。这可以提高计算效率，并可能减少过拟合的风险。
5. **实际成功案例**：在许多实际的机器学习任务中，深度神经网络（带有多个隐藏层）已经表现出比浅层网络更好的性能。例如，深度学习模型已经在图像识别、语音识别、机器翻译等任务中取得了突破性的结果。

总的来说，隐藏层提供了网络更多的能力和灵活性来学习和逼近复杂的关系和数据结构。当然，引入太多的隐藏层和神经元也可能导致模型的过拟合，因此需要采用适当的正则化策略来平衡模型的容量和训练数据的数量。

### 计算方式

让我们把上面的MLP细节化：

![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\v2-5a81c06789ad5e9323f93c6540263327_r.jpg)

在一般情况下，参与运算的各元素都是**矩阵**，其中的蓝色方块代表着**激活函数**，绿色方块代表着**权重Weight**和**偏置Bias**。需要注意的是，***权重和偏置对应上图中不同神经元的连线***，例如1->3和1->4的参数不同。详细计算方式如下式：
$$
\begin{align}
a1 &= W*h1+b\\
h2 &= F(a1)
\end{align}
$$
**在分类问题中，最后的输出层元素个数一般等于分类数目，最终的结果代表着该输入被这个MLP分为某一类的可能性大小，指越大，代表越可能属于该类。为了便于观测，我们通常使用argmax函数将输出与下标联系起来，转化为分类结果。**

同样的，我们可以使用Numpy帮我们完成计算（向前传播）部分：

```python
 def forward(self, x):
        x = x.flatten()
        self.layer1_output = np.dot(self.weights['fc1'], x) + self.biases['fc1']
        self.layer1_activation = np.maximum(0, self.layer1_output)
        self.layer2_output = np.dot(self.weights['fc2'], self.layer1_activation) + self.biases['fc2']
        self.layer2_activation = np.maximum(0, self.layer2_output)
        self.layer3_output = np.dot(self.weights['fc3'], self.layer2_activation) + self.biases['fc3']
        return np.argmax(self.layer3_output)
```

其中，np.dot()函数提供了矩阵乘法，np.maximum()作为我们的激活函数，最后的np.argmax()用来找到最大值的下标，方便我们观测结果。

### 激活函数

!!! question "什么？你有问题？"
	“*到这里，可能有同学要问了，为什么要有激活函数？（上图中的**f(x)**，引例中的**是否大于0**）*”
	“谁问你了（×”
	“我们来看下面这幅图片，对于下面这样更偏向于现实的情况，你还能找出一条**直线**，尽可能多的将所有的点（包括还没画出的）分开吗？”
<img src="C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\1702218719184.png" alt="1702218719184" style="zoom:50%;" />

很明显，直线是无法做到的，也就意味着，***仅有线性函数无法处理复杂问题***。使用激活函数，能够给神经元引入非线性因素，使得神经网络增加了模型的表示能力，能够捕捉到数据中更复杂的模式和关系，这样神经网络就可以利用到更多的现实复杂模型中。

<img src="C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\image-20231210225600016.png" alt="image-20231210225600016" style="zoom:67%;" />

其次，处理复杂问题时，仅靠一个神经元是远远不够的，我们更多的是使用多层感知机，不妨来看下面的推导：


$$
\begin{align}
&f_1(x)  = a_1x+b_1\\
&f_2(x)  = a_2f_1(x)+b_2\\
&f_i(x)  = a_if_{i-1} (x)+bi\\
&其中的f(x)均为线性函数，由数学归纳法可得n层感知机的输出\\
& \left\{\begin{matrix} 
Bias = \sum_{k=1}^{n}\prod_{j=1}^{k-1}a_j \cdot b_k  \\
Weight = \prod_{k=1}^{n}a_{k}\\
Output = Weight \cdot x + Bias
\end{matrix}\right.    
\end{align}
$$
我们可以看到最后的Output表达式和一个神经元的别无两样，因此***如果不使用激活函数，每一层输出都是上层输入的线性函数，无论神经网络有多少层，输出都是输入的线性组合。***

常见的激活函数我们会在另一章节详细讲解。

## 图片的另一种形态

了解了什么是MLP，每一层如何计算，输出是怎么样的，我们再来思考一下输入，如何把一张图片塞到计算机中？

!!! question "从misc看图片"
    如果让你向一位视力障碍人来描述一幅图片，你会怎样去描述它？物体和他们的属性、风格、情感、布局
    如果是想计算机呢，你又该怎么去描述它？

每一张图片，我们都可以看作是几个二维矩阵的叠加（ARGB-4个，RGB-3个，L-1个），如下图这张黑白图片所示，每个x，y所对应的点都具有自己的值，我们通过归一化将他们从0-255整型数映射到0.0-1.0的浮点数，颜色越淡（白），值越大。这样，我们可以把每一张图片拆为一个n维矩阵。通过这样的方式，我们可以把我们的视觉和计算机的数据联系起来，然后通过一些方式进行计算。

![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\pixel-values.png)

因此对于一张28 * 28的灰度图像，我们可以将他**展平flatten**为一个28 * 28 = 784个元素的矩阵

<iframe src=".\assets\pixels-to-neurons.mp4" width="100%" height="700" frameborder="no" scrolling="no" allowfullscreen="allowfullscreen"> </iframe> 

紧接着，用我们上面讲到的知识，将这个矩阵放到MLP中进行计算，得到最后的输出，选择最大值的下标作为它的预测结果。下图中亮起的神经元代表某次计算中，输出经过激活函数后激活了。

<iframe src=".\assets\network-propagation.mp4" width="100%" height="700" frameborder="no" scrolling="no" allowfullscreen="allowfullscreen"> </iframe> 

!!! note "骚话环节"
    怎么样？经过可视化后，现在是不是好理解多了？那快夸夸Cain宝（×

### BP误差反向传播法

!!! question "如何训练呢？"
	“那么我该如何训练我自己的MLP呢？”
	“谁问你了...”
	“我问的！（举手”

下图简要的展示了反向传播算法的核心概念，大致来说：**通过比较现实输出与期望输出之间的差异，根据差异来反向更新每一层的参数，从而使现实输出更加贴近于期望输出。**

![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\v2-b84fee51daf26d27bd90420311d410a2_r-1701958087743-6.jpg)

!!! quote "多一行公式，少一个观众"
	~~为什么要大致的说呢，因为我猜下面的推导没有人看（bushi~~

#### 数学推导

损失对参数梯度的反向传播可以被这样直观解释：由A到传播B，即由 $\partial L/\partial A$ 得到 $\partial L/\partial B$ ，由导数链式法则$\partial L/\partial B=(\partial L/\partial A)\cdot(\partial A/\partial B)$。所以神经网络的BP就是通过链式法则求出 $L$ 对所有参数梯度的过程。


$$
\begin{aligned}\frac{\partial l}{\partial a_{21}}&=\frac{\partial l}{\partial h_{21}}\cdot\frac{\partial h_{21}}{\partial a_{21}}=\frac{\partial l}{\partial h_{21}}\cdot activate'(a_{21})\end{aligned}
$$
![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\v2-ec822b0f10066f097a074e1ff09167b1_r.jpg)



![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\v2-d38c136a7b018fb3ea7344a902d0e3d1_r.jpg)



![img](C:\Users\17845\Desktop\Hello-CTF\docs\HC_AI\assets\v2-1223ca671593b057371819e3f4e52c90_r.jpg)







## 代码实现与解析

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



