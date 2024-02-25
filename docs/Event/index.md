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
        
        const cnEvents = await fetchCNCTFTime('json/CN.json')
        const globalEvents = await fetchGlobalCTFTime('json/Global.json')

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
    [full_open]: javascript:(function(){document.querySelectorAll('details.quote').forEach(function(detail){detail.open=true;});})()
    [full_close]: javascript:(function(){document.querySelectorAll('details.quote').forEach(function(detail){detail.open=false;});})()

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
            
    === "*即将开始*"
        === "国内赛事"
            ??? Quote "[DubheCTF 2024](https://adworld.xctf.org.cn/contest/assess?hash=94938be6-ce42-11ee-ab28-000c29bc20bf)"  
                **比赛名称** : [DubheCTF 2024](https://adworld.xctf.org.cn/contest/assess?hash=94938be6-ce42-11ee-ab28-000c29bc20bf)  
                **比赛类型** : 团队赛 | 1-n  
                **报名时间** : 2024年03月01日 09:00 - 2024年03月16日 08:00  
                **比赛时间** : 2024年03月16日 09:00 - 2024年03月18日 09:00  
                **其他说明** : Discord: https://discord.gg/hq4m3KrVfG QQ群：512066352 本届DubheCTF2024由XCTF联赛的合作单位天枢Dubhe战队组织，由赛宁网安提供技术支持。作为第八届XCTF国际联赛的分站赛，本次比赛将采用在线网络安全夺旗挑战赛的形式，面向全球开放。 此次比赛冠军队伍将直接晋级第八届XCTF总决赛（总决赛具体地点待定，将在确定后通知获得资格的国际和国内队伍）。其他参赛的队伍也将获得积分，来竞争XCTF总决赛的其他席位。  
                
            ??? Quote "[青少年CTF擂台挑战赛 2024 #Round 1](https://www.qsnctf.com/#/main/race-center/race-guide?id=11)"  
                **比赛名称** : [青少年CTF擂台挑战赛 2024 #Round 1](https://www.qsnctf.com/#/main/race-center/race-guide?id=11)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年02月05日 00:00 - 2024年02月28日 22:00  
                **比赛时间** : 2024年02月29日 09:00 - 2024年03月01日 22:00  
                **其他说明** : QQ 群号：820016571  
                
            ??? Quote "[第一届“长城杯”信息安全铁人三项赛初赛](http://ccb.itsec.gov.cn/)"  
                **比赛名称** : [第一届“长城杯”信息安全铁人三项赛初赛](http://ccb.itsec.gov.cn/)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2023年12月21日 00:00 - 2024年02月20日 18:00  
                **比赛时间** : 2024年03月01日 09:00 - 2024年03月31日 18:00  
                **其他说明** : 比赛时间2024年3月  
                
        === "国外赛事"
            ??? Quote "[VishwaCTF 2024](https://vishwactf.com/)"  
                [![](https://ctftime.org/media/events/VishwaCTF_3.png){ width="200" align=left }](https://vishwactf.com/)  
                **比赛名称** : [VishwaCTF 2024](https://vishwactf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-01 18:30:00 - 2024-03-03 18:29:59 UTC+8  
                **比赛权重** : 33.43  
                **赛事主办** : CyberCellVIIT (https://ctftime.org/team/144677)  
                **添加日历** : https://ctftime.org/event/2272.ics  
                
            ??? Quote "[osu!gaming CTF 2024](https://www.osugaming.lol/)"  
                [![](https://ctftime.org/media/events/unknown_1.png){ width="200" align=left }](https://www.osugaming.lol/)  
                **比赛名称** : [osu!gaming CTF 2024](https://www.osugaming.lol/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-02 01:00:00 - 2024-03-04 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : osu!gaming (https://ctftime.org/team/186954)  
                **添加日历** : https://ctftime.org/event/2165.ics  
                
            ??? Quote "[GCC CTF 2024](https://gcc-ctf.com/)"  
                [![](https://ctftime.org/media/events/Logo_GCC_White_Font.png){ width="200" align=left }](https://gcc-ctf.com/)  
                **比赛名称** : [GCC CTF 2024](https://gcc-ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-02 04:00:00 - 2024-03-04 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Galette Cidre CTF (https://ctftime.org/team/246488)  
                **添加日历** : https://ctftime.org/event/2251.ics  
                
            ??? Quote "[AthackCTF 2024](https://www.athackctf.com/)"  
                [![](https://ctftime.org/media/events/_hacklogo_v2_720.png){ width="200" align=left }](https://www.athackctf.com/)  
                **比赛名称** : [AthackCTF 2024](https://www.athackctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-02 16:00:00 - 2024-03-04 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : athackPrivate (https://ctftime.org/team/278003)  
                **添加日历** : https://ctftime.org/event/2228.ics  
                
            ??? Quote "[Pearl CTF](https://pearlctf.in/)"  
                [![](https://ctftime.org/media/events/_croppearl_logo_1_of_1.png){ width="200" align=left }](https://pearlctf.in/)  
                **比赛名称** : [Pearl CTF](https://pearlctf.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-08 20:00:00 - 2024-03-10 07:59:59 UTC+8  
                **比赛权重** : 23.95  
                **赛事主办** : BIT CRIMINALS (https://ctftime.org/team/151727)  
                **添加日历** : https://ctftime.org/event/2231.ics  
                
            ??? Quote "[Shakti CTF](https://ctf.shakticon.com/)"  
                [![](https://ctftime.org/media/events/shaktictf_1_1.png){ width="200" align=left }](https://ctf.shakticon.com/)  
                **比赛名称** : [Shakti CTF](https://ctf.shakticon.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-08 20:30:00 - 2024-03-09 20:30:00 UTC+8  
                **比赛权重** : 24.10  
                **赛事主办** : TeamShakti (https://ctftime.org/team/61083)  
                **添加日历** : https://ctftime.org/event/2268.ics  
                
            ??? Quote "[HackDay 2024 - Finals](https://www.hackday.fr/)"  
                [![](https://ctftime.org/media/events/CREA_LOGO_Blason_Espion_1.png){ width="200" align=left }](https://www.hackday.fr/)  
                **比赛名称** : [HackDay 2024 - Finals](https://www.hackday.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-09 02:00:00 - 2024-03-10 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HackDayCTF (https://ctftime.org/team/277562)  
                **添加日历** : https://ctftime.org/event/2267.ics  
                
            ??? Quote "[WxMCTF 2024](https://ctf.mcpt.ca/contest/wxmctf)"  
                [![](https://ctftime.org/media/events/Logo_thing_1.png){ width="200" align=left }](https://ctf.mcpt.ca/contest/wxmctf)  
                **比赛名称** : [WxMCTF 2024](https://ctf.mcpt.ca/contest/wxmctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-09 08:00:00 - 2024-03-11 07:00:00 UTC+8  
                **比赛权重** : 23.59  
                **赛事主办** : wxmctf (https://ctftime.org/team/211390)  
                **添加日历** : https://ctftime.org/event/2179.ics  
                
            ??? Quote "[vikeCTF 2024](https://ctf.vikesec.ca/)"  
                [![](https://ctftime.org/media/events/vikesec.png){ width="200" align=left }](https://ctf.vikesec.ca/)  
                **比赛名称** : [vikeCTF 2024](https://ctf.vikesec.ca/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-09 08:00:00 - 2024-03-11 08:00:00 UTC+8  
                **比赛权重** : 23.64  
                **赛事主办** : PencilTesters (https://ctftime.org/team/178288)  
                **添加日历** : https://ctftime.org/event/2263.ics  
                
            ??? Quote "[Cyber Apocalypse 2024: Hacker Royale](https://ctf.hackthebox.com/event/details/cyber-apocalypse-2024-hacker-royale-1386)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hackthebox.com/event/details/cyber-apocalypse-2024-hacker-royale-1386)  
                **比赛名称** : [Cyber Apocalypse 2024: Hacker Royale](https://ctf.hackthebox.com/event/details/cyber-apocalypse-2024-hacker-royale-1386)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-09 21:00:00 - 2024-03-13 20:59:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Hack The Box (https://ctftime.org/team/136056)  
                **添加日历** : https://ctftime.org/event/2255.ics  
                
            ??? Quote "[Snowfort 2024](https://snowfort2024.cyberscoring.ca/)"  
                [![](https://ctftime.org/media/events/logo_2024.png){ width="200" align=left }](https://snowfort2024.cyberscoring.ca/)  
                **比赛名称** : [Snowfort 2024](https://snowfort2024.cyberscoring.ca/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-03-10 00:00:00 - 2024-03-10 08:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Shell We Hack? (https://ctftime.org/team/220236)  
                **添加日历** : https://ctftime.org/event/2260.ics  
                
            ??? Quote "[Nullcon Berlin HackIM 2024 CTF](https://ctf.nullcon.net/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.nullcon.net/)  
                **比赛名称** : [Nullcon Berlin HackIM 2024 CTF](https://ctf.nullcon.net/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-14 17:30:00 - 2024-03-15 19:00:00 UTC+8  
                **比赛权重** : 20.00  
                **赛事主办** : ENOFLAG (https://ctftime.org/team/1438)  
                **添加日历** : https://ctftime.org/event/2264.ics  
                
            ??? Quote "[KalmarCTF 2024](http://KalmarC.TF/)"  
                [![](https://ctftime.org/media/events/logo_square_756x756.png){ width="200" align=left }](http://KalmarC.TF/)  
                **比赛名称** : [KalmarCTF 2024](http://KalmarC.TF/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-16 01:00:00 - 2024-03-18 01:00:00 UTC+8  
                **比赛权重** : 24.21  
                **赛事主办** : kalmarunionen (https://ctftime.org/team/114856)  
                **添加日历** : https://ctftime.org/event/2227.ics  
                
            ??? Quote "[1753CTF 2024](https://1753ctf.com/)"  
                [![](https://ctftime.org/media/events/badge.png){ width="200" align=left }](https://1753ctf.com/)  
                **比赛名称** : [1753CTF 2024](https://1753ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-16 05:00:00 - 2024-03-17 05:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : 1753c (https://ctftime.org/team/178287)  
                **添加日历** : https://ctftime.org/event/2234.ics  
                
            ??? Quote "[WolvCTF 2024](https://wolvctf.io/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://wolvctf.io/)  
                **比赛名称** : [WolvCTF 2024](https://wolvctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-16 07:00:00 - 2024-03-18 07:00:00 UTC+8  
                **比赛权重** : 35.25  
                **赛事主办** : wolvsec (https://ctftime.org/team/83621)  
                **添加日历** : https://ctftime.org/event/2240.ics  
                
            ??? Quote "[LINE CTF 2024](https://linectf.me/)"  
                [![](https://ctftime.org/media/events/Image_1.jpeg){ width="200" align=left }](https://linectf.me/)  
                **比赛名称** : [LINE CTF 2024](https://linectf.me/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-23 08:00:00 - 2024-03-24 08:00:00 UTC+8  
                **比赛权重** : 49.10  
                **赛事主办** : LINE CTF (https://ctftime.org/team/144094)  
                **添加日历** : https://ctftime.org/event/2119.ics  
                
            ??? Quote "[Grey Cat The Flag 2024 Qualifiers](https://ctf.nusgreyhats.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.nusgreyhats.org/)  
                **比赛名称** : [Grey Cat The Flag 2024 Qualifiers](https://ctf.nusgreyhats.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-23 12:00:00 - 2024-03-24 12:00:00 UTC+8  
                **比赛权重** : 22.46  
                **赛事主办** : NUSGreyhats (https://ctftime.org/team/16740)  
                **添加日历** : https://ctftime.org/event/2242.ics  
                
            ??? Quote "[ZeroDays CTF](https://zerodays.ie/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://zerodays.ie/)  
                **比赛名称** : [ZeroDays CTF](https://zerodays.ie/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-23 18:00:00 - 2024-03-24 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Ireland without the RE (https://ctftime.org/team/179144)  
                **添加日历** : https://ctftime.org/event/2196.ics  
                
            ??? Quote "[JerseyCTF IV](https://ctf.jerseyctf.com/)"  
                [![](https://ctftime.org/media/events/lock.png){ width="200" align=left }](https://ctf.jerseyctf.com/)  
                **比赛名称** : [JerseyCTF IV](https://ctf.jerseyctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-24 00:00:00 - 2024-03-25 00:00:00 UTC+8  
                **比赛权重** : 21.26  
                **赛事主办** : Highlander Hackers (https://ctftime.org/team/173925)  
                **添加日历** : https://ctftime.org/event/2230.ics  
                
            ??? Quote "[CursedCTF 2024 Quals](https://cursedc.tf/)"  
                [![](https://ctftime.org/media/events/Screenshot_2024-01-23_at_11.45.46_AM.png){ width="200" align=left }](https://cursedc.tf/)  
                **比赛名称** : [CursedCTF 2024 Quals](https://cursedc.tf/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-03-30 08:00:00 - 2024-04-01 08:00:00 UTC+8  
                **比赛权重** : 19.50  
                **赛事主办** : cursed (https://ctftime.org/team/199492)  
                **添加日历** : https://ctftime.org/event/2239.ics  
                
            ??? Quote "[SummitCTF 2024](https://summitctf.org/)"  
                [![](https://ctftime.org/media/events/default_background_removed.png){ width="200" align=left }](https://summitctf.org/)  
                **比赛名称** : [SummitCTF 2024](https://summitctf.org/)  
                **比赛形式** : Hack quest  
                **比赛时间** : 2024-03-30 21:00:00 - 2024-04-01 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CyberVT (https://ctftime.org/team/173872)  
                **添加日历** : https://ctftime.org/event/2237.ics  
                
            ??? Quote "[VolgaCTF 2024 Qualifier](https://q.2024.volgactf.ru/)"  
                [![](https://ctftime.org/media/events/logo-social-yellow_14.png){ width="200" align=left }](https://q.2024.volgactf.ru/)  
                **比赛名称** : [VolgaCTF 2024 Qualifier](https://q.2024.volgactf.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-30 23:00:00 - 2024-03-31 23:00:00 UTC+8  
                **比赛权重** : 35.91  
                **赛事主办** : VolgaCTF.org (https://ctftime.org/team/27094)  
                **添加日历** : https://ctftime.org/event/2200.ics  
                
            ??? Quote "[AmateursCTF 2024](https://ctf.amateurs.team/)"  
                [![](https://ctftime.org/media/events/2d6bd602-ecce-47e6-8f53-b352af222287.915ceb9574bb9759b4dd16bf8a744d25_1.jpeg){ width="200" align=left }](https://ctf.amateurs.team/)  
                **比赛名称** : [AmateursCTF 2024](https://ctf.amateurs.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-05 22:00:00 - 2024-04-10 11:00:00 UTC+8  
                **比赛权重** : 24.54  
                **赛事主办** : les amateurs (https://ctftime.org/team/166729)  
                **添加日历** : https://ctftime.org/event/2226.ics  
                
            ??? Quote "[SwampCTF 2024](https://swampctf.com/)"  
                [![](https://ctftime.org/media/events/swampctf.png){ width="200" align=left }](https://swampctf.com/)  
                **比赛名称** : [SwampCTF 2024](https://swampctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 06:00:00 - 2024-04-08 06:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Kernel Sanders (https://ctftime.org/team/397)  
                **添加日历** : https://ctftime.org/event/2138.ics  
                
            ??? Quote "[TAMUctf 2024](https://tamuctf.com/)"  
                [![](https://ctftime.org/media/events/TAMUCTF_cmaroon_2.png){ width="200" align=left }](https://tamuctf.com/)  
                **比赛名称** : [TAMUctf 2024](https://tamuctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 06:00:00 - 2024-04-08 06:00:00 UTC+8  
                **比赛权重** : 48.25  
                **赛事主办** : TAMUctf (https://ctftime.org/team/37721)  
                **添加日历** : https://ctftime.org/event/2238.ics  
                
            ??? Quote "[DamCTF 2024](https://damctf.xyz/)"  
                [![](https://ctftime.org/media/events/DAM-CTF-2020-Icon_1.png){ width="200" align=left }](https://damctf.xyz/)  
                **比赛名称** : [DamCTF 2024](https://damctf.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 08:00:00 - 2024-04-08 08:00:00 UTC+8  
                **比赛权重** : 47.75  
                **赛事主办** : OSUSEC (https://ctftime.org/team/12858)  
                **添加日历** : https://ctftime.org/event/2262.ics  
                
            ??? Quote "[Midnight Sun CTF 2024 Quals](https://midnightsunctf.com/)"  
                [![](https://ctftime.org/media/events/midnight.png){ width="200" align=left }](https://midnightsunctf.com/)  
                **比赛名称** : [Midnight Sun CTF 2024 Quals](https://midnightsunctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 20:00:00 - 2024-04-06 20:00:00 UTC+8  
                **比赛权重** : 35.74  
                **赛事主办** : HackingForSoju (https://ctftime.org/team/3208)  
                **添加日历** : https://ctftime.org/event/2247.ics  
                
            ??? Quote "[b01lers CTF 2024](http://ctf.b01lers.com/)"  
                [![](https://ctftime.org/media/events/b01lers-griffen_1.png){ width="200" align=left }](http://ctf.b01lers.com/)  
                **比赛名称** : [b01lers CTF 2024](http://ctf.b01lers.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-12 20:00:00 - 2024-04-14 20:00:00 UTC+8  
                **比赛权重** : 30.80  
                **赛事主办** : b01lers (https://ctftime.org/team/11464)  
                **添加日历** : https://ctftime.org/event/2250.ics  
                
            ??? Quote "[PlaidCTF 2024](https://plaidctf.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://plaidctf.com/)  
                **比赛名称** : [PlaidCTF 2024](https://plaidctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-13 05:00:00 - 2024-04-15 05:00:00 UTC+8  
                **比赛权重** : 95.19  
                **赛事主办** : Plaid Parliament of Pwning (https://ctftime.org/team/284)  
                **添加日历** : https://ctftime.org/event/2245.ics  
                
            ??? Quote "[Space Heroes 2024](https://spaceheroes.ctfd.io/)"  
                [![](https://ctftime.org/media/events/moon.png){ width="200" align=left }](https://spaceheroes.ctfd.io/)  
                **比赛名称** : [Space Heroes 2024](https://spaceheroes.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-13 06:00:00 - 2024-04-15 06:00:00 UTC+8  
                **比赛权重** : 24.50  
                **赛事主办** : FITSEC (https://ctftime.org/team/65296)  
                **添加日历** : https://ctftime.org/event/2254.ics  
                
            ??? Quote "[Challenge the Cyber - Cyber Chef](https://challengethecyber.nl/)"  
                [![](https://ctftime.org/media/events/12e936bf3a5de410fc3506bfdffb608a.jpg){ width="200" align=left }](https://challengethecyber.nl/)  
                **比赛名称** : [Challenge the Cyber - Cyber Chef](https://challengethecyber.nl/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-20 19:00:00 - 2024-04-21 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Challenge the Cyber (https://ctftime.org/team/181210)  
                **添加日历** : https://ctftime.org/event/2277.ics  
                
            ??? Quote "[Insomni'hack 2024](https://insomnihack.ch/contests/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://insomnihack.ch/contests/)  
                **比赛名称** : [Insomni'hack 2024](https://insomnihack.ch/contests/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 02:00:00 - 2024-04-27 13:00:00 UTC+8  
                **比赛权重** : 33.40  
                **赛事主办** : Insomni'hack Team (https://ctftime.org/team/104742)  
                **添加日历** : https://ctftime.org/event/2271.ics  
                
            ??? Quote "[LakeCTF Finals 23](https://lakectf.epfl.ch/)"  
                [![](https://ctftime.org/media/events/lakeCTFLogo.png){ width="200" align=left }](https://lakectf.epfl.ch/)  
                **比赛名称** : [LakeCTF Finals 23](https://lakectf.epfl.ch/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-03 16:00:00 - 2024-05-04 00:00:00 UTC+8  
                **比赛权重** : 36.00  
                **赛事主办** : polygl0ts (https://ctftime.org/team/53791)  
                **添加日历** : https://ctftime.org/event/2246.ics  
                
            ??? Quote "[DEF CON CTF Qualifier 2024](https://nautilus.institute/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://nautilus.institute/)  
                **比赛名称** : [DEF CON CTF Qualifier 2024](https://nautilus.institute/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-04 08:00:00 - 2024-05-06 08:00:00 UTC+8  
                **比赛权重** : 77.38  
                **赛事主办** : Nautilus Institute (https://ctftime.org/team/181536)  
                **添加日历** : https://ctftime.org/event/2229.ics  
                
            ??? Quote "[CyberSecurityRumble Quals](https://hacking-meisterschaft.de/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://hacking-meisterschaft.de/)  
                **比赛名称** : [CyberSecurityRumble Quals](https://hacking-meisterschaft.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-11 21:00:00 - 2024-05-12 21:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : RedRocket (https://ctftime.org/team/48677)  
                **添加日历** : https://ctftime.org/event/2224.ics  
                
            ??? Quote "[BYUCTF 2024](https://cyberjousting.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://cyberjousting.com/)  
                **比赛名称** : [BYUCTF 2024](https://cyberjousting.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-17 08:00:00 - 2024-05-19 08:00:00 UTC+8  
                **比赛权重** : 30.75  
                **赛事主办** : BYU Cyberia (https://ctftime.org/team/155711)  
                **添加日历** : https://ctftime.org/event/2252.ics  
                
            ??? Quote "[Black Cell SecOps 2024 - Online Blue Teaming Jeopardy CTF](https://blackcell.io/ctf/)"  
                [![](https://ctftime.org/media/events/SecOps2024_logo.png){ width="200" align=left }](https://blackcell.io/ctf/)  
                **比赛名称** : [Black Cell SecOps 2024 - Online Blue Teaming Jeopardy CTF](https://blackcell.io/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-17 17:00:00 - 2024-05-20 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Black Cell Secops (https://ctftime.org/team/270941)  
                **添加日历** : https://ctftime.org/event/2135.ics  
                
            ??? Quote "[R3CTF/YUANHENGCTF 2024](https://ctf2024.r3kapig.com/)"  
                [![](https://ctftime.org/media/events/r3_logo.png){ width="200" align=left }](https://ctf2024.r3kapig.com/)  
                **比赛名称** : [R3CTF/YUANHENGCTF 2024](https://ctf2024.r3kapig.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 10:00:00 - 2024-05-20 10:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : r3kapig (https://ctftime.org/team/58979)  
                **添加日历** : https://ctftime.org/event/2273.ics  
                
            ??? Quote "[CrewCTF 2024](https://crewc.tf/)"  
                [![](https://ctftime.org/media/events/THC_new.png){ width="200" align=left }](https://crewc.tf/)  
                **比赛名称** : [CrewCTF 2024](https://crewc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-25 01:00:00 - 2024-05-27 01:00:00 UTC+8  
                **比赛权重** : 26.89  
                **赛事主办** : thehackerscrew (https://ctftime.org/team/85618)  
                **添加日历** : https://ctftime.org/event/2223.ics  
                
            ??? Quote "[GPN CTF 2024](https://ctf.kitctf.de/)"  
                [![](https://ctftime.org/media/events/2acc1e50ba516aa0bc42a61798cfa10d.png){ width="200" align=left }](https://ctf.kitctf.de/)  
                **比赛名称** : [GPN CTF 2024](https://ctf.kitctf.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-31 18:00:00 - 2024-06-02 06:00:00 UTC+8  
                **比赛权重** : 31.17  
                **赛事主办** : KITCTF (https://ctftime.org/team/7221)  
                **添加日历** : https://ctftime.org/event/2257.ics  
                
            ??? Quote "[vsCTF 2024](https://ctf.viewsource.me/)"  
                [![](https://ctftime.org/media/events/vsctf_2024_2x.png){ width="200" align=left }](https://ctf.viewsource.me/)  
                **比赛名称** : [vsCTF 2024](https://ctf.viewsource.me/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-01 00:00:00 - 2024-06-03 00:00:00 UTC+8  
                **比赛权重** : 34.00  
                **赛事主办** : View Source (https://ctftime.org/team/175828)  
                **添加日历** : https://ctftime.org/event/2248.ics  
                
            ??? Quote "[AkaSec CTF 2024]()"  
                [![](https://ctftime.org/media/events/akasec_icon-15.png){ width="200" align=left }]()  
                **比赛名称** : [AkaSec CTF 2024]()  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-07 21:37:00 - 2024-06-09 21:37:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : AkaSec (https://ctftime.org/team/107202)  
                **添加日历** : https://ctftime.org/event/2222.ics  
                
            ??? Quote "[Crypto CTF 2024](https://cr.yp.toc.tf/)"  
                [![](https://ctftime.org/media/events/cryptoctf.jpg){ width="200" align=left }](https://cr.yp.toc.tf/)  
                **比赛名称** : [Crypto CTF 2024](https://cr.yp.toc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-08 22:00:00 - 2024-06-09 22:00:00 UTC+8  
                **比赛权重** : 65.62  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2210.ics  
                
            ??? Quote "[Grey Cat The Flag 2024 Finals](https://ctf.nusgreyhats.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.nusgreyhats.org/)  
                **比赛名称** : [Grey Cat The Flag 2024 Finals](https://ctf.nusgreyhats.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-20 10:00:00 - 2024-06-21 18:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : NUSGreyhats (https://ctftime.org/team/16740)  
                **添加日历** : https://ctftime.org/event/2244.ics  
                
            ??? Quote "[Junior.Crypt.2024 CTF](http://ctf-spcs.mf.grsu.by/)"  
                [![](https://ctftime.org/media/events/logo_NY.jpg){ width="200" align=left }](http://ctf-spcs.mf.grsu.by/)  
                **比赛名称** : [Junior.Crypt.2024 CTF](http://ctf-spcs.mf.grsu.by/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-03 23:00:00 - 2024-07-05 23:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Beavers0 (https://ctftime.org/team/269281)  
                **添加日历** : https://ctftime.org/event/2259.ics  
                
            ??? Quote "[SekaiCTF 2024](https://ctf.sekai.team/)"  
                [![](https://ctftime.org/media/events/sekai2_SEKAI_CTF_Square_Black_BG.r_1_1.png){ width="200" align=left }](https://ctf.sekai.team/)  
                **比赛名称** : [SekaiCTF 2024](https://ctf.sekai.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-24 00:00:00 - 2024-08-26 00:00:00 UTC+8  
                **比赛权重** : 36.96  
                **赛事主办** : Project Sekai (https://ctftime.org/team/169557)  
                **添加日历** : https://ctftime.org/event/2243.ics  
                
            ??? Quote "[Pointer Overflow CTF - 2024](http://pointeroverflowctf.com/)"  
                [![](https://ctftime.org/media/events/poctflogo1transp.png){ width="200" align=left }](http://pointeroverflowctf.com/)  
                **比赛名称** : [Pointer Overflow CTF - 2024](http://pointeroverflowctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-15 20:00:00 - 2025-01-19 20:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : UWSP Pointers (https://ctftime.org/team/231536)  
                **添加日历** : https://ctftime.org/event/2121.ics  
                
            ??? Quote "[ASIS CTF Quals 2024](https://asisctf.com/)"  
                [![](https://ctftime.org/media/events/asisctf.jpg){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Quals 2024](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 22:00:00 - 2024-09-22 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2211.ics  
                
            ??? Quote "[TCP1P CTF 2024: Exploring Nusantara's Digital Realm](https://ctf.tcp1p.com/)"  
                [![](https://ctftime.org/media/events/TCP1P-logo.png){ width="200" align=left }](https://ctf.tcp1p.com/)  
                **比赛名称** : [TCP1P CTF 2024: Exploring Nusantara's Digital Realm](https://ctf.tcp1p.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-11 20:00:00 - 2024-10-13 20:00:00 UTC+8  
                **比赛权重** : 24.85  
                **赛事主办** : TCP1P (https://ctftime.org/team/187248)  
                **添加日历** : https://ctftime.org/event/2256.ics  
                
    === "*正在进行*"
        === "国内赛事"
            ??? Quote "[HGAME2024网络攻防大赛](https://hgame.vidar.club)"  
                **比赛名称** : [HGAME2024网络攻防大赛](https://hgame.vidar.club)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年01月20日 20:00 - 2024年02月05日 20:00  
                **比赛时间** : 2024年01月29日 20:00 - 2024年02月27日 20:00  
                **其他说明** : QQ群：134591168   适合新手参加  
                
        === "国外赛事"
            ??? Quote "[Sydbox CTF: read /etc/CTF](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)"  
                [![](https://ctftime.org){ width="200" align=left }](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)  
                **比赛名称** : [Sydbox CTF: read /etc/CTF](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-16 22:26:32 - 2024-11-16 22:26:32 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Exherbo GNU/Linux (https://ctftime.org/team/275214)  
                **添加日历** : https://ctftime.org/event/2178.ics  
                
            ??? Quote "[bi0sCTF 2024](https://ctf.bi0s.in/)"  
                [![](https://ctftime.org/media/events/Untitled-removebg-preview_1.png){ width="200" align=left }](https://ctf.bi0s.in/)  
                **比赛名称** : [bi0sCTF 2024](https://ctf.bi0s.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-24 20:00:00 - 2024-02-26 08:00:00 UTC+8  
                **比赛权重** : 79.83  
                **赛事主办** : bi0s (https://ctftime.org/team/662)  
                **添加日历** : https://ctftime.org/event/2117.ics  
                
    === "*已经结束*"
        === "国内赛事"
            ??? Quote "[第二届数据安全大赛暨首届“数信杯”数据安全大赛](https://shuxinbei.ichunqiu.com/)"  
                **比赛名称** : [第二届数据安全大赛暨首届“数信杯”数据安全大赛](https://shuxinbei.ichunqiu.com/)  
                **比赛类型** : 团队赛|1-3人  
                **报名时间** : 2023年11月15日 00:00 - 2024年01月19日 18:00  
                **比赛时间** : 2024年02月24日 10:00 - 2024年02月24日 18:00  
                **其他说明** : 比赛时间未定  
                
            ??? Quote "[SICTF Round#3](https://yuanshen.life/)"  
                **比赛名称** : [SICTF Round#3](https://yuanshen.life/)  
                **比赛类型** : 团队赛|1-3人  
                **报名时间** : 2024年01月11日 14:00 - 2024年02月18日 09:00  
                **比赛时间** : 2024年02月16日 09:00 - 2024年02月18日 18:00  
                **其他说明** : 比赛QQ群：737732413  本次比赛采用CTF赛制，题目难度两级分化，无论是刚刚入门的萌新还是轻车熟路的大神，都可以快速找到属于你的比赛乐趣哦~  
                
            ??? Quote "[VNCTF 2024](https://vnctf2024.manqiu.top/)"  
                **比赛名称** : [VNCTF 2024](https://vnctf2024.manqiu.top/)  
                **比赛类型** : 个人赛  
                **报名时间** : 2023年02月18日 21:00 - 2024年02月17日 20:00  
                **比赛时间** : 2024年02月17日 08:00 - 2024年02月17日 20:00  
                **其他说明** : V&N 联合战队招新赛，赛事QQ群：717513199  
                
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
            ??? Quote "[BraekerCTF](https://braekerctf.ctfd.io/)"  
                [![](https://ctftime.org/media/events/AI_Robot4.png){ width="200" align=left }](https://braekerctf.ctfd.io/)  
                **比赛名称** : [BraekerCTF](https://braekerctf.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-23 20:00:00 - 2024-02-25 00:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Braeker (https://ctftime.org/team/274910)  
                **添加日历** : https://ctftime.org/event/2181.ics  
                
            ??? Quote "[BroncoCTF 2024](http://broncoctf.xyz/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://broncoctf.xyz/)  
                **比赛名称** : [BroncoCTF 2024](http://broncoctf.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-18 03:00:00 - 2024-02-19 03:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : BroncoSec (https://ctftime.org/team/112673)  
                **添加日历** : https://ctftime.org/event/2261.ics  
                
            ??? Quote "[LA CTF 2024](https://lac.tf/)"  
                [![](https://ctftime.org/media/events/lactf-square-logo_1.png){ width="200" align=left }](https://lac.tf/)  
                **比赛名称** : [LA CTF 2024](https://lac.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-17 12:00:00 - 2024-02-19 06:00:00 UTC+8  
                **比赛权重** : 24.93  
                **赛事主办** : PBR | UCLA (https://ctftime.org/team/186494)  
                **添加日历** : https://ctftime.org/event/2102.ics  
                
            ??? Quote "[SAIBORG - Elite Hacking Competition](https://www.saiborg.io/)"  
                [![](https://ctftime.org/media/events/saiborg-profile.jpg){ width="200" align=left }](https://www.saiborg.io/)  
                **比赛名称** : [SAIBORG - Elite Hacking Competition](https://www.saiborg.io/)  
                **比赛形式** : Hack quest  
                **比赛时间** : 2024-02-16 12:00:00 - 2024-02-16 18:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Saiborg (https://ctftime.org/team/271868)  
                **添加日历** : https://ctftime.org/event/2147.ics  
                
            ??? Quote "[BITSCTF 2024](https://ctf.bitskrieg.org/)"  
                [![](https://ctftime.org/media/events/bitskrieg.jpg){ width="200" align=left }](https://ctf.bitskrieg.org/)  
                **比赛名称** : [BITSCTF 2024](https://ctf.bitskrieg.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-16 02:30:00 - 2024-02-18 02:30:00 UTC+8  
                **比赛权重** : 22.73  
                **赛事主办** : BITSkrieg (https://ctftime.org/team/22310)  
                **添加日历** : https://ctftime.org/event/2235.ics  
                
            ??? Quote "[GoldCTF 2024](https://register.cbsctf.live/)"  
                [![](https://ctftime.org/media/events/Frame_13734128.png){ width="200" align=left }](https://register.cbsctf.live/)  
                **比赛名称** : [GoldCTF 2024](https://register.cbsctf.live/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-02-10 15:00:00 - 2024-02-10 23:00:00 UTC+8  
                **比赛权重** : 24.93  
                **赛事主办** : C4T BuT S4D (https://ctftime.org/team/83435)  
                **添加日历** : https://ctftime.org/event/2249.ics  
                
            ??? Quote "[Ugra CTF Quals 2024](https://2024.ugractf.ru/)"  
                [![](https://ctftime.org/media/events/a5000124fdb12cd1be2c435692b3a8e6.jpg){ width="200" align=left }](https://2024.ugractf.ru/)  
                **比赛名称** : [Ugra CTF Quals 2024](https://2024.ugractf.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-10 15:00:00 - 2024-02-12 03:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : [team Team] (https://ctftime.org/team/49808)  
                **添加日历** : https://ctftime.org/event/2241.ics  
                
            ??? Quote "[0xL4ugh CTF 2024](https://ctf24.0xl4ugh.com/)"  
                [![](https://ctftime.org/media/events/logo_94.png){ width="200" align=left }](https://ctf24.0xl4ugh.com/)  
                **比赛名称** : [0xL4ugh CTF 2024](https://ctf24.0xl4ugh.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-09 21:00:00 - 2024-02-10 21:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : 0xL4ugh (https://ctftime.org/team/132776)  
                **添加日历** : https://ctftime.org/event/2216.ics  
                
            ??? Quote "[Bearcat CTF 2024](https://www.bearcatctf.io/)"  
                [![](https://ctftime.org/media/events/bearcatlogo-cyberatuc.png){ width="200" align=left }](https://www.bearcatctf.io/)  
                **比赛名称** : [Bearcat CTF 2024](https://www.bearcatctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-04 03:00:00 - 2024-02-05 03:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Cyber@UC (https://ctftime.org/team/87727)  
                **添加日历** : https://ctftime.org/event/2208.ics  
                
            ??? Quote "[ESCAPE CTF Final](https://ctf.t3n4ci0us.kr/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.t3n4ci0us.kr/)  
                **比赛名称** : [ESCAPE CTF Final](https://ctf.t3n4ci0us.kr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-03 20:00:00 - 2024-02-04 05:30:00 UTC+8  
                **比赛权重** : 9.64  
                **赛事主办** : CYB3R_T3N4CI0US (https://ctftime.org/team/160305)  
                **添加日历** : https://ctftime.org/event/2213.ics  
                
            ??? Quote "[L3HCTF 2024](https://l3hctf2024.xctf.org.cn/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://l3hctf2024.xctf.org.cn/)  
                **比赛名称** : [L3HCTF 2024](https://l3hctf2024.xctf.org.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-03 09:00:00 - 2024-02-05 09:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : L3H Sec (https://ctftime.org/team/75946)  
                **添加日历** : https://ctftime.org/event/2236.ics  
                
            ??? Quote "[DiceCTF 2024 Quals](https://ctf.dicega.ng/)"  
                [![](https://ctftime.org/media/events/dicectf_2_1.png){ width="200" align=left }](https://ctf.dicega.ng/)  
                **比赛名称** : [DiceCTF 2024 Quals](https://ctf.dicega.ng/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-03 05:00:00 - 2024-02-05 05:00:00 UTC+8  
                **比赛权重** : 54.40  
                **赛事主办** : DiceGang (https://ctftime.org/team/109452)  
                **添加日历** : https://ctftime.org/event/2217.ics  
                
            ??? Quote "[ISSessions Espionage CTF](https://ctf.issessions.ca/)"  
                [![](https://ctftime.org/media/events/unnamed_2.png){ width="200" align=left }](https://ctf.issessions.ca/)  
                **比赛名称** : [ISSessions Espionage CTF](https://ctf.issessions.ca/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-27 22:00:00 - 2024-01-29 06:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ISSesssions (https://ctftime.org/team/278504)  
                **添加日历** : https://ctftime.org/event/2221.ics  
                
            ??? Quote "[TetCTF 2024](https://ctf.hackemall.live/)"  
                [![](https://ctftime.org/media/events/tetlogo.png){ width="200" align=left }](https://ctf.hackemall.live/)  
                **比赛名称** : [TetCTF 2024](https://ctf.hackemall.live/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-27 08:00:00 - 2024-01-29 08:00:00 UTC+8  
                **比赛权重** : 74.41  
                **赛事主办** : TetCTF (https://ctftime.org/team/71781)  
                **添加日历** : https://ctftime.org/event/2212.ics  
                
            ??? Quote "[RCS CTF 24](https://play.encryptedge.in/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://play.encryptedge.in/)  
                **比赛名称** : [RCS CTF 24](https://play.encryptedge.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-26 19:30:00 - 2024-01-27 16:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : EN¢R¥PT_EDGE€ (https://ctftime.org/team/273673)  
                **添加日历** : https://ctftime.org/event/2233.ics  
                
            ??? Quote "[Real World CTF 6th](https://realworldctf.com/)"  
                [![](https://ctftime.org/media/events/rwctf.png){ width="200" align=left }](https://realworldctf.com/)  
                **比赛名称** : [Real World CTF 6th](https://realworldctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-26 19:00:00 - 2024-01-28 19:00:00 UTC+8  
                **比赛权重** : 97.04  
                **赛事主办** : Chaitin Tech (https://ctftime.org/team/60371)  
                **添加日历** : https://ctftime.org/event/2172.ics  
                
            ??? Quote "[4N0NYM0US3 2024](http://ctf.appinprogress.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://ctf.appinprogress.com/)  
                **比赛名称** : [4N0NYM0US3 2024](http://ctf.appinprogress.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-21 13:04:43 - 2024-01-21 13:04:43 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : WyteHat (https://ctftime.org/team/231105)  
                **添加日历** : https://ctftime.org/event/2232.ics  
                
            ??? Quote "[KnightCTF 2024](https://knightctf.com/)"  
                [![](https://ctftime.org/media/events/KnightCTF.png){ width="200" align=left }](https://knightctf.com/)  
                **比赛名称** : [KnightCTF 2024](https://knightctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-20 23:00:00 - 2024-01-21 23:00:00 UTC+8  
                **比赛权重** : 6.65  
                **赛事主办** : Knight Squad (https://ctftime.org/team/141739)  
                **添加日历** : https://ctftime.org/event/2209.ics  
                
            ??? Quote "[Mapna CTF 2024](https://mapnactf.com/)"  
                [![](https://ctftime.org/media/events/MAPNA.jpg){ width="200" align=left }](https://mapnactf.com/)  
                **比赛名称** : [Mapna CTF 2024](https://mapnactf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-20 23:00:00 - 2024-01-21 23:00:00 UTC+8  
                **比赛权重** : 24.53  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2205.ics  
                
            ??? Quote "[Insomni'hack teaser 2024](https://teaser.insomnihack.ch/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://teaser.insomnihack.ch/)  
                **比赛名称** : [Insomni'hack teaser 2024](https://teaser.insomnihack.ch/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-20 17:00:00 - 2024-01-21 17:00:00 UTC+8  
                **比赛权重** : 32.00  
                **赛事主办** : Insomni'hack Team (https://ctftime.org/team/104742)  
                **添加日历** : https://ctftime.org/event/2139.ics  
                
            ??? Quote "[HKUST Firebird CTF Competition 2024](http://ctf.firebird.sh/)"  
                [![](https://ctftime.org/media/events/FirebirdCTFCompetition2.png){ width="200" align=left }](http://ctf.firebird.sh/)  
                **比赛名称** : [HKUST Firebird CTF Competition 2024](http://ctf.firebird.sh/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-20 10:00:00 - 2024-01-21 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HKUSTFirebird (https://ctftime.org/team/65249)  
                **添加日历** : https://ctftime.org/event/2225.ics  
                
            ??? Quote "[UofTCTF 2024](https://ctf.uoftctf.org/)"  
                [![](https://ctftime.org/media/events/ctf_logo_1.png){ width="200" align=left }](https://ctf.uoftctf.org/)  
                **比赛名称** : [UofTCTF 2024](https://ctf.uoftctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-14 01:00:00 - 2024-01-15 12:59:00 UTC+8  
                **比赛权重** : 23.52  
                **赛事主办** : UofTCTF (https://ctftime.org/team/139261)  
                **添加日历** : https://ctftime.org/event/2219.ics  
                
            ??? Quote "[IrisCTF 2024](https://2024.irisc.tf/)"  
                [![](https://ctftime.org/media/events/IrisCTF_Logo.png){ width="200" align=left }](https://2024.irisc.tf/)  
                **比赛名称** : [IrisCTF 2024](https://2024.irisc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-06 08:00:00 - 2024-01-08 08:00:00 UTC+8  
                **比赛权重** : 24.59  
                **赛事主办** : IrisSec (https://ctftime.org/team/127034)  
                **添加日历** : https://ctftime.org/event/2085.ics  
                
            ??? Quote "[Shaastra CTF '24](https://ctf.shaastractf2024.online/)"  
                [![](https://ctftime.org/media/events/Shaastralogo.png){ width="200" align=left }](https://ctf.shaastractf2024.online/)  
                **比赛名称** : [Shaastra CTF '24](https://ctf.shaastractf2024.online/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-04 16:30:00 - 2024-01-04 18:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ShaastraCTF2024 (https://ctftime.org/team/276568)  
                **添加日历** : https://ctftime.org/event/2220.ics  
                
            ??? Quote "[New Year CTF 2024](http://ctf-spcs.mf.grsu.by/)"  
                [![](https://ctftime.org/media/events/logo_25_2.png){ width="200" align=left }](http://ctf-spcs.mf.grsu.by/)  
                **比赛名称** : [New Year CTF 2024](http://ctf-spcs.mf.grsu.by/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-31 01:00:00 - 2024-01-15 05:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Beavers0 (https://ctftime.org/team/269281)  
                **添加日历** : https://ctftime.org/event/2218.ics  
                
            ??? Quote "[ASIS CTF Finals 2023](https://asisctf.com/)"  
                [![](https://ctftime.org/media/events/asis_logo_512_2.png){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Finals 2023](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-29 22:30:00 - 2023-12-30 22:30:00 UTC+8  
                **比赛权重** : 83.00  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/1953.ics  
                
            ??? Quote "[37C3 Potluck CTF](https://potluckctf.com/)"  
                [![](https://ctftime.org/media/events/logo-512-white.png){ width="200" align=left }](https://potluckctf.com/)  
                **比赛名称** : [37C3 Potluck CTF](https://potluckctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-29 02:00:00 - 2023-12-30 02:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ZetaTwo (https://ctftime.org/team/9407)  
                **添加日历** : https://ctftime.org/event/2199.ics  
                
            ??? Quote "[Code X Sport Jung'23 CTF](http://kiet-intra-ctf.site/)"  
                [![](https://ctftime.org/media/events/event_logo.jpeg){ width="200" align=left }](http://kiet-intra-ctf.site/)  
                **比赛名称** : [Code X Sport Jung'23 CTF](http://kiet-intra-ctf.site/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-23 13:30:00 - 2023-12-23 16:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : cornered_tiger (https://ctftime.org/team/216139)  
                **添加日历** : https://ctftime.org/event/2215.ics  
                
            ??? Quote "[SECCON CTF 2023 Domestic Finals](https://ctf.seccon.jp/)"  
                [![](https://ctftime.org/media/events/seccon_s_6.png){ width="200" align=left }](https://ctf.seccon.jp/)  
                **比赛名称** : [SECCON CTF 2023 Domestic Finals](https://ctf.seccon.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-23 09:00:00 - 2023-12-24 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SECCON CTF (https://ctftime.org/team/11918)  
                **添加日历** : https://ctftime.org/event/2160.ics  
                
            ??? Quote "[SECCON CTF 2023 International Finals](https://ctf.seccon.jp/)"  
                [![](https://ctftime.org/media/events/seccon_s_5.png){ width="200" align=left }](https://ctf.seccon.jp/)  
                **比赛名称** : [SECCON CTF 2023 International Finals](https://ctf.seccon.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-23 09:00:00 - 2023-12-24 17:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : SECCON CTF (https://ctftime.org/team/11918)  
                **添加日历** : https://ctftime.org/event/2159.ics  
                
            ??? Quote "[niteCTF](http://nitectf.live/)"  
                [![](https://ctftime.org/media/events/WhatsApp_Image_2021-08-06_at_11.28.13_2.jpeg){ width="200" align=left }](http://nitectf.live/)  
                **比赛名称** : [niteCTF](http://nitectf.live/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-17 19:30:00 - 2023-12-19 19:30:00 UTC+8  
                **比赛权重** : 24.00  
                **赛事主办** : Cryptonite (https://ctftime.org/team/62713)  
                **添加日历** : https://ctftime.org/event/2207.ics  
                
            ??? Quote "[1st Annual TCM Invitational CTF](https://www.tcm.rocks/TCM2023CTF)"  
                [![](https://ctftime.org/media/events/tcm-logo-small.png){ width="200" align=left }](https://www.tcm.rocks/TCM2023CTF)  
                **比赛名称** : [1st Annual TCM Invitational CTF](https://www.tcm.rocks/TCM2023CTF)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-16 23:00:00 - 2023-12-17 07:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : TCM Security (https://ctftime.org/team/275972)  
                **添加日历** : https://ctftime.org/event/2201.ics  
                
            ??? Quote "[BackdoorCTF 2023](https://backdoor.infoseciitr.in/)"  
                [![](https://ctftime.org/media/events/bckdr.png){ width="200" align=left }](https://backdoor.infoseciitr.in/)  
                **比赛名称** : [BackdoorCTF 2023](https://backdoor.infoseciitr.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-16 20:00:00 - 2023-12-18 20:00:00 UTC+8  
                **比赛权重** : 34.00  
                **赛事主办** : InfoSecIITR (https://ctftime.org/team/16691)  
                **添加日历** : https://ctftime.org/event/2153.ics  
                
            ??? Quote "[DiceCTF Teaser 2023](https://ctf.dicega.ng/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.dicega.ng/)  
                **比赛名称** : [DiceCTF Teaser 2023](https://ctf.dicega.ng/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-16 05:00:00 - 2023-12-17 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : DiceGang (https://ctftime.org/team/109452)  
                **添加日历** : https://ctftime.org/event/2162.ics  
                
            ??? Quote "[Wargames.MY CTF 2023](https://pro2023.wargames.my/)"  
                [![](https://ctftime.org/media/events/wgmy2023_logo.png){ width="200" align=left }](https://pro2023.wargames.my/)  
                **比赛名称** : [Wargames.MY CTF 2023](https://pro2023.wargames.my/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-16 00:00:00 - 2023-12-17 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Wargames.MY (https://ctftime.org/team/86069)  
                **添加日历** : https://ctftime.org/event/2203.ics  
                
            ??? Quote "[The Cyber Cooperative CTF](https://thecybercoopctf.ctfd.io/)"  
                [![](https://ctftime.org/media/events/logo_servericon.png){ width="200" align=left }](https://thecybercoopctf.ctfd.io/)  
                **比赛名称** : [The Cyber Cooperative CTF](https://thecybercoopctf.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-15 13:01:01 - 2023-12-18 12:59:00 UTC+8  
                **比赛权重** : 24.21  
                **赛事主办** : The Cyber Cooperative (https://ctftime.org/team/276494)  
                **添加日历** : https://ctftime.org/event/2206.ics  
                
            ??? Quote "[7th Stage MetaRed TIC Portugal 2023](http://eventos.metared.org/go/CTFMetaRed2023-7thSTAGE)"  
                [![](https://ctftime.org){ width="200" align=left }](http://eventos.metared.org/go/CTFMetaRed2023-7thSTAGE)  
                **比赛名称** : [7th Stage MetaRed TIC Portugal 2023](http://eventos.metared.org/go/CTFMetaRed2023-7thSTAGE)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-14 21:00:00 - 2023-12-15 21:00:00 UTC+8  
                **比赛权重** : 6.67  
                **赛事主办** : UAC (https://ctftime.org/team/140846)  
                **添加日历** : https://ctftime.org/event/2099.ics  
                
            ??? Quote "[IWCON CTF](https://iwcon.live/ctf)"  
                [![](https://ctftime.org){ width="200" align=left }](https://iwcon.live/ctf)  
                **比赛名称** : [IWCON CTF](https://iwcon.live/ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-14 18:26:53 - 2023-12-15 18:26:53 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : IWCON (https://ctftime.org/team/277281)  
                **添加日历** : https://ctftime.org/event/2214.ics  
                
            ??? Quote "[Intent CTF 2023](https://intentsummit.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://intentsummit.org/)  
                **比赛名称** : [Intent CTF 2023](https://intentsummit.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-13 16:30:00 - 2023-12-15 16:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Security Research Summit (SRS) (https://ctftime.org/team/163107)  
                **添加日历** : https://ctftime.org/event/2130.ics  
                
            ??? Quote "[HACKOLINE](https://mrwebx.com/event/#/home)"  
                [![](https://ctftime.org/media/events/instagram.jpeg){ width="200" align=left }](https://mrwebx.com/event/#/home)  
                **比赛名称** : [HACKOLINE](https://mrwebx.com/event/#/home)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-12-10 17:00:00 - 2023-12-11 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : mrwebsecure (https://ctftime.org/team/276542)  
                **添加日历** : https://ctftime.org/event/2204.ics  
                
            ??? Quote "[ISITDTU CTF 2023 Finals](https://ctf.isitdtu.com/)"  
                [![](https://ctftime.org/media/events/index_1.gif){ width="200" align=left }](https://ctf.isitdtu.com/)  
                **比赛名称** : [ISITDTU CTF 2023 Finals](https://ctf.isitdtu.com/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-12-10 09:00:00 - 2023-12-10 17:00:00 UTC+8  
                **比赛权重** : 37.00  
                **赛事主办** : ISITDTU (https://ctftime.org/team/8241)  
                **添加日历** : https://ctftime.org/event/2090.ics  
                
            ??? Quote "[HacktorX CTF 2023](https://hacktorx.com/hxctf2023/)"  
                [![](https://ctftime.org/media/events/logo1_2.png){ width="200" align=left }](https://hacktorx.com/hxctf2023/)  
                **比赛名称** : [HacktorX CTF 2023](https://hacktorx.com/hxctf2023/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-09 21:00:00 - 2023-12-10 15:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HacktorX (https://ctftime.org/team/274645)  
                **添加日历** : https://ctftime.org/event/2174.ics  
                
            ??? Quote "[snakeCTF 2023](https://2023.snakectf.org/)"  
                [![](https://ctftime.org/media/events/LogoCroppable.png){ width="200" align=left }](https://2023.snakectf.org/)  
                **比赛名称** : [snakeCTF 2023](https://2023.snakectf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-09 17:00:00 - 2023-12-10 17:00:00 UTC+8  
                **比赛权重** : 24.79  
                **赛事主办** : MadrHacks (https://ctftime.org/team/114509)  
                **添加日历** : https://ctftime.org/event/2158.ics  
                
            ??? Quote "[TsukuCTF 2023](http://tsukuctf.sechack365.com/)"  
                [![](https://ctftime.org/media/events/icon_6.png){ width="200" align=left }](http://tsukuctf.sechack365.com/)  
                **比赛名称** : [TsukuCTF 2023](http://tsukuctf.sechack365.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-09 11:20:00 - 2023-12-10 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : TaruTaru (https://ctftime.org/team/157513)  
                **添加日历** : https://ctftime.org/event/2169.ics  
                
            ??? Quote "[0CTF/TCTF 2023](https://ctf.0ops.sjtu.cn/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.0ops.sjtu.cn/)  
                **比赛名称** : [0CTF/TCTF 2023](https://ctf.0ops.sjtu.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-09 10:00:00 - 2023-12-11 10:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : 0ops (https://ctftime.org/team/4419)  
                **添加日历** : https://ctftime.org/event/2073.ics  
                
            ??? Quote "[pingCTF 2023](https://ctf.knping.pl/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.knping.pl/)  
                **比赛名称** : [pingCTF 2023](https://ctf.knping.pl/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-09 01:30:00 - 2023-12-11 06:00:00 UTC+8  
                **比赛权重** : 24.29  
                **赛事主办** : pingCTF (https://ctftime.org/team/147266)  
                **添加日历** : https://ctftime.org/event/1987.ics  
                
            ??? Quote "[HTB University CTF 2023: Brains & Bytes](https://ctf.hackthebox.com/event/details/university-ctf-2023-brains-bytes-1231)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hackthebox.com/event/details/university-ctf-2023-brains-bytes-1231)  
                **比赛名称** : [HTB University CTF 2023: Brains & Bytes](https://ctf.hackthebox.com/event/details/university-ctf-2023-brains-bytes-1231)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-08 21:00:00 - 2023-12-11 05:00:00 UTC+8  
                **比赛权重** : 23.21  
                **赛事主办** : Hack The Box (https://ctftime.org/team/136056)  
                **添加日历** : https://ctftime.org/event/2149.ics  
                
            ??? Quote "[Hackappatoi CTF '23](https://hctf.hackappatoi.com/)"  
                [![](https://ctftime.org/media/events/3cea5d7bcded4dcba103009b24246cd6.png){ width="200" align=left }](https://hctf.hackappatoi.com/)  
                **比赛名称** : [Hackappatoi CTF '23](https://hctf.hackappatoi.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-08 01:00:00 - 2023-12-09 17:00:00 UTC+8  
                **比赛权重** : 24.71  
                **赛事主办** : Hackappatoi (https://ctftime.org/team/140428)  
                **添加日历** : https://ctftime.org/event/2163.ics  
                
            ??? Quote "[HUNTING SEASON: GROUP-IB 20TH ANNIVERSARY CTF](https://go.group-ib.com/ctf-2023?utm_source=&utm_campaign=ctf-2023&utm_medium=&utm_content=ctftime)"  
                [![](https://ctftime.org/media/events/InstaTelega__1080x1080_12.png){ width="200" align=left }](https://go.group-ib.com/ctf-2023?utm_source=&utm_campaign=ctf-2023&utm_medium=&utm_content=ctftime)  
                **比赛名称** : [HUNTING SEASON: GROUP-IB 20TH ANNIVERSARY CTF](https://go.group-ib.com/ctf-2023?utm_source=&utm_campaign=ctf-2023&utm_medium=&utm_content=ctftime)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-07 17:00:00 - 2023-12-07 21:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Group-IB (https://ctftime.org/team/273085)  
                **添加日历** : https://ctftime.org/event/2177.ics  
                
            ??? Quote "[M*CTF 2023 Finals](https://mctf.mtuci.ru/)"  
                [![](https://ctftime.org/media/events/Immagine_PNG_2.png){ width="200" align=left }](https://mctf.mtuci.ru/)  
                **比赛名称** : [M*CTF 2023 Finals](https://mctf.mtuci.ru/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-12-03 15:00:00 - 2023-12-04 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2198.ics  
                
            ??? Quote "[M*CTF 2023 Junior Finals](https://mctf.mtuci.ru/)"  
                [![](https://ctftime.org/media/events/Immagine_PNG_1.png){ width="200" align=left }](https://mctf.mtuci.ru/)  
                **比赛名称** : [M*CTF 2023 Junior Finals](https://mctf.mtuci.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-02 15:00:00 - 2023-12-02 23:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2197.ics  
                
            ??? Quote "[WannaGame Championship 2023](https://cnsc.uit.edu.vn/ctf/)"  
                [![](https://ctftime.org/media/events/405223021_1146746909620738_23415812653969977_n.png){ width="200" align=left }](https://cnsc.uit.edu.vn/ctf/)  
                **比赛名称** : [WannaGame Championship 2023](https://cnsc.uit.edu.vn/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-02 09:00:00 - 2023-12-04 09:00:00 UTC+8  
                **比赛权重** : 19.80  
                **赛事主办** : Wanna.W1n (https://ctftime.org/team/138431)  
                **添加日历** : https://ctftime.org/event/2146.ics  
                
            ??? Quote "[NewportBlakeCTF 2023](https://nbctf.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://nbctf.com/)  
                **比赛名称** : [NewportBlakeCTF 2023](https://nbctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-02 08:00:00 - 2023-12-04 08:00:00 UTC+8  
                **比赛权重** : 24.67  
                **赛事主办** : NewportBlakeCTF (https://ctftime.org/team/258029)  
                **添加日历** : https://ctftime.org/event/2072.ics  
                
            ??? Quote "[CTF Internacional MetaRed 2023 - 6th STAGE](https://ctfhn.unitec.edu/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctfhn.unitec.edu/)  
                **比赛名称** : [CTF Internacional MetaRed 2023 - 6th STAGE](https://ctfhn.unitec.edu/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-02 03:00:00 - 2023-12-03 02:59:00 UTC+8  
                **比赛权重** : 6.67  
                **赛事主办** : MiTeam (https://ctftime.org/team/168552)  
                **添加日历** : https://ctftime.org/event/2202.ics  
                
            ??? Quote "[BlazCTF 2023](https://ctf.blaz.ai/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.blaz.ai/)  
                **比赛名称** : [BlazCTF 2023](https://ctf.blaz.ai/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-02 02:00:00 - 2023-12-04 02:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : FuzzLand (https://ctftime.org/team/270659)  
                **添加日历** : https://ctftime.org/event/2145.ics  
                
            ??? Quote "[TUCTF 2023](https://tuctf.com/)"  
                [![](https://ctftime.org/media/events/tuctf_small.png){ width="200" align=left }](https://tuctf.com/)  
                **比赛名称** : [TUCTF 2023](https://tuctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-02 01:00:00 - 2023-12-04 01:00:00 UTC+8  
                **比赛权重** : 22.07  
                **赛事主办** : ascii overflow (https://ctftime.org/team/15360)  
                **添加日历** : https://ctftime.org/event/2173.ics  
                
            ??? Quote "[BSides Odisha Web3 CTF](https://academy.quillaudits.com/challenges)"  
                [![](https://ctftime.org/media/events/Neon_Blue_and_Black_Gamer_Badge_Logo.png){ width="200" align=left }](https://academy.quillaudits.com/challenges)  
                **比赛名称** : [BSides Odisha Web3 CTF](https://academy.quillaudits.com/challenges)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-01 04:00:00 - 2023-12-02 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BSides Odisha (https://ctftime.org/team/274130)  
                **添加日历** : https://ctftime.org/event/2180.ics  
                
            ??? Quote "[m0leCon CTF 2023](https://finals.m0lecon.it/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://finals.m0lecon.it/)  
                **比赛名称** : [m0leCon CTF 2023](https://finals.m0lecon.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-12-01 01:00:00 - 2023-12-02 01:00:00 UTC+8  
                **比赛权重** : 50.00  
                **赛事主办** : pwnthem0le (https://ctftime.org/team/60467)  
                **添加日历** : https://ctftime.org/event/2033.ics  
                
            ??? Quote "[m0leCon Beginner CTF 2023](https://beginner.m0lecon.it/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://beginner.m0lecon.it/)  
                **比赛名称** : [m0leCon Beginner CTF 2023](https://beginner.m0lecon.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-25 21:00:00 - 2023-11-26 02:00:00 UTC+8  
                **比赛权重** : 50.00  
                **赛事主办** : pwnthem0le (https://ctftime.org/team/60467)  
                **添加日历** : https://ctftime.org/event/2170.ics  
                
            ??? Quote "[Ph0wn 2023](https://ph0wn.org/)"  
                [![](https://ctftime.org/media/events/logo-ph0wn_4.png){ width="200" align=left }](https://ph0wn.org/)  
                **比赛名称** : [Ph0wn 2023](https://ph0wn.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-25 18:00:00 - 2023-11-26 02:00:00 UTC+8  
                **比赛权重** : 18.00  
                **赛事主办** : Pic0wn (https://ctftime.org/team/6514)  
                **添加日历** : https://ctftime.org/event/2168.ics  
                
            ??? Quote "[CTFZone 2023 Final](http://ctf.bi.zone/)"  
                [![](https://ctftime.org/media/events/logo2_6.png){ width="200" align=left }](http://ctf.bi.zone/)  
                **比赛名称** : [CTFZone 2023 Final](http://ctf.bi.zone/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-11-25 17:00:00 - 2023-11-26 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BIZone (https://ctftime.org/team/32190)  
                **添加日历** : https://ctftime.org/event/2131.ics  
                
            ??? Quote "[TPCTF 2023](https://tpctf2023.xctf.org.cn/)"  
                [![](https://ctftime.org/media/events/TPCTF_ba-stylenulla.top.png){ width="200" align=left }](https://tpctf2023.xctf.org.cn/)  
                **比赛名称** : [TPCTF 2023](https://tpctf2023.xctf.org.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-25 09:00:00 - 2023-11-27 09:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : TP-Link (https://ctftime.org/team/273760)  
                **添加日历** : https://ctftime.org/event/2161.ics  
                
            ??? Quote "[GlacierCTF 2023](https://glacierctf.com/)"  
                [![](https://ctftime.org/media/events/3ae6516246966c8d08c81d3bd5451cfa.png){ width="200" align=left }](https://glacierctf.com/)  
                **比赛名称** : [GlacierCTF 2023](https://glacierctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-25 02:00:00 - 2023-11-27 02:00:00 UTC+8  
                **比赛权重** : 24.32  
                **赛事主办** : LosFuzzys (https://ctftime.org/team/8323)  
                **添加日历** : https://ctftime.org/event/1992.ics  
                
            ??? Quote "[DefCamp CTF Finals 2023](https://dctf23-ad.cyber-edu.co/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://dctf23-ad.cyber-edu.co/)  
                **比赛名称** : [DefCamp CTF Finals 2023](https://dctf23-ad.cyber-edu.co/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-11-23 16:00:00 - 2023-11-24 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CCSIR.org (https://ctftime.org/team/9831)  
                **添加日历** : https://ctftime.org/event/2182.ics  
                
            ??? Quote "[ASEAN Cyber Shield Hacking Contest 2023 (Main)](https://forms.gle/9KcV5WRAutbQqHn48)"  
                [![](https://ctftime.org/media/events/square.png){ width="200" align=left }](https://forms.gle/9KcV5WRAutbQqHn48)  
                **比赛名称** : [ASEAN Cyber Shield Hacking Contest 2023 (Main)](https://forms.gle/9KcV5WRAutbQqHn48)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-11-23 10:00:00 - 2023-11-24 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ASEAN Cyber Shield (https://ctftime.org/team/269126)  
                **添加日历** : https://ctftime.org/event/2148.ics  
                
            ??? Quote "[5th stage MetaRed CTF Ecuador 2023](https://eventos.metared.org/101614/detail/ctf-internacional-metared-2023-5th-stage.html)"  
                [![](https://ctftime.org/media/events/Log.png){ width="200" align=left }](https://eventos.metared.org/101614/detail/ctf-internacional-metared-2023-5th-stage.html)  
                **比赛名称** : [5th stage MetaRed CTF Ecuador 2023](https://eventos.metared.org/101614/detail/ctf-internacional-metared-2023-5th-stage.html)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-21 23:00:00 - 2023-11-22 22:59:59 UTC+8  
                **比赛权重** : 6.67  
                **赛事主办** : MiTeam (https://ctftime.org/team/168552)  
                **添加日历** : https://ctftime.org/event/2164.ics  
                
            ??? Quote "[ASEAN Cyber Shield Hacking Contest 2023 (Preliminary)](https://forms.gle/9KcV5WRAutbQqHn48)"  
                [![](https://ctftime.org){ width="200" align=left }](https://forms.gle/9KcV5WRAutbQqHn48)  
                **比赛名称** : [ASEAN Cyber Shield Hacking Contest 2023 (Preliminary)](https://forms.gle/9KcV5WRAutbQqHn48)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-21 14:00:00 - 2023-11-22 19:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ASEAN Cyber Shield (https://ctftime.org/team/269126)  
                **添加日历** : https://ctftime.org/event/2127.ics  
                
            ??? Quote "[SibirCTF 2023](https://vk.com/sibirctf)"  
                [![](https://ctftime.org/media/events/glaz2023.jpg){ width="200" align=left }](https://vk.com/sibirctf)  
                **比赛名称** : [SibirCTF 2023](https://vk.com/sibirctf)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-11-19 18:00:00 - 2023-11-20 03:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : keva (https://ctftime.org/team/2980)  
                **添加日历** : https://ctftime.org/event/2132.ics  
                
            ??? Quote "[CyberSci Regional Qualifiers 2023-24](https://CyberSci.ca/)"  
                [![](https://ctftime.org/media/events/f064d8074a08720a1fceac259a831e7e.png){ width="200" align=left }](https://CyberSci.ca/)  
                **比赛名称** : [CyberSci Regional Qualifiers 2023-24](https://CyberSci.ca/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-19 00:00:00 - 2023-11-19 07:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CyberSciOrganizers (https://ctftime.org/team/157536)  
                **添加日历** : https://ctftime.org/event/2171.ics  
                
            ??? Quote "[saarCTF 2023](https://ctf.saarland/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.saarland/)  
                **比赛名称** : [saarCTF 2023](https://ctf.saarland/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-11-18 21:00:00 - 2023-11-19 06:00:00 UTC+8  
                **比赛权重** : 90.62  
                **赛事主办** : saarsec (https://ctftime.org/team/15337)  
                **添加日历** : https://ctftime.org/event/2049.ics  
                
            ??? Quote "[isfcr{ctf} 2023](https://isfcr.ctfd.io/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://isfcr.ctfd.io/)  
                **比赛名称** : [isfcr{ctf} 2023](https://isfcr.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-18 18:30:00 - 2023-11-19 18:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ISFCR PESU (https://ctftime.org/team/166645)  
                **添加日历** : https://ctftime.org/event/2167.ics  
                
            ??? Quote "[MUST CTF Qualifier 2023](https://ctf.ccs-security.club/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.ccs-security.club/)  
                **比赛名称** : [MUST CTF Qualifier 2023](https://ctf.ccs-security.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-18 12:00:00 - 2023-11-18 16:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Computer&Communication Security Club (https://ctftime.org/team/274658)  
                **添加日历** : https://ctftime.org/event/2175.ics  
                
            ??? Quote "[Square CTF 2023](https://squarectf.com/)"  
                [![](https://ctftime.org/media/events/flagv4_edited-svg_1.png){ width="200" align=left }](https://squarectf.com/)  
                **比赛名称** : [Square CTF 2023](https://squarectf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-18 02:00:00 - 2023-11-19 02:00:00 UTC+8  
                **比赛权重** : 40.71  
                **赛事主办** : Square (https://ctftime.org/team/46747)  
                **添加日历** : https://ctftime.org/event/2111.ics  
                
            ??? Quote "[1337UP LIVE CTF](https://ctf.intigriti.io/)"  
                [![](https://ctftime.org/media/events/1337up_4.png){ width="200" align=left }](https://ctf.intigriti.io/)  
                **比赛名称** : [1337UP LIVE CTF](https://ctf.intigriti.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-17 19:59:59 - 2023-11-19 07:59:59 UTC+8  
                **比赛权重** : 24.23  
                **赛事主办** : Intigriti (https://ctftime.org/team/178083)  
                **添加日历** : https://ctftime.org/event/2134.ics  
                
            ??? Quote "[Die Abenteuer von KIM & TIM - Kapt. I - Mission (K)IMpossible](https://ctfd.gematik.de/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctfd.gematik.de/)  
                **比赛名称** : [Die Abenteuer von KIM & TIM - Kapt. I - Mission (K)IMpossible](https://ctfd.gematik.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-17 16:00:00 - 2023-11-18 00:00:10 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : H34lthineer (https://ctftime.org/team/170109)  
                **添加日历** : https://ctftime.org/event/2070.ics  
                
            ??? Quote "[BlackHat MEA CTF Final 2023](https://blackhatmea.com/capture-the-flag)"  
                [![](https://ctftime.org/media/events/e0c283c95f7b0db516dae505d31ca20b_1.jpg){ width="200" align=left }](https://blackhatmea.com/capture-the-flag)  
                **比赛名称** : [BlackHat MEA CTF Final 2023](https://blackhatmea.com/capture-the-flag)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-14 15:00:00 - 2023-11-16 22:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SAFCSP (https://ctftime.org/team/54707)  
                **添加日历** : https://ctftime.org/event/2113.ics  
                
            ??? Quote "[HITCON CTF 2023 Final](http://ctf.hitcon.org/)"  
                [![](https://ctftime.org/media/events/hitcon2_5_1_2.png){ width="200" align=left }](http://ctf.hitcon.org/)  
                **比赛名称** : [HITCON CTF 2023 Final](http://ctf.hitcon.org/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-11-14 08:00:00 - 2023-11-15 16:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : HITCON (https://ctftime.org/team/8299)  
                **添加日历** : https://ctftime.org/event/2035.ics  
                
            ??? Quote "[M*CTF 2023 Quals](https://mctf.mtuci.ru/)"  
                [![](https://ctftime.org/media/events/GRuJspCP73s.jpg){ width="200" align=left }](https://mctf.mtuci.ru/)  
                **比赛名称** : [M*CTF 2023 Quals](https://mctf.mtuci.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-11 19:00:00 - 2023-11-12 19:00:00 UTC+8  
                **比赛权重** : 23.92  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2096.ics  
                
            ??? Quote "[BRICS+ CTF Finals 2023](https://brics-ctf.ru/)"  
                [![](https://ctftime.org/media/events/br2_1.png){ width="200" align=left }](https://brics-ctf.ru/)  
                **比赛名称** : [BRICS+ CTF Finals 2023](https://brics-ctf.ru/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-11-11 18:00:00 - 2023-11-12 02:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ITMO FSIT (https://ctftime.org/team/264636)  
                **添加日历** : https://ctftime.org/event/2128.ics  
                
            ??? Quote "[Equinor CTF](https://ctf.equinor.com/)"  
                [![](https://ctftime.org/media/events/ept.png){ width="200" align=left }](https://ctf.equinor.com/)  
                **比赛名称** : [Equinor CTF](https://ctf.equinor.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-11 17:00:00 - 2023-11-12 03:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : EPT (https://ctftime.org/team/119480)  
                **添加日历** : https://ctftime.org/event/2109.ics  
                
            ??? Quote "[USC CTF — Fall 2023](https://usc.pwn.day/)"  
                [![](https://ctftime.org/media/events/ctflogo_1.png){ width="200" align=left }](https://usc.pwn.day/)  
                **比赛名称** : [USC CTF — Fall 2023](https://usc.pwn.day/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-11 16:00:00 - 2023-11-13 16:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : trojan pwnies (https://ctftime.org/team/217061)  
                **添加日历** : https://ctftime.org/event/2166.ics  
                
            ??? Quote "[Cybercoliseum II](https://cybercoliseum.codeby.games/en)"  
                [![](https://ctftime.org/media/events/asd.png){ width="200" align=left }](https://cybercoliseum.codeby.games/en)  
                **比赛名称** : [Cybercoliseum II](https://cybercoliseum.codeby.games/en)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-11 15:00:00 - 2023-11-13 15:00:00 UTC+8  
                **比赛权重** : 20.95  
                **赛事主办** : RedHazzarTeam (https://ctftime.org/team/186788)  
                **添加日历** : https://ctftime.org/event/2100.ics  
                
            ??? Quote "[CakeCTF 2023](https://2023.cakectf.com/)"  
                [![](https://ctftime.org/media/events/neko.e0c2a45acc10cf9f42e3c3cb9f3e45fe.png){ width="200" align=left }](https://2023.cakectf.com/)  
                **比赛名称** : [CakeCTF 2023](https://2023.cakectf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-11 13:00:00 - 2023-11-12 13:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : insecure (https://ctftime.org/team/21761)  
                **添加日历** : https://ctftime.org/event/1973.ics  
                
            ??? Quote "[WannaGame Freshman 2023](https://cnsc.uit.edu.vn/ctf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://cnsc.uit.edu.vn/ctf/)  
                **比赛名称** : [WannaGame Freshman 2023](https://cnsc.uit.edu.vn/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-11 09:00:00 - 2023-11-11 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Wanna.W1n (https://ctftime.org/team/138431)  
                **添加日历** : https://ctftime.org/event/2155.ics  
                
            ??? Quote "[CSAW CTF Final Round 2023](https://ctf.csaw.io/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.csaw.io/)  
                **比赛名称** : [CSAW CTF Final Round 2023](https://ctf.csaw.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-11 00:00:00 - 2023-11-12 12:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : NYUSEC (https://ctftime.org/team/439)  
                **添加日历** : https://ctftime.org/event/2091.ics  
                
            ??? Quote "[Bambi CTF #9](https://bambi9.enoflag.de/)"  
                [![](https://ctftime.org/media/events/reh.png){ width="200" align=left }](https://bambi9.enoflag.de/)  
                **比赛名称** : [Bambi CTF #9](https://bambi9.enoflag.de/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-11-11 00:00:00 - 2023-11-11 07:00:00 UTC+8  
                **比赛权重** : 50.00  
                **赛事主办** : ENOFLAG (https://ctftime.org/team/1438)  
                **添加日历** : https://ctftime.org/event/2150.ics  
                
            ??? Quote "[HK Cyber Security New Generation CTF Challenge 2023 (Online)](https://ctf.hkcert.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hkcert.org/)  
                **比赛名称** : [HK Cyber Security New Generation CTF Challenge 2023 (Online)](https://ctf.hkcert.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-10 18:00:00 - 2023-11-12 18:00:00 UTC+8  
                **比赛权重** : 55.00  
                **赛事主办** : Black Bauhinia, HKCERT (https://ctftime.org/team/83678, https://ctftime.org/team/134746)  
                **添加日历** : https://ctftime.org/event/2122.ics  
                
            ??? Quote "[LakeCTF Quals 23](https://lakectf.epfl.ch/)"  
                [![](https://ctftime.org/media/events/LakeCTF-512x512_1.png){ width="200" align=left }](https://lakectf.epfl.ch/)  
                **比赛名称** : [LakeCTF Quals 23](https://lakectf.epfl.ch/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-05 02:00:00 - 2023-11-06 02:00:00 UTC+8  
                **比赛权重** : 24.00  
                **赛事主办** : polygl0ts (https://ctftime.org/team/53791)  
                **添加日历** : https://ctftime.org/event/2069.ics  
                
            ??? Quote "[RuCTF 2023](https://ructf.org/)"  
                [![](https://ctftime.org/media/events/logo_2_1.jpeg){ width="200" align=left }](https://ructf.org/)  
                **比赛名称** : [RuCTF 2023](https://ructf.org/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2023-11-04 18:00:00 - 2023-11-05 03:00:00 UTC+8  
                **比赛权重** : 71.71  
                **赛事主办** : HackerDom (https://ctftime.org/team/552)  
                **添加日历** : https://ctftime.org/event/2120.ics  
                
            ??? Quote "[Oscar Zulu OSINT CTF Disparue(s)](https://ctfisended.old/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctfisended.old/)  
                **比赛名称** : [Oscar Zulu OSINT CTF Disparue(s)](https://ctfisended.old/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-04 17:00:00 - 2024-01-01 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : OSCAR ZULU (https://ctftime.org/team/270624)  
                **添加日历** : https://ctftime.org/event/2154.ics  
                
            ??? Quote "[M*CTF 2023 Junior Quals](https://mctf.mtuci.ru/)"  
                [![](https://ctftime.org/media/events/GRuJspCP73s_1.jpg){ width="200" align=left }](https://mctf.mtuci.ru/)  
                **比赛名称** : [M*CTF 2023 Junior Quals](https://mctf.mtuci.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-04 17:00:00 - 2023-11-05 17:00:00 UTC+8  
                **比赛权重** : 24.23  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2095.ics  
                
            ??? Quote "[cruXipher 2023 - ATMoS '23, BITS Hyderabad](https://cruxipher.crux-bphc.com/)"  
                [![](https://ctftime.org/media/events/logo_1-removebg-preview.jpg){ width="200" align=left }](https://cruxipher.crux-bphc.com/)  
                **比赛名称** : [cruXipher 2023 - ATMoS '23, BITS Hyderabad](https://cruxipher.crux-bphc.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-04 16:30:00 - 2023-11-06 16:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CRUx BPHC (https://ctftime.org/team/270645)  
                **添加日历** : https://ctftime.org/event/2156.ics  
                
            ??? Quote "[TSG CTF 2023](https://ctf.tsg.ne.jp/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.tsg.ne.jp/)  
                **比赛名称** : [TSG CTF 2023](https://ctf.tsg.ne.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-04 15:00:00 - 2023-11-05 15:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : TSG (https://ctftime.org/team/16088)  
                **添加日历** : https://ctftime.org/event/2013.ics  
                
            ??? Quote "[BlackAlps CTF 2023](https://www.blackalps.ch/ba-23/ctf.php)"  
                [![](https://ctftime.org/media/events/blackalps-v5-mountain-black1.png){ width="200" align=left }](https://www.blackalps.ch/ba-23/ctf.php)  
                **比赛名称** : [BlackAlps CTF 2023](https://www.blackalps.ch/ba-23/ctf.php)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-04 00:45:00 - 2023-11-04 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BlackAlps (https://ctftime.org/team/89021)  
                **添加日历** : https://ctftime.org/event/2157.ics  
                
            ??? Quote "[Hardwear.io NL 2023 Hardware CTF](https://hwctf.quarkslab.com/)"  
                [![](https://ctftime.org/media/events/logohwcolor.svg.png){ width="200" align=left }](https://hwctf.quarkslab.com/)  
                **比赛名称** : [Hardwear.io NL 2023 Hardware CTF](https://hwctf.quarkslab.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-02 18:00:00 - 2023-11-03 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hardware CTF by Quarkslab (https://ctftime.org/team/274600)  
                **添加日历** : https://ctftime.org/event/2176.ics  
                
            ??? Quote "[Ajman University CTF](https://au.pentestgarage.com/)"  
                [![](https://ctftime.org/media/events/ctf11.png){ width="200" align=left }](https://au.pentestgarage.com/)  
                **比赛名称** : [Ajman University CTF](https://au.pentestgarage.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-02 17:00:00 - 2023-11-03 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : RedTeam Hacker Academy (https://ctftime.org/team/250923)  
                **添加日历** : https://ctftime.org/event/2152.ics  
                
            ??? Quote "[EKOPARTY CTF 2023](https://ctf.ekoparty.org/)"  
                [![](https://ctftime.org/media/events/Logo_10.png){ width="200" align=left }](https://ctf.ekoparty.org/)  
                **比赛名称** : [EKOPARTY CTF 2023](https://ctf.ekoparty.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-01 21:00:00 - 2023-11-04 05:00:00 UTC+8  
                **比赛权重** : 20.82  
                **赛事主办** : NULL Life (https://ctftime.org/team/321)  
                **添加日历** : https://ctftime.org/event/2143.ics  
                
            ??? Quote "[cursedCTF 2024 Halloween Teaser](https://cursedc.tf/)"  
                [![](https://ctftime.org/media/events/cursedctf_halloween_teaser.jpg){ width="200" align=left }](https://cursedc.tf/)  
                **比赛名称** : [cursedCTF 2024 Halloween Teaser](https://cursedc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-10-31 08:00:00 - 2023-11-02 07:59:59 UTC+8  
                **比赛权重** : 19.50  
                **赛事主办** : cursed (https://ctftime.org/team/199492)  
                **添加日历** : https://ctftime.org/event/2144.ics  
                
            ??? Quote "[Platypwn 2023](https://platypwn.ctf.platypwnies.de/)"  
                [![](https://ctftime.org/media/events/a1c3d5bc6d43496ab202de9be30f3cd9.jpg){ width="200" align=left }](https://platypwn.ctf.platypwnies.de/)  
                **比赛名称** : [Platypwn 2023](https://platypwn.ctf.platypwnies.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-10-28 20:00:00 - 2023-10-29 20:00:00 UTC+8  
                **比赛权重** : 24.75  
                **赛事主办** : Platypwnies (https://ctftime.org/team/112550)  
                **添加日历** : https://ctftime.org/event/2082.ics  
                
            ??? Quote "[Russian CTF Cup 2023 Qualifier](https://ctfcup.ru/)"  
                [![](https://ctftime.org/media/events/CMjwD0td2vU.jpg){ width="200" align=left }](https://ctfcup.ru/)  
                **比赛名称** : [Russian CTF Cup 2023 Qualifier](https://ctfcup.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-10-28 17:00:00 - 2023-10-29 17:00:00 UTC+8  
                **比赛权重** : 24.21  
                **赛事主办** : ctfcup (https://ctftime.org/team/203499)  
                **添加日历** : https://ctftime.org/event/2136.ics  
                
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
