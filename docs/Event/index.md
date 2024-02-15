---
isevent: true
comments: true
hide:
  - footer
  - toc
  - edit
  - view
---

<style>
#calendar {
  margin-bottom: 0;
  margin-top: 0;
  font-size: 0.75rem;
}

#calendar :is(button[title="Next month"], button[title="list view"]) {
  border-left: 0;
}

.fc-event-main {
    color: black !important;
}

.fc .event-running {
    border: 1px solid #64dd17;
    background-color: #64dd171a;
    box-shadow: 0 0 5px #0000001a;
}

.fc .event-oncoming {
    border: 1px solid #00b0ff;
    background-color: #00b0ff1a;
    box-shadow: 0 0 5px #0000001a;
}

.fc .event-ended {
    border: 1px solid #9e9e9e;
    background-color: #9e9e9e26;
    box-shadow: 0 0 5px #0000001a;
}
</style>

<script>
    /** 
     * @description 解析日期 格式为 YYYY年MM月DD日 HH:mm
     * @param rawTime {string}
     */
    function parseCNTime(rawTime) {
        const year = parseInt(rawTime.substr(0, 4))
        const month = parseInt(rawTime.substr(5, 2)) - 1
        const day = parseInt(rawTime.substr(8, 2))
        const hour = parseInt(rawTime.substr(12, 2))
        const minute = parseInt(rawTime.substr(15, 2))
        return new Date(year, month, day, hour, minute)
    }
    
    /** 
     * @description 解析日期 格式为 YYYY年MM月DD日 HH:mm
     * @param rawTime {string}
     */
    function parseGlobalTime(rawTime) {
        const [startDate, endDate] = rawTime.split(' - ')
        return [new Date(startDate), new Date(endDate)]
    }
    
    const CN = 'cn'
    const GLOBAL = 'gl'

    /**
     * @param feed {string}
     */
    async function fetchCNCTFTime(feed) {
        const res = await fetch(feed)
        /** 
         * @type {{data: {result: Array<{
         *   name: string
         *   link: string
         *   type: string
         *   bmks: string
         *   bmjz: string
         *   bsks: string
         *   bsjs: string
         *   readmore: string
         *   id: number
         *   status: number
         * }>}}}
         */
        const timeData = await res.json();
        
        /**
         * @description 传给 fullcalendar
         * @type {Array<{
         *   id: number
         *   start: string
         *   end: string
         *   title: string
         *   url: link
         *   className: string
         *   region: CN | GLOBAL
         * >}}
         */
        const events = []
        timeData.data.result.forEach((v) => {
            try {
                // // 报名时间段
                // events.push({
                //     id: v.id,
                //     start: parseTime(v.bmks),
                //     end: parseTime(v.bmjz),
                //     title: v.name + '（报名时间）',
                //     url: v.link,
                //     region: CN
                // })
                const startTime = parseCNTime(v.bsks)
                const endTime = parseCNTime(v.bsjs)

                // 比赛时间段
                events.push({
                    id: v.id,
                    start: startTime.toISOString(),
                    end: endTime.toISOString(),
                    title: v.name,
                    url: v.link,
                    className: endTime < new Date() ? 'event-ended' : startTime > new Date() ? 'event-oncoming' : 'event-running',
                    region: CN,
                    display: 'block'
                })
            } catch(err) {
                console.error('日期解析错误！', err)
                console.error(v)
            }
        })
        
        return events;
    }

    /**
     * @param feed {string}
     */
    async function fetchGlobalCTFTime(feed) {
        const res = await fetch(feed)
        /** 
         * @type Array<{
         *   "比赛名称": string
         *   "比赛时间": string
         *   "比赛链接": string
         *   "比赛ID": string
         * }>
         */
        const timeData = await res.json();
        
        /**
         * @description 传给 fullcalendar
         * @type {Array<{
         *   id: number
         *   start: string
         *   end: string
         *   title: string
         *   url: link
         *   classNames: string[]
         *   region: CN | GLOBAL
         * }>}
         */
        const events = []

        timeData.forEach((v) => {
            try {
                const [startTime, endTime] = parseGlobalTime(v.比赛时间)

                events.push({
                    id: v.id,
                    start: startTime.toISOString(),
                    end: endTime.toISOString(),
                    title: v.比赛名称,
                    url: v.比赛链接,
                    className: endTime < new Date() ? 'event-ended' : startTime > new Date() ? 'event-oncoming' : 'event-running',
                    region: GLOBAL,
                    display: 'block'
                })
            } catch(err) {
                console.error('日期解析错误！', err)
                console.error(v)
            }
        })
        
        return events;
    }

    async function loadCalendar() {
        const calendarEl = document.getElementById('calendar')
        
        const cnEvents = await fetchCNCTFTime('https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/CN.json')
        const globalEvents = await fetchGlobalCTFTime('https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/Global.json')

        const calendar = new FullCalendar.Calendar(calendarEl, {
            height: 'auto',
            locale: "zh",
            headerToolbar: {
              start: "custom2 custom1",
              center: "title",
              end: "prev,next dayGridMonth,listMonth"
            },
            customButtons: {
              custom1: {
                text: "只看国内",
                click: function () {
                    calendar.removeAllEventSources();
                    calendar.addEventSource(cnEvents);
                }
              },
              custom2: {
                text: "只看国外",
                click: function () {
                    calendar.removeAllEventSources();
                    calendar.addEventSource(globalEvents);
                }
              }
            },
            viewDidMount() {
                calendarEl.querySelectorAll('button').forEach((ele) => {
                    ele.classList.remove(...ele.classList)
                    ele.classList.add('md-button')
                    ele.style.padding = '0.5em'
                    ele.style.borderRadius = '0'
                })
            },
            events: globalEvents,
            eventClick: function (info) {
                info.jsEvent.preventDefault();

                if (info.event.url) window.open(info.event.url);
            }
        });
        calendar.render();
        
        globalThis.calendar = calendar;
        
        // set class
        calendarEl.querySelectorAll('button').forEach((ele) => {
            ele.classList.remove(...ele.classList)
            ele.classList.add('md-button')
            ele.style.padding = '0.5em'
            ele.style.borderRadius = '0'
        })
    }
    
    // 前端路由变更
    if (document.getElementById('calendar')) loadCalendar()
    else 
    // 首次进入
        document.addEventListener('DOMContentLoaded', loadCalendar)

