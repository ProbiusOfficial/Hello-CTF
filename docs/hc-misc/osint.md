---
comments: true

---

## 开源情报获取 OSINT

### 简介

**「开源网络情报 Open source intelligence,OSINT」** ，是一种情报搜集手段，从各种公开的信息资源中寻找和获取有价值的情报。

在国内，大家也喜欢称这类题目为 "**社工题**" ，这类题目通常以 各类标志性建筑，街景，行程信息等内容的 **图片** 作为题目，选手需要从有限信息中不断检索修补信息差，寻找细节突破点，依次来获得题目要求的信息 —— 拍摄地点，拍摄人的一些身份信息等。

OSINT 题目是比较吃经验和技巧的

### 图片定位

对于仅给定图片的 OSINT 题目，通常从图片本身和图片内容入手。

#### 图片文件信息

 一些图片的EXIF信息中可能含有拍摄的经纬度，角度，设备型号等信息，通过图片 经纬度 + 图片内容 进行误差修正的 OSINT 题目也算是简单题目中的常客。

####  街景

街景的维度很广，笔者在此尽量列举，但不能保证完全包含：

- 建筑风格

- 从是否有地标性或者其他标志性建筑

- 显眼的店铺名称

- 各种路牌 指示牌

- 围栏特征

- 车牌

- 行人服饰特点

  ......

#### 交通要地

如 火车站，地铁站，机场，码头等。

- 布局
- 各类提示性文字 指示牌
- 交题工具是否出镜 —— 外形 具体型号

#### 行程信息

如 各类车票 / 机票 ，已对部分要素打码，但依旧能获取到其他如 时间等有效要素的图片。

### 信息检索

<待更新>

### 工具

#### 图片搜索

| 网站名称与网址                                     | 描述                                                         |
| -------------------------------------------------- | ------------------------------------------------------------ |
| [谷歌识图](https://www.google.com/imghp)           | 优秀的图片搜索引擎，以搜索效果著称。手机用户可点击浏览器菜单→开启“浏览电脑版网页”以访问上传图片功能。 |
| [百度识图](https://image.baidu.com/?fr=shitu)      | 适合中文网站图片资源搜索的工具。                             |
| [搜狗识图](https://pic.sogou.com/)                 | 提供人性化的图片识别功能，包括「通用识图」「猫狗识别」「明星识别」「找高清大图」等选项，根据需求选择提高识别效率。 |
| [Yandex.Images](https://yandex.com/images)         | 俄罗斯最受欢迎的搜索引擎，支持英文搜索。在其他搜索引擎无法找到结果时，不妨尝试使用Yandex以获取更好的搜索效果。 |
| [TinEye](https://www.tineye.com/)                  | 老牌图片逆向搜索引擎，资源丰富。安装浏览器插件后可通过右键菜单直接使用。 |
| [必应可视化搜索](https://cn.bing.com/visualsearch) | 由微软必应推出的视觉搜索引擎，支持特色搜索如植物、商品、家具、宠物、文字、人物、建筑等。 |
| [What Anime Is This?](https://trace.moe/)          | 动漫视频截图识别工具，专为动漫迷设计。可通过视频截图找到动画图片的来源和片段位置。 |
| [SauceNAO Image Search](https://saucenao.com/)     | 知名的图片逆向搜索引擎，对动画、漫画、插画、二次元等领域有出色的识图效果。可获取图片来源和作者主页链接。包含数十亿张图像，尤其在Pixiv（pixiv.net）的识别效果出色。 |

#### 定位辅助

| 网址                                                         | 描述                                     |
| ------------------------------------------------------------ | ---------------------------------------- |
| [Google Geolocation](https://developers.google.com/maps/documentation/geolocation/intro) | 谷歌地理定位                             |
| [移动OneNET平台](https://open.iot.10086.cn/)                 | 智能硬件位置定位                         |
| [OpenGPS](https://www.opengps.cn/)                           | 高精度定位                               |
| [CellLocation](http://www.cellocation.com/)                  | 经纬度、WiFi mac地址、BSSID、gps         |
| [Seeker](https://github.com/thewhiteh4t/seeker)              | 获取高精度地理信息和设备信息的工具       |
| [MAC地址查询工具](https://www.nirsoft.net/utils/mac_address_lookup_find.html) | MAC地址库查询工具                        |
| [MaxMind GeoIP](https://dev.maxmind.com/geoip/geoip2/geolite2/) | geoip2全球IPV4                           |
| [IPIP](https://www.ipip.net/)                                | IPV4，可查IP归属数据中心。               |
| [IPPlus360](https://www.ipplus360.com/)                      | IPV4/IPV6地址库。                        |
| [OpenCellID](http://opencellid.org/)                         | GSM定位                                  |
| [SunCalc](https://www.suncalc.org/)                          | 通过太阳和投射的阴影进行人员地理位置定位 |

#### 社交媒体

| 网站名称与网址                                               | 描述                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [lyzem.com](https://lyzem.com/)                              | Telegram搜索引擎。                                           |
| [Social Mapper](https://github.com/Greenwolf/social_mapper)  | 由Trustwave公司SpiderLabs开源的社交媒体枚举和关联工具，通过人脸识别关联人物侧写。 |
| [Sniff-Paste](https://github.com/needmorecowbell/sniff-paste) | 针对Pastebin的开源情报收集工具。                             |
| [Linkedin2Username](https://github.com/initstring/linkedin2username) | 通过Linkedin领英获取相关公司员工列表的工具。                 |
| [Mailget](https://github.com/Ridter/Mailget)                 | 通过脉脉用户猜测企业邮箱的工具。                             |
| [Picdeer](http://picdeer.org/)                               | Instagram内容和用户在线搜索工具。                            |
| [Ransombile](https://github.com/martinvigo/ransombile)       | 用于根据社交媒体密码找回信息的Ruby工具。                     |
| [Reg007](https://www.reg007.com/)                            | 查找注册过的网站和应用的工具。                               |
| [Check Your Weibo](https://github.com/rtcatc/check-your-weibo) | 微博互关检测脚本的工具。                                     |

#### 交题运输

| 网站名称与网址                                               | 描述                       |
| ------------------------------------------------------------ | -------------------------- |
| [Flightradar24](https://www.flightradar24.com/)              | 提供全球实时飞行跟踪信息。 |
| [MarineTraffic](https://www.marinetraffic.com/en/ais/home/centerx:5.4/centery:50.8/zoom:2) | 提供全球船舶跟踪情报。     |

### 小结

CTF中的 OSINT考察 是比较狭义的，虽然多以街景分析定位为主，但里面依旧融合了不少知识。作为比赛题目，重在考察选手的信息收集和整理能力，这也是作为计算机和网络安全领域必不可少的技能。

在现实中，情况往往比题目更加复杂，OSINT 涉及到的信息维度和信息量会远远超出预期，希望读者能够在题目中提升，而不是一味的沉沦。
