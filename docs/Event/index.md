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
    
        === "国外赛事"
            ??? Quote "[AI CTF 2025](https://aictf.phdays.fun/)"  
                [![](https://ctftime.org/media/events/821553befa9c3ad5b7d17e5e1cbb36a7.png){ width="200" align=left }](https://aictf.phdays.fun/)  
                **比赛名称** : [AI CTF 2025](https://aictf.phdays.fun/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-23 01:00:00 - 2025-05-24 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : [TechnoPandas] (https://ctftime.org/team/1946)  
                **添加日历** : https://ctftime.org/event/2778.ics  
                
            ??? Quote "[Global Cyber Skills Benchmark CTF 2025: Operation Blackout](https://ctf.hackthebox.com/event/details/global-cyber-skills-benchmark-ctf-2025-operation-blackout-2174)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hackthebox.com/event/details/global-cyber-skills-benchmark-ctf-2025-operation-blackout-2174)  
                **比赛名称** : [Global Cyber Skills Benchmark CTF 2025: Operation Blackout](https://ctf.hackthebox.com/event/details/global-cyber-skills-benchmark-ctf-2025-operation-blackout-2174)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-23 21:00:00 - 2025-05-27 21:00:00 UTC+8  
                **比赛权重** : 24.00  
                **赛事主办** : Hack The Box (https://ctftime.org/team/136056)  
                **添加日历** : https://ctftime.org/event/2707.ics  
                
            ??? Quote "[HACK'OSINT CTF - 2025](https://ctf.hackolyte.fr/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hackolyte.fr/)  
                **比赛名称** : [HACK'OSINT CTF - 2025](https://ctf.hackolyte.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-24 03:00:00 - 2025-05-26 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hack'olyte (https://ctftime.org/team/222944)  
                **添加日历** : https://ctftime.org/event/2722.ics  
                
            ??? Quote "[NahamCon CTF 2025](https://ctf.nahamcon.com/)"  
                [![](https://ctftime.org/media/events/NAHAMCON-LOGOBRANDING_D3_A3.png){ width="200" align=left }](https://ctf.nahamcon.com/)  
                **比赛名称** : [NahamCon CTF 2025](https://ctf.nahamcon.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-24 03:00:00 - 2025-05-26 03:00:00 UTC+8  
                **比赛权重** : 53.77  
                **赛事主办** : JustHacking (https://ctftime.org/team/59573)  
                **添加日历** : https://ctftime.org/event/2782.ics  
                
            ??? Quote "[DaVinciCTF 2025](https://dvc.tf/)"  
                [![](https://ctftime.org/media/events/davincictf_vectorized.png){ width="200" align=left }](https://dvc.tf/)  
                **比赛名称** : [DaVinciCTF 2025](https://dvc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-24 18:00:00 - 2025-05-26 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : DaVinciCode (https://ctftime.org/team/112645)  
                **添加日历** : https://ctftime.org/event/2675.ics  
                
            ??? Quote "[SAS CTF 2025 Quals](https://ctf.thesascon.com/)"  
                [![](https://ctftime.org/media/events/SAS25_new.png){ width="200" align=left }](https://ctf.thesascon.com/)  
                **比赛名称** : [SAS CTF 2025 Quals](https://ctf.thesascon.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-24 20:00:00 - 2025-05-25 20:00:00 UTC+8  
                **比赛权重** : 20.72  
                **赛事主办** : SAS CREW (https://ctftime.org/team/283057)  
                **添加日历** : https://ctftime.org/event/2636.ics  
                
            ??? Quote "[D^3CTF 2025](https://d3c.tf/)"  
                [![](https://ctftime.org/media/events/ddd_1.png){ width="200" align=left }](https://d3c.tf/)  
                **比赛名称** : [D^3CTF 2025](https://d3c.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-30 20:00:00 - 2025-05-31 20:00:00 UTC+8  
                **比赛权重** : 54.67  
                **赛事主办** : D^3CTF Organizers (https://ctftime.org/team/91096)  
                **添加日历** : https://ctftime.org/event/2770.ics  
                
            ??? Quote "[Hardwear.io USA 2025 Hardware CTF](https://hwctf.quarkslab.com/)"  
                [![](https://ctftime.org/media/events/logohwcolor_15.png){ width="200" align=left }](https://hwctf.quarkslab.com/)  
                **比赛名称** : [Hardwear.io USA 2025 Hardware CTF](https://hwctf.quarkslab.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-31 01:00:00 - 2025-06-01 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hardware CTF by Quarkslab (https://ctftime.org/team/274600)  
                **添加日历** : https://ctftime.org/event/2788.ics  
                
            ??? Quote "[N0PSctf](https://ctf.nops.re/)"  
                [![](https://ctftime.org/media/events/logo-news.png){ width="200" align=left }](https://ctf.nops.re/)  
                **比赛名称** : [N0PSctf](https://ctf.nops.re/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-31 16:00:00 - 2025-06-02 04:00:00 UTC+8  
                **比赛权重** : 24.34  
                **赛事主办** : NOPS (https://ctftime.org/team/4056)  
                **添加日历** : https://ctftime.org/event/2486.ics  
                
            ??? Quote "[[POSTPONED] Internet Festival 2025 CTF Quals](https://ifctf.fibonhack.it/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ifctf.fibonhack.it/)  
                **比赛名称** : [[POSTPONED] Internet Festival 2025 CTF Quals](https://ifctf.fibonhack.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-31 19:00:00 - 2025-06-01 19:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : fibonhack (https://ctftime.org/team/117538)  
                **添加日历** : https://ctftime.org/event/2605.ics  
                
            ??? Quote "[Grey Cat The Flag 2025](https://ctf.nusgreyhats.org/)"  
                [![](https://ctftime.org/media/events/New_Project_1.jpg){ width="200" align=left }](https://ctf.nusgreyhats.org/)  
                **比赛名称** : [Grey Cat The Flag 2025](https://ctf.nusgreyhats.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-31 20:00:00 - 2025-06-01 20:00:00 UTC+8  
                **比赛权重** : 32.92  
                **赛事主办** : NUS GreyHats (https://ctftime.org/team/16740)  
                **添加日历** : https://ctftime.org/event/2765.ics  
                
            ??? Quote "[MindBreak 2025 by ESGI](https://m1ndbr34k.fr/)"  
                [![](https://ctftime.org/media/events/image_7s.png){ width="200" align=left }](https://m1ndbr34k.fr/)  
                **比赛名称** : [MindBreak 2025 by ESGI](https://m1ndbr34k.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-07 05:00:00 - 2025-06-07 14:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ESGI (https://ctftime.org/team/3151)  
                **添加日历** : https://ctftime.org/event/2766.ics  
                
            ??? Quote "[Season V, US Cyber Open Beginner's Game Room CTF](https://www.uscybergames.com/)"  
                [![](https://ctftime.org/media/events/2021-04-USCG_logos_cybergames.png){ width="200" align=left }](https://www.uscybergames.com/)  
                **比赛名称** : [Season V, US Cyber Open Beginner's Game Room CTF](https://www.uscybergames.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-07 05:30:00 - 2025-06-20 07:59:59 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : PlayCyber (https://ctftime.org/team/165788)  
                **添加日历** : https://ctftime.org/event/2716.ics  
                
            ??? Quote "[BCACTF 6.0](https://www.bcactf.com/)"  
                [![](https://ctftime.org/media/events/CO.png){ width="200" align=left }](https://www.bcactf.com/)  
                **比赛名称** : [BCACTF 6.0](https://www.bcactf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-07 09:00:00 - 2025-06-10 09:00:00 UTC+8  
                **比赛权重** : 62.97  
                **赛事主办** : BCACTF (https://ctftime.org/team/81702)  
                **添加日历** : https://ctftime.org/event/2609.ics  
                
            ??? Quote "[DIVER OSINT CTF 2025](https://ctfd.diverctf.org/)"  
                [![](https://ctftime.org/media/events/logo_circle.png){ width="200" align=left }](https://ctfd.diverctf.org/)  
                **比赛名称** : [DIVER OSINT CTF 2025](https://ctfd.diverctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-07 11:00:00 - 2025-06-08 11:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : diver_osint (https://ctftime.org/team/299569)  
                **添加日历** : https://ctftime.org/event/2751.ics  
                
            ??? Quote "[bi0sCTF 2025](https://ctf.bi0s.in/)"  
                [![](https://ctftime.org/media/events/image_2025-03-25_143431330.png){ width="200" align=left }](https://ctf.bi0s.in/)  
                **比赛名称** : [bi0sCTF 2025](https://ctf.bi0s.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-07 13:30:00 - 2025-06-09 01:30:00 UTC+8  
                **比赛权重** : 95.79  
                **赛事主办** : bi0s (https://ctftime.org/team/662)  
                **添加日历** : https://ctftime.org/event/2672.ics  
                
            ??? Quote "[Goldrush Gauntlet 2025](https://ggctf.cyberhawks.org/)"  
                [![](https://ctftime.org/media/events/CyberHawks_Logo3.png){ width="200" align=left }](https://ggctf.cyberhawks.org/)  
                **比赛名称** : [Goldrush Gauntlet 2025](https://ggctf.cyberhawks.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-07 21:00:00 - 2025-06-09 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CyberHawks at UNG (https://ctftime.org/team/368776)  
                **添加日历** : https://ctftime.org/event/2691.ics  
                
            ??? Quote "[DFIR Labs CTF by The DFIR Report](https://thedfirreport.com/services/dfir-labs/ctf/)"  
                [![](https://ctftime.org/media/events/DFIR_Labs_Icon_1.png){ width="200" align=left }](https://thedfirreport.com/services/dfir-labs/ctf/)  
                **比赛名称** : [DFIR Labs CTF by The DFIR Report](https://thedfirreport.com/services/dfir-labs/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-08 00:30:00 - 2025-06-08 04:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : The DFIR Report (https://ctftime.org/team/309500)  
                **添加日历** : https://ctftime.org/event/2750.ics  
                
            ??? Quote "[Season V, US Cyber Open Competitive CTF](https://www.uscybergames.com/)"  
                [![](https://ctftime.org/media/events/2021-04-USCG_logos_cybergames_1.png){ width="200" align=left }](https://www.uscybergames.com/)  
                **比赛名称** : [Season V, US Cyber Open Competitive CTF](https://www.uscybergames.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-10 04:00:00 - 2025-06-20 07:59:59 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : PlayCyber (https://ctftime.org/team/165788)  
                **添加日历** : https://ctftime.org/event/2717.ics  
                
            ??? Quote "[AMSI CTF 2025](https://amsi-sorbonne.fr/)"  
                [![](https://ctftime.org/media/events/amsi_logo_animated.gif){ width="200" align=left }](https://amsi-sorbonne.fr/)  
                **比赛名称** : [AMSI CTF 2025](https://amsi-sorbonne.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-14 04:00:00 - 2025-06-15 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : AMSI CTF Team (https://ctftime.org/team/383289)  
                **添加日历** : https://ctftime.org/event/2790.ics  
                
            ??? Quote "[Crypto CTF 2025](https://cr.yp.toc.tf/)"  
                [![](https://ctftime.org/media/events/cryptoctf_1.jpg){ width="200" align=left }](https://cr.yp.toc.tf/)  
                **比赛名称** : [Crypto CTF 2025](https://cr.yp.toc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-14 14:00:00 - 2025-06-15 14:00:00 UTC+8  
                **比赛权重** : 88.25  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2577.ics  
                
            ??? Quote "[Midnight Sun CTF 2025 Finals](https://play.midnightsunctf.com/)"  
                [![](https://ctftime.org/media/events/midnightsun_2024_log_TRIMMEDo_2.png){ width="200" align=left }](https://play.midnightsunctf.com/)  
                **比赛名称** : [Midnight Sun CTF 2025 Finals](https://play.midnightsunctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-14 18:00:00 - 2025-06-15 18:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : HackingForSoju (https://ctftime.org/team/3208)  
                **添加日历** : https://ctftime.org/event/2772.ics  
                
            ??? Quote "[CyberSci Nationals 2025](https://cybersecuritychallenge.ca/)"  
                [![](https://ctftime.org/media/events/fa9a3545467f5a51f11b512adb2f6183.png){ width="200" align=left }](https://cybersecuritychallenge.ca/)  
                **比赛名称** : [CyberSci Nationals 2025](https://cybersecuritychallenge.ca/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-14 21:00:00 - 2025-06-16 07:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : 0xD13A (https://ctftime.org/team/31765)  
                **添加日历** : https://ctftime.org/event/2689.ics  
                
            ??? Quote "[GPN CTF 2025](https://2025.ctf.kitctf.de/)"  
                [![](https://ctftime.org/media/events/2acc1e50ba516aa0bc42a61798cfa10d_1.png){ width="200" align=left }](https://2025.ctf.kitctf.de/)  
                **比赛名称** : [GPN CTF 2025](https://2025.ctf.kitctf.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-20 18:00:00 - 2025-06-22 06:00:00 UTC+8  
                **比赛权重** : 46.00  
                **赛事主办** : KITCTF (https://ctftime.org/team/7221)  
                **添加日历** : https://ctftime.org/event/2694.ics  
                
            ??? Quote "[GMO Cybersecurity Contest - IERAE CTF 2025](https://gmo-cybersecurity.com/event/ieraectf25/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://gmo-cybersecurity.com/event/ieraectf25/)  
                **比赛名称** : [GMO Cybersecurity Contest - IERAE CTF 2025](https://gmo-cybersecurity.com/event/ieraectf25/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-21 14:00:00 - 2025-06-22 14:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ierae (https://ctftime.org/team/224122)  
                **添加日历** : https://ctftime.org/event/2655.ics  
                
            ??? Quote "[MaltaCTF 2025 Quals](https://ctf.mt/)"  
                [![](https://ctftime.org/media/events/MaltaCTF.png){ width="200" align=left }](https://ctf.mt/)  
                **比赛名称** : [MaltaCTF 2025 Quals](https://ctf.mt/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-21 15:00:00 - 2025-06-22 15:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Friendly Maltese Citizens (https://ctftime.org/team/220769)  
                **添加日历** : https://ctftime.org/event/2776.ics  
                
            ??? Quote "[cornCTF 2025](https://cornc.tf/)"  
                [![](https://ctftime.org/media/events/cornctf.png){ width="200" align=left }](https://cornc.tf/)  
                **比赛名称** : [cornCTF 2025](https://cornc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-21 20:00:00 - 2025-06-22 20:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : pwnlentoni (https://ctftime.org/team/230457)  
                **添加日历** : https://ctftime.org/event/2762.ics  
                
            ??? Quote "[Google Capture The Flag 2025](https://g.co/ctf)"  
                [![](https://ctftime.org){ width="200" align=left }](https://g.co/ctf)  
                **比赛名称** : [Google Capture The Flag 2025](https://g.co/ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-28 02:00:00 - 2025-06-30 02:00:00 UTC+8  
                **比赛权重** : 97.17  
                **赛事主办** : Google CTF (https://ctftime.org/team/23929)  
                **添加日历** : https://ctftime.org/event/2718.ics  
                
            ??? Quote "[BSides Mumbai CTF 2025](https://ctf.bsidesmumbai.in/)"  
                [![](https://ctftime.org/media/events/Layed1.B3529NWW_3.png){ width="200" align=left }](https://ctf.bsidesmumbai.in/)  
                **比赛名称** : [BSides Mumbai CTF 2025](https://ctf.bsidesmumbai.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-06-28 18:00:00 - 2025-06-29 18:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : DarkArmy (https://ctftime.org/team/26569)  
                **添加日历** : https://ctftime.org/event/2781.ics  
                
            ??? Quote "[R3CTF 2025](https://ctf2025.r3kapig.com/)"  
                [![](https://ctftime.org/media/events/111_1.png){ width="200" align=left }](https://ctf2025.r3kapig.com/)  
                **比赛名称** : [R3CTF 2025](https://ctf2025.r3kapig.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-07-05 10:00:00 - 2025-07-07 10:00:00 UTC+8  
                **比赛权重** : 24.50  
                **赛事主办** : r3kapig (https://ctftime.org/team/58979)  
                **添加日历** : https://ctftime.org/event/2731.ics  
                
            ??? Quote "[L3akCTF 2025](https://ctf.l3ak.team/)"  
                [![](https://ctftime.org/media/events/l3ak-color-transparent.png){ width="200" align=left }](https://ctf.l3ak.team/)  
                **比赛名称** : [L3akCTF 2025](https://ctf.l3ak.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-07-12 01:00:00 - 2025-07-14 01:00:00 UTC+8  
                **比赛权重** : 24.43  
                **赛事主办** : L3ak (https://ctftime.org/team/220336)  
                **添加日历** : https://ctftime.org/event/2629.ics  
                
            ??? Quote "[UIUCTF 2025](https://uiuc.tf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://uiuc.tf/)  
                **比赛名称** : [UIUCTF 2025](https://uiuc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-07-12 08:00:00 - 2025-07-14 08:00:00 UTC+8  
                **比赛权重** : 91.43  
                **赛事主办** : SIGPwny (https://ctftime.org/team/27763)  
                **添加日历** : https://ctftime.org/event/2640.ics  
                
            ??? Quote "[smileyCTF 2025](https://play.ctf.gg/)"  
                [![](https://ctftime.org/media/events/smiley.png){ width="200" align=left }](https://play.ctf.gg/)  
                **比赛名称** : [smileyCTF 2025](https://play.ctf.gg/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-07-12 09:00:00 - 2025-07-14 09:00:00 UTC+8  
                **比赛权重** : 48.61  
                **赛事主办** : .;,;. (https://ctftime.org/team/222911)  
                **添加日历** : https://ctftime.org/event/2591.ics  
                
            ??? Quote "[DownUnderCTF 2025](https://play.duc.tf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://play.duc.tf/)  
                **比赛名称** : [DownUnderCTF 2025](https://play.duc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-07-18 17:30:00 - 2025-07-20 17:30:00 UTC+8  
                **比赛权重** : 91.66  
                **赛事主办** : DownUnderCTF (https://ctftime.org/team/126400)  
                **添加日历** : https://ctftime.org/event/2669.ics  
                
            ??? Quote "[BDSec CTF 2025](https://bdsec-ctf.com/)"  
                [![](https://ctftime.org/media/events/bdsec-ctf-logo.png){ width="200" align=left }](https://bdsec-ctf.com/)  
                **比赛名称** : [BDSec CTF 2025](https://bdsec-ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-07-20 23:00:00 - 2025-07-21 23:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Knight Squad (https://ctftime.org/team/141739)  
                **添加日历** : https://ctftime.org/event/2784.ics  
                
            ??? Quote "[DeadSec CTF 2025](https://www.deadsec.xyz/)"  
                [![](https://ctftime.org/media/events/Picture1_2.png){ width="200" align=left }](https://www.deadsec.xyz/)  
                **比赛名称** : [DeadSec CTF 2025](https://www.deadsec.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-07-26 06:00:00 - 2025-07-28 06:00:00 UTC+8  
                **比赛权重** : 31.29  
                **赛事主办** : DeadSec (https://ctftime.org/team/19339)  
                **添加日历** : https://ctftime.org/event/2631.ics  
                
            ??? Quote "[World Wide CTF 2025](https://wwctf.com/)"  
                [![](https://ctftime.org/media/events/logobg_1.png){ width="200" align=left }](https://wwctf.com/)  
                **比赛名称** : [World Wide CTF 2025](https://wwctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-07-26 20:00:00 - 2025-07-28 20:00:00 UTC+8  
                **比赛权重** : 24.48  
                **赛事主办** : 🐧‎ (https://ctftime.org/team/283853)  
                **添加日历** : https://ctftime.org/event/2753.ics  
                
            ??? Quote "[idekCTF 2025](https://ctf.idek.team/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.idek.team/)  
                **比赛名称** : [idekCTF 2025](https://ctf.idek.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-08-02 08:00:00 - 2025-08-04 08:00:00 UTC+8  
                **比赛权重** : 52.06  
                **赛事主办** : idek (https://ctftime.org/team/157039)  
                **添加日历** : https://ctftime.org/event/2746.ics  
                
            ??? Quote "[justCTF 2025 teaser](http://2025.justctf.team/)"  
                [![](https://ctftime.org/media/events/b6f4bd9df7efba86c9b2d4eea9f8bc74.png){ width="200" align=left }](http://2025.justctf.team/)  
                **比赛名称** : [justCTF 2025 teaser](http://2025.justctf.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-08-02 14:00:00 - 2025-08-04 03:00:00 UTC+8  
                **比赛权重** : 97.20  
                **赛事主办** : justCatTheFish (https://ctftime.org/team/33893)  
                **添加日历** : https://ctftime.org/event/2711.ics  
                
            ??? Quote "[GaianSpace CTF 2025](https://gaian.space/ctf)"  
                [![](https://ctftime.org/media/events/gaianspace-logo-new.png){ width="200" align=left }](https://gaian.space/ctf)  
                **比赛名称** : [GaianSpace CTF 2025](https://gaian.space/ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-08-08 22:00:00 - 2025-08-12 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : GaianSpace (https://ctftime.org/team/373034)  
                **添加日历** : https://ctftime.org/event/2732.ics  
                
            ??? Quote "[WHY2025 CTF](https://ctf.why2025.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.why2025.org/)  
                **比赛名称** : [WHY2025 CTF](https://ctf.why2025.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-08-09 00:00:00 - 2025-08-12 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Eindbazen (https://ctftime.org/team/322)  
                **添加日历** : https://ctftime.org/event/2680.ics  
                
            ??? Quote "[jailCTF 2025](https://ctf.pyjail.club/)"  
                [![](https://ctftime.org/media/events/jailctf.png){ width="200" align=left }](https://ctf.pyjail.club/)  
                **比赛名称** : [jailCTF 2025](https://ctf.pyjail.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-08-16 04:00:00 - 2025-08-19 04:00:00 UTC+8  
                **比赛权重** : 24.88  
                **赛事主办** : jailctf (https://ctftime.org/team/311088)  
                **添加日历** : https://ctftime.org/event/2737.ics  
                
            ??? Quote "[SekaiCTF 2025](https://ctf.sekai.team/)"  
                [![](https://ctftime.org/media/events/sekai2_SEKAI_CTF_Square_Black_BG.r_1_1_1.png){ width="200" align=left }](https://ctf.sekai.team/)  
                **比赛名称** : [SekaiCTF 2025](https://ctf.sekai.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-08-16 09:00:00 - 2025-08-18 09:00:00 UTC+8  
                **比赛权重** : 55.00  
                **赛事主办** : Project Sekai (https://ctftime.org/team/169557)  
                **添加日历** : https://ctftime.org/event/2683.ics  
                
            ??? Quote "[RCTF 2025](https://rctf.rois.io/)"  
                [![](https://ctftime.org/media/events/rois.jpg){ width="200" align=left }](https://rctf.rois.io/)  
                **比赛名称** : [RCTF 2025](https://rctf.rois.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-08-20 18:00:00 - 2025-08-22 18:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ROIS (https://ctftime.org/team/6476)  
                **添加日历** : https://ctftime.org/event/2771.ics  
                
            ??? Quote "[HITCON CTF 2025](http://ctf.hitcon.org/)"  
                [![](https://ctftime.org/media/events/83e99b182fd8f8a8e11a44a7c2f44557.png){ width="200" align=left }](http://ctf.hitcon.org/)  
                **比赛名称** : [HITCON CTF 2025](http://ctf.hitcon.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-08-22 22:00:00 - 2025-08-24 22:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : HITCON (https://ctftime.org/team/8299)  
                **添加日历** : https://ctftime.org/event/2783.ics  
                
            ??? Quote "[NNS CTF 2025](https://nnsc.tf/)"  
                [![](https://ctftime.org/media/events/Logo_D.png){ width="200" align=left }](https://nnsc.tf/)  
                **比赛名称** : [NNS CTF 2025](https://nnsc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-08-30 00:00:00 - 2025-09-01 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Norske Nøkkelsnikere (https://ctftime.org/team/222749)  
                **添加日历** : https://ctftime.org/event/2684.ics  
                
            ??? Quote "[corCTF 2025](https://ctf.cor.team/)"  
                [![](https://ctftime.org/media/events/corctflogo_4.png){ width="200" align=left }](https://ctf.cor.team/)  
                **比赛名称** : [corCTF 2025](https://ctf.cor.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-08-30 08:00:00 - 2025-09-01 08:00:00 UTC+8  
                **比赛权重** : 82.00  
                **赛事主办** : Crusaders of Rust (https://ctftime.org/team/132628)  
                **添加日历** : https://ctftime.org/event/2763.ics  
                
            ??? Quote "[ASIS CTF Quals 2025](https://asisctf.com/)"  
                [![](https://ctftime.org/media/events/asisctf_1.jpg){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Quals 2025](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-09-06 22:00:00 - 2025-09-07 22:00:00 UTC+8  
                **比赛权重** : 96.29  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2612.ics  
                
            ??? Quote "[MaltaCTF 2025 Finals](https://ctf.mt/)"  
                [![](https://ctftime.org/media/events/MaltaCTF_1.png){ width="200" align=left }](https://ctf.mt/)  
                **比赛名称** : [MaltaCTF 2025 Finals](https://ctf.mt/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-09-13 18:00:00 - 2025-09-14 18:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Friendly Maltese Citizens (https://ctftime.org/team/220769)  
                **添加日历** : https://ctftime.org/event/2777.ics  
                
            ??? Quote "[CrewCTF 2025](https://2025.crewc.tf/)"  
                [![](https://ctftime.org/media/events/thc_icon_processed.png){ width="200" align=left }](https://2025.crewc.tf/)  
                **比赛名称** : [CrewCTF 2025](https://2025.crewc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-09-20 05:00:00 - 2025-09-22 05:00:00 UTC+8  
                **比赛权重** : 38.93  
                **赛事主办** : thehackerscrew (https://ctftime.org/team/85618)  
                **添加日历** : https://ctftime.org/event/2704.ics  
                
            ??? Quote "[Iran Tech Olympics CTF 2025](https://ctf.olympics.tech/)"  
                [![](https://ctftime.org/media/events/tech_olympic_logo.jpg){ width="200" align=left }](https://ctf.olympics.tech/)  
                **比赛名称** : [Iran Tech Olympics CTF 2025](https://ctf.olympics.tech/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-09-26 21:00:00 - 2025-09-28 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2775.ics  
                
            ??? Quote "[FAUST CTF 2025](https://2025.faustctf.net/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://2025.faustctf.net/)  
                **比赛名称** : [FAUST CTF 2025](https://2025.faustctf.net/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2025-09-27 20:00:00 - 2025-09-28 05:00:00 UTC+8  
                **比赛权重** : 92.50  
                **赛事主办** : FAUST (https://ctftime.org/team/550)  
                **添加日历** : https://ctftime.org/event/2780.ics  
                
            ??? Quote "[Equinor CTF 2025](https://ctf.equinor.com/)"  
                [![](https://ctftime.org/media/events/ept_2.png){ width="200" align=left }](https://ctf.equinor.com/)  
                **比赛名称** : [Equinor CTF 2025](https://ctf.equinor.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-08 17:00:00 - 2025-11-09 03:00:00 UTC+8  
                **比赛权重** : 37.00  
                **赛事主办** : EPT (https://ctftime.org/team/119480)  
                **添加日历** : https://ctftime.org/event/2646.ics  
                
            ??? Quote "[Platypwn 2025](https://platypwnies.de/events/platypwn/)"  
                [![](https://ctftime.org/media/events/platypwnies-512_1.png){ width="200" align=left }](https://platypwnies.de/events/platypwn/)  
                **比赛名称** : [Platypwn 2025](https://platypwnies.de/events/platypwn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-15 20:00:00 - 2025-11-16 20:00:00 UTC+8  
                **比赛权重** : 33.29  
                **赛事主办** : Platypwnies (https://ctftime.org/team/112550)  
                **添加日历** : https://ctftime.org/event/2606.ics  
                
            ??? Quote "[GlacierCTF 2025](https://glacierctf.com/)"  
                [![](https://ctftime.org/media/events/glacierlogo.png){ width="200" align=left }](https://glacierctf.com/)  
                **比赛名称** : [GlacierCTF 2025](https://glacierctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-23 02:00:00 - 2025-11-24 02:00:00 UTC+8  
                **比赛权重** : 52.57  
                **赛事主办** : LosFuzzys (https://ctftime.org/team/8323)  
                **添加日历** : https://ctftime.org/event/2714.ics  
                
            ??? Quote "[WP CTF 2025](https://wpctf.it/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://wpctf.it/)  
                **比赛名称** : [WP CTF 2025](https://wpctf.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-29 16:00:00 - 2025-11-30 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : WP CTF (https://ctftime.org/team/303099)  
                **添加日历** : https://ctftime.org/event/2764.ics  
                
            ??? Quote "[ASIS CTF Final 2025](https://asisctf.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Final 2025](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-27 22:00:00 - 2025-12-28 22:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2613.ics  
                
            ??? Quote "[PascalCTF Beginners 2026](https://ctf.pascalctf.it/)"  
                [![](https://ctftime.org/media/events/log.jpg){ width="200" align=left }](https://ctf.pascalctf.it/)  
                **比赛名称** : [PascalCTF Beginners 2026](https://ctf.pascalctf.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-31 16:00:00 - 2026-02-01 16:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Paolo (https://ctftime.org/team/263145)  
                **添加日历** : https://ctftime.org/event/2767.ics  
                
            ??? Quote "[Midnight Sun CTF 2026 Quals](https://play.midnightsunctf.com/)"  
                [![](https://ctftime.org/media/events/midnightsun_2024_log_TRIMMEDo.png){ width="200" align=left }](https://play.midnightsunctf.com/)  
                **比赛名称** : [Midnight Sun CTF 2026 Quals](https://play.midnightsunctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-04-11 18:00:00 - 2026-04-12 18:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HackingForSoju (https://ctftime.org/team/3208)  
                **添加日历** : https://ctftime.org/event/2773.ics  
                
    === "*正在进行*"
        === "国内赛事"
            ??? Quote "[2025年能源网络安全大赛](https://www.cers.org.cn/site/content/883b36f00aff466fa37efcef0c074915.html)"  
                **比赛名称** : [2025年能源网络安全大赛](https://www.cers.org.cn/site/content/883b36f00aff466fa37efcef0c074915.html)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2025年3月1日 00:00 - 2025年3月31日 23:59  
                **比赛时间** : 2025年4月1日 00:00 - 2025年6月30日 23:59  
                **其他说明** : 2025年能源网络安全大赛由中国能源研究会主办，面向电网企业、发电及电力建设企业、石油石化企业、煤炭企业等单位网络安全技术、运维和管理人员，以及国内网络安全领域知名高校、科研机构、产业单位等代表。报名截止日期为2025年3月31日，可通过扫描二维码下载报名表并发送至icc@cers.org.cn邮箱。联系人包括屈庆红、李理和陈炜，可通过电话或邮箱进行咨询。  
                
        === "国外赛事"
            ??? Quote "[CyberGame 2025](https://cybergame.sk/)"  
                [![](https://ctftime.org/media/events/cybergame.png){ width="200" align=left }](https://cybergame.sk/)  
                **比赛名称** : [CyberGame 2025](https://cybergame.sk/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-01 08:00:00 - 2025-06-10 07:59:59 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : SK-CERT (https://ctftime.org/team/378916)  
                **添加日历** : https://ctftime.org/event/2774.ics  
                
            ??? Quote "[BYUCTF 2025](https://ctfd.cyberjousting.com/)"  
                [![](https://ctftime.org/media/events/byuctf.jpg){ width="200" align=left }](https://ctfd.cyberjousting.com/)  
                **比赛名称** : [BYUCTF 2025](https://ctfd.cyberjousting.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-17 10:00:00 - 2025-05-18 10:00:00 UTC+8  
                **比赛权重** : 36.94  
                **赛事主办** : BYU Cyberia (https://ctftime.org/team/155711)  
                **添加日历** : https://ctftime.org/event/2715.ics  
                
            ??? Quote "[Midnight Sun CTF 2025 Quals](https://midnightsunctf.com/)"  
                [![](https://ctftime.org/media/events/midnightsun_2024_log_TRIMMEDo_1.png){ width="200" align=left }](https://midnightsunctf.com/)  
                **比赛名称** : [Midnight Sun CTF 2025 Quals](https://midnightsunctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-17 20:00:00 - 2025-05-18 20:00:00 UTC+8  
                **比赛权重** : 53.00  
                **赛事主办** : HackingForSoju (https://ctftime.org/team/3208)  
                **添加日历** : https://ctftime.org/event/2632.ics  
                
    === "*已经结束*"
        === "国内赛事"
            ??? Quote "[ACTF 2025](https://actf2025.xctf.org.cn/)"  
                **比赛名称** : [ACTF 2025](https://actf2025.xctf.org.cn/)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2025年04月16日 08:59 - 2025年04月26日 08:59  
                **比赛时间** : 2025年04月26日 09:00 - 2025年04月27日 09:00  
                **其他说明** : ACTF 2025由XCTF联赛主办，比赛时间为2025年4月26日至4月27日，更多信息请访问官方网站。选手可通过QQ群512066352进行沟通交流。  
                
            ??? Quote "[TGCTF 2025](https://tgctf.woooo.tech/)"  
                **比赛名称** : [TGCTF 2025](https://tgctf.woooo.tech/)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2025年04月12日 09:00 - 2025年04月11日 21:00  
                **比赛时间** : 2025年04月12日 09:00 - 2025年04月13日 21:00  
                **其他说明** : TGCTF 2025（杭州师范大学第六届网络与信息安全竞赛）由杭州师范大学主办，报名截止时间为2025年4月11日21点，比赛时间为4月12号9点至4月13号21点，共36小时。  
                
            ??? Quote "[商丘师范学院第四届网络安全及信息对抗大赛（公开赛道）](www.qsnctf.com)"  
                **比赛名称** : [商丘师范学院第四届网络安全及信息对抗大赛（公开赛道）](www.qsnctf.com)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2025年04月01日 00:00 - 2025年04月07日 09:59  
                **比赛时间** : 2025年04月07日 10:00 - 2025年04月13日 17:00  
                **其他说明** : 商丘师范学院第四届网络安全及信息对抗大赛（公开赛道）是一个由商丘师范学院主办的线上个人赛。报名开始时间为2025年04月01日 00:00，报名结束时间为2025年04月07日 09:59。比赛时间为2025年04月07日 10:00至2025年04月13日 17:00。更多信息请访问比赛官网www.qsnctf.com，或加入QQ群1021827215进行咨询。比赛设有证书和周边奖励。  
                
            ??? Quote "[XYCTF 2025](xyctf.top)"  
                **比赛名称** : [XYCTF 2025](xyctf.top)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2025年04月04日 10:00 - 2025年04月07日 19:59  
                **比赛时间** : 2025年04月04日 10:00 - 2025年04月07日 20:00  
                **其他说明** : XYCTF 2025 官方邮箱为ctf_xiao@163.com，赛事QQ群为798794707。  
                
            ??? Quote "[HellCTF 2025](ctfplus.cn)"  
                **比赛名称** : [HellCTF 2025](ctfplus.cn)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2025年04月03日 00:00 - 2025年04月04日 14:43  
                **比赛时间** : 2025年04月04日 14:44 - 2025年04月06日 14:44  
                **其他说明** : HellCTF 2025是一个公开赛，主办方为公开赛。比赛群为879334917。时候赚取你来生的财富了! 最高奖励1,000,000.000.000元，奖品设置包括每题一血解出者每人一份R.E.D.O.(Steam版本)，每题所有解出者中抽取两位获得大额冥币(可代烧)，所有参赛者中抽取两位获得纸扎大house(可代烧)。  
                
            ??? Quote "[NCTF 2024](https://nctf.exp10it.cn/)"  
                **比赛名称** : [NCTF 2024](https://nctf.exp10it.cn/)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2025年03月22日 09:00 - 2025年03月22日 08:59  
                **比赛时间** : 2025年03月22日 09:00 - 2025年03月23日 21:00  
                **其他说明** : NCTF 2025 由 NCTF 2025 组织委员会主办，比赛时间为 3 月 22 日 9:00 - 3 月 23 日 21:00，共计 36 小时，比赛形式为团队赛，每队 1-4 人，分为校内、校外两个赛道。  
                
        === "国外赛事"
            ??? Quote "[WhiteHats TrojanCTF 2025](https://discord.gg/fXHCe9zsHC)"  
                [![](https://ctftime.org/media/events/TrojanCTF_logo.png){ width="200" align=left }](https://discord.gg/fXHCe9zsHC)  
                **比赛名称** : [WhiteHats TrojanCTF 2025](https://discord.gg/fXHCe9zsHC)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-17 17:00:00 - 2025-05-18 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : E.S.H.A. Trojan (https://ctftime.org/team/248605)  
                **添加日历** : https://ctftime.org/event/2644.ics  
                
            ??? Quote "[Cyshock - The Awakening](https://cyshock.ctfd.io/)"  
                [![](https://ctftime.org/media/events/Cyshock_Banner_Transparent.png){ width="200" align=left }](https://cyshock.ctfd.io/)  
                **比赛名称** : [Cyshock - The Awakening](https://cyshock.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-14 16:00:00 - 2025-05-16 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Visionspace (https://ctftime.org/team/383284)  
                **添加日历** : https://ctftime.org/event/2787.ics  
                
            ??? Quote "[Rams CTF 2025](https://rams-ctf.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://rams-ctf.com/)  
                **比赛名称** : [Rams CTF 2025](https://rams-ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-10 23:11:20 - 2025-05-10 23:11:20 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : RAM Overflow (https://ctftime.org/team/378601)  
                **添加日历** : https://ctftime.org/event/2791.ics  
                
            ??? Quote "[GooseCTF - misc0nfig 25](https://goosectf.lilypadd.com/)"  
                [![](https://ctftime.org/media/events/misc0nfig_banner_transparent.png){ width="200" align=left }](https://goosectf.lilypadd.com/)  
                **比赛名称** : [GooseCTF - misc0nfig 25](https://goosectf.lilypadd.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-10 19:00:00 - 2025-05-12 06:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Warwick Cyber Security Society (https://ctftime.org/team/277289)  
                **添加日历** : https://ctftime.org/event/2789.ics  
                
            ??? Quote "[DamCTF 2025](https://damctf.xyz/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://damctf.xyz/)  
                **比赛名称** : [DamCTF 2025](https://damctf.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-10 08:00:00 - 2025-05-12 08:00:00 UTC+8  
                **比赛权重** : 60.67  
                **赛事主办** : OSUSEC (https://ctftime.org/team/12858)  
                **添加日历** : https://ctftime.org/event/2585.ics  
                
            ??? Quote "[San Diego CTF 2025](https://ctf.sdc.tf/)"  
                [![](https://ctftime.org/media/events/sdctf_1.png){ width="200" align=left }](https://ctf.sdc.tf/)  
                **比赛名称** : [San Diego CTF 2025](https://ctf.sdc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-10 07:00:00 - 2025-05-12 07:00:00 UTC+8  
                **比赛权重** : 22.18  
                **赛事主办** : 3 Prongs And a Computer (https://ctftime.org/team/112558)  
                **添加日历** : https://ctftime.org/event/2785.ics  
                
            ??? Quote "[Break the Syntax CTF 2025](https://bts2025.wh.edu.pl/)"  
                [![](https://ctftime.org/media/events/btslogo.png){ width="200" align=left }](https://bts2025.wh.edu.pl/)  
                **比赛名称** : [Break the Syntax CTF 2025](https://bts2025.wh.edu.pl/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-10 00:00:00 - 2025-05-11 18:00:00 UTC+8  
                **比赛权重** : 42.00  
                **赛事主办** : PWr Synt@x Err0r (https://ctftime.org/team/88205)  
                **添加日历** : https://ctftime.org/event/2749.ics  
                
            ??? Quote "[LakeCTF Finals 24-25](https://lakectf.epfl.ch/)"  
                [![](https://ctftime.org/media/events/5ee3dccc1b28b5f04bdf2f7b871b1d07.png){ width="200" align=left }](https://lakectf.epfl.ch/)  
                **比赛名称** : [LakeCTF Finals 24-25](https://lakectf.epfl.ch/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-09 16:00:00 - 2025-05-10 00:00:00 UTC+8  
                **比赛权重** : 36.00  
                **赛事主办** : polygl0ts (https://ctftime.org/team/53791)  
                **添加日历** : https://ctftime.org/event/2568.ics  
                
            ??? Quote "[DevSecOps CTF 2025](https://ctf.punksecurity.co.uk/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.punksecurity.co.uk/)  
                **比赛名称** : [DevSecOps CTF 2025](https://ctf.punksecurity.co.uk/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-04 18:00:00 - 2025-05-05 06:00:00 UTC+8  
                **比赛权重** : 37.00  
                **赛事主办** : Punk Security (https://ctftime.org/team/212540)  
                **添加日历** : https://ctftime.org/event/2682.ics  
                
            ??? Quote "[UniVsThreats 25 CTF](https://univsthreats-2025.cyber-edu.co/?tenant=cyberedu)"  
                [![](https://ctftime.org/media/events/Project.6jpg_1.jpg){ width="200" align=left }](https://univsthreats-2025.cyber-edu.co/?tenant=cyberedu)  
                **比赛名称** : [UniVsThreats 25 CTF](https://univsthreats-2025.cyber-edu.co/?tenant=cyberedu)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-03 18:00:00 - 2025-05-04 18:00:00 UTC+8  
                **比赛权重** : 18.29  
                **赛事主办** : UVT-CTF (https://ctftime.org/team/214520)  
                **添加日历** : https://ctftime.org/event/2726.ics  
                
            ??? Quote "[TsukuCTF 2025](https://tsukuctf.org/)"  
                [![](https://ctftime.org/media/events/icon_8.png){ width="200" align=left }](https://tsukuctf.org/)  
                **比赛名称** : [TsukuCTF 2025](https://tsukuctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-03 11:00:00 - 2025-05-04 11:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : TaruTaru (https://ctftime.org/team/157513)  
                **添加日历** : https://ctftime.org/event/2769.ics  
                
            ??? Quote "[RPCA CTF 2025](https://grandctf.rpca.ac.th/)"  
                [![](https://ctftime.org/media/events/Screenshot_4.jpg){ width="200" align=left }](https://grandctf.rpca.ac.th/)  
                **比赛名称** : [RPCA CTF 2025](https://grandctf.rpca.ac.th/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-03 01:00:00 - 2025-05-06 01:00:00 UTC+8  
                **比赛权重** : 54.00  
                **赛事主办** : RPCA Cyber Club (https://ctftime.org/team/132960)  
                **添加日历** : https://ctftime.org/event/2755.ics  
                
            ??? Quote "[SpringForwardCTF 2025 (cancelled)](https://the-event-is-cancelled.com/)"  
                [![](https://ctftime.org/media/events/Social_Media_Icon.png){ width="200" align=left }](https://the-event-is-cancelled.com/)  
                **比赛名称** : [SpringForwardCTF 2025 (cancelled)](https://the-event-is-cancelled.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-03 00:00:00 - 2025-05-04 00:00:00 UTC+8  
                **比赛权重** : 24.20  
                **赛事主办** : NICC (https://ctftime.org/team/214936)  
                **添加日历** : https://ctftime.org/event/2756.ics  
                
            ??? Quote "[Nexzero.Ftc](https://nexzero-ftc.vercel.app/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://nexzero-ftc.vercel.app/)  
                **比赛名称** : [Nexzero.Ftc](https://nexzero-ftc.vercel.app/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-02 04:00:00 - 2025-05-04 03:44:06 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Nexus Team (https://ctftime.org/team/361096)  
                **添加日历** : https://ctftime.org/event/2779.ics  
                
            ??? Quote "[CU school CTF 2025](https://game.cut-ctf.team/)"  
                [![](https://ctftime.org/media/events/Screenshot_from_2025-05-09_13-11-44.png){ width="200" align=left }](https://game.cut-ctf.team/)  
                **比赛名称** : [CU school CTF 2025](https://game.cut-ctf.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-30 16:00:00 - 2025-05-01 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CUT (https://ctftime.org/team/358931)  
                **添加日历** : https://ctftime.org/event/2786.ics  
                
            ??? Quote "[ICCSDFAI](https://ctf.astanait.edu.kz/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.astanait.edu.kz/)  
                **比赛名称** : [ICCSDFAI](https://ctf.astanait.edu.kz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-29 19:00:00 - 2025-05-01 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HackOrda (https://ctftime.org/team/367962)  
                **添加日历** : https://ctftime.org/event/2685.ics  
                
            ??? Quote "[Incognito 6.0](https://incognito.axiosiiitl.dev/)"  
                [![](https://ctftime.org/media/events/logo_108.png){ width="200" align=left }](https://incognito.axiosiiitl.dev/)  
                **比赛名称** : [Incognito 6.0](https://incognito.axiosiiitl.dev/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-28 08:00:00 - 2025-04-29 08:00:00 UTC+8  
                **比赛权重** : 30.43  
                **赛事主办** : Byt3Scr4pp3rs (https://ctftime.org/team/57772)  
                **添加日历** : https://ctftime.org/event/2761.ics  
                
            ??? Quote "[WOCS'hAck 4d edition](https://wocshack.org/)"  
                [![](https://ctftime.org/media/events/WOCSHACK_FINAL.jpg){ width="200" align=left }](https://wocshack.org/)  
                **比赛名称** : [WOCS'hAck 4d edition](https://wocshack.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-26 22:00:00 - 2025-04-27 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : WOCSA (https://ctftime.org/team/286608)  
                **添加日历** : https://ctftime.org/event/2729.ics  
                
            ??? Quote "[Haruulzangi U18 2025 Domestic Quals](https://u18-2025.haruulzangi.mn/)"  
                [![](https://ctftime.org/media/events/android-chrome-512x512.png){ width="200" align=left }](https://u18-2025.haruulzangi.mn/)  
                **比赛名称** : [Haruulzangi U18 2025 Domestic Quals](https://u18-2025.haruulzangi.mn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-26 20:00:00 - 2025-04-27 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : haruulzangi-organizers (https://ctftime.org/team/266812)  
                **添加日历** : https://ctftime.org/event/2768.ics  
                
            ??? Quote "[Azure Assassin Alliance CTF 2025](https://actf2025.xctf.org.cn/)"  
                [![](https://ctftime.org/media/events/AAA.jpg){ width="200" align=left }](https://actf2025.xctf.org.cn/)  
                **比赛名称** : [Azure Assassin Alliance CTF 2025](https://actf2025.xctf.org.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-26 09:00:00 - 2025-04-27 09:00:00 UTC+8  
                **比赛权重** : 35.00  
                **赛事主办** : Azure Assassin Alliance (https://ctftime.org/team/194222)  
                **添加日历** : https://ctftime.org/event/2758.ics  
                
            ??? Quote "[HACKTHEON SEJONG 2025 Preliminaries](https://hacktheon.org/)"  
                [![](https://ctftime.org/media/events/2025_hacktheon.png){ width="200" align=left }](https://hacktheon.org/)  
                **比赛名称** : [HACKTHEON SEJONG 2025 Preliminaries](https://hacktheon.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-26 08:00:00 - 2025-04-26 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Sejong City Hall (https://ctftime.org/team/214900)  
                **添加日历** : https://ctftime.org/event/2719.ics  
                
            ??? Quote "[BSidesSF 2025 CTF](https://ctf.bsidessf.net/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.bsidessf.net/)  
                **比赛名称** : [BSidesSF 2025 CTF](https://ctf.bsidessf.net/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-26 07:00:00 - 2025-04-28 07:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : BSidesSF (https://ctftime.org/team/54737)  
                **添加日历** : https://ctftime.org/event/2721.ics  
                
            ??? Quote "[UMDCTF 2025](https://umdctf.io/)"  
                [![](https://ctftime.org/media/events/logo-cropped.png){ width="200" align=left }](https://umdctf.io/)  
                **比赛名称** : [UMDCTF 2025](https://umdctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-26 06:00:00 - 2025-04-28 06:00:00 UTC+8  
                **比赛权重** : 70.86  
                **赛事主办** : UMDCSEC (https://ctftime.org/team/87711)  
                **添加日历** : https://ctftime.org/event/2563.ics  
                
            ??? Quote "[CTF@CIT 2025](https://ctf.cyber-cit.club/)"  
                [![](https://ctftime.org/media/events/CTF-CIT-ctftime_2.png){ width="200" align=left }](https://ctf.cyber-cit.club/)  
                **比赛名称** : [CTF@CIT 2025](https://ctf.cyber-cit.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-26 05:00:00 - 2025-04-28 03:00:00 UTC+8  
                **比赛权重** : 24.57  
                **赛事主办** : HACK@CIT (https://ctftime.org/team/287896)  
                **添加日历** : https://ctftime.org/event/2759.ics  
                
            ??? Quote "[WSUCTF25](https://waynestateuniversity-ctf.ctfd.io/)"  
                [![](https://ctftime.org/media/events/WSU-CDC.jpg){ width="200" align=left }](https://waynestateuniversity-ctf.ctfd.io/)  
                **比赛名称** : [WSUCTF25](https://waynestateuniversity-ctf.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-19 21:00:00 - 2025-04-20 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : WayneStateCTF (https://ctftime.org/team/135263)  
                **添加日历** : https://ctftime.org/event/2757.ics  
                
            ??? Quote "[T-CTF 2025](https://t-ctf.ru/)"  
                [![](https://ctftime.org/media/events/t-ctf.jpg){ width="200" align=left }](https://t-ctf.ru/)  
                **比赛名称** : [T-CTF 2025](https://t-ctf.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-19 14:00:00 - 2025-04-21 02:00:00 UTC+8  
                **比赛权重** : 24.60  
                **赛事主办** : SPbCTF (https://ctftime.org/team/30003)  
                **添加日历** : https://ctftime.org/event/2741.ics  
                
            ??? Quote "[THJCC CTF 2025](https://ctf.scint.org/)"  
                [![](https://ctftime.org/media/events/24e103c1a070a7e5d42606fdd5749653.png){ width="200" align=left }](https://ctf.scint.org/)  
                **比赛名称** : [THJCC CTF 2025](https://ctf.scint.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-19 08:00:01 - 2025-04-20 20:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : CakeisTheFake (https://ctftime.org/team/276544)  
                **添加日历** : https://ctftime.org/event/2744.ics  
                
            ??? Quote "[b01lers CTF 2025](https://b01lersc.tf/)"  
                [![](https://ctftime.org/media/events/b01lers-griffen_2.png){ width="200" align=left }](https://b01lersc.tf/)  
                **比赛名称** : [b01lers CTF 2025](https://b01lersc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-19 07:00:00 - 2025-04-21 07:00:00 UTC+8  
                **比赛权重** : 44.50  
                **赛事主办** : b01lers (https://ctftime.org/team/11464)  
                **添加日历** : https://ctftime.org/event/2652.ics  
                
            ??? Quote "[UMassCTF 2025](https://ctf.umasscybersec.org/)"  
                [![](https://ctftime.org/media/events/889a1e484f0b51dd3d865b3a53b26200_1.jpg){ width="200" align=left }](https://ctf.umasscybersec.org/)  
                **比赛名称** : [UMassCTF 2025](https://ctf.umasscybersec.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-19 02:00:00 - 2025-04-21 08:00:00 UTC+8  
                **比赛权重** : 48.38  
                **赛事主办** : SavedByTheShell (https://ctftime.org/team/78233)  
                **添加日历** : https://ctftime.org/event/2653.ics  
                
            ??? Quote "[HackPack CTF 2025](https://hackpack.club/ctf2025/)"  
                [![](https://ctftime.org/media/events/logo_wolf.png){ width="200" align=left }](https://hackpack.club/ctf2025/)  
                **比赛名称** : [HackPack CTF 2025](https://hackpack.club/ctf2025/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-19 00:00:00 - 2025-04-19 23:59:59 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : hackpack (https://ctftime.org/team/25905)  
                **添加日历** : https://ctftime.org/event/2743.ics  
                
            ??? Quote "[DawgCTF 2025](https://metactf.com/join/dawgctf25)"  
                [![](https://ctftime.org/media/events/dawgsec_shield-ctftime_2.png){ width="200" align=left }](https://metactf.com/join/dawgctf25)  
                **比赛名称** : [DawgCTF 2025](https://metactf.com/join/dawgctf25)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-18 20:00:00 - 2025-04-20 20:00:00 UTC+8  
                **比赛权重** : 69.00  
                **赛事主办** : UMBC Cyber Dawgs (https://ctftime.org/team/18405)  
                **添加日历** : https://ctftime.org/event/2651.ics  
                
            ??? Quote "[CPCTF 2025](https://cpctf.space/)"  
                [![](https://ctftime.org/media/events/cpctf_logo_1.png){ width="200" align=left }](https://cpctf.space/)  
                **比赛名称** : [CPCTF 2025](https://cpctf.space/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-18 19:00:00 - 2025-04-20 19:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : traP (https://ctftime.org/team/62510)  
                **添加日历** : https://ctftime.org/event/2760.ics  
                
            ??? Quote "[SECPlayground Cybersplash 2025](https://lobby-ctf.secplayground.com/lobby/df6ff4f1-4187-472e-979d-b45ebc7f236d)"  
                [![](https://ctftime.org/media/events/Cybersplash_2025__FB_Profile_500_x_500_px.png){ width="200" align=left }](https://lobby-ctf.secplayground.com/lobby/df6ff4f1-4187-472e-979d-b45ebc7f236d)  
                **比赛名称** : [SECPlayground Cybersplash 2025](https://lobby-ctf.secplayground.com/lobby/df6ff4f1-4187-472e-979d-b45ebc7f236d)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-18 10:00:00 - 2025-04-19 10:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SECPlayground (https://ctftime.org/team/375409)  
                **添加日历** : https://ctftime.org/event/2754.ics  
                
            ??? Quote "[Operation Cipher Shadows](https://discord.gg/JQ3RGuhPkq)"  
                [![](https://ctftime.org){ width="200" align=left }](https://discord.gg/JQ3RGuhPkq)  
                **比赛名称** : [Operation Cipher Shadows](https://discord.gg/JQ3RGuhPkq)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-13 01:00:00 - 2025-04-14 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : IIT JAMMU (https://ctftime.org/team/375458)  
                **添加日历** : https://ctftime.org/event/2745.ics  
                
            ??? Quote "[SummitCTF 2025](https://summitctf.org/)"  
                [![](https://ctftime.org/media/events/Summitctf.png){ width="200" align=left }](https://summitctf.org/)  
                **比赛名称** : [SummitCTF 2025](https://summitctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-12 22:00:00 - 2025-04-13 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CyberVT (https://ctftime.org/team/173872)  
                **添加日历** : https://ctftime.org/event/2662.ics  
                
            ??? Quote "[PwnMe CTF Finals 2025](https://pwnme.fr/)"  
                [![](https://ctftime.org/media/events/PWNME_ReseauxPP1.jpg){ width="200" align=left }](https://pwnme.fr/)  
                **比赛名称** : [PwnMe CTF Finals 2025](https://pwnme.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-12 18:00:00 - 2025-04-13 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : PHREAKS 2600 (https://ctftime.org/team/200877)  
                **添加日历** : https://ctftime.org/event/2659.ics  
                
            ??? Quote "[Challenge the Cyber - Security Samurais](https://challengethecyber.nl/)"  
                [![](https://ctftime.org/media/events/ed5e44feb7f4c1e2ca1d000808871c14.jpg){ width="200" align=left }](https://challengethecyber.nl/)  
                **比赛名称** : [Challenge the Cyber - Security Samurais](https://challengethecyber.nl/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-12 17:00:00 - 2025-04-12 23:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Challenge the Cyber (https://ctftime.org/team/181210)  
                **添加日历** : https://ctftime.org/event/2701.ics  
                
            ??? Quote "[Midnight Flag CTF - INSURRECTION](https://midnightflag.fr/)"  
                [![](https://ctftime.org/media/events/logo-midnightflag_500.png){ width="200" align=left }](https://midnightflag.fr/)  
                **比赛名称** : [Midnight Flag CTF - INSURRECTION](https://midnightflag.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-12 16:00:00 - 2025-04-14 00:00:00 UTC+8  
                **比赛权重** : 24.50  
                **赛事主办** : Midnight Flag (https://ctftime.org/team/179110)  
                **添加日历** : https://ctftime.org/event/2687.ics  
                
            ??? Quote "[THCon 2K25 CTF](https://thcon.party/)"  
                [![](https://ctftime.org/media/events/Sans_titre.ico){ width="200" align=left }](https://thcon.party/)  
                **比赛名称** : [THCon 2K25 CTF](https://thcon.party/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-12 16:00:00 - 2025-04-13 16:00:00 UTC+8  
                **比赛权重** : 23.65  
                **赛事主办** : FirewallFoxes, pony7 (https://ctftime.org/team/278913, https://ctftime.org/team/20769)  
                **添加日历** : https://ctftime.org/event/2660.ics  
                
            ??? Quote "[DEF CON CTF Qualifier 2025](https://nautilus.institute/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://nautilus.institute/)  
                **比赛名称** : [DEF CON CTF Qualifier 2025](https://nautilus.institute/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-12 08:00:00 - 2025-04-14 08:00:00 UTC+8  
                **比赛权重** : 69.44  
                **赛事主办** : Nautilus Institute (https://ctftime.org/team/181536)  
                **添加日历** : https://ctftime.org/event/2604.ics  
                
            ??? Quote "[Texas Security Awareness Week 2025](https://ctf.texsaw.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.texsaw.org/)  
                **比赛名称** : [Texas Security Awareness Week 2025](https://ctf.texsaw.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-12 03:00:00 - 2025-04-14 03:00:00 UTC+8  
                **比赛权重** : 31.00  
                **赛事主办** : CSG (https://ctftime.org/team/333)  
                **添加日历** : https://ctftime.org/event/2736.ics  
                
            ??? Quote "[1753CTF 2025](https://1753ctf.com/)"  
                [![](https://ctftime.org/media/events/badge_1.png){ width="200" align=left }](https://1753ctf.com/)  
                **比赛名称** : [1753CTF 2025](https://1753ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-12 01:00:00 - 2025-04-13 01:00:00 UTC+8  
                **比赛权重** : 34.82  
                **赛事主办** : 1753c (https://ctftime.org/team/178287)  
                **添加日历** : https://ctftime.org/event/2639.ics  
                
            ??? Quote "[Dreamhack Invitational 2025](https://dreamhack.io/)"  
                [![](https://ctftime.org/media/events/e66fed5653581908ac8e93f82ad73cae.jpg){ width="200" align=left }](https://dreamhack.io/)  
                **比赛名称** : [Dreamhack Invitational 2025](https://dreamhack.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-08 08:00:00 - 2025-04-09 05:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Dreamhack (https://ctftime.org/team/367894)  
                **添加日历** : https://ctftime.org/event/2628.ics  
                
            ??? Quote "[Ulisse CTF 2025](https://2025.ulis.se/)"  
                [![](https://ctftime.org/media/events/logo_640x640.jpg){ width="200" align=left }](https://2025.ulis.se/)  
                **比赛名称** : [Ulisse CTF 2025](https://2025.ulis.se/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-06 01:00:00 - 2025-04-07 01:00:00 UTC+8  
                **比赛权重** : 24.81  
                **赛事主办** : Ulisse (https://ctftime.org/team/71738)  
                **添加日历** : https://ctftime.org/event/2735.ics  
                
            ??? Quote "[Auvergn'Hack](https://ctf.zitf.fr/)"  
                [![](https://ctftime.org/media/events/gorilla_auvergnhack3.jpg){ width="200" align=left }](https://ctf.zitf.fr/)  
                **比赛名称** : [Auvergn'Hack](https://ctf.zitf.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-05 20:45:00 - 2025-04-06 03:00:00 UTC+8  
                **比赛权重** : 22.75  
                **赛事主办** : ZiTF (https://ctftime.org/team/376047)  
                **添加日历** : https://ctftime.org/event/2752.ics  
                
            ??? Quote "[Moscow CTF School 2025](http://ctf.cs.msu.ru/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://ctf.cs.msu.ru/)  
                **比赛名称** : [Moscow CTF School 2025](http://ctf.cs.msu.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-05 18:00:00 - 2025-04-06 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Bushwhackers (https://ctftime.org/team/586)  
                **添加日历** : https://ctftime.org/event/2712.ics  
                
            ??? Quote "[Breach CTF 2025](https://www.breachers.in/)"  
                [![](https://ctftime.org/media/events/BreachCTF2025_Logo.jpeg){ width="200" align=left }](https://www.breachers.in/)  
                **比赛名称** : [Breach CTF 2025](https://www.breachers.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-05 10:30:00 - 2025-04-06 10:30:00 UTC+8  
                **比赛权重** : 23.77  
                **赛事主办** : IITBreachers (https://ctftime.org/team/165802)  
                **添加日历** : https://ctftime.org/event/2671.ics  
                
            ??? Quote "[squ1rrel CTF 2025](https://ctf.squ1rrel.dev/)"  
                [![](https://ctftime.org/media/events/squ1rrel_logo.png){ width="200" align=left }](https://ctf.squ1rrel.dev/)  
                **比赛名称** : [squ1rrel CTF 2025](https://ctf.squ1rrel.dev/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-05 07:00:00 - 2025-04-07 01:00:00 UTC+8  
                **比赛权重** : 24.25  
                **赛事主办** : squ1rrel (https://ctftime.org/team/201730)  
                **添加日历** : https://ctftime.org/event/2708.ics  
                
            ??? Quote "[PlaidCTF 2025](https://plaidctf.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://plaidctf.com/)  
                **比赛名称** : [PlaidCTF 2025](https://plaidctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-04-05 05:00:00 - 2025-04-07 05:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : Plaid Parliament of Pwning (https://ctftime.org/team/284)  
                **添加日历** : https://ctftime.org/event/2508.ics  
                
            ??? Quote "[Capture Point 5353 3.0](https://iiitv.capturepoint5353.tech/)"  
                [![](https://ctftime.org/media/events/Untitled_design_2.png){ width="200" align=left }](https://iiitv.capturepoint5353.tech/)  
                **比赛名称** : [Capture Point 5353 3.0](https://iiitv.capturepoint5353.tech/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-31 02:00:00 - 2025-04-01 16:10:29 UTC+8  
                **比赛权重** : 22.05  
                **赛事主办** : HORIZON_03 (https://ctftime.org/team/375436)  
                **添加日历** : https://ctftime.org/event/2747.ics  
                
            ??? Quote "[JerseyCTF V](https://ctf.jerseyctf.com/)"  
                [![](https://ctftime.org/media/events/jctfv_hat_1.png){ width="200" align=left }](https://ctf.jerseyctf.com/)  
                **比赛名称** : [JerseyCTF V](https://ctf.jerseyctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-30 03:00:00 - 2025-03-31 03:00:00 UTC+8  
                **比赛权重** : 24.73  
                **赛事主办** : Highlander Hackers (https://ctftime.org/team/173925)  
                **添加日历** : https://ctftime.org/event/2667.ics  
                
            ??? Quote "[CodeVinci Beginner CTF 2025](https://codevincictf.itis.pr.it/)"  
                [![](https://ctftime.org/media/events/logo_CodeVinci.jpg){ width="200" align=left }](https://codevincictf.itis.pr.it/)  
                **比赛名称** : [CodeVinci Beginner CTF 2025](https://codevincictf.itis.pr.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 21:00:00 - 2025-03-29 21:00:00 UTC+8  
                **比赛权重** : 18.57  
                **赛事主办** : CodeVincii (https://ctftime.org/team/367123)  
                **添加日历** : https://ctftime.org/event/2738.ics  
                
            ??? Quote "[SillyCTF 2025](https://sillyctf.psuccso.org/)"  
                [![](https://ctftime.org/media/events/SillyCTF.png){ width="200" align=left }](https://sillyctf.psuccso.org/)  
                **比赛名称** : [SillyCTF 2025](https://sillyctf.psuccso.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 20:00:00 - 2025-03-30 08:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Penn State CCSO (https://ctftime.org/team/367931)  
                **添加日历** : https://ctftime.org/event/2637.ics  
                
            ??? Quote "[VolgaCTF 2025 Qualifier](https://q.2025.volgactf.ru/)"  
                [![](https://ctftime.org/media/events/logo-social-yellow_16.png){ width="200" align=left }](https://q.2025.volgactf.ru/)  
                **比赛名称** : [VolgaCTF 2025 Qualifier](https://q.2025.volgactf.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 20:00:00 - 2025-03-30 20:00:00 UTC+8  
                **比赛权重** : 27.14  
                **赛事主办** : VolgaCTF.org (https://ctftime.org/team/27094)  
                **添加日历** : https://ctftime.org/event/2676.ics  
                
            ??? Quote "[Undutmaning 2025](https://undutmaning.se/)"  
                [![](https://ctftime.org/media/events/2025logo_ctfd.jpg){ width="200" align=left }](https://undutmaning.se/)  
                **比赛名称** : [Undutmaning 2025](https://undutmaning.se/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 19:00:00 - 2025-03-30 03:00:00 UTC+8  
                **比赛权重** : 24.50  
                **赛事主办** : Undutmaning (https://ctftime.org/team/212504)  
                **添加日历** : https://ctftime.org/event/2589.ics  
                
            ??? Quote "[PolyPwnCTF 2025](https://pwn.polycyber.io/)"  
                [![](https://ctftime.org/media/events/Logo_PolyPwn_CTF.jpg){ width="200" align=left }](https://pwn.polycyber.io/)  
                **比赛名称** : [PolyPwnCTF 2025](https://pwn.polycyber.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 18:00:00 - 2025-03-31 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : PolyCyber (https://ctftime.org/team/212241)  
                **添加日历** : https://ctftime.org/event/2734.ics  
                
            ??? Quote "[LBC2 2025](http://lbc2.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://lbc2.org/)  
                **比赛名称** : [LBC2 2025](http://lbc2.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 17:00:00 - 2025-03-29 23:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : LBC2 (https://ctftime.org/team/373963)  
                **添加日历** : https://ctftime.org/event/2728.ics  
                
            ??? Quote "[Dreamhack CTF Season 7 Round #6 (Div. 2)](https://dreamhack.io/ctf/660)"  
                [![](https://ctftime.org/media/events/cover06.jpg){ width="200" align=left }](https://dreamhack.io/ctf/660)  
                **比赛名称** : [Dreamhack CTF Season 7 Round #6 (Div. 2)](https://dreamhack.io/ctf/660)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 08:00:00 - 2025-03-29 23:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Dreamhack (https://ctftime.org/team/367894)  
                **添加日历** : https://ctftime.org/event/2626.ics  
                
            ??? Quote "[Codegate CTF 2025 Preliminary](http://ctf.codegate.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://ctf.codegate.org/)  
                **比赛名称** : [Codegate CTF 2025 Preliminary](http://ctf.codegate.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 08:00:00 - 2025-03-29 23:00:00 UTC+8  
                **比赛权重** : 54.00  
                **赛事主办** : CODEGATE (https://ctftime.org/team/39352)  
                **添加日历** : https://ctftime.org/event/2706.ics  
                
            ??? Quote "[TAMUctf 2025](https://tamuctf.com/)"  
                [![](https://ctftime.org/media/events/TAMUCTF_cmaroon_1_1.png){ width="200" align=left }](https://tamuctf.com/)  
                **比赛名称** : [TAMUctf 2025](https://tamuctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 06:00:00 - 2025-03-31 06:00:00 UTC+8  
                **比赛权重** : 56.66  
                **赛事主办** : TAMUctf (https://ctftime.org/team/37721)  
                **添加日历** : https://ctftime.org/event/2681.ics  
                
            ??? Quote "[SpartanCTF 2025](https://spartan.ctfd.io/)"  
                [![](https://ctftime.org/media/events/spctf.png){ width="200" align=left }](https://spartan.ctfd.io/)  
                **比赛名称** : [SpartanCTF 2025](https://spartan.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 05:00:00 - 2025-03-31 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Zero Day Club (https://ctftime.org/team/286318)  
                **添加日历** : https://ctftime.org/event/2447.ics  
                
            ??? Quote "[SwampCTF 2025](https://swampctf.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://swampctf.com/)  
                **比赛名称** : [SwampCTF 2025](https://swampctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 05:00:00 - 2025-03-31 05:00:00 UTC+8  
                **比赛权重** : 40.40  
                **赛事主办** : Kernel Sanders (https://ctftime.org/team/397)  
                **添加日历** : https://ctftime.org/event/2573.ics  
                
            ??? Quote "[DiceCTF 2025 Quals](https://ctf.dicega.ng/)"  
                [![](https://ctftime.org/media/events/dicectf_2_1_1_1.png){ width="200" align=left }](https://ctf.dicega.ng/)  
                **比赛名称** : [DiceCTF 2025 Quals](https://ctf.dicega.ng/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 05:00:00 - 2025-03-31 05:00:00 UTC+8  
                **比赛权重** : 81.00  
                **赛事主办** : DiceGang (https://ctftime.org/team/109452)  
                **添加日历** : https://ctftime.org/event/2617.ics  
                
            ??? Quote "[HackDay 2025 - Finals](https://hackday.fr/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://hackday.fr/)  
                **比赛名称** : [HackDay 2025 - Finals](https://hackday.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-29 02:00:00 - 2025-03-30 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HackDayCTF (https://ctftime.org/team/277562)  
                **添加日历** : https://ctftime.org/event/2616.ics  
                
            ??? Quote "[UNbreakable International 2025 - Individual Phase](https://unr25i-international.cyber-edu.co/)"  
                [![](https://ctftime.org/media/events/MfknElGVExHGiftE.png){ width="200" align=left }](https://unr25i-international.cyber-edu.co/)  
                **比赛名称** : [UNbreakable International 2025 - Individual Phase](https://unr25i-international.cyber-edu.co/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-28 17:00:00 - 2025-03-28 18:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : bitsentinel (https://ctftime.org/team/280005)  
                **添加日历** : https://ctftime.org/event/2739.ics  
                
            ??? Quote "[StealthCup](https://stealth.ait.ac.at/)"  
                [![](https://ctftime.org/media/events/StealthCup-2-1311x2048.png){ width="200" align=left }](https://stealth.ait.ac.at/)  
                **比赛名称** : [StealthCup](https://stealth.ait.ac.at/)  
                **比赛形式** : Hack quest  
                **比赛时间** : 2025-03-28 15:00:00 - 2025-03-28 23:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : 0x01DA (https://ctftime.org/team/104949)  
                **添加日历** : https://ctftime.org/event/2666.ics  
                
            ??? Quote "[SibirCTF 2025](https://vk.com/sibirctf)"  
                [![](https://ctftime.org/media/events/cybersibir2025logo_1.png){ width="200" align=left }](https://vk.com/sibirctf)  
                **比赛名称** : [SibirCTF 2025](https://vk.com/sibirctf)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2025-03-28 11:15:00 - 2025-03-29 20:15:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : keva (https://ctftime.org/team/2980)  
                **添加日历** : https://ctftime.org/event/2742.ics  
                
            ??? Quote "[HICAThon 1.0](https://hicathon01.xyz/)"  
                [![](https://ctftime.org/media/events/Frame_4034.png){ width="200" align=left }](https://hicathon01.xyz/)  
                **比赛名称** : [HICAThon 1.0](https://hicathon01.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-25 11:00:00 - 2025-03-26 20:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HICA SSPU (https://ctftime.org/team/372831)  
                **添加日历** : https://ctftime.org/event/2724.ics  
                
            ??? Quote "[AlpacaHack Round 10 (Pwn)](https://alpacahack.com/ctfs/round-10)"  
                [![](https://ctftime.org/media/events/ctftime_9.png){ width="200" align=left }](https://alpacahack.com/ctfs/round-10)  
                **比赛名称** : [AlpacaHack Round 10 (Pwn)](https://alpacahack.com/ctfs/round-10)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-23 11:00:00 - 2025-03-23 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : AlpacaHack (https://ctftime.org/team/312315)  
                **添加日历** : https://ctftime.org/event/2709.ics  
                
            ??? Quote "[ZeroDays CTF 2025](http://www.zerodays.ie/)"  
                [![](https://ctftime.org/media/events/zerodays_logo.png){ width="200" align=left }](http://www.zerodays.ie/)  
                **比赛名称** : [ZeroDays CTF 2025](http://www.zerodays.ie/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-22 17:30:00 - 2025-03-23 01:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Ireland without the RE (https://ctftime.org/team/179144)  
                **添加日历** : https://ctftime.org/event/2614.ics  
                
            ??? Quote "[FooBar CTF 2025](https://foobarctf.nitdgplug.org/)"  
                [![](https://ctftime.org/media/events/Foobar_logo_1.png){ width="200" align=left }](https://foobarctf.nitdgplug.org/)  
                **比赛名称** : [FooBar CTF 2025](https://foobarctf.nitdgplug.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-22 14:30:00 - 2025-03-23 14:30:00 UTC+8  
                **比赛权重** : 35.50  
                **赛事主办** : Alchemists of Kernel (https://ctftime.org/team/130794)  
                **添加日历** : https://ctftime.org/event/2720.ics  
                
            ??? Quote "[WolvCTF 2025](https://wolvctf.io/)"  
                [![](https://ctftime.org/media/events/4ec5f36875124e118429b66c41edf271.png){ width="200" align=left }](https://wolvctf.io/)  
                **比赛名称** : [WolvCTF 2025](https://wolvctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-22 07:00:00 - 2025-03-24 07:00:00 UTC+8  
                **比赛权重** : 47.25  
                **赛事主办** : wolvsec (https://ctftime.org/team/83621)  
                **添加日历** : https://ctftime.org/event/2579.ics  
                
            ??? Quote "[RITSEC CTF 2025](https://ctfd.ritsec.club/)"  
                [![](https://ctftime.org/media/events/Screenshot_From_2025-03-04_12-03-08.png){ width="200" align=left }](https://ctfd.ritsec.club/)  
                **比赛名称** : [RITSEC CTF 2025](https://ctfd.ritsec.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-22 05:00:00 - 2025-03-24 05:00:00 UTC+8  
                **比赛权重** : 34.14  
                **赛事主办** : Contagion (https://ctftime.org/team/152691)  
                **添加日历** : https://ctftime.org/event/2673.ics  
                
            ??? Quote "[WHY2025 CTF Teaser](https://ctf.why2025.org/)"  
                [![](https://ctftime.org/media/events/CTF_logo_v0.2.jpg){ width="200" align=left }](https://ctf.why2025.org/)  
                **比赛名称** : [WHY2025 CTF Teaser](https://ctf.why2025.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-22 03:00:00 - 2025-03-24 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Eindbazen (https://ctftime.org/team/322)  
                **添加日历** : https://ctftime.org/event/2679.ics  
                
            ??? Quote "[pingCTF 2025](https://knping.pl/ctf)"  
                [![](https://ctftime.org/media/events/CTF_blank_1.png){ width="200" align=left }](https://knping.pl/ctf)  
                **比赛名称** : [pingCTF 2025](https://knping.pl/ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-22 03:00:00 - 2025-03-24 03:00:00 UTC+8  
                **比赛权重** : 32.50  
                **赛事主办** : pingCTF (https://ctftime.org/team/147266)  
                **添加日历** : https://ctftime.org/event/2670.ics  
                
            ??? Quote "[Cyber Apocalypse CTF 2025: Tales from Eldoria](https://ctf.hackthebox.com/event/details/cyber-apocalypse-ctf-2025-tales-from-eldoria-2107)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hackthebox.com/event/details/cyber-apocalypse-ctf-2025-tales-from-eldoria-2107)  
                **比赛名称** : [Cyber Apocalypse CTF 2025: Tales from Eldoria](https://ctf.hackthebox.com/event/details/cyber-apocalypse-ctf-2025-tales-from-eldoria-2107)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-21 21:00:00 - 2025-03-26 20:59:00 UTC+8  
                **比赛权重** : 24.00  
                **赛事主办** : Hack The Box (https://ctftime.org/team/136056)  
                **添加日历** : https://ctftime.org/event/2674.ics  
                
            ??? Quote "[DC509 CTF 2025](https://dc509.com/)"  
                [![](https://ctftime.org/media/events/dc509.png){ width="200" align=left }](https://dc509.com/)  
                **比赛名称** : [DC509 CTF 2025](https://dc509.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-21 08:00:00 - 2025-03-21 10:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : dc509 (https://ctftime.org/team/372660)  
                **添加日历** : https://ctftime.org/event/2730.ics  
                
            ??? Quote "[m0leCon CTF 2025](https://finals.m0lecon.it/)"  
                [![](https://ctftime.org/media/events/ctftime_4_1.png){ width="200" align=left }](https://finals.m0lecon.it/)  
                **比赛名称** : [m0leCon CTF 2025](https://finals.m0lecon.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-21 00:00:00 - 2025-03-22 00:00:00 UTC+8  
                **比赛权重** : 75.00  
                **赛事主办** : pwnthem0le (https://ctftime.org/team/60467)  
                **添加日历** : https://ctftime.org/event/2725.ics  
                
            ??? Quote "[PascalCTF Beginners 2025](https://ctf.pascalctf.it/)"  
                [![](https://ctftime.org/media/events/Untitled_2_1.png){ width="200" align=left }](https://ctf.pascalctf.it/)  
                **比赛名称** : [PascalCTF Beginners 2025](https://ctf.pascalctf.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-19 23:00:00 - 2025-03-20 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Paolo (https://ctftime.org/team/263145)  
                **添加日历** : https://ctftime.org/event/2664.ics  
                
            ??? Quote "[WatCTF W25](https://watctf.org/)"  
                [![](https://ctftime.org/media/events/Black_Back_Yellow_Lock.png){ width="200" align=left }](https://watctf.org/)  
                **比赛名称** : [WatCTF W25](https://watctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-16 03:00:00 - 2025-03-17 03:00:00 UTC+8  
                **比赛权重** : 24.79  
                **赛事主办** : WATCTF (https://ctftime.org/team/373968)  
                **添加日历** : https://ctftime.org/event/2727.ics  
                
            ??? Quote "[Nowruz 1404](https://1404.fmc.tf/)"  
                [![](https://ctftime.org/media/events/FMCTF.png){ width="200" align=left }](https://1404.fmc.tf/)  
                **比赛名称** : [Nowruz 1404](https://1404.fmc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-15 21:30:00 - 2025-03-16 21:30:00 UTC+8  
                **比赛权重** : 24.47  
                **赛事主办** : FlagMotori (https://ctftime.org/team/222060)  
                **添加日历** : https://ctftime.org/event/2601.ics  
                
            ??? Quote "[K!nd4SUS CTF 2025](https://ctf.k1nd4sus.it/)"  
                [![](https://ctftime.org/media/events/iconH.png){ width="200" align=left }](https://ctf.k1nd4sus.it/)  
                **比赛名称** : [K!nd4SUS CTF 2025](https://ctf.k1nd4sus.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-15 21:00:00 - 2025-03-16 21:00:00 UTC+8  
                **比赛权重** : 18.70  
                **赛事主办** : K!nd4SUS (https://ctftime.org/team/150337)  
                **添加日历** : https://ctftime.org/event/2703.ics  
                
            ??? Quote "[@Hack 2025](https://2025.athackctf.com/)"  
                [![](https://ctftime.org/media/events/Hack_Logo_WIDTH_600px.png){ width="200" align=left }](https://2025.athackctf.com/)  
                **比赛名称** : [@Hack 2025](https://2025.athackctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-15 19:00:00 - 2025-03-16 19:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hexploit Alliance (https://ctftime.org/team/278003)  
                **添加日历** : https://ctftime.org/event/2558.ics  
                
            ??? Quote "[UTCTF 2025](https://utctf.live/)"  
                [![](https://ctftime.org/media/events/Illustration.png){ width="200" align=left }](https://utctf.live/)  
                **比赛名称** : [UTCTF 2025](https://utctf.live/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-15 07:00:00 - 2025-03-17 07:00:00 UTC+8  
                **比赛权重** : 67.21  
                **赛事主办** : isss (https://ctftime.org/team/69010)  
                **添加日历** : https://ctftime.org/event/2641.ics  
                
            ??? Quote "[Insomni'hack 2025](https://insomnihack.ch/contest/)"  
                [![](https://ctftime.org/media/events/skull.jpg){ width="200" align=left }](https://insomnihack.ch/contest/)  
                **比赛名称** : [Insomni'hack 2025](https://insomnihack.ch/contest/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-15 01:00:00 - 2025-03-15 12:00:00 UTC+8  
                **比赛权重** : 24.14  
                **赛事主办** : Insomni'hack Team (https://ctftime.org/team/104742)  
                **添加日历** : https://ctftime.org/event/2634.ics  
                
            ??? Quote "[AI vs Human CTF Challenge](https://ctf.hackthebox.com/event/details/ai-vs-human-ctf-challenge-2000)"  
                [![](https://ctftime.org/media/events/TakdFKeKQfMuBnauH5bjw8olSIcjpOdGkCOjJ3Mn.png){ width="200" align=left }](https://ctf.hackthebox.com/event/details/ai-vs-human-ctf-challenge-2000)  
                **比赛名称** : [AI vs Human CTF Challenge](https://ctf.hackthebox.com/event/details/ai-vs-human-ctf-challenge-2000)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-14 23:00:00 - 2025-03-16 23:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Palisade Research (https://ctftime.org/team/373097)  
                **添加日历** : https://ctftime.org/event/2723.ics  
                
            ??? Quote "[LiU CTF 2025](https://ctf.lithehax.se/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.lithehax.se/)  
                **比赛名称** : [LiU CTF 2025](https://ctf.lithehax.se/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-09 01:15:00 - 2025-03-09 06:45:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : LiTHeHax (https://ctftime.org/team/361438)  
                **添加日历** : https://ctftime.org/event/2733.ics  
                
            ??? Quote "[DFIR Labs CTF by The DFIR Report](https://thedfirreport.com/services/dfir-labs/ctf/)"  
                [![](https://ctftime.org/media/events/DFIR_Labs_Icon.png){ width="200" align=left }](https://thedfirreport.com/services/dfir-labs/ctf/)  
                **比赛名称** : [DFIR Labs CTF by The DFIR Report](https://thedfirreport.com/services/dfir-labs/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-09 00:00:00 - 2025-03-09 04:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : The DFIR Report (https://ctftime.org/team/309500)  
                **添加日历** : https://ctftime.org/event/2643.ics  
                
            ??? Quote "[Ugra CTF Quals 2025](https://2025.ugractf.ru/quals)"  
                [![](https://ctftime.org/media/events/150.jpg){ width="200" align=left }](https://2025.ugractf.ru/quals)  
                **比赛名称** : [Ugra CTF Quals 2025](https://2025.ugractf.ru/quals)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-08 15:00:00 - 2025-03-10 03:00:00 UTC+8  
                **比赛权重** : 32.59  
                **赛事主办** : [team Team] (https://ctftime.org/team/49808)  
                **添加日历** : https://ctftime.org/event/2693.ics  
                
            ??? Quote "[TPCTF 2025](https://tpctf2025.xctf.org.cn/)"  
                [![](https://ctftime.org/media/events/TPCTF_ba-stylenulla.top_1.png){ width="200" align=left }](https://tpctf2025.xctf.org.cn/)  
                **比赛名称** : [TPCTF 2025](https://tpctf2025.xctf.org.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-08 09:00:00 - 2025-03-10 09:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : TP-Link (https://ctftime.org/team/273760)  
                **添加日历** : https://ctftime.org/event/2645.ics  
                
            ??? Quote "[Dreamhack CTF Season 7 Round #5 (Div. 1)](https://dreamhack.io/ctf/659)"  
                [![](https://ctftime.org/media/events/cover05.jpg){ width="200" align=left }](https://dreamhack.io/ctf/659)  
                **比赛名称** : [Dreamhack CTF Season 7 Round #5 (Div. 1)](https://dreamhack.io/ctf/659)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-08 08:00:00 - 2025-03-08 23:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Dreamhack (https://ctftime.org/team/367894)  
                **添加日历** : https://ctftime.org/event/2625.ics  
                
            ??? Quote "[KalmarCTF 2025](http://KalmarC.TF/)"  
                [![](https://ctftime.org/media/events/kalmar-logo.png){ width="200" align=left }](http://KalmarC.TF/)  
                **比赛名称** : [KalmarCTF 2025](http://KalmarC.TF/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-08 01:00:00 - 2025-03-10 01:00:00 UTC+8  
                **比赛权重** : 33.89  
                **赛事主办** : kalmarunionen (https://ctftime.org/team/114856)  
                **添加日历** : https://ctftime.org/event/2599.ics  
                
            ??? Quote "[Pearl CTF](https://pearlctf.in/)"  
                [![](https://ctftime.org/media/events/Pearl_Logo.png){ width="200" align=left }](https://pearlctf.in/)  
                **比赛名称** : [Pearl CTF](https://pearlctf.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-07 20:30:00 - 2025-03-08 20:30:00 UTC+8  
                **比赛权重** : 33.81  
                **赛事主办** : BIT CRIMINALS (https://ctftime.org/team/151727)  
                **添加日历** : https://ctftime.org/event/2647.ics  
                
            ??? Quote "[VishwaCTF 2025](https://vishwactf.com/)"  
                [![](https://ctftime.org/media/events/VishwaCTF-Circular_1.png){ width="200" align=left }](https://vishwactf.com/)  
                **比赛名称** : [VishwaCTF 2025](https://vishwactf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-03 18:30:00 - 2025-03-05 18:29:59 UTC+8  
                **比赛权重** : 27.90  
                **赛事主办** : CyberCellVIIT (https://ctftime.org/team/144677)  
                **添加日历** : https://ctftime.org/event/2630.ics  
                
            ??? Quote "[Winja CTF | Nullcon Goa 2025](https://ctf.winja.org/)"  
                [![](https://ctftime.org/media/events/winja-logo-transparent_2.png){ width="200" align=left }](https://ctf.winja.org/)  
                **比赛名称** : [Winja CTF | Nullcon Goa 2025](https://ctf.winja.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-02 14:00:00 - 2025-03-02 19:00:00 UTC+8  
                **比赛权重** : 13.00  
                **赛事主办** : Winja CTF (https://ctftime.org/team/145228)  
                **添加日历** : https://ctftime.org/event/2692.ics  
                
            ??? Quote "[CSCG 2025](https://play.cscg.live/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://play.cscg.live/)  
                **比赛名称** : [CSCG 2025](https://play.cscg.live/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-02 01:00:00 - 2025-05-02 00:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : NFITS (https://ctftime.org/team/360674)  
                **添加日历** : https://ctftime.org/event/2588.ics  
                
            ??? Quote "[WEC CTF 2025](https://wecctf.nitk.ac.in/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://wecctf.nitk.ac.in/)  
                **比赛名称** : [WEC CTF 2025](https://wecctf.nitk.ac.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-01 19:30:00 - 2025-03-02 19:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Web Club NITK (https://ctftime.org/team/216903)  
                **添加日历** : https://ctftime.org/event/2705.ics  
                
            ??? Quote "[SECCON CTF 13 Domestic Finals](https://ctf.seccon.jp/)"  
                [![](https://ctftime.org/media/events/seccon_s_9.png){ width="200" align=left }](https://ctf.seccon.jp/)  
                **比赛名称** : [SECCON CTF 13 Domestic Finals](https://ctf.seccon.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-01 09:00:00 - 2025-03-02 19:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : SECCON CTF (https://ctftime.org/team/11918)  
                **添加日历** : https://ctftime.org/event/2650.ics  
                
            ??? Quote "[SECCON CTF 13 International Finals](https://ctf.seccon.jp/)"  
                [![](https://ctftime.org/media/events/seccon_s_8.png){ width="200" align=left }](https://ctf.seccon.jp/)  
                **比赛名称** : [SECCON CTF 13 International Finals](https://ctf.seccon.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-01 09:00:00 - 2025-03-02 19:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : SECCON CTF (https://ctftime.org/team/11918)  
                **添加日历** : https://ctftime.org/event/2649.ics  
                
            ??? Quote "[PwnMe CTF Quals 2025](https://pwnme.phreaks.fr/)"  
                [![](https://ctftime.org/media/events/PWNME_ReseauxPP1_1.jpg){ width="200" align=left }](https://pwnme.phreaks.fr/)  
                **比赛名称** : [PwnMe CTF Quals 2025](https://pwnme.phreaks.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-03-01 04:00:00 - 2025-03-03 02:00:00 UTC+8  
                **比赛权重** : 24.94  
                **赛事主办** : PHREAKS 2600 (https://ctftime.org/team/200877)  
                **添加日历** : https://ctftime.org/event/2658.ics  
                
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