</script>

<div class="grid cards">
  <ul>
    <li>
      <p><span class="twemoji lg middle"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M14 14H7v2h7m5 3H5V8h14m0-5h-1V1h-2v2H8V1H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2m-2 7H7v2h10v-2Z"></path></svg></span> <strong>赛事日历</strong></p>
      <hr>
      <div class="grid cards">
        <!-- 日历 HTML部分 -->
        <div id='calendar' />
      </div>
    </li>
  </ul>
</div>

<div class="grid cards"  markdown>

-   :material-flag-triangle:{ .lg .middle } __比赛一览__

    --- 
    > 在此处控制赛事标签状态 : [∨全部展开][full_open] | [∧全部收起][full_close]
    [full_open]: javascript:(function(){document.querySelectorAll('details.abstract').forEach(function(detail){detail.open=true;});})()
    [full_close]: javascript:(function(){document.querySelectorAll('details.abstract').forEach(function(detail){detail.open=false;});})()

    <!-- 赛事内容部分_开始 -->
    === "查看比赛:"
    
        !!! warning "健康比赛忠告"
            抵制不良比赛，拒绝盗版比赛。注意自我保护，谨防受骗上当。  
            适度CTF益脑，沉迷CTF伤身。合理安排时间，享受健康生活。
    
    === "*正在报名*"
        ??? Quote "[青少年CTF擂台挑战赛 2024 #Round 1](https://www.qsnctf.com/#/main/race-center/race-guide?id=11)"  
            **比赛名称** : [青少年CTF擂台挑战赛 2024 #Round 1](https://www.qsnctf.com/#/main/race-center/race-guide?id=11)  
            **比赛类型** : 团队赛|1-4人  
            **报名时间** : 2024年02月05日 00:00 - 2024年02月28日 22:00  
            **比赛时间** : 2024年02月29日 09:00 - 2024年03月01日 22:00  
            **其他说明** : QQ 群号：820016571  
            
        ??? Quote "[VNCTF 2024](https://vnctf2024.manqiu.top/)"  
            **比赛名称** : [VNCTF 2024](https://vnctf2024.manqiu.top/)  
            **比赛类型** : 个人赛  
            **报名时间** : 2023年02月18日 21:00 - 2024年02月17日 20:00  
            **比赛时间** : 2024年02月17日 08:00 - 2024年02月17日 20:00  
            **其他说明** : V&N 联合战队招新赛，赛事QQ群：717513199  
            
        ??? Quote "[第一届“长城杯”信息安全铁人三项赛初赛](http://ccb.itsec.gov.cn/)"  
            **比赛名称** : [第一届“长城杯”信息安全铁人三项赛初赛](http://ccb.itsec.gov.cn/)  
            **比赛类型** : 团队赛|1-4人  
            **报名时间** : 2023年12月21日 00:00 - 2024年02月20日 18:00  
            **比赛时间** : 2024年03月01日 09:00 - 2024年03月31日 18:00  
            **其他说明** : 比赛时间2024年3月  
            
        ??? Quote "[SICTF Round#3](https://yuanshen.life/)"  
            **比赛名称** : [SICTF Round#3](https://yuanshen.life/)  
            **比赛类型** : 团队赛|1-3人  
            **报名时间** : 2024年01月11日 14:00 - 2024年02月18日 09:00  
            **比赛时间** : 2024年02月16日 09:00 - 2024年02月18日 18:00  
            **其他说明** : 比赛QQ群：737732413  本次比赛采用CTF赛制，题目难度两级分化，无论是刚刚入门的萌新还是轻车熟路的大神，都可以快速找到属于你的比赛乐趣哦~  
            
    === "*即将开始*"
        === "国内赛事"
            ??? Quote "[青少年CTF擂台挑战赛 2024 #Round 1](https://www.qsnctf.com/#/main/race-center/race-guide?id=11)"  
                **比赛名称** : [青少年CTF擂台挑战赛 2024 #Round 1](https://www.qsnctf.com/#/main/race-center/race-guide?id=11)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年02月05日 00:00 - 2024年02月28日 22:00  
                **比赛时间** : 2024年02月29日 09:00 - 2024年03月01日 22:00  
                **其他说明** : QQ 群号：820016571  
                
            ??? Quote "[VNCTF 2024](https://vnctf2024.manqiu.top/)"  
                **比赛名称** : [VNCTF 2024](https://vnctf2024.manqiu.top/)  
                **比赛类型** : 个人赛  
                **报名时间** : 2023年02月18日 21:00 - 2024年02月17日 20:00  
                **比赛时间** : 2024年02月17日 08:00 - 2024年02月17日 20:00  
                **其他说明** : V&N 联合战队招新赛，赛事QQ群：717513199  
                
            ??? Quote "[第一届“长城杯”信息安全铁人三项赛初赛](http://ccb.itsec.gov.cn/)"  
                **比赛名称** : [第一届“长城杯”信息安全铁人三项赛初赛](http://ccb.itsec.gov.cn/)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2023年12月21日 00:00 - 2024年02月20日 18:00  
                **比赛时间** : 2024年03月01日 09:00 - 2024年03月31日 18:00  
                **其他说明** : 比赛时间2024年3月  
                
            ??? Quote "[SICTF Round#3](https://yuanshen.life/)"  
                **比赛名称** : [SICTF Round#3](https://yuanshen.life/)  
                **比赛类型** : 团队赛|1-3人  
                **报名时间** : 2024年01月11日 14:00 - 2024年02月18日 09:00  
                **比赛时间** : 2024年02月16日 09:00 - 2024年02月18日 18:00  
                **其他说明** : 比赛QQ群：737732413  本次比赛采用CTF赛制，题目难度两级分化，无论是刚刚入门的萌新还是轻车熟路的大神，都可以快速找到属于你的比赛乐趣哦~  
                
            ??? Quote "[第二届数据安全大赛暨首届“数信杯”数据安全大赛](https://shuxinbei.ichunqiu.com/)"  
                **比赛名称** : [第二届数据安全大赛暨首届“数信杯”数据安全大赛](https://shuxinbei.ichunqiu.com/)  
                **比赛类型** : 团队赛|1-3人  
                **报名时间** : 2023年11月15日 00:00 - 2024年01月19日 18:00  
                **比赛时间** : 2024年02月24日 10:00 - 2024年02月24日 18:00  
                **其他说明** : 比赛时间未定  
                
        === "国外赛事"
    
    === "*正在进行*"
        === "国内赛事"
            ??? Quote "[HGAME2024网络攻防大赛](https://hgame.vidar.club)"  
                **比赛名称** : [HGAME2024网络攻防大赛](https://hgame.vidar.club)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年01月20日 20:00 - 2024年02月05日 20:00  
                **比赛时间** : 2024年01月29日 20:00 - 2024年02月27日 20:00  
                **其他说明** : QQ群：134591168   适合新手参加  
                
        === "国外赛事"
    
    === "*已经结束*"
        === "国内赛事"
            ??? Quote "[NSSCTF Round#18 Basic](https://www.nssctf.cn/contest/317/)"  
                **比赛名称** : [NSSCTF Round#18 Basic](https://www.nssctf.cn/contest/317/)  
                **比赛类型** : 团队赛|1-3人  
                **报名时间** : 2024年02月06日 09:30 - 2024年02月14日 09:30  
                **比赛时间** : 2024年02月14日 09:30 - 2024年02月14日 17:30  
                **其他说明** : QQ群：521330139  
                
            ??? Quote "[第二届BeginCTF](http://47.100.169.26/)"  
                **比赛名称** : [第二届BeginCTF](http://47.100.169.26/)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年01月24日 00:00 - 2024年02月06日 10:00  
                **比赛时间** : 2024年01月31日 10:00 - 2024年02月06日 10:00  
                **其他说明** : qq群：612995005  适合新手参加  
                
            ??? Quote "[L3HCTF 2024](https://l3hctf2024.xctf.org.cn/)"  
                **比赛名称** : [L3HCTF 2024](https://l3hctf2024.xctf.org.cn/)  
                **比赛类型** : 团队赛  
                **报名时间** : 2024年01月24日 00:00 - 2024年02月05日 09:00  
                **比赛时间** : 2024年02月03日 09:00 - 2024年02月05日 09:00  
                **其他说明** : QQ群：512066352  
                
            ??? Quote "[zkCTF](https://zkctf.scalebit.xyz)"  
                **比赛名称** : [zkCTF](https://zkctf.scalebit.xyz)  
                **比赛类型** : 个人赛 | WEB3  
                **报名时间** : 2024年01月16日 00:00 - 2024年02月05日 09:00  
                **比赛时间** : 2024年02月03日 09:00 - 2024年02月05日 09:00  
                **其他说明** : TG官方群：https://t.me/ScaleBitAudit  
                
            ??? Quote "[第二届N1CTF Junior](https://ctf.junior.nu1l.com/)"  
                **比赛名称** : [第二届N1CTF Junior](https://ctf.junior.nu1l.com/)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年01月22日 08:00 - 2024年02月03日 00:00  
                **比赛时间** : 2024年02月03日 09:00 - 2024年02月04日 18:00  
                **其他说明** : N1CTFJunior是Nu1L Team组织的官方纳新  赛事旨在选拔年轻优秀人才加入Nu1LTeam  QQ群:180885587  
                
            ??? Quote "[第二届红桥杯渗透测试挑战赛](https://tryhackme.com/)"  
                **比赛名称** : [第二届红桥杯渗透测试挑战赛](https://tryhackme.com/)  
                **比赛类型** : 个人赛  
                **报名时间** : 2023年12月01日 00:00 - 2024年01月31日 00:00  
                **比赛时间** : 2023年11月30日 00:00 - 2024年01月31日 00:00  
                **其他说明** : QQ群：751273347  比赛时间待定  
                
            ??? Quote "[第七届西湖论剑网络安全技能大赛初赛](https://game.gcsis.cn/)"  
                **比赛名称** : [第七届西湖论剑网络安全技能大赛初赛](https://game.gcsis.cn/)  
                **比赛类型** : 团队赛|4-8人  
                **报名时间** : 2024年01月09日 00:00 - 2024年01月24日 18:00  
                **比赛时间** : 2024年01月30日 10:00 - 2024年01月30日 18:00  
                **其他说明** : QQ群：666010671 768342822    
                
            ??? Quote "[Real World CTF 6th](https://realworldctf.com/)"  
                **比赛名称** : [Real World CTF 6th](https://realworldctf.com/)  
                **比赛类型** : 团队赛  
                **报名时间** : 2023年12月28日 16:30 - 2024年01月28日 19:00  
                **比赛时间** : 2024年01月26日 19:00 - 2024年01月28日 19:00  
                **其他说明** : Discord: https://discord.com/invite/8GNqypNaxB  
                
            ??? Quote "[獬豸杯电子数据取证比武](https://mp.weixin.qq.com/s/kTUbGvh4EGZf5Jx87NyCgQ)"  
                **比赛名称** : [獬豸杯电子数据取证比武](https://mp.weixin.qq.com/s/kTUbGvh4EGZf5Jx87NyCgQ)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年01月25日 00:00 - 2024年01月27日 18:00  
                **比赛时间** : 2024年01月28日 10:00 - 2024年01月28日 18:00  
                **其他说明** : QQ群号：955391766  
                
            ??? Quote "[NSSCTF Round#17 Basic](https://www.nssctf.cn/contest/)"  
                **比赛名称** : [NSSCTF Round#17 Basic](https://www.nssctf.cn/contest/)  
                **比赛类型** : 团队赛|1-3人  
                **报名时间** : 2024年01月16日 00:00 - 2024年01月28日 17:30  
                **比赛时间** : 2024年01月28日 14:00 - 2024年01月28日 17:30  
                **其他说明** : QQ群：521330139  
                
            ??? Quote "[Real World CTF 6th 体验赛](https://be-a-rwctfer.realworldctf.com/)"  
                **比赛名称** : [Real World CTF 6th 体验赛](https://be-a-rwctfer.realworldctf.com/)  
                **比赛类型** : 团队赛 | 邀请制  
                **报名时间** : 2023年12月28日 16:30 - 2024年01月17日 18:00  
                **比赛时间** : 2024年01月27日 10:00 - 2024年01月28日 10:00  
                **其他说明** : 选手交流群：612460086  
                
            ??? Quote "[春秋杯网络安全联赛冬季赛](https://endbm.ichunqiu.com/2023cqgames2)"  
                **比赛名称** : [春秋杯网络安全联赛冬季赛](https://endbm.ichunqiu.com/2023cqgames2)  
                **比赛类型** : 个人赛CTF+RDG  
                **报名时间** : 2023年12月18日 00:00 - 2024年01月22日 17:00  
                **比赛时间** : 2024年01月20日 10:00 - 2024年01月22日 18:00  
                **其他说明** : 赛事QQ群：277328440  
                
            ??? Quote "[第三届WEBSHELL伏魔挑战赛](https://mp.weixin.qq.com/s/e8OE3rXyIqPkHrOHBDL5Kw)"  
                **比赛名称** : [第三届WEBSHELL伏魔挑战赛](https://mp.weixin.qq.com/s/e8OE3rXyIqPkHrOHBDL5Kw)  
                **比赛类型** : 个人赛  
                **报名时间** : 2023年12月29日 10:00 - 2024年01月17日 10:00  
                **比赛时间** : 2024年01月12日 14:00 - 2024年01月17日 10:00  
                **其他说明** :   
                
            ??? Quote "[第七届强网杯全国网络安全挑战赛决赛](https://qiangwangbei.com/)"  
                **比赛名称** : [第七届强网杯全国网络安全挑战赛决赛](https://qiangwangbei.com/)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2023年05月01日 00:00 - 2023年12月09日 00:00  
                **比赛时间** : 2024年01月13日 09:00 - 2024年01月14日 16:00  
                **其他说明** : QQ群：723023839  
                
            ??? Quote "[movectf 2024](https://movectf2024.movebit.xyz/)"  
                **比赛名称** : [movectf 2024](https://movectf2024.movebit.xyz/)  
                **比赛类型** : 个人赛 | WEB3  
                **报名时间** : 2023年12月25日 00:00 - 2024年01月14日 09:00  
                **比赛时间** : 2024年01月12日 09:00 - 2024年01月14日 09:00  
                **其他说明** : 旗舰级 Move 安全竞赛，旨在吸引更多对   Move 语言和 Move 生态系统感兴趣的安全专业人士  和开发人员。  QQ学习交流群：163569170  
                
            ??? Quote "[ NSSCTF Round#16 Basic](https://www.nssctf.cn/contest)"  
                **比赛名称** : [ NSSCTF Round#16 Basic](https://www.nssctf.cn/contest)  
                **比赛类型** : 团队赛|1-3人  
                **报名时间** : 2024年01月03日 00:00 - 2024年01月13日 17:40  
                **比赛时间** : 2024年01月13日 14:00 - 2024年01月13日 17:40  
                **其他说明** : QQ群：521330139  
                
            ??? Quote "[“复兴杯”2023年第四届大学生网络安全精英赛初赛](https://www.nisp.org.cn/wads)"  
                **比赛名称** : [“复兴杯”2023年第四届大学生网络安全精英赛初赛](https://www.nisp.org.cn/wads)  
                **比赛类型** : 个人赛  
                **报名时间** : 2023年11月10日 12:00 - 2024年01月02日 18:00  
                **比赛时间** : 2024年01月03日 09:00 - 2024年01月07日 18:00  
                **其他说明** :   
                
        === "国外赛事"
    
    <!-- 赛事内容部分_结束 -->
</div>
  

## 添加赛事Bot到群聊

=== "Usage"

    [![](./index_demo/add_bot.png){ width="200" align=left }](https://qun.qq.com/qunpro/robot/qunshare?robot_uin=3889001776&robot_appid=102074091)
    赛事API现已接入QQ官方机器人，通过扫描二维码或者点击跳转到对应页面可将机器人添加到自己的群聊中。  
    添加后在聊天框中输入 / 会自动弹出功能列表 (*该功能需要最新版本的手机QQ)  
    具体命令:
    ```
    @DKbot /比赛列表 - 获取国内所有比赛信息  
    @DKbot /比赛列表 g - 获取国外所有比赛信息  
    @DKbot /比赛 +比赛序号 - 获取国内对应比赛的详细信息 (*比赛序号在比赛列表中获取)  
    @DKbot /比赛g +比赛序号 - 获取国外对应比赛的详细信息 (*比赛序号在比赛列表中获取)  
    ```


=== "Demo"

    <figure markdown>
    ![](./index_demo/bot_demo.png)
    <figcaption>Demo</figcaption>
    </figure>
    

    
## 获取数据？

> 数据基于[Hello-CTFtime](https://github.com/ProbiusOfficial/Hello-CTFtime)项目，每小时更新一次。  
  数据获取以及示例:

=== "国内赛事"

    ``` markdown title="CN.json"
    /GET https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/CN.json
    ```

    <div class="result" markdown>

    ```json
    {
      "success": true,
      "data": {
        "result": [
          {
            "name": "HelloCTF",
            "link": "https://hello-ctf.com/",
            "type": "团队赛|1-3人",
            "bmks": "2099年11月15日 00:00",
            "bmjz": "2099年12月31日 00:00",
            "bsks": "2099年12月31日 00:00",
            "bsjs": "2099年12月31日 00:00",
            "readmore": "这是一条备注",
            "id": 114,
            "status": 1 /0 报名未开始 /1 报名进行中 /2 报名已结束 /3 比赛进行中 /4 比赛已结束
          },
              ],
        "total": 62,
        "page": 1,
        "size": 20
      },...
      "msg": ""
    }
    ```

    </div>

=== "国外赛事"

    ``` markdown title="Global.json"
    /GET https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/Global.json
    ```

    <div class="result" markdown>

    ```json
    [
      {
        "比赛名称": "Example CTF",
        "比赛时间": "2024-01-01 00:00:00 - 2024-01-01 08:00:00 UTC+8",
        "添加日历": "https://ctftime.org/event/1234.ics",
        "比赛形式": "Jeopardy",
        "比赛链接": "https://examplectf.com/",
        "比赛标志": "https://ctftime.org/media/events/logo",
        "比赛权重": "0.00",
        "赛事主办": "Example (https://ctftime.org/team/1234)",
        "比赛ID": "1234",
        "比赛状态": "oncoming / nowrunning / past"
      },...
    ]
    ```

    </div>

## 数据源

> 国内赛事数据来源: 三哈，探姬 - https://github.com/ProbiusOfficial/Hello-CTFtime 
  国外赛事数据来源: CTFtime RSS源 - https://ctftime.org

加入赛事交流群体验Bot获取比赛信息:
=== "CTF赛事通知报名群_1"
    <figure markdown>
      ![group_1](./index_demo/group_1.png){ width="300" }
    </figure>
=== "CTF赛事通知报名群_2"
    <figure markdown>
      ![group_2](./index_demo/group_2.png){ width="300" }
    </figure>
