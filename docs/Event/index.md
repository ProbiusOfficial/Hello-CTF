---
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
        const [datePart, timePart] = rawTime.split(' ');
        const [year, month, day] = datePart.match(/\d+/g).map(Number);
        const [hour, minute] = timePart.split(':').map(Number);

        const formattedMonth = (month - 1).toString().padStart(2, '0');
        const formattedDay = day.toString().padStart(2, '0');
        return new Date(year, formattedMonth, formattedDay, hour, minute);
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
         *   reg_time_start: string
         *   reg_time_end: string
         *   comp_time_start: string
         *   comp_time_end: string
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
                //     start: parseTime(v.reg_time_start),
                //     end: parseTime(v.reg_time_end),
                //     title: v.name + '（报名时间）',
                //     url: v.link,
                //     region: CN
                // })
                const startTime = parseCNTime(v.comp_time_start)
                const endTime = parseCNTime(v.comp_time_end)

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
    
    === "*即将开始*"
        === "国内赛事"
            ??? Quote "[VNCTF 2025](https://ctf.vnteam.cn)"  
                **比赛名称** : [VNCTF 2025](https://ctf.vnteam.cn)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2025年01月01日 00:00 - 2025年02月08日 09:59  
                **比赛时间** : 2025年02月08日 10:00 - 2025年02月09日 10:00  
                **其他说明** : VNCTF 2025由V&N Team主办，个人赛，可报名，即将开始，中途不可加入。报名开始时间为2025年01月01日 00:00，比赛时间为2025年02月08日 10:00至2025年02月09日 10:00。更多信息请加QQ群717513199。  
                
        === "国外赛事"
            ??? Quote "[Srdnlen CTF 2025](https://ctf.srdnlen.it/)"  
                [![](https://ctftime.org/media/events/e04b66f1d17c437f935e29d0fbe7beed.png){ width="200" align=left }](https://ctf.srdnlen.it/)  
                **比赛名称** : [Srdnlen CTF 2025](https://ctf.srdnlen.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-19 02:00:00 - 2025-01-20 02:00:00 UTC+8  
                **比赛权重** : 32.28  
                **赛事主办** : Srdnlen (https://ctftime.org/team/83421)  
                **添加日历** : https://ctftime.org/event/2576.ics  
                
            ??? Quote "[HKCERT CTF 2024 (Final Round)](https://ctf.hkcert.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hkcert.org/)  
                **比赛名称** : [HKCERT CTF 2024 (Final Round)](https://ctf.hkcert.org/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2025-01-20 09:30:00 - 2025-01-21 12:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HKCERT (https://ctftime.org/team/134746)  
                **添加日历** : https://ctftime.org/event/2583.ics  
                
            ??? Quote "[KnightCTF 2025](https://2025.knightctf.com/)"  
                [![](https://ctftime.org/media/events/knight_ctf_logo_dark_bg_small.png){ width="200" align=left }](https://2025.knightctf.com/)  
                **比赛名称** : [KnightCTF 2025](https://2025.knightctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-20 23:00:00 - 2025-01-21 23:00:00 UTC+8  
                **比赛权重** : 18.78  
                **赛事主办** : Knight Squad (https://ctftime.org/team/141739)  
                **添加日历** : https://ctftime.org/event/2610.ics  
                
            ??? Quote "[Remedy CTF 2025](https://ctf.r.xyz/)"  
                [![](https://ctftime.org/media/events/remedy_logo.jpg){ width="200" align=left }](https://ctf.r.xyz/)  
                **比赛名称** : [Remedy CTF 2025](https://ctf.r.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-24 20:00:00 - 2025-01-26 20:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hexens (https://ctftime.org/team/355136)  
                **添加日历** : https://ctftime.org/event/2618.ics  
                
            ??? Quote "[x3CTF 2025 (feat. mvm)](https://x3c.tf/)"  
                [![](https://ctftime.org/media/events/temp_pfp.png){ width="200" align=left }](https://x3c.tf/)  
                **比赛名称** : [x3CTF 2025 (feat. mvm)](https://x3c.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-25 02:00:00 - 2025-01-27 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : x3CTF (https://ctftime.org/team/309820)  
                **添加日历** : https://ctftime.org/event/2467.ics  
                
            ??? Quote "[HackDay 2025 - Qualifications](https://hackday.fr/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://hackday.fr/)  
                **比赛名称** : [HackDay 2025 - Qualifications](https://hackday.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-25 04:00:00 - 2025-01-27 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HackDayCTF (https://ctftime.org/team/277562)  
                **添加日历** : https://ctftime.org/event/2615.ics  
                
            ??? Quote "[Dreamhack CTF Season 7 Round #2 (Div. 2)](https://dreamhack.io/ctf/656)"  
                [![](https://ctftime.org/media/events/bg2.jpg){ width="200" align=left }](https://dreamhack.io/ctf/656)  
                **比赛名称** : [Dreamhack CTF Season 7 Round #2 (Div. 2)](https://dreamhack.io/ctf/656)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-25 08:00:00 - 2025-01-25 23:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Dreamhack (https://ctftime.org/team/367894)  
                **添加日历** : https://ctftime.org/event/2622.ics  
                
            ??? Quote "[BITSCTF 2025](https://ctf.bitskrieg.in/)"  
                [![](https://ctftime.org/media/events/BITSkrieg_logo.png){ width="200" align=left }](https://ctf.bitskrieg.in/)  
                **比赛名称** : [BITSCTF 2025](https://ctf.bitskrieg.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-02-07 20:00:00 - 2025-02-09 20:00:00 UTC+8  
                **比赛权重** : 21.81  
                **赛事主办** : BITSkrieg (https://ctftime.org/team/22310)  
                **添加日历** : https://ctftime.org/event/2607.ics  
                
            ??? Quote "[LA CTF 2025](https://lac.tf/)"  
                [![](https://ctftime.org/media/events/lactf-square-logo_1_1.png){ width="200" align=left }](https://lac.tf/)  
                **比赛名称** : [LA CTF 2025](https://lac.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-02-08 12:00:00 - 2025-02-10 06:00:00 UTC+8  
                **比赛权重** : 36.70  
                **赛事主办** : PBR | UCLA (https://ctftime.org/team/186494)  
                **添加日历** : https://ctftime.org/event/2592.ics  
                
            ??? Quote "[SAIBORG | Elite Hacking Competition | Edition #2 | 21/Feb/2025](https://www.saiborg.io/)"  
                [![](https://ctftime.org/media/events/saiborg-profile_1.jpg){ width="200" align=left }](https://www.saiborg.io/)  
                **比赛名称** : [SAIBORG | Elite Hacking Competition | Edition #2 | 21/Feb/2025](https://www.saiborg.io/)  
                **比赛形式** : Hack quest  
                **比赛时间** : 2025-02-21 22:30:00 - 2025-02-22 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Saiborg (https://ctftime.org/team/271868)  
                **添加日历** : https://ctftime.org/event/2557.ics  
                
            ??? Quote "[@Hack 2025](https://athackctf.com/?s=ju8uvw)"  
                [![](https://ctftime.org/media/events/Hack_Logo_WIDTH_600px.png){ width="200" align=left }](https://athackctf.com/?s=ju8uvw)  
                **比赛名称** : [@Hack 2025](https://athackctf.com/?s=ju8uvw)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-15 19:00:00 - 2025-03-16 19:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hexploit Alliance (https://ctftime.org/team/278003)  
                **添加日历** : https://ctftime.org/event/2558.ics  
                
            ??? Quote "[SwampCTF 2025](https://swampctf.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://swampctf.com/)  
                **比赛名称** : [SwampCTF 2025](https://swampctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-28 08:21:00 - 2025-03-30 08:21:00 UTC+8  
                **比赛权重** : 40.40  
                **赛事主办** : Kernel Sanders (https://ctftime.org/team/397)  
                **添加日历** : https://ctftime.org/event/2573.ics  
                
            ??? Quote "[SpartanCTF 2025](https://spartan.ctfd.io/)"  
                [![](https://ctftime.org/media/events/spctf.png){ width="200" align=left }](https://spartan.ctfd.io/)  
                **比赛名称** : [SpartanCTF 2025](https://spartan.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 05:00:00 - 2025-03-31 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Zero Day Club (https://ctftime.org/team/286318)  
                **添加日历** : https://ctftime.org/event/2447.ics  
                
            ??? Quote "[PlaidCTF 2025](https://plaidctf.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://plaidctf.com/)  
                **比赛名称** : [PlaidCTF 2025](https://plaidctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-05 05:00:00 - 2025-04-07 05:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : Plaid Parliament of Pwning (https://ctftime.org/team/284)  
                **添加日历** : https://ctftime.org/event/2508.ics  
                
            ??? Quote "[UMassCTF 2025](https://ctf.umasscybersec.org/)"  
                [![](https://ctftime.org/media/events/889a1e484f0b51dd3d865b3a53b26200.jpg){ width="200" align=left }](https://ctf.umasscybersec.org/)  
                **比赛名称** : [UMassCTF 2025](https://ctf.umasscybersec.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-05 07:00:00 - 2025-04-07 07:00:00 UTC+8  
                **比赛权重** : 48.38  
                **赛事主办** : SavedByTheShell (https://ctftime.org/team/78233)  
                **添加日历** : https://ctftime.org/event/2519.ics  
                
            ??? Quote "[DamCTF 2025](https://damctf.xyz/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://damctf.xyz/)  
                **比赛名称** : [DamCTF 2025](https://damctf.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-05 08:00:00 - 2025-04-07 08:00:00 UTC+8  
                **比赛权重** : 60.67  
                **赛事主办** : OSUSEC (https://ctftime.org/team/12858)  
                **添加日历** : https://ctftime.org/event/2585.ics  
                
            ??? Quote "[UMDCTF 2025](https://umdctf.io/)"  
                [![](https://ctftime.org/media/events/ae1c27549ce5fb7832b0ff1bc873c622.png){ width="200" align=left }](https://umdctf.io/)  
                **比赛名称** : [UMDCTF 2025](https://umdctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-26 06:00:00 - 2025-04-28 06:00:00 UTC+8  
                **比赛权重** : 70.86  
                **赛事主办** : UMDCSEC (https://ctftime.org/team/87711)  
                **添加日历** : https://ctftime.org/event/2563.ics  
                
            ??? Quote "[LakeCTF Finals 24-25](https://lakectf.epfl.ch/)"  
                [![](https://ctftime.org/media/events/5ee3dccc1b28b5f04bdf2f7b871b1d07.png){ width="200" align=left }](https://lakectf.epfl.ch/)  
                **比赛名称** : [LakeCTF Finals 24-25](https://lakectf.epfl.ch/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-09 16:00:00 - 2025-05-10 00:00:00 UTC+8  
                **比赛权重** : 36.00  
                **赛事主办** : polygl0ts (https://ctftime.org/team/53791)  
                **添加日历** : https://ctftime.org/event/2568.ics  
                
            ??? Quote "[N0PSctf](https://www.nops.re/)"  
                [![](https://ctftime.org/media/events/logo-news.png){ width="200" align=left }](https://www.nops.re/)  
                **比赛名称** : [N0PSctf](https://www.nops.re/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-31 16:00:00 - 2025-06-02 04:00:00 UTC+8  
                **比赛权重** : 24.34  
                **赛事主办** : NOPS (https://ctftime.org/team/4056)  
                **添加日历** : https://ctftime.org/event/2486.ics  
                
            ??? Quote "[Crypto CTF 2025](https://cr.yp.toc.tf/)"  
                [![](https://ctftime.org/media/events/cryptoctf_1.jpg){ width="200" align=left }](https://cr.yp.toc.tf/)  
                **比赛名称** : [Crypto CTF 2025](https://cr.yp.toc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-14 14:00:00 - 2025-06-15 14:00:00 UTC+8  
                **比赛权重** : 88.25  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2577.ics  
                
    === "*正在进行*"
        === "国内赛事"
    
        === "国外赛事"
            ??? Quote "[Pointer Overflow CTF - 2024](http://pointeroverflowctf.com/)"  
                [![](https://ctftime.org/media/events/poctflogo1transp.png){ width="200" align=left }](http://pointeroverflowctf.com/)  
                **比赛名称** : [Pointer Overflow CTF - 2024](http://pointeroverflowctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-15 20:00:00 - 2025-01-19 20:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : UWSP Pointers (https://ctftime.org/team/231536)  
                **添加日历** : https://ctftime.org/event/2121.ics  
                
            ??? Quote "[2025 Embedded Capture the Flag](https://ectf.mitre.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ectf.mitre.org/)  
                **比赛名称** : [2025 Embedded Capture the Flag](https://ectf.mitre.org/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2025-01-16 01:00:00 - 2025-04-17 00:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : ectfmitre (https://ctftime.org/team/87292)  
                **添加日历** : https://ctftime.org/event/2542.ics  
                
    === "*已经结束*"
        === "国内赛事"
            ??? Quote "[NSSCTF Round26](https://www.nssctf.cn/contest)"  
                **比赛名称** : [NSSCTF Round26](https://www.nssctf.cn/contest)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2024年12月28日 14:00 - 2024年12月28日 13:59  
                **比赛时间** : 2024年12月28日 14:00 - 2024年12月28日 17:00  
                **其他说明** : NSSCTF Round26 由NSSCTF主办，比赛时间为2024年12月28日 14:00至17:00，报名已结束，比赛QQ群为864395049。  
                
            ??? Quote "[国城杯初赛](https://ctf2024.goalcent.com/)"  
                **比赛名称** : [国城杯初赛](https://ctf2024.goalcent.com/)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2024年11月23日 00:00 - 2024年12月06日 00:00  
                **比赛时间** : 2024年12月07日 09:00 - 2024年12月07日 17:00  
                **其他说明** : 国城杯初赛由国城杯初赛主办，比赛链接为https://ctf2024.goalcent.com/，4人组队，报名开始时间为2024年11月23日，报名截止时间为2024年12月06日，比赛开始时间为2024年12月07日，选手可通过QQ群629910816进行沟通。  
                
            ??? Quote "[第一届吾杯网络安全技能大赛](https://www.wucup.net/games/1)"  
                **比赛名称** : [第一届吾杯网络安全技能大赛](https://www.wucup.net/games/1)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2024年12月01日 08:59 - 2024年12月01日 08:59  
                **比赛时间** : 2024年12月01日 09:00 - 2024年12月01日 16:00  
                **其他说明** : 第一届吾杯网络安全技能大赛由东莞市东城小宇网络工作室主办，潮州市极玩网络科技有限公司承办。比赛时间为2024年12月01日 09:00至16:00，报名截止时间为2024年12月01日 08:59。更多信息请访问比赛官网。  
                
        === "国外赛事"
            ??? Quote "[TSCCTF 2025](https://ctfd.tscctf.com/)"  
                [![](https://ctftime.org/media/events/TSC_logo_extra_large.png){ width="200" align=left }](https://ctfd.tscctf.com/)  
                **比赛名称** : [TSCCTF 2025](https://ctfd.tscctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-13 10:00:00 - 2025-01-16 10:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Taiwan Security Club (https://ctftime.org/team/365248)  
                **添加日历** : https://ctftime.org/event/2598.ics  
                
            ??? Quote "[New Year CTF 2025](http://ctf-spcs.mf.grsu.by/)"  
                [![](https://ctftime.org/media/events/NY2025.jpg){ width="200" align=left }](http://ctf-spcs.mf.grsu.by/)  
                **比赛名称** : [New Year CTF 2025](http://ctf-spcs.mf.grsu.by/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-13 01:00:00 - 2025-01-15 01:00:00 UTC+8  
                **比赛权重** : 23.13  
                **赛事主办** : Beavers0 (https://ctftime.org/team/269281)  
                **添加日历** : https://ctftime.org/event/2582.ics  
                
            ??? Quote "[Cyber League 2025 - Major](https://ctfd.cyberleague.co/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctfd.cyberleague.co/)  
                **比赛名称** : [Cyber League 2025 - Major](https://ctfd.cyberleague.co/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-11 10:00:00 - 2025-01-12 10:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : DIV0-N0H4TS (https://ctftime.org/team/354275)  
                **添加日历** : https://ctftime.org/event/2530.ics  
                
            ??? Quote "[SUCTF 2025](https://suctf2025.xctf.org.cn/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://suctf2025.xctf.org.cn/)  
                **比赛名称** : [SUCTF 2025](https://suctf2025.xctf.org.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-11 09:00:00 - 2025-01-13 09:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : SU (https://ctftime.org/team/29641)  
                **添加日历** : https://ctftime.org/event/2620.ics  
                
            ??? Quote "[Dreamhack CTF Season 7 Round #1 (Div. 1)](https://dreamhack.io/ctf/655)"  
                [![](https://ctftime.org/media/events/cover01.jpg){ width="200" align=left }](https://dreamhack.io/ctf/655)  
                **比赛名称** : [Dreamhack CTF Season 7 Round #1 (Div. 1)](https://dreamhack.io/ctf/655)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-11 08:00:00 - 2025-01-11 23:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Dreamhack (https://ctftime.org/team/367894)  
                **添加日历** : https://ctftime.org/event/2621.ics  
                
            ??? Quote "[UofTCTF 2025](https://ctf.uoftctf.org/)"  
                [![](https://ctftime.org/media/events/uoftctf_logo_3000_black.png){ width="200" align=left }](https://ctf.uoftctf.org/)  
                **比赛名称** : [UofTCTF 2025](https://ctf.uoftctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-11 08:00:00 - 2025-01-13 08:00:00 UTC+8  
                **比赛权重** : 23.90  
                **赛事主办** : UofTCTF (https://ctftime.org/team/139261)  
                **添加日历** : https://ctftime.org/event/2570.ics  
                
            ??? Quote "[GoIda CTF](https://goidactf.ru/)"  
                [![](https://ctftime.org/media/events/goida.jpg){ width="200" align=left }](https://goidactf.ru/)  
                **比赛名称** : [GoIda CTF](https://goidactf.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-07 08:00:00 - 2025-01-10 07:59:59 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : GoIda CTF ORG (https://ctftime.org/team/361741)  
                **添加日历** : https://ctftime.org/event/2611.ics  
                
            ??? Quote "[IrisCTF 2025](https://2025.irisc.tf/)"  
                [![](https://ctftime.org/media/events/IrisSec.png){ width="200" align=left }](https://2025.irisc.tf/)  
                **比赛名称** : [IrisCTF 2025](https://2025.irisc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-04 08:00:00 - 2025-01-06 08:00:00 UTC+8  
                **比赛权重** : 34.30  
                **赛事主办** : IrisSec (https://ctftime.org/team/127034)  
                **添加日历** : https://ctftime.org/event/2503.ics  
                
            ??? Quote "[AlpacaHack Round 8 (Rev)](https://alpacahack.com/)"  
                [![](https://ctftime.org/media/events/dark_512_2.png){ width="200" align=left }](https://alpacahack.com/)  
                **比赛名称** : [AlpacaHack Round 8 (Rev)](https://alpacahack.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-30 11:00:00 - 2024-12-30 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : AlpacaHack (https://ctftime.org/team/312315)  
                **添加日历** : https://ctftime.org/event/2590.ics  
                
            ??? Quote "[ASIS CTF Finals 2024](https://asisctf.com/)"  
                [![](https://ctftime.org/media/events/asis_logo.png){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Finals 2024](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-28 22:00:00 - 2024-12-29 22:00:00 UTC+8  
                **比赛权重** : 92.75  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2403.ics  
                
            ??? Quote "[hxp 38C3 CTF](https://2024.ctf.link/)"  
                [![](https://ctftime.org/media/events/hxp-38c3.png){ width="200" align=left }](https://2024.ctf.link/)  
                **比赛名称** : [hxp 38C3 CTF](https://2024.ctf.link/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-28 04:00:00 - 2024-12-30 04:00:00 UTC+8  
                **比赛权重** : 98.14  
                **赛事主办** : hxp (https://ctftime.org/team/585)  
                **添加日历** : https://ctftime.org/event/2437.ics  
                
            ??? Quote "[Wargames.MY CTF 2024](https://ctf2024.wargames.my/)"  
                [![](https://ctftime.org/media/events/WGMY24-PFP1.png){ width="200" align=left }](https://ctf2024.wargames.my/)  
                **比赛名称** : [Wargames.MY CTF 2024](https://ctf2024.wargames.my/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-28 00:00:00 - 2024-12-29 00:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Wargames.MY (https://ctftime.org/team/86069)  
                **添加日历** : https://ctftime.org/event/2597.ics  
                
            ??? Quote "[0xL4ugh CTF](https://0xl4ugh.ctf.ae/)"  
                [![](https://ctftime.org/media/events/logo_101.png){ width="200" align=left }](https://0xl4ugh.ctf.ae/)  
                **比赛名称** : [0xL4ugh CTF](https://0xl4ugh.ctf.ae/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-27 20:00:00 - 2024-12-28 20:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : 0xL4ugh (https://ctftime.org/team/132776)  
                **添加日历** : https://ctftime.org/event/2587.ics  
                
            ??? Quote "[BackdoorCTF 2024](https://backdoor.infoseciitr.in/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://backdoor.infoseciitr.in/)  
                **比赛名称** : [BackdoorCTF 2024](https://backdoor.infoseciitr.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-22 20:00:00 - 2024-12-23 20:00:00 UTC+8  
                **比赛权重** : 49.48  
                **赛事主办** : InfoSecIITR (https://ctftime.org/team/16691)  
                **添加日历** : https://ctftime.org/event/2540.ics  
                
            ??? Quote "[0CTF 2024](https://ctf.0ops.sjtu.cn/)"  
                [![](https://ctftime.org/media/events/0ctf.png){ width="200" align=left }](https://ctf.0ops.sjtu.cn/)  
                **比赛名称** : [0CTF 2024](https://ctf.0ops.sjtu.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-21 10:00:00 - 2024-12-23 10:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : 0ops (https://ctftime.org/team/4419)  
                **添加日历** : https://ctftime.org/event/2448.ics  
                
            ??? Quote "[NTUA_H4CK](https://ctfnhack.ctflib.eu/)"  
                [![](https://ctftime.org/media/events/Copy_of_Untitled_Design1.png){ width="200" align=left }](https://ctfnhack.ctflib.eu/)  
                **比赛名称** : [NTUA_H4CK](https://ctfnhack.ctflib.eu/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-15 17:00:00 - 2024-12-16 05:00:00 UTC+8  
                **比赛权重** : 24.86  
                **赛事主办** : Thread in the Needle (https://ctftime.org/team/278978)  
                **添加日历** : https://ctftime.org/event/2571.ics  
                
            ??? Quote "[m0leCon 2025 Beginner CTF](https://beginner.m0lecon.it/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://beginner.m0lecon.it/)  
                **比赛名称** : [m0leCon 2025 Beginner CTF](https://beginner.m0lecon.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-14 21:00:00 - 2024-12-15 02:00:00 UTC+8  
                **比赛权重** : 75.00  
                **赛事主办** : pwnthem0le (https://ctftime.org/team/60467)  
                **添加日历** : https://ctftime.org/event/2578.ics  
                
            ??? Quote "[Russian CTF Cup 2024 Final](https://ctfcup.ru/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctfcup.ru/)  
                **比赛名称** : [Russian CTF Cup 2024 Final](https://ctfcup.ru/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-12-14 18:00:00 - 2024-12-16 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ctfcup (https://ctftime.org/team/203499)  
                **添加日历** : https://ctftime.org/event/2406.ics  
                
            ??? Quote "[TSG CTF 2024](https://ctf.tsg.ne.jp/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.tsg.ne.jp/)  
                **比赛名称** : [TSG CTF 2024](https://ctf.tsg.ne.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-14 15:00:00 - 2024-12-15 15:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : TSG (https://ctftime.org/team/16088)  
                **添加日历** : https://ctftime.org/event/2424.ics  
                
            ??? Quote "[THJCC CTF 2024 winter](https://ctf.scint.org/)"  
                [![](https://ctftime.org/media/events/THJCC_logo.png){ width="200" align=left }](https://ctf.scint.org/)  
                **比赛名称** : [THJCC CTF 2024 winter](https://ctf.scint.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-14 08:00:01 - 2024-12-15 20:00:01 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CakeisTheFake (https://ctftime.org/team/276544)  
                **添加日历** : https://ctftime.org/event/2581.ics  
                
            ??? Quote "[HTB University CTF 2024: Binary Badlands](https://ctf.hackthebox.com/event/details/university-ctf-2024-binary-badlands-1822)"  
                [![](https://ctftime.org/media/events/htbctf-logo_1.png){ width="200" align=left }](https://ctf.hackthebox.com/event/details/university-ctf-2024-binary-badlands-1822)  
                **比赛名称** : [HTB University CTF 2024: Binary Badlands](https://ctf.hackthebox.com/event/details/university-ctf-2024-binary-badlands-1822)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-13 21:00:00 - 2024-12-16 05:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Hack The Box (https://ctftime.org/team/136056)  
                **添加日历** : https://ctftime.org/event/2539.ics  
                
            ??? Quote "[niteCTF 2024](https://play.nitectf2024.live/)"  
                [![](https://ctftime.org/media/events/nitectf_2024_logo.jpg){ width="200" align=left }](https://play.nitectf2024.live/)  
                **比赛名称** : [niteCTF 2024](https://play.nitectf2024.live/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-13 20:00:00 - 2024-12-15 20:00:00 UTC+8  
                **比赛权重** : 29.33  
                **赛事主办** : Cryptonite (https://ctftime.org/team/62713)  
                **添加日历** : https://ctftime.org/event/2461.ics  
                
            ??? Quote "[WannaGame Championship 2024](https://cnsc.com.vn/ctf/)"  
                [![](https://ctftime.org/media/events/WGC2024_2.png){ width="200" align=left }](https://cnsc.com.vn/ctf/)  
                **比赛名称** : [WannaGame Championship 2024](https://cnsc.com.vn/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-13 09:00:00 - 2024-12-14 09:00:00 UTC+8  
                **比赛权重** : 19.80  
                **赛事主办** : Wanna.W1n (https://ctftime.org/team/138431)  
                **添加日历** : https://ctftime.org/event/2515.ics  
                
            ??? Quote "[LakeCTF Quals 24-25](https://lakectf.epfl.ch/)"  
                [![](https://ctftime.org/media/events/7fb065c04dbec7e33dfbb1f4456196c7.png){ width="200" align=left }](https://lakectf.epfl.ch/)  
                **比赛名称** : [LakeCTF Quals 24-25](https://lakectf.epfl.ch/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-08 02:00:00 - 2024-12-09 02:00:00 UTC+8  
                **比赛权重** : 35.94  
                **赛事主办** : polygl0ts (https://ctftime.org/team/53791)  
                **添加日历** : https://ctftime.org/event/2502.ics  
                
            ??? Quote "[DFIR Labs CTF by The DFIR Report](https://thedfirreport.com/services/dfir-labs/ctf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://thedfirreport.com/services/dfir-labs/ctf/)  
                **比赛名称** : [DFIR Labs CTF by The DFIR Report](https://thedfirreport.com/services/dfir-labs/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-08 00:00:00 - 2024-12-08 04:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : The DFIR Report (https://ctftime.org/team/309500)  
                **添加日历** : https://ctftime.org/event/2488.ics  
                
            ??? Quote "[Platypwn 2024](https://platypwn.ctf.platypwnies.de/)"  
                [![](https://ctftime.org/media/events/Platypwnie.png){ width="200" align=left }](https://platypwn.ctf.platypwnies.de/)  
                **比赛名称** : [Platypwn 2024](https://platypwn.ctf.platypwnies.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-07 22:00:00 - 2024-12-08 22:00:00 UTC+8  
                **比赛权重** : 24.75  
                **赛事主办** : Platypwnies (https://ctftime.org/team/112550)  
                **添加日历** : https://ctftime.org/event/2407.ics  
                
            ??? Quote "[RedShift.Eclipse 2 Finals]()"  
                [![](https://ctftime.org/media/events/5202034882946130981.jpg){ width="200" align=left }]()  
                **比赛名称** : [RedShift.Eclipse 2 Finals]()  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-12-07 18:00:00 - 2024-12-08 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : o1d_bu7_go1d (https://ctftime.org/team/213673)  
                **添加日历** : https://ctftime.org/event/2538.ics  
                
            ??? Quote "[M*CTF 2024 Finals](https://mctf.ru/)"  
                [![](https://ctftime.org/media/events/IMG_2613_1.PNG){ width="200" align=left }](https://mctf.ru/)  
                **比赛名称** : [M*CTF 2024 Finals](https://mctf.ru/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-12-07 15:30:00 - 2024-12-08 00:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2595.ics  
                
            ??? Quote "[ISITDTU CTF 2024 Finals](https://ctf.isitdtu.com/)"  
                [![](https://ctftime.org/media/events/index_3.gif){ width="200" align=left }](https://ctf.isitdtu.com/)  
                **比赛名称** : [ISITDTU CTF 2024 Finals](https://ctf.isitdtu.com/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-12-07 10:00:00 - 2024-12-08 19:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ISITDTU (https://ctftime.org/team/8241)  
                **添加日历** : https://ctftime.org/event/2510.ics  
                
            ??? Quote "[snakeCTF 2024 Finals](https://2024.snakectf.org/)"  
                [![](https://ctftime.org/media/events/LogoCroppable_2.png){ width="200" align=left }](https://2024.snakectf.org/)  
                **比赛名称** : [snakeCTF 2024 Finals](https://2024.snakectf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-05 16:00:00 - 2024-12-08 16:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : MadrHacks (https://ctftime.org/team/114509)  
                **添加日历** : https://ctftime.org/event/2419.ics  
                
            ??? Quote "[Advent of CTF 2024](https://cyberstudents.net/advent)"  
                [![](https://ctftime.org/media/events/IMG_4522.png){ width="200" align=left }](https://cyberstudents.net/advent)  
                **比赛名称** : [Advent of CTF 2024](https://cyberstudents.net/advent)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-02 04:00:00 - 2025-01-01 12:59:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : CyberStudentsCTF (https://ctftime.org/team/365239)  
                **添加日历** : https://ctftime.org/event/2600.ics  
                
            ??? Quote "[M*CTF 2024 Junior Finals](https://mctf.ru/)"  
                [![](https://ctftime.org/media/events/IMG_2613.PNG){ width="200" align=left }](https://mctf.ru/)  
                **比赛名称** : [M*CTF 2024 Junior Finals](https://mctf.ru/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-12-01 15:00:00 - 2024-12-01 21:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2586.ics  
                
            ??? Quote "[saarCTF 2024](https://ctf.saarland/)"  
                [![](https://ctftime.org/media/events/e21b4ef017572441617115eaa6bd9823.jpg){ width="200" align=left }](https://ctf.saarland/)  
                **比赛名称** : [saarCTF 2024](https://ctf.saarland/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-11-30 21:00:00 - 2024-12-01 06:00:00 UTC+8  
                **比赛权重** : 98.50  
                **赛事主办** : saarsec (https://ctftime.org/team/15337)  
                **添加日历** : https://ctftime.org/event/2490.ics  
                
            ??? Quote "[HackTM CTF 2024 - Postponed](https://ctf.hacktm.ro/)"  
                [![](https://ctftime.org/media/events/e2b12b3390413f1cf2cdeb7b12e076c6.jpg){ width="200" align=left }](https://ctf.hacktm.ro/)  
                **比赛名称** : [HackTM CTF 2024 - Postponed](https://ctf.hacktm.ro/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-30 20:00:00 - 2024-12-01 20:00:00 UTC+8  
                **比赛权重** : 24.67  
                **赛事主办** : WreckTheLine (https://ctftime.org/team/57908)  
                **添加日历** : https://ctftime.org/event/2452.ics  
                
            ??? Quote "[World Wide CTF 2024](https://wwctf.com/)"  
                [![](https://ctftime.org/media/events/logobg.png){ width="200" align=left }](https://wwctf.com/)  
                **比赛名称** : [World Wide CTF 2024](https://wwctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-30 20:00:00 - 2024-12-01 20:00:00 UTC+8  
                **比赛权重** : 24.48  
                **赛事主办** : World Wide Flags (https://ctftime.org/team/283853)  
                **添加日历** : https://ctftime.org/event/2572.ics  
                
            ??? Quote "[CYBERGON CTF_2024](https://cybergon.ctfd.io/)"  
                [![](https://ctftime.org/media/events/CYBERGON_Logo.png){ width="200" align=left }](https://cybergon.ctfd.io/)  
                **比赛名称** : [CYBERGON CTF_2024](https://cybergon.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-30 20:00:00 - 2024-12-02 20:00:00 UTC+8  
                **比赛权重** : 23.08  
                **赛事主办** : My4nM4r (https://ctftime.org/team/145625)  
                **添加日历** : https://ctftime.org/event/2560.ics  
                
            ??? Quote "[Ph0wn 2024](https://ph0wn.org/)"  
                [![](https://ctftime.org/media/events/logo-ph0wn_5.png){ width="200" align=left }](https://ph0wn.org/)  
                **比赛名称** : [Ph0wn 2024](https://ph0wn.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-30 18:00:00 - 2024-12-01 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Pic0wn (https://ctftime.org/team/6514)  
                **添加日历** : https://ctftime.org/event/2564.ics  
                
            ??? Quote "[AlpacaHack Round 7 (Web)](https://alpacahack.com/ctfs/round-7)"  
                [![](https://ctftime.org/media/events/ctftime_8.png){ width="200" align=left }](https://alpacahack.com/ctfs/round-7)  
                **比赛名称** : [AlpacaHack Round 7 (Web)](https://alpacahack.com/ctfs/round-7)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-30 11:00:00 - 2024-11-30 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : AlpacaHack (https://ctftime.org/team/312315)  
                **添加日历** : https://ctftime.org/event/2544.ics  
                
            ??? Quote "[BlackHat MEA CTF Final 2024](https://blackhatmea.com/capture-the-flag)"  
                [![](https://ctftime.org/media/events/e0c283c95f7b0db516dae505d31ca20b_3.jpg){ width="200" align=left }](https://blackhatmea.com/capture-the-flag)  
                **比赛名称** : [BlackHat MEA CTF Final 2024](https://blackhatmea.com/capture-the-flag)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-26 16:00:00 - 2024-11-28 11:00:00 UTC+8  
                **比赛权重** : 22.50  
                **赛事主办** : SAFCSP (https://ctftime.org/team/54707)  
                **添加日历** : https://ctftime.org/event/2431.ics  
                
            ??? Quote "[CTFZone 2024 Final](http://ctf.bi.zone/)"  
                [![](https://ctftime.org/media/events/aa86f826480a008ed91d88a917a0c33b.png){ width="200" align=left }](http://ctf.bi.zone/)  
                **比赛名称** : [CTFZone 2024 Final](http://ctf.bi.zone/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-11-24 17:00:00 - 2024-11-25 01:00:00 UTC+8  
                **比赛权重** : 96.90  
                **赛事主办** : BIZone (https://ctftime.org/team/32190)  
                **添加日历** : https://ctftime.org/event/2506.ics  
                
            ??? Quote "[CyberSci Regional Qualifiers 2024-25](https://cybersecuritychallenge.ca/)"  
                [![](https://ctftime.org/media/events/9ad26ba791d2c5418b515bd4699ea7e2.png){ width="200" align=left }](https://cybersecuritychallenge.ca/)  
                **比赛名称** : [CyberSci Regional Qualifiers 2024-25](https://cybersecuritychallenge.ca/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-24 00:00:00 - 2024-11-24 07:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CyberSciOrganizers (https://ctftime.org/team/157536)  
                **添加日历** : https://ctftime.org/event/2511.ics  
                
            ??? Quote "[The Hacker Conclave v2](https://ctf.thehackerconclave.es/)"  
                [![](https://ctftime.org/media/events/ctftime2.png){ width="200" align=left }](https://ctf.thehackerconclave.es/)  
                **比赛名称** : [The Hacker Conclave v2](https://ctf.thehackerconclave.es/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-23 17:00:00 - 2024-11-23 20:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : C0ncl4v3 (https://ctftime.org/team/303692)  
                **添加日历** : https://ctftime.org/event/2575.ics  
                
            ??? Quote "[WP CTF 2024](https://wpctf.it/)"  
                [![](https://ctftime.org/media/events/WP_CTF_logo.png){ width="200" align=left }](https://wpctf.it/)  
                **比赛名称** : [WP CTF 2024](https://wpctf.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-23 16:00:00 - 2024-11-24 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : WP CTF (https://ctftime.org/team/303099)  
                **添加日历** : https://ctftime.org/event/2395.ics  
                
            ??? Quote "[SECCON CTF 13 Quals](https://ctf.seccon.jp/)"  
                [![](https://ctftime.org/media/events/seccon_s_7.png){ width="200" align=left }](https://ctf.seccon.jp/)  
                **比赛名称** : [SECCON CTF 13 Quals](https://ctf.seccon.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-23 13:00:00 - 2024-11-24 13:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : SECCON CTF (https://ctftime.org/team/11918)  
                **添加日历** : https://ctftime.org/event/2478.ics  
                
            ??? Quote "[Hackvens 2024](https://hackvens.fr/)"  
                [![](https://ctftime.org/media/events/Logo_Hackvens.png){ width="200" align=left }](https://hackvens.fr/)  
                **比赛名称** : [Hackvens 2024](https://hackvens.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-23 04:00:00 - 2024-11-23 14:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hackvens (https://ctftime.org/team/194092)  
                **添加日历** : https://ctftime.org/event/2401.ics  
                
            ??? Quote "[GlacierCTF 2024](https://glacierctf.com/)"  
                [![](https://ctftime.org/media/events/3ae6516246966c8d08c81d3bd5451cfa_1.png){ width="200" align=left }](https://glacierctf.com/)  
                **比赛名称** : [GlacierCTF 2024](https://glacierctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-23 02:00:00 - 2024-11-24 02:00:00 UTC+8  
                **比赛权重** : 35.69  
                **赛事主办** : LosFuzzys (https://ctftime.org/team/8323)  
                **添加日历** : https://ctftime.org/event/2402.ics  
                
            ??? Quote "[iCTF 2024 (Undergrad)](https://ictf.cs.ucsb.edu/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ictf.cs.ucsb.edu/)  
                **比赛名称** : [iCTF 2024 (Undergrad)](https://ictf.cs.ucsb.edu/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-17 02:00:00 - 2024-11-23 08:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Shellphish (https://ctftime.org/team/285)  
                **添加日历** : https://ctftime.org/event/2565.ics  
                
            ??? Quote "[iCTF 2024 (Highschool)](https://ictf.cs.ucsb.edu/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ictf.cs.ucsb.edu/)  
                **比赛名称** : [iCTF 2024 (Highschool)](https://ictf.cs.ucsb.edu/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-17 02:00:00 - 2024-11-23 08:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Shellphish (https://ctftime.org/team/285)  
                **添加日历** : https://ctftime.org/event/2566.ics  
                
            ??? Quote "[Crate-CTF 2024](https://foi.se/cratectf)"  
                [![](https://ctftime.org/media/events/crate-ctf-2024.png){ width="200" align=left }](https://foi.se/cratectf)  
                **比赛名称** : [Crate-CTF 2024](https://foi.se/cratectf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-16 21:00:00 - 2024-11-17 05:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Crate-CTF (https://ctftime.org/team/352250)  
                **添加日历** : https://ctftime.org/event/2489.ics  
                
            ??? Quote "[BRICS+ CTF Finals 2024](https://brics-ctf.com/)"  
                [![](https://ctftime.org/media/events/brics-logo-2024-square.png){ width="200" align=left }](https://brics-ctf.com/)  
                **比赛名称** : [BRICS+ CTF Finals 2024](https://brics-ctf.com/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-11-16 18:00:00 - 2024-11-17 02:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ITMO FSIT (https://ctftime.org/team/264636)  
                **添加日历** : https://ctftime.org/event/2521.ics  
                
            ??? Quote "[No Hack No CTF 2024](https://nhnc.ic3dt3a.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://nhnc.ic3dt3a.org/)  
                **比赛名称** : [No Hack No CTF 2024](https://nhnc.ic3dt3a.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-16 09:30:00 - 2024-11-17 21:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ICEDTEA (https://ctftime.org/team/303514)  
                **添加日历** : https://ctftime.org/event/2574.ics  
                
            ??? Quote "[PwnSec CTF 2024](https://ctf.pwnsec.xyz/)"  
                [![](https://ctftime.org/media/events/Logo_12.png){ width="200" align=left }](https://ctf.pwnsec.xyz/)  
                **比赛名称** : [PwnSec CTF 2024](https://ctf.pwnsec.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-15 23:00:00 - 2024-11-16 23:00:00 UTC+8  
                **比赛权重** : 23.92  
                **赛事主办** : PwnSec (https://ctftime.org/team/28797)  
                **添加日历** : https://ctftime.org/event/2454.ics  
                
            ??? Quote "[1337UP LIVE CTF](https://ctf.intigriti.io/)"  
                [![](https://ctftime.org/media/events/intigriti_icon_cmyk_navy.png){ width="200" align=left }](https://ctf.intigriti.io/)  
                **比赛名称** : [1337UP LIVE CTF](https://ctf.intigriti.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-15 19:59:59 - 2024-11-17 07:59:59 UTC+8  
                **比赛权重** : 24.23  
                **赛事主办** : CryptoCat (https://ctftime.org/team/124896)  
                **添加日历** : https://ctftime.org/event/2446.ics  
                
            ??? Quote "[Die Abenteuer von KIM & TIM Kapt. II - To TI-Mfinity and Beyond](http://ctf.gematik.de/)"  
                [![](https://ctftime.org/media/events/Bild_1.png){ width="200" align=left }](http://ctf.gematik.de/)  
                **比赛名称** : [Die Abenteuer von KIM & TIM Kapt. II - To TI-Mfinity and Beyond](http://ctf.gematik.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-15 17:00:00 - 2024-11-16 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : H34lthineer (https://ctftime.org/team/170109)  
                **添加日历** : https://ctftime.org/event/2481.ics  
                
            ??? Quote "[BlockCTF 2024 (Formerly SquareCTF)](https://2024.blockctf.com/)"  
                [![](https://ctftime.org/media/events/0ed304c3c4dcb6a3e887778f3928e26e.png){ width="200" align=left }](https://2024.blockctf.com/)  
                **比赛名称** : [BlockCTF 2024 (Formerly SquareCTF)](https://2024.blockctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-14 06:00:00 - 2024-11-15 06:00:00 UTC+8  
                **比赛权重** : 52.43  
                **赛事主办** : Square (https://ctftime.org/team/46747)  
                **添加日历** : https://ctftime.org/event/2517.ics  
                
            ??? Quote "[EKOPARTY CTF 2024](https://ctf.ekoparty.org/)"  
                [![](https://ctftime.org/media/events/LOGO_eko_2024.png){ width="200" align=left }](https://ctf.ekoparty.org/)  
                **比赛名称** : [EKOPARTY CTF 2024](https://ctf.ekoparty.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-13 21:00:00 - 2024-11-16 03:00:00 UTC+8  
                **比赛权重** : 16.00  
                **赛事主办** : NULL (https://ctftime.org/team/321)  
                **添加日历** : https://ctftime.org/event/2507.ics  
                
            ??? Quote "[DataCon2024](https://datacon.qianxin.com/datacon2024-en)"  
                [![](https://ctftime.org/media/events/16945a7ddd36ca5428bca66728c36df3.png){ width="200" align=left }](https://datacon.qianxin.com/datacon2024-en)  
                **比赛名称** : [DataCon2024](https://datacon.qianxin.com/datacon2024-en)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-13 10:00:00 - 2024-11-22 18:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : DataCon (https://ctftime.org/team/361332)  
                **添加日历** : https://ctftime.org/event/2580.ics  
                
            ??? Quote "[N1CTF 2024](https://ctf2024.nu1l.com/)"  
                [![](https://ctftime.org/media/events/logo2_5_1.png){ width="200" align=left }](https://ctf2024.nu1l.com/)  
                **比赛名称** : [N1CTF 2024](https://ctf2024.nu1l.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-09 20:00:00 - 2024-11-10 20:00:00 UTC+8  
                **比赛权重** : 89.85  
                **赛事主办** : Nu1L (https://ctftime.org/team/19208)  
                **添加日历** : https://ctftime.org/event/2459.ics  
                
            ??? Quote "[Bambi CTF #11](https://bambi11.enoflag.de/)"  
                [![](https://ctftime.org/media/events/reh_1.png){ width="200" align=left }](https://bambi11.enoflag.de/)  
                **比赛名称** : [Bambi CTF #11](https://bambi11.enoflag.de/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-11-09 19:00:00 - 2024-11-10 01:00:00 UTC+8  
                **比赛权重** : 85.71  
                **赛事主办** : ENOFLAG (https://ctftime.org/team/1438)  
                **添加日历** : https://ctftime.org/event/2551.ics  
                
            ??? Quote "[M*CTF 2024 Quals](https://mctf.mtuci.ru/)"  
                [![](https://ctftime.org/media/events/6sKaJXoc4I4.jpg){ width="200" align=left }](https://mctf.mtuci.ru/)  
                **比赛名称** : [M*CTF 2024 Quals](https://mctf.mtuci.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-09 17:00:00 - 2024-11-10 17:00:00 UTC+8  
                **比赛权重** : 33.59  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2534.ics  
                
            ??? Quote "[HITCON CTF 2024 Final](http://ctf.hitcon.org/)"  
                [![](https://ctftime.org/media/events/eb3c04d49c017eda197bab74939403eb.jpg){ width="200" align=left }](http://ctf.hitcon.org/)  
                **比赛名称** : [HITCON CTF 2024 Final](http://ctf.hitcon.org/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-11-09 08:00:00 - 2024-11-10 16:00:00 UTC+8  
                **比赛权重** : 1.00  
                **赛事主办** : HITCON (https://ctftime.org/team/8299)  
                **添加日历** : https://ctftime.org/event/2523.ics  
                
            ??? Quote "[4T$ CTF](https://ctf.4ts.fr/)"  
                [![](https://ctftime.org/media/events/53b0900ddae2f59936bcc4eafc1458cf.jpg){ width="200" align=left }](https://ctf.4ts.fr/)  
                **比赛名称** : [4T$ CTF](https://ctf.4ts.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-09 02:00:00 - 2024-11-11 02:00:00 UTC+8  
                **比赛权重** : 24.40  
                **赛事主办** : 4T$ (https://ctftime.org/team/302295)  
                **添加日历** : https://ctftime.org/event/2545.ics  
                
            ??? Quote "[BlueHens CTF 2024](https://bluehens.ctfd.io/)"  
                [![](https://ctftime.org/media/events/UDCTF-logo_2.png){ width="200" align=left }](https://bluehens.ctfd.io/)  
                **比赛名称** : [BlueHens CTF 2024](https://bluehens.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-09 01:00:00 - 2024-11-10 13:00:00 UTC+8  
                **比赛权重** : 34.05  
                **赛事主办** : Blue Hens (https://ctftime.org/team/64660)  
                **添加日历** : https://ctftime.org/event/2512.ics  
                
            ??? Quote "[cruXipher 2024 - ATMoS '24, BITS Hyderabad](https://cruxipher.crux-bphc.com/)"  
                [![](https://ctftime.org/media/events/b93b251d190e41c5976063cdc151ac47.jpg){ width="200" align=left }](https://cruxipher.crux-bphc.com/)  
                **比赛名称** : [cruXipher 2024 - ATMoS '24, BITS Hyderabad](https://cruxipher.crux-bphc.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-08 20:30:00 - 2024-11-10 20:30:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : CRUx BPHC (https://ctftime.org/team/270645)  
                **添加日历** : https://ctftime.org/event/2559.ics  
                
            ??? Quote "[Metared Argentina CERTUNLP](https://ctf.cert.unlp.edu.ar/)"  
                [![](https://ctftime.org/media/events/unlp.png){ width="200" align=left }](https://ctf.cert.unlp.edu.ar/)  
                **比赛名称** : [Metared Argentina CERTUNLP](https://ctf.cert.unlp.edu.ar/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-08 19:00:00 - 2024-11-09 19:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : CERTUNLP (https://ctftime.org/team/89294)  
                **添加日历** : https://ctftime.org/event/2537.ics  
                
            ??? Quote "[HKCERT CTF 2024 (Qualifying Round)](https://platform.ctf.hkcert.org/)"  
                [![](https://ctftime.org/media/events/Screenshot_2024-08-13_100427.png){ width="200" align=left }](https://platform.ctf.hkcert.org/)  
                **比赛名称** : [HKCERT CTF 2024 (Qualifying Round)](https://platform.ctf.hkcert.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-08 18:00:00 - 2024-11-10 18:00:00 UTC+8  
                **比赛权重** : 61.22  
                **赛事主办** : Black Bauhinia, HKCERT (https://ctftime.org/team/83678, https://ctftime.org/team/134746)  
                **添加日历** : https://ctftime.org/event/2455.ics  
                
            ??? Quote "[BlackAlps CTF 2024](https://www.blackalps.ch/ba-24/ctf.php)"  
                [![](https://ctftime.org/media/events/blackalps-v5-logo-black_2.png){ width="200" align=left }](https://www.blackalps.ch/ba-24/ctf.php)  
                **比赛名称** : [BlackAlps CTF 2024](https://www.blackalps.ch/ba-24/ctf.php)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-08 03:15:00 - 2024-11-08 07:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BlackAlps (https://ctftime.org/team/89021)  
                **添加日历** : https://ctftime.org/event/2504.ics  
                
            ??? Quote "[CSAW CTF Final Round 2024](https://ctf.csaw.io/)"  
                [![](https://ctftime.org/media/events/CSAW15LOGO_COLOR_1.png){ width="200" align=left }](https://ctf.csaw.io/)  
                **比赛名称** : [CSAW CTF Final Round 2024](https://ctf.csaw.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-08 00:00:00 - 2024-11-09 12:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : NYUSEC (https://ctftime.org/team/439)  
                **添加日历** : https://ctftime.org/event/2567.ics  
                
            ??? Quote "[Sudocrypt v14.0](https://sudocrypt.com/)"  
                [![](https://ctftime.org/media/events/eac9d32fd3264f0c9dbe542e9f853468.png){ width="200" align=left }](https://sudocrypt.com/)  
                **比赛名称** : [Sudocrypt v14.0](https://sudocrypt.com/)  
                **比赛形式** : Hack quest  
                **比赛时间** : 2024-11-07 11:30:00 - 2024-11-08 23:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : exunclan (https://ctftime.org/team/83987)  
                **添加日历** : https://ctftime.org/event/2562.ics  
                
            ??? Quote "[RedShift.Eclipse 2 Quals](https://quals.o1d-bu7-go1d.ru/)"  
                [![](https://ctftime.org/media/events/IMG_5703.JPG){ width="200" align=left }](https://quals.o1d-bu7-go1d.ru/)  
                **比赛名称** : [RedShift.Eclipse 2 Quals](https://quals.o1d-bu7-go1d.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-03 20:00:00 - 2024-11-04 20:00:00 UTC+8  
                **比赛权重** : 23.40  
                **赛事主办** : o1d_bu7_go1d (https://ctftime.org/team/213673)  
                **添加日历** : https://ctftime.org/event/2541.ics  
                
            ??? Quote "[AlpacaHack Round 6 (Pwn)](https://alpacahack.com/ctfs/round-6)"  
                [![](https://ctftime.org/media/events/ctftime_7.png){ width="200" align=left }](https://alpacahack.com/ctfs/round-6)  
                **比赛名称** : [AlpacaHack Round 6 (Pwn)](https://alpacahack.com/ctfs/round-6)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-03 11:00:00 - 2024-11-03 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : AlpacaHack (https://ctftime.org/team/312315)  
                **添加日历** : https://ctftime.org/event/2501.ics  
                
            ??? Quote "[Pacific Hackers Conference 2024](https://www.phack.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://www.phack.org/)  
                **比赛名称** : [Pacific Hackers Conference 2024](https://www.phack.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-03 01:00:00 - 2024-11-03 09:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Pacific Hackers Association (https://ctftime.org/team/304096)  
                **添加日历** : https://ctftime.org/event/2453.ics  
                
            ??? Quote "[Hackers N' Hops](https://hackersnhops.ctfd.io/)"  
                [![](https://ctftime.org/media/events/HACKERSNHOPS.png){ width="200" align=left }](https://hackersnhops.ctfd.io/)  
                **比赛名称** : [Hackers N' Hops](https://hackersnhops.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 18:00:00 - 2024-11-04 02:00:00 UTC+8  
                **比赛权重** : 24.71  
                **赛事主办** : Hackers N' Hops (https://ctftime.org/team/119910)  
                **添加日历** : https://ctftime.org/event/2550.ics  
                
            ??? Quote "[Equinor CTF 2024](https://ctf.equinor.com/)"  
                [![](https://ctftime.org/media/events/ept_1.png){ width="200" align=left }](https://ctf.equinor.com/)  
                **比赛名称** : [Equinor CTF 2024](https://ctf.equinor.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 17:00:00 - 2024-11-03 03:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : EPT (https://ctftime.org/team/119480)  
                **添加日历** : https://ctftime.org/event/2292.ics  
                
            ??? Quote "[M*CTF 2024 Junior Quals](https://mctf.mtuci.ru/)"  
                [![](https://ctftime.org/media/events/NbK6tTQdEPQ.jpg){ width="200" align=left }](https://mctf.mtuci.ru/)  
                **比赛名称** : [M*CTF 2024 Junior Quals](https://mctf.mtuci.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 15:00:00 - 2024-11-03 01:00:00 UTC+8  
                **比赛权重** : 24.23  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2535.ics  
                
            ??? Quote "[USC CTF Fall 2024](https://usc.ctfd.io/)"  
                [![](https://ctftime.org/media/events/USC_CTF_Logo_Handdrawn.png){ width="200" align=left }](https://usc.ctfd.io/)  
                **比赛名称** : [USC CTF Fall 2024](https://usc.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 11:00:00 - 2024-11-04 12:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : 7r0j4npwn135 (https://ctftime.org/team/214221)  
                **添加日历** : https://ctftime.org/event/2543.ics  
                
            ??? Quote "[Hack The Vote 2024](https://hackthe.vote/)"  
                [![](https://ctftime.org/media/events/image_center.png){ width="200" align=left }](https://hackthe.vote/)  
                **比赛名称** : [Hack The Vote 2024](https://hackthe.vote/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 07:00:00 - 2024-11-04 07:00:00 UTC+8  
                **比赛权重** : 24.43  
                **赛事主办** : RPISEC (https://ctftime.org/team/572)  
                **添加日历** : https://ctftime.org/event/2498.ics  
                
            ??? Quote "[BUET CTF 2024](http://ctf.buetcsefest2024.com/)"  
                [![](https://ctftime.org/media/events/BUET_CTF_2024.png){ width="200" align=left }](http://ctf.buetcsefest2024.com/)  
                **比赛名称** : [BUET CTF 2024](http://ctf.buetcsefest2024.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-31 11:00:00 - 2024-10-31 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BUETSec (https://ctftime.org/team/357430)  
                **添加日历** : https://ctftime.org/event/2525.ics  
                
            ??? Quote "[TuxCTF V2](https://www.instagram.com/tuxpwners/)"  
                [![](https://ctftime.org/media/events/tuxpwners-logo.png){ width="200" align=left }](https://www.instagram.com/tuxpwners/)  
                **比赛名称** : [TuxCTF V2](https://www.instagram.com/tuxpwners/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-29 17:00:00 - 2024-10-29 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : TuxPwners (https://ctftime.org/team/274660)  
                **添加日历** : https://ctftime.org/event/2553.ics  
                
            ??? Quote "[The Cyber Jawara International 2024](https://international.cyberjawara.pro/)"  
                [![](https://ctftime.org/media/events/73b32f71c82304b9e3df7fe9dedada59-transformed.png){ width="200" align=left }](https://international.cyberjawara.pro/)  
                **比赛名称** : [The Cyber Jawara International 2024](https://international.cyberjawara.pro/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-27 10:00:00 - 2024-10-28 10:00:00 UTC+8  
                **比赛权重** : 23.62  
                **赛事主办** : SKSD (https://ctftime.org/team/211952)  
                **添加日历** : https://ctftime.org/event/2552.ics  
                
            ??? Quote "[Russian CTF Cup 2024 Qualifier](https://ctfcup.ru/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctfcup.ru/)  
                **比赛名称** : [Russian CTF Cup 2024 Qualifier](https://ctfcup.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 17:00:00 - 2024-10-27 17:00:00 UTC+8  
                **比赛权重** : 24.21  
                **赛事主办** : ctfcup (https://ctftime.org/team/203499)  
                **添加日历** : https://ctftime.org/event/2405.ics  
                
            ??? Quote "[Singapore AI CTF](https://www.tech.gov.sg/media/events/singapore-ai-ctf-2024/)"  
                [![](https://ctftime.org/media/events/SG_AI_CTF_FB-Post-4.png){ width="200" align=left }](https://www.tech.gov.sg/media/events/singapore-ai-ctf-2024/)  
                **比赛名称** : [Singapore AI CTF](https://www.tech.gov.sg/media/events/singapore-ai-ctf-2024/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 16:00:00 - 2024-10-28 16:00:00 UTC+8  
                **比赛权重** : 1.00  
                **赛事主办** : Singapore AI CTF (https://ctftime.org/team/357504)  
                **添加日历** : https://ctftime.org/event/2546.ics  
                
            ??? Quote "[UrchinSec Aware CTF](https://ctf.urchinsec.com/)"  
                [![](https://ctftime.org/media/events/URCHINSEC_free-file_1.png){ width="200" align=left }](https://ctf.urchinsec.com/)  
                **比赛名称** : [UrchinSec Aware CTF](https://ctf.urchinsec.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 15:00:00 - 2024-10-28 03:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : UrchinSec (https://ctftime.org/team/175663)  
                **添加日历** : https://ctftime.org/event/2527.ics  
                
            ??? Quote "[ISITDTU CTF 2024 Quals](https://ctf.isitdtu.com/)"  
                [![](https://ctftime.org/media/events/index_2.gif){ width="200" align=left }](https://ctf.isitdtu.com/)  
                **比赛名称** : [ISITDTU CTF 2024 Quals](https://ctf.isitdtu.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 10:00:00 - 2024-10-27 18:00:00 UTC+8  
                **比赛权重** : 51.00  
                **赛事主办** : ISITDTU (https://ctftime.org/team/8241)  
                **添加日历** : https://ctftime.org/event/2456.ics  
                
            ??? Quote "[SpookyCTF 2024](https://spookyctf.ctfd.io/)"  
                [![](https://ctftime.org/media/events/Spooky.png){ width="200" align=left }](https://spookyctf.ctfd.io/)  
                **比赛名称** : [SpookyCTF 2024](https://spookyctf.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 07:00:00 - 2024-10-28 07:30:00 UTC+8  
                **比赛权重** : 22.40  
                **赛事主办** : NICC (https://ctftime.org/team/214936)  
                **添加日历** : https://ctftime.org/event/2516.ics  
                
            ??? Quote "[HeroCTF v6](https://ctf.heroctf.fr/)"  
                [![](https://ctftime.org/media/events/HeroCTF_icon_500_1_1.png){ width="200" align=left }](https://ctf.heroctf.fr/)  
                **比赛名称** : [HeroCTF v6](https://ctf.heroctf.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 05:00:00 - 2024-10-28 07:00:00 UTC+8  
                **比赛权重** : 43.94  
                **赛事主办** : HeroCTF (https://ctftime.org/team/145166)  
                **添加日历** : https://ctftime.org/event/2496.ics  
                
            ??? Quote "[CipherHunt CTF](https://cipherhunt.ycfteam.in/)"  
                [![](https://ctftime.org/media/events/logo_1_2.png){ width="200" align=left }](https://cipherhunt.ycfteam.in/)  
                **比赛名称** : [CipherHunt CTF](https://cipherhunt.ycfteam.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-25 15:30:00 - 2024-10-26 15:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CypherLock (https://ctftime.org/team/356395)  
                **添加日历** : https://ctftime.org/event/2556.ics  
                
            ??? Quote "[Enigma Xplore 2.0 CTF](https://enigmaxplore.ctfd.io/)"  
                [![](https://ctftime.org/media/events/tf-logo-24-min.png){ width="200" align=left }](https://enigmaxplore.ctfd.io/)  
                **比赛名称** : [Enigma Xplore 2.0 CTF](https://enigmaxplore.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-24 21:30:00 - 2024-10-25 21:29:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Crispr_iiitn (https://ctftime.org/team/270138)  
                **添加日历** : https://ctftime.org/event/2555.ics  
                
            ??? Quote "[EngimaXplore2.0 2024](https://enigmaxplore.ctfd.io/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://enigmaxplore.ctfd.io/)  
                **比赛名称** : [EngimaXplore2.0 2024](https://enigmaxplore.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-24 20:29:59 - 2024-10-25 20:30:00 UTC+8  
                **比赛权重** : 24.58  
                **赛事主办** : Crispr_iiitn (https://ctftime.org/team/270138)  
                **添加日历** : https://ctftime.org/event/2524.ics  
                
            ??? Quote "[Z3R0 D4Y CTF](https://ctf.zerologon.co.in/)"  
                [![](https://ctftime.org/media/events/Logo.c1dfc2e2d63945110c8d.png){ width="200" align=left }](https://ctf.zerologon.co.in/)  
                **比赛名称** : [Z3R0 D4Y CTF](https://ctf.zerologon.co.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-24 17:00:00 - 2024-10-25 05:00:00 UTC+8  
                **比赛权重** : 24.77  
                **赛事主办** : Z3r0_l0g0n (https://ctftime.org/team/227457)  
                **添加日历** : https://ctftime.org/event/2529.ics  
                
            ??? Quote "[Hardwear.io NL 2024 Hardware CTF](https://hwctf.quarkslab.com/)"  
                [![](https://ctftime.org/media/events/logohwcolor_14.png){ width="200" align=left }](https://hwctf.quarkslab.com/)  
                **比赛名称** : [Hardwear.io NL 2024 Hardware CTF](https://hwctf.quarkslab.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-24 16:00:00 - 2024-10-25 19:50:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hardware CTF by Quarkslab (https://ctftime.org/team/274600)  
                **添加日历** : https://ctftime.org/event/2561.ics  
                
            ??? Quote "[Questcon CTF](https://questcon.ctfd.io/)"  
                [![](https://ctftime.org/media/events/Picsart_24-10-01_16-40-39-530_1_1.png){ width="200" align=left }](https://questcon.ctfd.io/)  
                **比赛名称** : [Questcon CTF](https://questcon.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-22 14:30:00 - 2024-10-23 14:30:00 UTC+8  
                **比赛权重** : 22.45  
                **赛事主办** : OWASP_PCCOE-CORE (https://ctftime.org/team/206360)  
                **添加日历** : https://ctftime.org/event/2505.ics  
                
            ??? Quote "[SAS CTF 2024 Finals](https://ctf.thesascon.com/)"  
                [![](https://ctftime.org/media/events/SAS24_2_1.png){ width="200" align=left }](https://ctf.thesascon.com/)  
                **比赛名称** : [SAS CTF 2024 Finals](https://ctf.thesascon.com/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-10-22 10:00:00 - 2024-10-22 21:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : SAS CREW (https://ctftime.org/team/283057)  
                **添加日历** : https://ctftime.org/event/2435.ics  
                
            ??? Quote "[SunshineCTF 2024](https://2024.sunshinectf.org/)"  
                [![](https://ctftime.org/media/events/sctf_logo_24.png){ width="200" align=left }](https://2024.sunshinectf.org/)  
                **比赛名称** : [SunshineCTF 2024](https://2024.sunshinectf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-19 22:00:00 - 2024-10-21 22:00:00 UTC+8  
                **比赛权重** : 38.57  
                **赛事主办** : Knightsec (https://ctftime.org/team/2500)  
                **添加日历** : https://ctftime.org/event/2485.ics  
                
            ??? Quote "[Cyber Odyssey 2024 : Qualifications](https://ctf.akasec.club/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.akasec.club/)  
                **比赛名称** : [Cyber Odyssey 2024 : Qualifications](https://ctf.akasec.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-19 20:37:00 - 2024-10-20 20:37:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Akasec (https://ctftime.org/team/107202)  
                **添加日历** : https://ctftime.org/event/2533.ics  
                
            ??? Quote "[DASCTF 2024 Golden October | Autumn is Strong, the Flames of War](https://buuoj.cn/match/matches/211)"  
                [![](https://ctftime.org/media/events/20241009170303.png){ width="200" align=left }](https://buuoj.cn/match/matches/211)  
                **比赛名称** : [DASCTF 2024 Golden October | Autumn is Strong, the Flames of War](https://buuoj.cn/match/matches/211)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-19 18:00:00 - 2024-10-20 02:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : DASCTF (https://ctftime.org/team/303691)  
                **添加日历** : https://ctftime.org/event/2536.ics  
                
            ??? Quote "[SCAN 2024 Digital Asset Tracing Challenge Second Round](https://ctf.scan.sx/)"  
                [![](https://ctftime.org/media/events/cd3d670407e320464308a9e5e9875cbb.png){ width="200" align=left }](https://ctf.scan.sx/)  
                **比赛名称** : [SCAN 2024 Digital Asset Tracing Challenge Second Round](https://ctf.scan.sx/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-19 08:00:00 - 2024-10-20 08:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : D Asset Inc. (https://ctftime.org/team/310109)  
                **添加日历** : https://ctftime.org/event/2548.ics  
                
            ??? Quote "[Hack.lu CTF 2024](https://flu.xxx/)"  
                [![](https://ctftime.org/media/events/logo-small.png){ width="200" align=left }](https://flu.xxx/)  
                **比赛名称** : [Hack.lu CTF 2024](https://flu.xxx/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-19 02:00:00 - 2024-10-21 02:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : FluxFingers (https://ctftime.org/team/551)  
                **添加日历** : https://ctftime.org/event/2438.ics  
                
            ??? Quote "[DEADFACE CTF 2024](https://ctf.deadface.io/)"  
                [![](https://ctftime.org/media/events/logo_deadface_ctf_2024.png){ width="200" align=left }](https://ctf.deadface.io/)  
                **比赛名称** : [DEADFACE CTF 2024](https://ctf.deadface.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-18 22:00:00 - 2024-10-20 08:00:00 UTC+8  
                **比赛权重** : 38.70  
                **赛事主办** : Cyber Hacktics (https://ctftime.org/team/127017)  
                **添加日历** : https://ctftime.org/event/2443.ics  
                
            ??? Quote "[Hackceler8 2024](https://capturetheflag.withgoogle.com/hackceler8)"  
                [![](https://ctftime.org/media/events/HCL8.png){ width="200" align=left }](https://capturetheflag.withgoogle.com/hackceler8)  
                **比赛名称** : [Hackceler8 2024](https://capturetheflag.withgoogle.com/hackceler8)  
                **比赛形式** : Hack quest  
                **比赛时间** : 2024-10-18 08:00:00 - 2024-10-21 07:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Google CTF (https://ctftime.org/team/23929)  
                **添加日历** : https://ctftime.org/event/2379.ics  
                
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
            "reg_time_start": "2099年11月15日 00:00",
            "reg_time_end": "2099年12月31日 00:00",
            "comp_time_start": "2099年12月31日 00:00",
            "comp_time_end": "2099年12月31日 00:00",
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
