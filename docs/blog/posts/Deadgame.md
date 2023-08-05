---
date: 2023-07-30
authors: [probius]
description: >
  *CTF中星际2题目的通关题解和静态解法
categories:
  - CTF
links:
  - docs/blog/posts/Deadgame.md
comments: true
---

# *CTF Dead Game 题解 & 代码分析

> 星际玩家最后的倔强x By 国服第一探姬 (探姬#51276)
> 现在已经成亚服难民了x 探姬#31410

感觉本题作者预期的解应该是通关，不过通过银河编辑器解题也不算非预期,毕竟不难，难的是如今找到如今还在打星际的CTFer，并且他一定意义上熟悉银河编辑器。因为SC2兵种繁多，一个技能也会绑定很多演算体 触发器 脚本，因此让新手直接上手似乎不太可能，不过我还是打算讲讲怎么用银河编辑器直接算，说实话这很有意思ww（好吧其实是曾经有过一些优质mod和图产出却没拿到一血的mapmaker最后的尊严QaQ！

<!-- more -->

## 题面

![](https://nssctf.wdf.ink//img/WDTJ/202307292210607.png)

## 通关法

还是需要银河编辑器，打开后点绿色的测试

![](https://nssctf.wdf.ink//img/WDTJ/202307300135020.png)

虽然题目有防作弊检测，但是也就检测了泽叔的生命和护盾，以及玩家单位是否只有泽叔一个。

所以用作弊码就好了。

通关推荐使用这三个，追求速度可以开技能无冷却，老玩家开个无敌就够了，开图大可不必 www

```
god #上帝模式
hanshotfirst # 技能快速冷却
TookTheRedPill #开图 消除战争迷雾
```

然后跟着关卡走就行了。



## 银河编辑器解法【静态】

>在后面写文的复现中 发现纯银河编辑器好像很难做到直接手撕 这个地方大家看个乐子
>
>写这个方法是因为 做题的时候突然会想起自己之前做图和做mod然后拿自己做的图或者mod的后门调戏群友的快乐时光，不过遗憾的是后来大家都不打星际了，再加上现在国服无了，人也越来越少了（悲

任何一张星际争霸2游戏地图比较核心的地方就是触发器，而让每个地图作者头疼的也是触发器x

我们边讲边介绍x 问题不大

Map文件我们直接用银河编辑器打开即可。

![](https://nssctf.wdf.ink//img/WDTJ/202307292205963.png)

> 图圈常说 买银河编辑器送星际争霸2 就得益于银河编辑器基于的GE是一种强大的游戏引擎 你甚至能用他播放视频（

很乱，很正常，要素比较多，不过不必担心，你只需要认识几个我们题解需要用到的几个部件：

![](https://nssctf.wdf.ink//img/WDTJ/202307292208377.png)

分别对应 **触发器** **单位数据** **文本信息**

和大部分MISC题目一样，从文本入手是一个不错的解决方法，所以我们可以先尝试在Text选项中搜索flag或者ctf字样：

![](https://nssctf.wdf.ink//img/WDTJ/202307292215336.png)

其实大概就知道要干什么了，找三块碎片(其实就是碰瓷末日预言关卡泽叔去三个萨尔纳加神殿收集预言碎片x) 才能获得flag。

但其实这里直接只看flag相关的文本有个坏处——容易被误导x

除了最后一块碎片可以人眼看出以外，其实其他碎片的外部指向都不可用，都只能依靠游戏内部要素拿到。
![](https://nssctf.wdf.ink//img/WDTJ/202307292222179.png)

> 最后一块碎片 81!zZ@Rd —— 也就是Blizzard(暴雪)的CTF式写法ww

所以第一块和第二块碎片，显然是要依靠游戏内部运算的，所以这个时候，触发器就要登场了。

你可以根据text结果精确定位——很明显Flag有三个值，分别是：

- flag_part1
- flag_part2
- flag_part3

当然，也可以直接用Find 找flag 全部Fuzz一遍：

![](https://nssctf.wdf.ink//img/WDTJ/202307292235156.png)

可以看到在通关后的任务结束界面会显示解析到的flag——所以通关游戏也是不错的选择。

不过都到这了，我们不妨看看每个flag的part都是怎么计算的。

- flag_part1

  第一部分的表达式其实有点劝退的，主要是长——人有时候遇到长的东西，会下意识回避，不过不妨静下心来，慢慢看x

  ![](https://nssctf.wdf.ink//img/WDTJ/202307292239360.png)

  ```
  Variable -Set flag_part1 = (String({((Zeratul [162.87, 28.62] Maximum Life (Current))+(Zeratul [162.87, 28.62] Maximum Shields (Current)))*(Zeratul [162.87, 28.62] Maximum Shields (Current))*(Zeratul [162.87, 28.62] Shields Regeneration Rate (Current))+((Zeratul [162.87, 28.62] Maximum Life (Current))+(Zeratul [162.87, 28.62] Maximum Shields (Current)))*(Zeratul [162.87, 28.62] Shields Regeneration Rate (Current))+((Zeratul [162.87, 28.62] Movement Speed Max (Current))+(Zeratul [162.87, 28.62] Life Regeneration Rate (Current)))*(Zeratul [162.87, 28.62] Shields Regeneration Rate (Current))*10+2*(Zeratul [162.87, 28.62] Shields Regeneration Rate (Current))+(Zeratul [162.87, 28.62] Movement Speed Max (Current))+(Zeratul [162.87, 28.62] Life Regeneration Rate (Current))}))
  ```

  其实把数据填入后就是小学加减乘除，而问题就在于，又臭又长的表达式让人走不到这一步，上面涉及到一些单位的数据 如生命值 护盾值，这个时候我们就要去 **单位数据** Data里面去寻找了。

  我们先整理一下，我们需要什么数据：

  | 数据名称                                                    | 数量 | 代换           |
  | ----------------------------------------------------------- | ---- | -------------- |
  | Zeratul [162.87, 28.62] Maximum Life (Current)              | 2    | **记作** **A** |
  | Zeratul [162.87, 28.62] Maximum Shields (Current)           | 3    | **记作** **B** |
  | Zeratul [162.87, 28.62] Shields Regeneration Rate (Current) | 4    | **记作** **C** |
  | Zeratul [162.87, 28.62] Movement Speed Max (Current)        | 2    | **记作** **D** |
  | *Zeratul [162.87, 28.62] Life Regeneration Rate (Current)*  | 2    | **记作** **E** |

  可以看到全部都是泽拉图这个单位的数据 包括 `生命值 ` `护盾值` `护盾恢复速度` `最大移动速度` `生命回复速度`

  得到简化表达式：

  ```
  Variable -Set flag_part1 = (String({((A)+(B))*(B)*(C)+((A)+(B))*(C)+((D)+(E))*(C)*10+2*(C)+(D)+(E)}))
  ```

  要算的值也很简单：

  ```
  ((A)+(B))*(B)*(C)+((A)+(B))*(C)+((D)+(E))*(C)*10+2*(C)+(D)+(E)
  ```

  接下来只需要去Data里面找泽叔的数据：

  使用搜索功能即可：

  ![](https://nssctf.wdf.ink//img/WDTJ/202307292300509.png)

  要注意的是，星际2中不同场景的单位，单位名字虽然相同，但是背后的ID不是相同的 会附带单位的一些要素 所以要完全对应触发器的单位 一个字不差，这里触发器使用的是 Zeratul 的数据。

  | 数据名称                                                    | 值   |
  | :---------------------------------------------------------- | ---- |
  | Zeratul [162.87, 28.62] Maximum Life (Current)              | 300  |
  | Zeratul [162.87, 28.62] Maximum Shields (Current)           | 100  |
  | Zeratul [162.87, 28.62] Shields Regeneration Rate (Current) | 2    |
  | Zeratul [162.87, 28.62] Movement Speed Max (Current)        | 3    |
  | Zeratul [162.87, 28.62] Life Regeneration Rate (Current)    | 0    |

    ```
  ((300)+(100))*(100)*(2)+((300)+(100))*(2)+((3)+(0))*(2)*10+2*(2)+(3)+(0) = 80867
    ```

   看吧，我就说小学加减乘除啦~

  所以 flag_part1 的值我们就得到了 80867

  注意：

  > 因为作者没有使用行为升级的方式去更改默认数据，所以静态解析直接算值是可行的。
  >
  > 不过严格意义来讲 因为触发器使用的 (Current) 值 所以这样计算其实是不严谨的，因为我随时可以在游戏中动态的去调整生命值。
  >
  > 以及这里出现了一个小插曲 我把 Zeratul [162.87, 28.62] Movement Speed Max (Current)的值看成2了（所以还对着虚空找了老久的bug。
  > 但在截图中也可以看出 Zeratul [162.87, 28.62] Movement Speed Max (Current) 的值就是 3，而后续也没有任何行为的影响。
  > 也就是说，开局的表达式((A)+(B))*(B)*(C)+((A)+(B))*(C)+((D)+(E))*(C)*10+2*(C)+(D)+(E) 带入后是
  > ((300)+(100))*(100)*(2)+((300)+(100))*(2)+((3)+(0))*(2)*10+2*(2)+(3)+(0) = 80867
  > 没有任何问题
  > 而在测试中 Zeratul [162.87, 28.62] Life Regeneration Rate (Current) 的表现形式（即单位生命的回复）确实是 0
  > 所以编辑器静态环境完全能够做出，对数据错误表示抱歉。
  > 欢迎大家一起来玩星际呀~

  

- flag_part2

  同样我们用查找功能去找这个变量的触发器：

  ![](https://nssctf.wdf.ink//img/WDTJ/202307300125670.png)

  可以看到flag2的值有如下变化：

  ```
  Variable -Set flag_part2 = {flag_part2"K"}
  Variable -Set flag_part2 = {flag_part2(String((Zeratul count for player ijqvaelrggonccpy, counting Queued Or Better)))}       Variable -Set flag_part2 = {flag_part2(String({(Zeratul [162.87, 28.62] Maximum Life (Current))/300}))}
  Variable -Set flag_part2 = {flag_part2(String({(Zeratul [162.87, 28.62] Maximum Shields (Current))/100}))}
  Variable -Set flag_part2 = {flag_part2(String({((Zeratul [162.87, 28.62] Maximum Life (Current))+(Zeratul [162.87, 28.62] Maximum Shields (Current)))/80}))}
  ```

  而每一个变化对应一个独立的触发器，所以我在前面有说到，记得注意通关顺序节奏，得跟着任务目标走，不然flag就错了x

  结合我们之前拿到的数据，对应的值不难求出，唯一特殊的：

  `{flag_part2"K"}`给flag_2添加字符K，这里是当追猎喊出 " For Shakuras! " (为了夏古拉斯)的时候触发，不过作者很鸡贼用爆蚊把追猎爆了，所以这波属于是棺材板呐喊了！

  `String((Zeratul count for player ijqvaelrggonccpy, counting Queued Or Better))`应该是玩家泽叔的个数，在遇到巢虫领主时触发，为1。

  这两稍不注意 1和K就互换了 我当时卡在这卡了老久，因为通关节奏太快了（）导致flag一直不对nnd

  然后后面就是计算了，

  - `(Zeratul [162.87, 28.62] Maximum Life (Current))/300})) = 1`
  - `(Zeratul [162.87, 28.62] Maximum Shields (Current))/100})) = 1`
  - `((Zeratul [162.87, 28.62] Maximum Life (Current))+(Zeratul [162.87, 28.62] Maximum Shields (Current)))/80 = 400 / 80 =5`

  所以第二部分到没问题（

  flag_part2 的值为 K_1115

- flag_part3

  其实在看Text能看出个大概，如果你是忠诚的暴黑，那么这个字符就是送分的玻璃渣。

  ![](https://nssctf.wdf.ink//img/WDTJ/202307300221638.png)

  当然如果你不是，我们依旧可以通过触发器去算（）

  ![](https://nssctf.wdf.ink//img/WDTJ/202307300149535.png)

  提取出来内容如下：

  ```
  Variable -Set flag_part3 = {flag_part3(Substring(table, {(Xel'Naga Shrine [166.56, 111.52] Life (Current))%71}, {(Xel'Naga Shrine [166.56, 111.52] Life (Current))%71}))}
  
  Variable -Set flag_part3 = {flag_part3(Substring(table, {(Food of a Thousand Feasts [179.44, 9.73] Life (Current))+1}, {(Food of a Thousand Feasts [179.44, 9.73] Life (Current))+1}))}
  
  Variable -Set flag_part3 = {flag_part3(Substring(table, {(Super Warp Gate [181.00, 10.00] Life (Current))/10+13}, {(Super Warp Gate [181.00, 10.00] Life (Current))/10+13}))}
  
  Variable -Set flag_part3 = {flag_part3(Substring(table, {((Zeratul [162.87, 28.62] Movement Speed Max (Current))+3)*((Zeratul [162.87, 28.62] Movement Speed Max (Current))+3)}, {((Zeratul [162.87, 28.62] Movement Speed Max (Current))+3)*((Zeratul [162.87, 28.62] Movement Speed Max (Current))+3)}))}
  
  Variable -Set flag_part3 = {flag_part3(Substring(table, {(Void Seeker [69.01, 133.48] Life (Current))%69}, {(Void Seeker [69.01, 133.48] Life (Current))%69}))}
  
  Variable -Set flag_part3 = {flag_part3(Substring(table, {(Zeratul [162.87, 28.62] Maximum Life (Current))/2-66}, {(Zeratul [162.87, 28.62] Maximum Life (Current))/2-66}))}
  
  Variable -Set flag_part3 = {flag_part3(Substring(table, {(Zeratul [162.87, 28.62] Maximum Shields (Current))/2+4}, {(Zeratul [162.87, 28.62] Maximum Shields (Current))/2+4}))}
  
  Variable -Set flag_part3 = {flag_part3(Substring(table, {(Square root((Beacon (Protoss Large) [22.82, 96.07] Life (Current))))+9}, {(Square root((Beacon (Protoss Large) [22.82, 96.07] Life (Current))))+9}))}
  
  ```

  看着很吓人，其实确实很吓人（

  利用 **Substring** 函数 直接从 table里面取值，所以看着表达式长 但前后都一样

  以及最后的 **Square root** 平方根函数

  记得我们的table么：

  ![](https://nssctf.wdf.ink//img/WDTJ/202307300153948.png)

    ```
  0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ 
    ```

    ```json
  {
  "1": "0", "2": "1", "3": "2", "4": "3", "5": "4", "6": "5", "7": "6", "8": "7", "9": "8", "10": "9", "11": "a", "12": "b", "13": "c", "14": "d", "15": "e", "16": "f", "17": "g", "18": "h", "19": "i", "20": "j", "21": "k", "22": "l", "23": "m", "24": "n", "25": "o", "26": "p", "27": "q", "28": "r", "29": "s", "30": "t", "31": "u", "32": "v", "33": "w", "34": "x", "35": "y", "36": "z", "37": "A", "38": "B", "39": "C", "40": "D", "41": "E", "42": "F", "43": "G", "44": "H", "45": "I", "46": "J", "47": "K", "48": "L", "49": "M", "50": "N", "51": "O", "52": "P", "53": "Q", "54": "R", "55": "S", "56": "T", "57": "U", "58": "V", "59": "W", "60": "X", "61": "Y", "62": "Z", "63": "!", "64": "\ ", "65": "#", "66": "$", "67": "%", "68": "&", "69": "'", "70": "(", "71": ")", "72": "*", "73": "+", "74": ",", "75": "-", "76": ".", "77": "/", "78": ":", "79": ";", "80": "<", "81": "=", "82": ">", "83": "?", "84": "@", "85": "[", "86": "\\", "87": "]", "88": "^", "89": "_", "90": "`", "91": "{", "92": "|", "93": "}", "94": "~"
  }
  
    ```

  然后我们再去数据里找萨尔那加神殿(Xel'Naga Shrine)等缺失的数据：

  | 数据名称                                                | 值   |
  | ------------------------------------------------------- | ---- |
  | Xel'Naga Shrine [166.56, 111.52] Life (Current)         | 1500 |
  | Food of a Thousand Feasts [179.44, 9.73] Life (Current) | 1    |
  | Super Warp Gate [181.00, 10.00] Life (Current)          | 500  |
  | Zeratul [162.87, 28.62] Movement Speed Max (Current)    | 3    |
  | Void Seeker [69.01, 133.48] Life (Current)              | 200  |
  | Zeratul [162.87, 28.62] Maximum Life (Current)          | 300  |
  | Zeratul [162.87, 28.62] Maximum Shields (Current)       | 100  |
  | Beacon (Protoss Large)                                  | 25   |

  所以转换出来：

  ```
  (Substring(table, {(Xel'Naga Shrine [166.56, 111.52] Life (Current))%71}, {(Xel'Naga Shrine [166.56, 111.52] Life (Current))%71})) = 9 ——"8"
  
  (Substring(table, {(Food of a Thousand Feasts [179.44, 9.73] Life (Current))+1}, {(Food of a Thousand Feasts [179.44, 9.73] Life (Current))+1})) = 2 ——"1"
  
  (Substring(table, {(Super Warp Gate [181.00, 10.00] Life (Current))/10+13}, {(Super Warp Gate [181.00, 10.00] Life (Current))/10+13})) = 63 ——"!"
  
  (Substring(table, {((Zeratul [162.87, 28.62] Movement Speed Max (Current))+3)*((Zeratul [162.87, 28.62] Movement Speed Max (Current))+3)}, {((Zeratul [162.87, 28.62] Movement Speed Max (Current))+3)*((Zeratul [162.87, 28.62] Movement Speed Max (Current))+3)})) = 36 ——"z"
  
  (Substring(table, {(Void Seeker [69.01, 133.48] Life (Current))%69}, {(Void Seeker [69.01, 133.48] Life (Current))%69})) = 62 ——"Z"
  
  (Substring(table, {(Zeratul [162.87, 28.62] Maximum Life (Current))/2-66}, {(Zeratul [162.87, 28.62] Maximum Life (Current))/2-66})) = 84 ——"@"
  
  (Substring(table, {(Zeratul [162.87, 28.62] Maximum Shields (Current))/2+4}, {(Zeratul [162.87, 28.62] Maximum Shields (Current))/2+4})) = 54 ——"R"
  
  (Substring(table, {(Square root((Beacon (Protoss Large) [22.82, 96.07] Life (Current))))+9}, {(Square root((Beacon (Protoss Large) [22.82, 96.07] Life (Current))))+9})) = (5+9) ——"d"
  ```

  得到第三部分的flag `81!zZ@Rd`

最后拼接即可：**\*CTF{80867_K1115_81!zZ@Rd}**

![](https://nssctf.wdf.ink//img/WDTJ/202307300222344.png)

## 彩蛋

为什么换附件x

在第一次放题的时候，对最后一个字母的计算 出题人用的是

```
Variable -Set flag_part3 = {flag_part3(Substring(table, {(Square root((Beacon (Protoss Large) [22.82, 96.07] Life (Current))))+9}, {(Square root((Baneling (Burrowed) [30.75, 26.80] Life (Current))))+9}))}
```

emm 信标生命到毒爆虫，看样子还是对25气矿恋恋不忘呢x？？ 

不过，最后生成的字符是8，emm 神奇的编辑器 （）

![](https://nssctf.wdf.ink//img/WDTJ/202307300240389.png)

