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
        ??? Quote "[HGAME 2026](https://hgame.vidar.club/)"  
            **比赛名称** : [HGAME 2026](https://hgame.vidar.club/)  
            **比赛类型** : 线上Jeopardy解题赛  
            **报名时间** : 2026年01月26日 00:00 - 2026年02月15日 19:59  
            **比赛时间** : 2026年02月02日 10:00 - 2026年02月15日 20:00  
            **其他说明** : HGAME 2026 是一场由Vidar-Team组织的线上Jeopardy解题赛，。报名从2026年01月26日00:00开始，到2026年02月15日20:00结束。比赛从2026年02月02日10:00开始，至2026年02月15日20:00结束。更多信息，请加入QQ群576834793。  
            
    === "*即将开始*"
        === "国内赛事"
            ??? Quote "[HGAME 2026](https://hgame.vidar.club/)"  
                **比赛名称** : [HGAME 2026](https://hgame.vidar.club/)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2026年01月26日 00:00 - 2026年02月15日 19:59  
                **比赛时间** : 2026年02月02日 10:00 - 2026年02月15日 20:00  
                **其他说明** : HGAME 2026 是一场由Vidar-Team组织的线上Jeopardy解题赛，。报名从2026年01月26日00:00开始，到2026年02月15日20:00结束。比赛从2026年02月02日10:00开始，至2026年02月15日20:00结束。更多信息，请加入QQ群576834793。  
                
        === "国外赛事"
            ??? Quote "[BITSCTF 2026](https://ctf.bitskrieg.in/)"  
                [![](https://ctftime.org/media/events/bitskrieg_background.png){ width="200" align=left }](https://ctf.bitskrieg.in/)  
                **比赛名称** : [BITSCTF 2026](https://ctf.bitskrieg.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-06 13:30:00 - 2026-02-08 13:30:00 UTC+8  
                **比赛权重** : 25.54  
                **赛事主办** : BITSkrieg (https://ctftime.org/team/22310)  
                **添加日历** : https://ctftime.org/event/3047.ics  
                
            ??? Quote "[Pragyan CTF 2026](https://ctf.prgy.in/)"  
                [![](){ width="200" align=left }](https://ctf.prgy.in/)  
                **比赛名称** : [Pragyan CTF 2026](https://ctf.prgy.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-06 21:00:00 - 2026-02-08 21:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Pragyan (https://ctftime.org/team/33867)  
                **添加日历** : https://ctftime.org/event/3058.ics  
                
            ??? Quote "[LA CTF 2026](https://lac.tf/)"  
                [![](){ width="200" align=left }](https://lac.tf/)  
                **比赛名称** : [LA CTF 2026](https://lac.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-07 10:00:00 - 2026-02-09 10:00:00 UTC+8  
                **比赛权重** : 53.58  
                **赛事主办** : PBR | UCLA (https://ctftime.org/team/186494)  
                **添加日历** : https://ctftime.org/event/3015.ics  
                
            ??? Quote "[Nullcon Goa HackIM 2026 CTF](https://ctf.nullcon.net/)"  
                [![](https://ctftime.org/media/events/a3838829dc3fcbbebcc062b58d405747_1.png){ width="200" align=left }](https://ctf.nullcon.net/)  
                **比赛名称** : [Nullcon Goa HackIM 2026 CTF](https://ctf.nullcon.net/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-07 16:30:00 - 2026-02-08 16:30:00 UTC+8  
                **比赛权重** : 24.72  
                **赛事主办** : ENOFLAG (https://ctftime.org/team/1438)  
                **添加日历** : https://ctftime.org/event/3066.ics  
                
            ??? Quote "[DUCKERZ CTF 2026](https://teams.duckerz.ru/)"  
                [![](https://ctftime.org/media/events/DUCKERZ.png){ width="200" align=left }](https://teams.duckerz.ru/)  
                **比赛名称** : [DUCKERZ CTF 2026](https://teams.duckerz.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-07 17:00:00 - 2026-02-08 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : DUCKERZ (https://ctftime.org/team/372036)  
                **添加日历** : https://ctftime.org/event/3067.ics  
                
            ??? Quote "[EncipherX CTF 4.0](https://encipherx.in/)"  
                [![](https://ctftime.org/media/events/EncipherX_logo.png){ width="200" align=left }](https://encipherx.in/)  
                **比赛名称** : [EncipherX CTF 4.0](https://encipherx.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-07 19:00:00 - 2026-02-08 19:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Phoenixcybersecurity (https://ctftime.org/team/419257)  
                **添加日历** : https://ctftime.org/event/3074.ics  
                
            ??? Quote "[0xFUN CTF 2026](https://ctf.0xfun.org/)"  
                [![](https://ctftime.org/media/events/image_4.png){ width="200" align=left }](https://ctf.0xfun.org/)  
                **比赛名称** : [0xFUN CTF 2026](https://ctf.0xfun.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-13 02:00:00 - 2026-02-15 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : 0xFUN (https://ctftime.org/team/354033)  
                **添加日历** : https://ctftime.org/event/3081.ics  
                
            ??? Quote "[Crackmes.one Reverse Engineering CTF 2026](https://crackmesone.ctfd.io/)"  
                [![](https://ctftime.org/media/events/221804609.png){ width="200" align=left }](https://crackmesone.ctfd.io/)  
                **比赛名称** : [Crackmes.one Reverse Engineering CTF 2026](https://crackmesone.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-14 08:00:00 - 2026-02-21 08:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : crackmes.one (https://ctftime.org/team/388934)  
                **添加日历** : https://ctftime.org/event/3014.ics  
                
            ??? Quote "[Breach Point CTF - Siege Of Troy(Online Round)](https://breachpoint.live/)"  
                [![](https://ctftime.org/media/events/SIEGE_O_TROY_Trust_Was_the_Vulnerability..jpg){ width="200" align=left }](https://breachpoint.live/)  
                **比赛名称** : [Breach Point CTF - Siege Of Troy(Online Round)](https://breachpoint.live/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-14 15:30:00 - 2026-02-15 15:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : BreachPoint-SOT (https://ctftime.org/team/419090)  
                **添加日历** : https://ctftime.org/event/3075.ics  
                
            ??? Quote "[TaipanByte’s Chart CTF](https://chart.taipanbyte.ru/)"  
                [![](){ width="200" align=left }](https://chart.taipanbyte.ru/)  
                **比赛名称** : [TaipanByte’s Chart CTF](https://chart.taipanbyte.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-14 18:00:00 - 2026-02-15 18:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : TaipanByte (https://ctftime.org/team/301788)  
                **添加日历** : https://ctftime.org/event/3086.ics  
                
            ??? Quote "[Batman's Kitchen CTF 2026](https://ctf.batmans.kitchen/)"  
                [![](https://ctftime.org/media/events/bklogo.png){ width="200" align=left }](https://ctf.batmans.kitchen/)  
                **比赛名称** : [Batman's Kitchen CTF 2026](https://ctf.batmans.kitchen/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-21 02:30:00 - 2026-02-23 02:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Batman's Kitchen (https://ctftime.org/team/3135)  
                **添加日历** : https://ctftime.org/event/3098.ics  
                
            ??? Quote "[THJCC CTF 2026](https://ctf2026.thjcc.org/)"  
                [![](https://ctftime.org/media/events/3291aa527005a0771b15f8ca11d76637.png){ width="200" align=left }](https://ctf2026.thjcc.org/)  
                **比赛名称** : [THJCC CTF 2026](https://ctf2026.thjcc.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-21 08:00:01 - 2026-02-22 21:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CakeisTheFake (https://ctftime.org/team/276544)  
                **添加日历** : https://ctftime.org/event/3088.ics  
                
            ??? Quote "[Escathon CTF 2026 Finals](https://eschaton.mcsc.space/)"  
                [![](https://ctftime.org/media/events/mcsc_logo.jpg){ width="200" align=left }](https://eschaton.mcsc.space/)  
                **比赛名称** : [Escathon CTF 2026 Finals](https://eschaton.mcsc.space/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2026-02-21 12:30:00 - 2026-02-21 22:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Team MCSC (https://ctftime.org/team/418958)  
                **添加日历** : https://ctftime.org/event/3078.ics  
                
            ??? Quote "[EPIHACK CTF: L'arène numérique](https://ctf.epihack.tech/)"  
                [![](https://ctftime.org/media/events/logo-bg.png){ width="200" align=left }](https://ctf.epihack.tech/)  
                **比赛名称** : [EPIHACK CTF: L'arène numérique](https://ctf.epihack.tech/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-21 17:00:00 - 2026-02-22 01:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : EPIHACK (https://ctftime.org/team/419202)  
                **添加日历** : https://ctftime.org/event/3076.ics  
                
            ??? Quote "[BearcatCTF 2026 - Setting Sail](https://bearcatctf.io/)"  
                [![](https://ctftime.org/media/events/bearcat26_logo_black.png){ width="200" align=left }](https://bearcatctf.io/)  
                **比赛名称** : [BearcatCTF 2026 - Setting Sail](https://bearcatctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-22 01:00:00 - 2026-02-23 01:00:00 UTC+8  
                **比赛权重** : 23.89  
                **赛事主办** : Cyber@UC (https://ctftime.org/team/87727)  
                **添加日历** : https://ctftime.org/event/3046.ics  
                
            ??? Quote "[UniVsThreats 26 Quals CTF]()"  
                [![](https://ctftime.org/media/events/b5d87319c0fb32c513deeef45488af6a.jpg){ width="200" align=left }]()  
                **比赛名称** : [UniVsThreats 26 Quals CTF]()  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-27 16:00:00 - 2026-02-28 16:00:00 UTC+8  
                **比赛权重** : 18.35  
                **赛事主办** : UVT-CTF (https://ctftime.org/team/214520)  
                **添加日历** : https://ctftime.org/event/3092.ics  
                
            ??? Quote "[SECCON CTF 14 International Finals](https://ctf.seccon.jp/)"  
                [![](https://ctftime.org/media/events/seccon_s_11.png){ width="200" align=left }](https://ctf.seccon.jp/)  
                **比赛名称** : [SECCON CTF 14 International Finals](https://ctf.seccon.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-28 09:00:00 - 2026-03-01 17:00:00 UTC+8  
                **比赛权重** : 37.00  
                **赛事主办** : SECCON CTF (https://ctftime.org/team/11918)  
                **添加日历** : https://ctftime.org/event/3106.ics  
                
            ??? Quote "[SECCON CTF 14 Domestic Finals](https://ctf.seccon.jp/)"  
                [![](https://ctftime.org/media/events/seccon_s_12.png){ width="200" align=left }](https://ctf.seccon.jp/)  
                **比赛名称** : [SECCON CTF 14 Domestic Finals](https://ctf.seccon.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-02-28 09:00:00 - 2026-03-01 17:00:00 UTC+8  
                **比赛权重** : 37.00  
                **赛事主办** : SECCON CTF (https://ctftime.org/team/11918)  
                **添加日历** : https://ctftime.org/event/3107.ics  
                
            ??? Quote "[Srdnlen CTF 2026 Quals](https://ctf.srdnlen.it/)"  
                [![](https://ctftime.org/media/events/e04b66f1d17c437f935e29d0fbe7beed_1.png){ width="200" align=left }](https://ctf.srdnlen.it/)  
                **比赛名称** : [Srdnlen CTF 2026 Quals](https://ctf.srdnlen.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-01 02:00:00 - 2026-03-01 02:00:00 UTC+8  
                **比赛权重** : 34.76  
                **赛事主办** : Srdnlen (https://ctftime.org/team/83421)  
                **添加日历** : https://ctftime.org/event/3043.ics  
                
            ??? Quote "[CSCG 2026](https://play.cscg.live/)"  
                [![](){ width="200" align=left }](https://play.cscg.live/)  
                **比赛名称** : [CSCG 2026](https://play.cscg.live/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-02 01:00:00 - 2026-05-02 00:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : NFITS (https://ctftime.org/team/360674)  
                **添加日历** : https://ctftime.org/event/2907.ics  
                
            ??? Quote "[upCTF 2026](https://ctf.xstf.pt/)"  
                [![](https://ctftime.org/media/events/logo_yellow_1.png){ width="200" align=left }](https://ctf.xstf.pt/)  
                **比赛名称** : [upCTF 2026](https://ctf.xstf.pt/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-07 17:00:00 - 2026-03-09 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : xSTF (https://ctftime.org/team/15341)  
                **添加日历** : https://ctftime.org/event/3073.ics  
                
            ??? Quote "[@Hack 2026](https://athackctf.com/)"  
                [![](https://ctftime.org/media/events/athack_logo.png){ width="200" align=left }](https://athackctf.com/)  
                **比赛名称** : [@Hack 2026](https://athackctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-07 22:00:00 - 2026-03-09 03:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Hexploit Alliance (https://ctftime.org/team/278003)  
                **添加日历** : https://ctftime.org/event/3027.ics  
                
            ??? Quote "[CodeVinci CTF 2026](https://challs.codevinci.it/)"  
                [![](https://ctftime.org/media/events/Logo_.png){ width="200" align=left }](https://challs.codevinci.it/)  
                **比赛名称** : [CodeVinci CTF 2026](https://challs.codevinci.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-07 22:00:00 - 2026-03-08 03:00:00 UTC+8  
                **比赛权重** : 18.57  
                **赛事主办** : code-vinci (https://ctftime.org/team/365817)  
                **添加日历** : https://ctftime.org/event/3101.ics  
                
            ??? Quote "[DiceCTF 2026 Quals](https://dicega.ng/)"  
                [![](https://ctftime.org/media/events/dice.png){ width="200" align=left }](https://dicega.ng/)  
                **比赛名称** : [DiceCTF 2026 Quals](https://dicega.ng/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-08 01:00:00 - 2026-03-09 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : DiceGang (https://ctftime.org/team/109452)  
                **添加日历** : https://ctftime.org/event/3110.ics  
                
            ??? Quote "[Midnight Flag CTF - EXECUTION](https://midnightflag.fr/)"  
                [![](https://ctftime.org/media/events/logo_119.png){ width="200" align=left }](https://midnightflag.fr/)  
                **比赛名称** : [Midnight Flag CTF - EXECUTION](https://midnightflag.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-14 04:00:00 - 2026-03-16 04:00:00 UTC+8  
                **比赛权重** : 24.50  
                **赛事主办** : Midnight Flag (https://ctftime.org/team/179110)  
                **添加日历** : https://ctftime.org/event/3105.ics  
                
            ??? Quote "[WolvCTF 2026](https://wolvctf.io/)"  
                [![](https://ctftime.org/media/events/wolverine-logo-square1_1.jpg){ width="200" align=left }](https://wolvctf.io/)  
                **比赛名称** : [WolvCTF 2026](https://wolvctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-14 07:00:00 - 2026-03-16 07:00:00 UTC+8  
                **比赛权重** : 65.35  
                **赛事主办** : wolvsec (https://ctftime.org/team/83621)  
                **添加日历** : https://ctftime.org/event/3049.ics  
                
            ??? Quote "[tkbctf5](https://tkbctf.info/)"  
                [![](https://ctftime.org/media/events/tkbctf_logo.png){ width="200" align=left }](https://tkbctf.info/)  
                **比赛名称** : [tkbctf5](https://tkbctf.info/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-14 13:00:00 - 2026-03-15 13:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : TPC (https://ctftime.org/team/222485)  
                **添加日历** : https://ctftime.org/event/3091.ics  
                
            ??? Quote "[Curiosity CTF 2026](https://curiosityctf.xyz/)"  
                [![](){ width="200" align=left }](https://curiosityctf.xyz/)  
                **比赛名称** : [Curiosity CTF 2026](https://curiosityctf.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-21 03:00:00 - 2026-03-23 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Curioѕity (https://ctftime.org/team/392973)  
                **添加日历** : https://ctftime.org/event/3050.ics  
                
            ??? Quote "[TAMUctf 2026](https://tamuctf.com/)"  
                [![](https://ctftime.org/media/events/TAMUctf-logo.png){ width="200" align=left }](https://tamuctf.com/)  
                **比赛名称** : [TAMUctf 2026](https://tamuctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-21 06:00:00 - 2026-03-23 06:00:00 UTC+8  
                **比赛权重** : 76.22  
                **赛事主办** : TAMUctf (https://ctftime.org/team/37721)  
                **添加日历** : https://ctftime.org/event/3095.ics  
                
            ??? Quote "[ZeroDays CTF 2026](http://www.zerodays.ie/)"  
                [![](https://ctftime.org/media/events/4ed567668366c4f824552685fc0c6b04.png){ width="200" align=left }](http://www.zerodays.ie/)  
                **比赛名称** : [ZeroDays CTF 2026](http://www.zerodays.ie/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-21 18:00:00 - 2026-03-22 01:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Ireland without the RE (https://ctftime.org/team/179144)  
                **添加日历** : https://ctftime.org/event/3063.ics  
                
            ??? Quote "[Undutmaning 2026](https://undutmaning.se/)"  
                [![](https://ctftime.org/media/events/logo_2026_border.png){ width="200" align=left }](https://undutmaning.se/)  
                **比赛名称** : [Undutmaning 2026](https://undutmaning.se/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-21 19:00:00 - 2026-03-22 03:00:00 UTC+8  
                **比赛权重** : 33.00  
                **赛事主办** : Undutmaning (https://ctftime.org/team/212504)  
                **添加日历** : https://ctftime.org/event/2987.ics  
                
            ??? Quote "[KalmarCTF 2026](https://kalmarc.tf/)"  
                [![](https://ctftime.org/media/events/kalmar-logo_1.png){ width="200" align=left }](https://kalmarc.tf/)  
                **比赛名称** : [KalmarCTF 2026](https://kalmarc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-28 01:00:00 - 2026-03-30 01:00:00 UTC+8  
                **比赛权重** : 49.97  
                **赛事主办** : kalmarunionen (https://ctftime.org/team/114856)  
                **添加日历** : https://ctftime.org/event/2983.ics  
                
            ??? Quote "[HackDay 2026 - Finals](https://hackday.fr/)"  
                [![](https://ctftime.org/media/events/hackday_1.png){ width="200" align=left }](https://hackday.fr/)  
                **比赛名称** : [HackDay 2026 - Finals](https://hackday.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-28 02:00:00 - 2026-03-29 02:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : HackDayCTF (https://ctftime.org/team/277562)  
                **添加日历** : https://ctftime.org/event/3039.ics  
                
            ??? Quote "[Flag Wars](https://laokoon-security.com/ctf2026)"  
                [![](https://ctftime.org/media/events/image_5.png){ width="200" align=left }](https://laokoon-security.com/ctf2026)  
                **比赛名称** : [Flag Wars](https://laokoon-security.com/ctf2026)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-28 17:00:00 - 2026-03-29 03:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Laokoon SecurITy (https://ctftime.org/team/201667)  
                **添加日历** : https://ctftime.org/event/3084.ics  
                
            ??? Quote "[VolgaCTF 2026 Qualifier](https://volgactf.ru/en/volgactf-2026/qualifier/)"  
                [![](https://ctftime.org/media/events/logo-social-yellow_18.png){ width="200" align=left }](https://volgactf.ru/en/volgactf-2026/qualifier/)  
                **比赛名称** : [VolgaCTF 2026 Qualifier](https://volgactf.ru/en/volgactf-2026/qualifier/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-03-28 21:00:00 - 2026-03-29 21:00:00 UTC+8  
                **比赛权重** : 38.67  
                **赛事主办** : VolgaCTF.org (https://ctftime.org/team/27094)  
                **添加日历** : https://ctftime.org/event/3045.ics  
                
            ??? Quote "[GLOBAL CYBER GAMES: Women's Attack and Defense Edition @Wicked6](https://www.wicked6.com/tournament)"  
                [![](){ width="200" align=left }](https://www.wicked6.com/tournament)  
                **比赛名称** : [GLOBAL CYBER GAMES: Women's Attack and Defense Edition @Wicked6](https://www.wicked6.com/tournament)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2026-03-29 20:00:00 - 2026-03-30 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : PlayCyber (https://ctftime.org/team/165788)  
                **添加日历** : https://ctftime.org/event/3057.ics  
                
            ??? Quote "[SillyCTF 2](https://sillyctf.psuccso.org/)"  
                [![](https://ctftime.org/media/events/SillyCTF2logo.png){ width="200" align=left }](https://sillyctf.psuccso.org/)  
                **比赛名称** : [SillyCTF 2](https://sillyctf.psuccso.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-04-04 20:00:00 - 2026-04-05 12:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Penn State CCSO (https://ctftime.org/team/367931)  
                **添加日历** : https://ctftime.org/event/3042.ics  
                
            ??? Quote "[Dreamhack Invitational 2026](https://dreamhack.io/)"  
                [![](){ width="200" align=left }](https://dreamhack.io/)  
                **比赛名称** : [Dreamhack Invitational 2026](https://dreamhack.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-04-07 08:00:00 - 2026-04-07 23:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Dreamhack (https://ctftime.org/team/367894)  
                **添加日历** : https://ctftime.org/event/3026.ics  
                
            ??? Quote "[UMassCTF 2026](https://ctf.umasscybersec.org/)"  
                [![](https://ctftime.org/media/events/CTF_LOGO_20240401_190034_0000.jpg){ width="200" align=left }](https://ctf.umasscybersec.org/)  
                **比赛名称** : [UMassCTF 2026](https://ctf.umasscybersec.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-04-11 06:00:00 - 2026-04-13 06:00:00 UTC+8  
                **比赛权重** : 65.95  
                **赛事主办** : SavedByTheShell (https://ctftime.org/team/78233)  
                **添加日历** : https://ctftime.org/event/2937.ics  
                
            ??? Quote "[Midnight Sun CTF 2026 Quals](https://play.midnightsunctf.com/)"  
                [![](https://ctftime.org/media/events/midnightsun_2024_log_TRIMMEDo.png){ width="200" align=left }](https://play.midnightsunctf.com/)  
                **比赛名称** : [Midnight Sun CTF 2026 Quals](https://play.midnightsunctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-04-11 18:00:00 - 2026-04-12 18:00:00 UTC+8  
                **比赛权重** : 48.17  
                **赛事主办** : HackingForSoju (https://ctftime.org/team/3208)  
                **添加日历** : https://ctftime.org/event/2773.ics  
                
            ??? Quote "[CPCTF 2026](https://cpctf.space/)"  
                [![](https://ctftime.org/media/events/cpctf_logo_1_1.png){ width="200" align=left }](https://cpctf.space/)  
                **比赛名称** : [CPCTF 2026](https://cpctf.space/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-04-17 19:00:00 - 2026-04-19 19:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : traP (https://ctftime.org/team/62510)  
                **添加日历** : https://ctftime.org/event/3077.ics  
                
            ??? Quote "[BlueHens CTF 2025](https://bluehens.ctfd.io/)"  
                [![](https://ctftime.org/media/events/bluehens_1.png){ width="200" align=left }](https://bluehens.ctfd.io/)  
                **比赛名称** : [BlueHens CTF 2025](https://bluehens.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-04-18 01:00:00 - 2026-04-19 13:00:00 UTC+8  
                **比赛权重** : 44.77  
                **赛事主办** : Blue Hens (https://ctftime.org/team/64660)  
                **添加日历** : https://ctftime.org/event/2943.ics  
                
            ??? Quote "[UMDCTF 2026](https://umdctf.io/)"  
                [![](https://ctftime.org/media/events/icon_logo.png){ width="200" align=left }](https://umdctf.io/)  
                **比赛名称** : [UMDCTF 2026](https://umdctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-04-25 06:00:00 - 2026-04-27 06:00:00 UTC+8  
                **比赛权重** : 85.48  
                **赛事主办** : UMDCSEC (https://ctftime.org/team/87711)  
                **添加日历** : https://ctftime.org/event/3056.ics  
                
            ??? Quote "[PHONIX VIPER NOVA CTF#2](http://pwnctf.ro/)"  
                [![](https://ctftime.org/media/events/0b084a17fe379613dd5be4f540c64249.png){ width="200" align=left }](http://pwnctf.ro/)  
                **比赛名称** : [PHONIX VIPER NOVA CTF#2](http://pwnctf.ro/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-05-08 18:00:00 - 2026-05-11 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : PH03N1X V1P3R N0V4 CTF (https://ctftime.org/team/395369)  
                **添加日历** : https://ctftime.org/event/3018.ics  
                
            ??? Quote "[SAS CTF 2026 Quals](https://ctf.thesascon.com/)"  
                [![](https://ctftime.org/media/events/SAS26_temp.png){ width="200" align=left }](https://ctf.thesascon.com/)  
                **比赛名称** : [SAS CTF 2026 Quals](https://ctf.thesascon.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-05-23 20:00:00 - 2026-05-24 20:00:00 UTC+8  
                **比赛权重** : 31.00  
                **赛事主办** : Drovosec, SAS CREW (https://ctftime.org/team/210132, https://ctftime.org/team/283057)  
                **添加日历** : https://ctftime.org/event/3109.ics  
                
            ??? Quote "[GPN CTF 2026](https://gpn24.ctf.kitctf.de/)"  
                [![](){ width="200" align=left }](https://gpn24.ctf.kitctf.de/)  
                **比赛名称** : [GPN CTF 2026](https://gpn24.ctf.kitctf.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-06-05 18:00:00 - 2026-06-07 06:00:00 UTC+8  
                **比赛权重** : 69.00  
                **赛事主办** : KITCTF (https://ctftime.org/team/7221)  
                **添加日历** : https://ctftime.org/event/3041.ics  
                
            ??? Quote "[SSMCTF 2026 Qualifiers](https://ssmct.org/ctf)"  
                [![](){ width="200" align=left }](https://ssmct.org/ctf)  
                **比赛名称** : [SSMCTF 2026 Qualifiers](https://ssmct.org/ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-06-07 18:00:00 - 2026-06-08 18:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Singapore Students Merger (https://ctftime.org/team/299075)  
                **添加日历** : https://ctftime.org/event/2913.ics  
                
            ??? Quote "[Crypto CTF 2026](https://cr.yp.toc.tf/)"  
                [![](https://ctftime.org/media/events/cryptoctf_logo.jpg){ width="200" align=left }](https://cr.yp.toc.tf/)  
                **比赛名称** : [Crypto CTF 2026](https://cr.yp.toc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-06-13 22:00:00 - 2026-06-14 22:00:00 UTC+8  
                **比赛权重** : 91.00  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/3034.ics  
                
            ??? Quote "[L3akCTF 2026](https://ctf.l3ak.team/)"  
                [![](https://ctftime.org/media/events/6a9256e0b32707195ff9fe31b358a0e6.png){ width="200" align=left }](https://ctf.l3ak.team/)  
                **比赛名称** : [L3akCTF 2026](https://ctf.l3ak.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-07-11 02:00:00 - 2026-07-13 02:00:00 UTC+8  
                **比赛权重** : 34.47  
                **赛事主办** : L3ak (https://ctftime.org/team/220336)  
                **添加日历** : https://ctftime.org/event/3061.ics  
                
            ??? Quote "[OmniCTF 2026 Quals](https://omnictf.com/)"  
                [![](https://ctftime.org/media/events/logo1024x1024_1.png){ width="200" align=left }](https://omnictf.com/)  
                **比赛名称** : [OmniCTF 2026 Quals](https://omnictf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-07-17 23:00:00 - 2026-07-19 23:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : OmniCYBR (https://ctftime.org/team/383015)  
                **添加日历** : https://ctftime.org/event/3104.ics  
                
            ??? Quote "[scriptCTF 2026](https://ctf.scriptsorcerers.xyz/)"  
                [![](https://ctftime.org/media/events/final_logo_1.png){ width="200" align=left }](https://ctf.scriptsorcerers.xyz/)  
                **比赛名称** : [scriptCTF 2026](https://ctf.scriptsorcerers.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-08-08 08:00:00 - 2026-08-10 08:00:00 UTC+8  
                **比赛权重** : 24.70  
                **赛事主办** : ScriptSorcerers (https://ctftime.org/team/284260)  
                **添加日历** : https://ctftime.org/event/3052.ics  
                
            ??? Quote "[BrunnerCTF 2026](https://ctf.brunnerne.dk/)"  
                [![](https://ctftime.org/media/events/Logo_-_2-7.png){ width="200" align=left }](https://ctf.brunnerne.dk/)  
                **比赛名称** : [BrunnerCTF 2026](https://ctf.brunnerne.dk/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-08-21 20:00:00 - 2026-08-23 20:00:00 UTC+8  
                **比赛权重** : 24.66  
                **赛事主办** : Brunnerne (https://ctftime.org/team/155032)  
                **添加日历** : https://ctftime.org/event/3065.ics  
                
            ??? Quote "[ASIS CTF Quals 2026](https://asisctf.com/)"  
                [![](https://ctftime.org/media/events/asis_logo_1.png){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Quals 2026](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-08-29 22:00:00 - 2026-08-30 22:00:00 UTC+8  
                **比赛权重** : 90.53  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/3033.ics  
                
            ??? Quote "[NNS CTF 2026](https://nnsc.tf/)"  
                [![](https://ctftime.org/media/events/Logo_D_1.png){ width="200" align=left }](https://nnsc.tf/)  
                **比赛名称** : [NNS CTF 2026](https://nnsc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-09-05 00:00:00 - 2026-09-07 00:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Norske Nøkkelsnikere (https://ctftime.org/team/222749)  
                **添加日历** : https://ctftime.org/event/3097.ics  
                
            ??? Quote "[Pointer Overflow CTF - 2026](https://pointeroverflowctf.com/)"  
                [![](https://ctftime.org/media/events/logo-mini.png){ width="200" align=left }](https://pointeroverflowctf.com/)  
                **比赛名称** : [Pointer Overflow CTF - 2026](https://pointeroverflowctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-09-27 22:00:00 - 2026-12-06 22:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : UWSP Pointers (https://ctftime.org/team/231536)  
                **添加日历** : https://ctftime.org/event/3020.ics  
                
            ??? Quote "[Platypwn 2026](https://platypwnies.de/events/platypwn/)"  
                [![](https://ctftime.org/media/events/platypwnies-512_1_1.png){ width="200" align=left }](https://platypwnies.de/events/platypwn/)  
                **比赛名称** : [Platypwn 2026](https://platypwnies.de/events/platypwn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-11-14 17:00:00 - 2026-11-16 05:00:00 UTC+8  
                **比赛权重** : 37.00  
                **赛事主办** : Platypwnies (https://ctftime.org/team/112550)  
                **添加日历** : https://ctftime.org/event/3082.ics  
                
            ??? Quote "[ASIS CTF Finals 2026](https://asisctf.com/)"  
                [![](https://ctftime.org/media/events/asis_logo_2.png){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Finals 2026](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-12-27 22:00:00 - 2026-12-28 22:00:00 UTC+8  
                **比赛权重** : 99.38  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/3062.ics  
                
    === "*正在进行*"
        === "国内赛事"
            ??? Quote "[furryCTF 2025 高校联合新神赛](https://furryctf.com/)"  
                **比赛名称** : [furryCTF 2025 高校联合新神赛](https://furryctf.com/)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2026年01月01日 00:00 - 2026年02月04日 12:00  
                **比赛时间** : 2026年01月30日 12:00 - 2026年02月04日 12:00  
                **其他说明** : 主办方为furryCTF及POFP联合战队，严禁攻击平台或使用扫描器，设有多种奖品，详情请到QQ群查看；祝各位玩的开心~  
                
        === "国外赛事"
            ??? Quote "[2026 Embedded Capture the Flag](https://ectf.mitre.org/)"  
                [![](){ width="200" align=left }](https://ectf.mitre.org/)  
                **比赛名称** : [2026 Embedded Capture the Flag](https://ectf.mitre.org/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2026-01-14 20:00:00 - 2026-04-15 20:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : ectfmitre (https://ctftime.org/team/87292)  
                **添加日历** : https://ctftime.org/event/2916.ics  
                
            ??? Quote "[Hack for a Change 2026 January: UN SDG 15](http://www.hackforachange.org/)"  
                [![](https://ctftime.org/media/events/logo_117.png){ width="200" align=left }](http://www.hackforachange.org/)  
                **比赛名称** : [Hack for a Change 2026 January: UN SDG 15](http://www.hackforachange.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-30 08:00:00 - 2026-02-03 07:59:59 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Hack for a Change (https://ctftime.org/team/419248)  
                **添加日历** : https://ctftime.org/event/3083.ics  
                
    === "*已经结束*"
        === "国内赛事"
            ??? Quote "[UniCTF](https://unictf.play.ctfplus.cn/)"  
                **比赛名称** : [UniCTF](https://unictf.play.ctfplus.cn/)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2026年01月09日 10:09 - 2026年01月25日 09:59  
                **比赛时间** : 2026年01月25日 10:00 - 2026年01月31日 10:00  
                **其他说明** : 4人一组团队赛，需先在CTFPlus比赛大厅报名（https://www.ctfplus.cn）；奖项含社会赛道与新生赛道奖金及证书，单方向额外奖励。  
                
        === "国外赛事"
            ??? Quote "[PascalCTF 2026](https://ctf.pascalctf.it/)"  
                [![](https://ctftime.org/media/events/log.jpg){ width="200" align=left }](https://ctf.pascalctf.it/)  
                **比赛名称** : [PascalCTF 2026](https://ctf.pascalctf.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-31 16:00:00 - 2026-02-01 16:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Paolo (https://ctftime.org/team/263145)  
                **添加日历** : https://ctftime.org/event/2767.ics  
                
            ??? Quote "[Eschaton CTF 2026 Quals](https://eschaton.mcsc.space/)"  
                [![](){ width="200" align=left }](https://eschaton.mcsc.space/)  
                **比赛名称** : [Eschaton CTF 2026 Quals](https://eschaton.mcsc.space/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-31 12:30:00 - 2026-02-01 12:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Team MCSC (https://ctftime.org/team/418958)  
                **添加日历** : https://ctftime.org/event/3072.ics  
                
            ??? Quote "[RCS CTF 26](https://encryptedge.in/)"  
                [![](){ width="200" align=left }](https://encryptedge.in/)  
                **比赛名称** : [RCS CTF 26](https://encryptedge.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-31 03:00:00 - 2026-01-31 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : EN¢R¥PT_EDGE€ (https://ctftime.org/team/273673)  
                **添加日历** : https://ctftime.org/event/3114.ics  
                
            ??? Quote "[ATC Winter Vibes Community CTF 2.0](https://atcwintervibesctf.com/)"  
                [![](https://ctftime.org/media/events/ATC_Logo.PNG){ width="200" align=left }](https://atcwintervibesctf.com/)  
                **比赛名称** : [ATC Winter Vibes Community CTF 2.0](https://atcwintervibesctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-30 22:00:00 - 2026-01-31 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ATC CTF Team (https://ctftime.org/team/370333)  
                **添加日历** : https://ctftime.org/event/3068.ics  
                
            ??? Quote "[Jeanne d'Hack CTF 2026 | 3ème Édition](https://www.jeanne-hack-ctf.org/)"  
                [![](https://ctftime.org/media/events/LogoAlt.png){ width="200" align=left }](https://www.jeanne-hack-ctf.org/)  
                **比赛名称** : [Jeanne d'Hack CTF 2026 | 3ème Édition](https://www.jeanne-hack-ctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-30 17:00:00 - 2026-01-31 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Jeanne d'Hack CTF (https://ctftime.org/team/283058)  
                **添加日历** : https://ctftime.org/event/2941.ics  
                
            ??? Quote "[ASCF CTF](https://ctf.ascf.space/)"  
                [![](https://ctftime.org/media/events/ascf1.png){ width="200" align=left }](https://ctf.ascf.space/)  
                **比赛名称** : [ASCF CTF](https://ctf.ascf.space/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-30 17:00:00 - 2026-01-31 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : ASCF (https://ctftime.org/team/418960)  
                **添加日历** : https://ctftime.org/event/3099.ics  
                
            ??? Quote "[CyberQuest 26](https://ngpkanam.com/events/41)"  
                [![](https://ctftime.org/media/events/WhatsApp_Image_2026-01-15_at_16.42.06.jpeg){ width="200" align=left }](https://ngpkanam.com/events/41)  
                **比赛名称** : [CyberQuest 26](https://ngpkanam.com/events/41)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-28 11:30:00 - 2026-01-28 19:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Cybernexus (https://ctftime.org/team/400801)  
                **添加日历** : https://ctftime.org/event/3080.ics  
                
            ??? Quote "[Fluid Attacks' CTF 2026-1](https://fluidattacks.com/ctf)"  
                [![](https://ctftime.org/media/events/2.jpg){ width="200" align=left }](https://fluidattacks.com/ctf)  
                **比赛名称** : [Fluid Attacks' CTF 2026-1](https://fluidattacks.com/ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-24 21:00:00 - 2026-01-25 21:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Fluid Attacks (https://ctftime.org/team/126627)  
                **添加日历** : https://ctftime.org/event/3087.ics  
                
            ??? Quote "[VSL CTF 2026](https://vsl-ctf.com/)"  
                [![](https://ctftime.org/media/events/logo_16.jpg){ width="200" align=left }](https://vsl-ctf.com/)  
                **比赛名称** : [VSL CTF 2026](https://vsl-ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-24 16:00:00 - 2026-01-25 16:00:00 UTC+8  
                **比赛权重** : 23.60  
                **赛事主办** : VSL (https://ctftime.org/team/284373)  
                **添加日历** : https://ctftime.org/event/3060.ics  
                
            ??? Quote "[LilacCTF 2026](https://lilacctf2026.xctf.org.cn/)"  
                [![](https://ctftime.org/media/events/square.jpg){ width="200" align=left }](https://lilacctf2026.xctf.org.cn/)  
                **比赛名称** : [LilacCTF 2026](https://lilacctf2026.xctf.org.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-24 09:00:00 - 2026-01-26 09:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Lilac (https://ctftime.org/team/15163)  
                **添加日历** : https://ctftime.org/event/3071.ics  
                
            ??? Quote "[Dreamhack Invitational Quals 2026](https://dreamhack.io/ctf/772)"  
                [![](https://ctftime.org/media/events/e66fed5653581908ac8e93f82ad73cae_2.jpg){ width="200" align=left }](https://dreamhack.io/ctf/772)  
                **比赛名称** : [Dreamhack Invitational Quals 2026](https://dreamhack.io/ctf/772)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-24 08:00:00 - 2026-01-25 08:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Dreamhack (https://ctftime.org/team/367894)  
                **添加日历** : https://ctftime.org/event/3025.ics  
                
            ??? Quote "[Säkerhets-SM Quals 2026](https://ctf.sakerhetssm.se/)"  
                [![](){ width="200" align=left }](https://ctf.sakerhetssm.se/)  
                **比赛名称** : [Säkerhets-SM Quals 2026](https://ctf.sakerhetssm.se/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-24 03:00:00 - 2026-01-26 03:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Kodsport (https://ctftime.org/team/395272)  
                **添加日历** : https://ctftime.org/event/2945.ics  
                
            ??? Quote "[HackDay 2026 - Qualifications](https://register.hackday.fr/register/)"  
                [![](https://ctftime.org/media/events/5513a205a0a6489f9dc0ecff6fd7d669.png){ width="200" align=left }](https://register.hackday.fr/register/)  
                **比赛名称** : [HackDay 2026 - Qualifications](https://register.hackday.fr/register/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-24 03:00:00 - 2026-01-26 03:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : HackDayCTF (https://ctftime.org/team/277562)  
                **添加日历** : https://ctftime.org/event/3038.ics  
                
            ??? Quote "[0xL4ugh CTF v5](https://ctf.0xL4ugh.com/)"  
                [![](){ width="200" align=left }](https://ctf.0xL4ugh.com/)  
                **比赛名称** : [0xL4ugh CTF v5](https://ctf.0xL4ugh.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-23 21:00:00 - 2026-01-25 21:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : 0xL4ugh (https://ctftime.org/team/132776)  
                **添加日历** : https://ctftime.org/event/3024.ics  
                
            ??? Quote "[MetaCTF January 2026 Flash CTF](https://mctf.io/jan2026)"  
                [![](){ width="200" align=left }](https://mctf.io/jan2026)  
                **比赛名称** : [MetaCTF January 2026 Flash CTF](https://mctf.io/jan2026)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-23 06:00:00 - 2026-01-23 09:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : MetaCTF (https://ctftime.org/team/72254)  
                **添加日历** : https://ctftime.org/event/3079.ics  
                
            ??? Quote "[KnightCTF 2026](https://2026.knightctf.com/)"  
                [![](https://ctftime.org/media/events/knightctf-logo.png){ width="200" align=left }](https://2026.knightctf.com/)  
                **比赛名称** : [KnightCTF 2026](https://2026.knightctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-20 23:00:00 - 2026-01-21 23:00:00 UTC+8  
                **比赛权重** : 22.21  
                **赛事主办** : Knight Squad (https://ctftime.org/team/141739)  
                **添加日历** : https://ctftime.org/event/3053.ics  
                
            ??? Quote "[SWIMMER OSINT CTF](https://swimmer.diverctf.org/)"  
                [![](https://ctftime.org/media/events/circle-white-text.png){ width="200" align=left }](https://swimmer.diverctf.org/)  
                **比赛名称** : [SWIMMER OSINT CTF](https://swimmer.diverctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-17 11:10:00 - 2026-01-17 23:10:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : diver_osint (https://ctftime.org/team/299569)  
                **添加日历** : https://ctftime.org/event/2986.ics  
                
            ??? Quote "[CyberCup Indian Ocean](https://cybercup.ocoi.org/)"  
                [![](https://ctftime.org/media/events/logo2_8.png){ width="200" align=left }](https://cybercup.ocoi.org/)  
                **比赛名称** : [CyberCup Indian Ocean](https://cybercup.ocoi.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-17 00:00:00 - 2026-01-19 00:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Hacking Indian Ocean (https://ctftime.org/team/399138)  
                **添加日历** : https://ctftime.org/event/3089.ics  
                
            ??? Quote "[New Year CTF 2026](http://ctf-spcs.mf.grsu.by/)"  
                [![](https://ctftime.org/media/events/NY2026.jpg){ width="200" align=left }](http://ctf-spcs.mf.grsu.by/)  
                **比赛名称** : [New Year CTF 2026](http://ctf-spcs.mf.grsu.by/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-10 17:00:00 - 2026-01-12 17:00:00 UTC+8  
                **比赛权重** : 23.42  
                **赛事主办** : Beavers0 (https://ctftime.org/team/269281)  
                **添加日历** : https://ctftime.org/event/3021.ics  
                
            ??? Quote "[SCPCTF](https://scpctf.vercel.app/)"  
                [![](https://ctftime.org/media/events/Screenshot_2025-10-03_231925_1.png){ width="200" align=left }](https://scpctf.vercel.app/)  
                **比赛名称** : [SCPCTF](https://scpctf.vercel.app/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-10 11:30:00 - 2026-01-12 11:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : SCP CTF (https://ctftime.org/team/415339)  
                **添加日历** : https://ctftime.org/event/3064.ics  
                
            ??? Quote "[UofTCTF 2026](https://ctf.uoftctf.org/)"  
                [![](https://ctftime.org/media/events/uoftctf_logo_3000_black_1.png){ width="200" align=left }](https://ctf.uoftctf.org/)  
                **比赛名称** : [UofTCTF 2026](https://ctf.uoftctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-10 08:00:00 - 2026-01-12 08:00:00 UTC+8  
                **比赛权重** : 33.49  
                **赛事主办** : UofTCTF (https://ctftime.org/team/139261)  
                **添加日历** : https://ctftime.org/event/2969.ics  
                
            ??? Quote "[Scarlet CTF 2026](http://ctf.rusec.club/)"  
                [![](https://ctftime.org/media/events/8ed561b45f892df2a5b105e8537794b3_1.jpg){ width="200" align=left }](http://ctf.rusec.club/)  
                **比赛名称** : [Scarlet CTF 2026](http://ctf.rusec.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2026-01-09 08:00:00 - 2026-01-12 08:00:00 UTC+8  
                **比赛权重** : 22.80  
                **赛事主办** : ScarletCTF (https://ctftime.org/team/226444)  
                **添加日历** : https://ctftime.org/event/2981.ics  
                
            ??? Quote "[hxp 39C3 CTF](https://2025.ctf.link/)"  
                [![](https://ctftime.org/media/events/hxp-39c3.png){ width="200" align=left }](https://2025.ctf.link/)  
                **比赛名称** : [hxp 39C3 CTF](https://2025.ctf.link/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-28 04:00:00 - 2025-12-30 04:00:00 UTC+8  
                **比赛权重** : 98.14  
                **赛事主办** : hxp (https://ctftime.org/team/585)  
                **添加日历** : https://ctftime.org/event/2924.ics  
                
            ??? Quote "[ASIS CTF Finals 2025](https://asisctf.com/)"  
                [![](){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Finals 2025](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-27 22:00:00 - 2025-12-28 22:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2613.ics  
                
            ??? Quote "[MetaCTF December 2025 Flash CTF](https://mctf.io/dec2025)"  
                [![](){ width="200" align=left }](https://mctf.io/dec2025)  
                **比赛名称** : [MetaCTF December 2025 Flash CTF](https://mctf.io/dec2025)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-21 01:00:00 - 2025-12-21 04:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : MetaCTF (https://ctftime.org/team/72254)  
                **添加日历** : https://ctftime.org/event/3036.ics  
                
            ??? Quote "[TSG CTF 2025](https://score.ctf.tsg.ne.jp/)"  
                [![](https://ctftime.org/media/events/TSG_CTF.png){ width="200" align=left }](https://score.ctf.tsg.ne.jp/)  
                **比赛名称** : [TSG CTF 2025](https://score.ctf.tsg.ne.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-20 15:00:00 - 2025-12-21 15:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : TSG (https://ctftime.org/team/16088)  
                **添加日历** : https://ctftime.org/event/2867.ics  
                
            ??? Quote "[0CTF 2025](https://ctf.0ops.sjtu.cn/)"  
                [![](){ width="200" align=left }](https://ctf.0ops.sjtu.cn/)  
                **比赛名称** : [0CTF 2025](https://ctf.0ops.sjtu.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-20 08:00:00 - 2025-12-22 08:00:00 UTC+8  
                **比赛权重** : 96.88  
                **赛事主办** : 0ops (https://ctftime.org/team/4419)  
                **添加日历** : https://ctftime.org/event/2997.ics  
                
            ??? Quote "[HKCERT CTF 2025 (Qualifying Round)](https://ctf.hkcert.org/)"  
                [![](https://ctftime.org/media/events/CTF2025.png){ width="200" align=left }](https://ctf.hkcert.org/)  
                **比赛名称** : [HKCERT CTF 2025 (Qualifying Round)](https://ctf.hkcert.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-19 16:00:00 - 2025-12-21 16:00:00 UTC+8  
                **比赛权重** : 83.21  
                **赛事主办** : HKCERT (https://ctftime.org/team/134746)  
                **添加日历** : https://ctftime.org/event/2998.ics  
                
            ??? Quote "[BSides Algiers 2025](https://bsides-algiers-2k25.shellmates.club/)"  
                [![](https://ctftime.org/media/events/image.jpg){ width="200" align=left }](https://bsides-algiers-2k25.shellmates.club/)  
                **比赛名称** : [BSides Algiers 2025](https://bsides-algiers-2k25.shellmates.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-19 03:00:00 - 2025-12-20 15:00:00 UTC+8  
                **比赛权重** : 22.90  
                **赛事主办** : noreply (https://ctftime.org/team/210760)  
                **添加日历** : https://ctftime.org/event/2962.ics  
                
            ??? Quote "[SecurITy Challenge - VianuCTF 2025](https://vianuhack.club/)"  
                [![](https://ctftime.org/media/events/1e25f32d-068f-4ad2-9b7d-a750fa82b97d.jpeg){ width="200" align=left }](https://vianuhack.club/)  
                **比赛名称** : [SecurITy Challenge - VianuCTF 2025](https://vianuhack.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-16 15:30:00 - 2025-12-16 22:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : vianu_hack (https://ctftime.org/team/379530)  
                **添加日历** : https://ctftime.org/event/3032.ics  
                
            ??? Quote "[Cybercoliseum IV](https://cybercoliseum.hackerlab.pro/en)"  
                [![](https://ctftime.org/media/events/cybercoliseum.png){ width="200" align=left }](https://cybercoliseum.hackerlab.pro/en)  
                **比赛名称** : [Cybercoliseum IV](https://cybercoliseum.hackerlab.pro/en)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-13 15:00:00 - 2025-12-14 15:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HackerLab (https://ctftime.org/team/299486)  
                **添加日历** : https://ctftime.org/event/3019.ics  
                
            ??? Quote "[SECCON CTF 14 Quals](https://ctf.seccon.jp/)"  
                [![](https://ctftime.org/media/events/seccon_s_10.png){ width="200" align=left }](https://ctf.seccon.jp/)  
                **比赛名称** : [SECCON CTF 14 Quals](https://ctf.seccon.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-13 13:00:00 - 2025-12-14 13:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : SECCON CTF (https://ctftime.org/team/11918)  
                **添加日历** : https://ctftime.org/event/2862.ics  
                
            ??? Quote "[niteCTF 2025](https://nitectf25.live/)"  
                [![](https://ctftime.org/media/events/nitectf2025.png){ width="200" align=left }](https://nitectf25.live/)  
                **比赛名称** : [niteCTF 2025](https://nitectf25.live/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-12 20:00:00 - 2025-12-14 20:00:00 UTC+8  
                **比赛权重** : 39.87  
                **赛事主办** : Cryptonite (https://ctftime.org/team/62713)  
                **添加日历** : https://ctftime.org/event/2851.ics  
                
            ??? Quote "[NexHunt CTF](https://nexus-security.club/)"  
                [![](https://ctftime.org/media/events/Group_64_2.png){ width="200" align=left }](https://nexus-security.club/)  
                **比赛名称** : [NexHunt CTF](https://nexus-security.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-12 02:00:00 - 2025-12-13 18:00:00 UTC+8  
                **比赛权重** : 23.73  
                **赛事主办** : Nexus Team (https://ctftime.org/team/361096)  
                **添加日历** : https://ctftime.org/event/3037.ics  
                
            ??? Quote "[BackdoorCTF 2025](https://backdoor.infoseciitr.in/)"  
                [![](https://ctftime.org/media/events/0b4a317ba84bb2bd6e871c5eec6fdb00_1.png){ width="200" align=left }](https://backdoor.infoseciitr.in/)  
                **比赛名称** : [BackdoorCTF 2025](https://backdoor.infoseciitr.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-06 20:00:00 - 2025-12-08 20:00:00 UTC+8  
                **比赛权重** : 71.35  
                **赛事主办** : InfoSecIITR (https://ctftime.org/team/16691)  
                **添加日历** : https://ctftime.org/event/2915.ics  
                
            ??? Quote "[CyKor CTF 2025](https://ctf.cykor.kr/)"  
                [![](){ width="200" align=left }](https://ctf.cykor.kr/)  
                **比赛名称** : [CyKor CTF 2025](https://ctf.cykor.kr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-06 09:00:00 - 2025-12-07 09:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : CyKOR (https://ctftime.org/team/369)  
                **添加日历** : https://ctftime.org/event/3028.ics  
                
            ??? Quote "[WannaGame Championship 2025](https://ctf.cnsc.com.vn/)"  
                [![](https://ctftime.org/media/events/Artboard_13x.png){ width="200" align=left }](https://ctf.cnsc.com.vn/)  
                **比赛名称** : [WannaGame Championship 2025](https://ctf.cnsc.com.vn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-06 09:00:00 - 2025-12-08 09:00:00 UTC+8  
                **比赛权重** : 29.00  
                **赛事主办** : UIT-Wanna.W1n (https://ctftime.org/team/138431)  
                **添加日历** : https://ctftime.org/event/2898.ics  
                
            ??? Quote "[VuwCTF 2025](https://2025.vuwctf.com/)"  
                [![](https://ctftime.org/media/events/VUWCTF_logo.png){ width="200" align=left }](https://2025.vuwctf.com/)  
                **比赛名称** : [VuwCTF 2025](https://2025.vuwctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-06 05:00:00 - 2025-12-07 12:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : VuwCTF (https://ctftime.org/team/378359)  
                **添加日历** : https://ctftime.org/event/3012.ics  
                
            ??? Quote "[P3rf3ctr00t CTF 2025](https://ctf.perfectroot.wiki/)"  
                [![](https://ctftime.org/media/events/project_20240319_1256007-01.png){ width="200" align=left }](https://ctf.perfectroot.wiki/)  
                **比赛名称** : [P3rf3ctr00t CTF 2025](https://ctf.perfectroot.wiki/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-05 23:00:00 - 2025-12-07 23:00:00 UTC+8  
                **比赛权重** : 24.40  
                **赛事主办** : L3v3l 6 (https://ctftime.org/team/206364)  
                **添加日历** : https://ctftime.org/event/3009.ics  
                
            ??? Quote "[Null CTF 2025](https://ctf.r0devnull.team/)"  
                [![](https://ctftime.org/media/events/null_ctf_logo_temp_1.png){ width="200" align=left }](https://ctf.r0devnull.team/)  
                **比赛名称** : [Null CTF 2025](https://ctf.r0devnull.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-05 23:00:00 - 2025-12-07 23:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : r0/dev/null (https://ctftime.org/team/398024)  
                **添加日历** : https://ctftime.org/event/2901.ics  
                
            ??? Quote "[Metared Argentina 2025](https://ctf.cert.unlp.edu.ar/)"  
                [![](https://ctftime.org/media/events/0645ac9c15c72f7be37e5ff68bafea52.jpg){ width="200" align=left }](https://ctf.cert.unlp.edu.ar/)  
                **比赛名称** : [Metared Argentina 2025](https://ctf.cert.unlp.edu.ar/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-04 20:00:00 - 2025-12-05 20:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CERTUNLP (https://ctftime.org/team/89294)  
                **添加日历** : https://ctftime.org/event/3003.ics  
                
            ??? Quote "[BlackHat MEA CTF Final 2025](https://blackhatmea.com/capture-the-flag)"  
                [![](https://ctftime.org/media/events/e0c283c95f7b0db516dae505d31ca20b_2_2.jpg){ width="200" align=left }](https://blackhatmea.com/capture-the-flag)  
                **比赛名称** : [BlackHat MEA CTF Final 2025](https://blackhatmea.com/capture-the-flag)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-02 16:00:00 - 2025-12-04 23:00:00 UTC+8  
                **比赛权重** : 22.50  
                **赛事主办** : SAFCSP (https://ctftime.org/team/54707)  
                **添加日历** : https://ctftime.org/event/2877.ics  
                
            ??? Quote "[Advent of CTF 2025](https://cyberstudents.net/advent)"  
                [![](){ width="200" align=left }](https://cyberstudents.net/advent)  
                **比赛名称** : [Advent of CTF 2025](https://cyberstudents.net/advent)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-12-02 09:00:00 - 2026-01-01 12:59:59 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : CyberStudentsCTF (https://ctftime.org/team/365239)  
                **添加日历** : https://ctftime.org/event/3022.ics  
                
            ??? Quote "[m0leCon 2026 Beginner CTF](https://beginner.m0lecon.it/)"  
                [![](){ width="200" align=left }](https://beginner.m0lecon.it/)  
                **比赛名称** : [m0leCon 2026 Beginner CTF](https://beginner.m0lecon.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-29 21:00:00 - 2025-11-30 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : pwnthem0le (https://ctftime.org/team/60467)  
                **添加日历** : https://ctftime.org/event/3017.ics  
                
            ??? Quote "[Haix-la-Chapelle 2025](https://haix-la-chapelle.eu/)"  
                [![](https://ctftime.org/media/events/white-haix-la-chapelle.png){ width="200" align=left }](https://haix-la-chapelle.eu/)  
                **比赛名称** : [Haix-la-Chapelle 2025](https://haix-la-chapelle.eu/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-29 17:00:00 - 2025-11-30 17:00:00 UTC+8  
                **比赛权重** : 24.00  
                **赛事主办** : Pwn-la-Chapelle (https://ctftime.org/team/279433)  
                **添加日历** : https://ctftime.org/event/2951.ics  
                
            ??? Quote "[WP CTF 2025](https://wpctf.it/)"  
                [![](https://ctftime.org/media/events/WP_CTF_2025_-_Logo.png){ width="200" align=left }](https://wpctf.it/)  
                **比赛名称** : [WP CTF 2025](https://wpctf.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-29 16:00:00 - 2025-11-30 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : WP CTF (https://ctftime.org/team/303099)  
                **添加日历** : https://ctftime.org/event/2764.ics  
                
            ??? Quote "[HeroCTF v7](https://ctf.heroctf.fr/)"  
                [![](){ width="200" align=left }](https://ctf.heroctf.fr/)  
                **比赛名称** : [HeroCTF v7](https://ctf.heroctf.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-29 04:00:00 - 2025-12-01 06:00:00 UTC+8  
                **比赛权重** : 65.00  
                **赛事主办** : HeroCTF (https://ctftime.org/team/145166)  
                **添加日历** : https://ctftime.org/event/2869.ics  
                
            ??? Quote "[LakeCTF Quals 25-26](https://lakectf.epfl.ch/)"  
                [![](https://ctftime.org/media/events/lake_logo.png){ width="200" align=left }](https://lakectf.epfl.ch/)  
                **比赛名称** : [LakeCTF Quals 25-26](https://lakectf.epfl.ch/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-29 02:00:00 - 2025-11-30 02:00:00 UTC+8  
                **比赛权重** : 45.00  
                **赛事主办** : polygl0ts (https://ctftime.org/team/53791)  
                **添加日历** : https://ctftime.org/event/2944.ics  
                
            ??? Quote "[2025 Qiangwang Challenge on Cyber Mimic Defense Finals](https://nest.pmlabs.com.cn/#/internationalEliteChallenge)"  
                [![](https://ctftime.org/media/events/mimicoctupus.png){ width="200" align=left }](https://nest.pmlabs.com.cn/#/internationalEliteChallenge)  
                **比赛名称** : [2025 Qiangwang Challenge on Cyber Mimic Defense Finals](https://nest.pmlabs.com.cn/#/internationalEliteChallenge)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-26 12:00:00 - 2025-11-29 12:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : LoveFromMimic (https://ctftime.org/team/364644)  
                **添加日历** : https://ctftime.org/event/2999.ics  
                
            ??? Quote "[Infosec University Hackathon 2025](https://syfinfosechackathon.info/)"  
                [![](https://ctftime.org/media/events/OCTOBER_INFOSEC_AWARENESS_MONTH_-_Logo.jpg){ width="200" align=left }](https://syfinfosechackathon.info/)  
                **比赛名称** : [Infosec University Hackathon 2025](https://syfinfosechackathon.info/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-23 10:00:00 - 2025-11-23 15:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Synchrony Infosec University Hackathon (https://ctftime.org/team/412036)  
                **添加日历** : https://ctftime.org/event/3008.ics  
                
            ??? Quote "[GlacierCTF 2025](https://play.glacierctf.com/)"  
                [![](https://ctftime.org/media/events/glacierlogo.png){ width="200" align=left }](https://play.glacierctf.com/)  
                **比赛名称** : [GlacierCTF 2025](https://play.glacierctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-23 02:00:00 - 2025-11-24 02:00:00 UTC+8  
                **比赛权重** : 52.57  
                **赛事主办** : LosFuzzys (https://ctftime.org/team/8323)  
                **添加日历** : https://ctftime.org/event/2714.ics  
                
            ??? Quote "[CyberSci Regional Qualifiers 2025-26](https://cybersecuritychallenge.ca/)"  
                [![](https://ctftime.org/media/events/aa01b0217ba20e130d4605e9bf2b8e6c.jpg){ width="200" align=left }](https://cybersecuritychallenge.ca/)  
                **比赛名称** : [CyberSci Regional Qualifiers 2025-26](https://cybersecuritychallenge.ca/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-22 23:00:00 - 2025-11-23 06:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : CyberSciOrganizers (https://ctftime.org/team/157536)  
                **添加日历** : https://ctftime.org/event/2909.ics  
                
            ??? Quote "[CTFZone 2025 Final](https://ctfz.zone/)"  
                [![](https://ctftime.org/media/events/aa86f826480a008ed91d88a917a0c33b_1.png){ width="200" align=left }](https://ctfz.zone/)  
                **比赛名称** : [CTFZone 2025 Final](https://ctfz.zone/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2025-11-22 17:00:00 - 2025-11-23 01:00:00 UTC+8  
                **比赛权重** : 96.90  
                **赛事主办** : BIZone (https://ctftime.org/team/32190)  
                **添加日历** : https://ctftime.org/event/2972.ics  
                
            ??? Quote "[sknbCTF 2025](http://ctf.sknb.team/)"  
                [![](https://ctftime.org/media/events/sknb_logo.png){ width="200" align=left }](http://ctf.sknb.team/)  
                **比赛名称** : [sknbCTF 2025](http://ctf.sknb.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-22 11:00:00 - 2025-11-23 11:00:00 UTC+8  
                **比赛权重** : 24.68  
                **赛事主办** : sknb (https://ctftime.org/team/355880)  
                **添加日历** : https://ctftime.org/event/2947.ics  
                
            ??? Quote "[PatriotCTF 2025](http://pctf.competitivecyber.club/)"  
                [![](https://ctftime.org/media/events/71044796c6f64e9996d2077fd0b64c4c.jpg){ width="200" align=left }](http://pctf.competitivecyber.club/)  
                **比赛名称** : [PatriotCTF 2025](http://pctf.competitivecyber.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-22 02:00:00 - 2025-11-24 02:00:00 UTC+8  
                **比赛权重** : 42.42  
                **赛事主办** : Competitive Cyber at Mason (https://ctftime.org/team/176906)  
                **添加日历** : https://ctftime.org/event/2850.ics  
                
            ??? Quote "[MetaCTF November 2025 Flash CTF](https://mctf.io/nov2025)"  
                [![](){ width="200" align=left }](https://mctf.io/nov2025)  
                **比赛名称** : [MetaCTF November 2025 Flash CTF](https://mctf.io/nov2025)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-21 06:00:00 - 2025-11-21 08:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : MetaCTF (https://ctftime.org/team/72254)  
                **添加日历** : https://ctftime.org/event/3010.ics  
                
            ??? Quote "[Hardwear.io NL 2025 Hardware CTF](https://hwc.tf/)"  
                [![](https://ctftime.org/media/events/logohwcolor_16.png){ width="200" align=left }](https://hwc.tf/)  
                **比赛名称** : [Hardwear.io NL 2025 Hardware CTF](https://hwc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-20 17:00:00 - 2025-11-21 20:50:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hardware CTF (https://ctftime.org/team/274600)  
                **添加日历** : https://ctftime.org/event/3002.ics  
                
            ??? Quote "[snakeCTF 2025 Finals](https://snakectf.org/)"  
                [![](https://ctftime.org/media/events/LogoCroppable_2_1.png){ width="200" align=left }](https://snakectf.org/)  
                **比赛名称** : [snakeCTF 2025 Finals](https://snakectf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-20 16:00:00 - 2025-11-23 21:00:00 UTC+8  
                **比赛权重** : 21.00  
                **赛事主办** : MadrHacks (https://ctftime.org/team/114509)  
                **添加日历** : https://ctftime.org/event/2994.ics  
                
            ??? Quote "[Ukrainian National CTF](https://hackenproof.com/gur-national-ctf-en)"  
                [![](https://ctftime.org/media/events/nationalCtf.jpg){ width="200" align=left }](https://hackenproof.com/gur-national-ctf-en)  
                **比赛名称** : [Ukrainian National CTF](https://hackenproof.com/gur-national-ctf-en)  
                **比赛形式** : Hack quest  
                **比赛时间** : 2025-11-20 08:00:00 - 2025-12-01 08:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Hacken Proof (https://ctftime.org/team/411613)  
                **添加日历** : https://ctftime.org/event/3007.ics  
                
            ??? Quote "[M*CTF 2025 Quals](https://mctf.mtuci.ru/)"  
                [![](https://ctftime.org/media/events/logo_15.jpg){ width="200" align=left }](https://mctf.mtuci.ru/)  
                **比赛名称** : [M*CTF 2025 Quals](https://mctf.mtuci.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-16 17:00:00 - 2025-11-17 17:00:00 UTC+8  
                **比赛权重** : 45.64  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2996.ics  
                
            ??? Quote "[PwnSec CTF 2025](https://pwnsec.ctf.ae/)"  
                [![](https://ctftime.org/media/events/pwnsec.png){ width="200" align=left }](https://pwnsec.ctf.ae/)  
                **比赛名称** : [PwnSec CTF 2025](https://pwnsec.ctf.ae/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-15 23:00:00 - 2025-11-16 23:00:00 UTC+8  
                **比赛权重** : 23.92  
                **赛事主办** : PwnSec (https://ctftime.org/team/28797)  
                **添加日历** : https://ctftime.org/event/2906.ics  
                
            ??? Quote "[Crate-CTF 2025](https://foi.se/cratectf)"  
                [![](https://ctftime.org/media/events/CTF_2025.png){ width="200" align=left }](https://foi.se/cratectf)  
                **比赛名称** : [Crate-CTF 2025](https://foi.se/cratectf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-15 21:00:00 - 2025-11-16 05:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Crate-CTF (https://ctftime.org/team/352250)  
                **添加日历** : https://ctftime.org/event/2838.ics  
                
            ??? Quote "[Platypwn 2025](https://platypwnies.de/events/platypwn/)"  
                [![](https://ctftime.org/media/events/platypwnies-512_1.png){ width="200" align=left }](https://platypwnies.de/events/platypwn/)  
                **比赛名称** : [Platypwn 2025](https://platypwnies.de/events/platypwn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-15 17:00:00 - 2025-11-17 05:00:00 UTC+8  
                **比赛权重** : 33.29  
                **赛事主办** : Platypwnies (https://ctftime.org/team/112550)  
                **添加日历** : https://ctftime.org/event/2606.ics  
                
            ??? Quote "[TU Delft CTF 2025](https://ctf.ewi.tudelft.nl/?source=ctftime)"  
                [![](){ width="200" align=left }](https://ctf.ewi.tudelft.nl/?source=ctftime)  
                **比赛名称** : [TU Delft CTF 2025](https://ctf.ewi.tudelft.nl/?source=ctftime)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-15 16:00:00 - 2025-11-16 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : TU Delft CTF Team (https://ctftime.org/team/134822)  
                **添加日历** : https://ctftime.org/event/2953.ics  
                
            ??? Quote "[RCTF 2025](https://rctf2025.xctf.org.cn/)"  
                [![](https://ctftime.org/media/events/rois_1.jpg){ width="200" align=left }](https://rctf2025.xctf.org.cn/)  
                **比赛名称** : [RCTF 2025](https://rctf2025.xctf.org.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-15 10:00:00 - 2025-11-17 10:00:00 UTC+8  
                **比赛权重** : 41.75  
                **赛事主办** : ROIS (https://ctftime.org/team/6476)  
                **添加日历** : https://ctftime.org/event/2992.ics  
                
            ??? Quote "[Layer7 CTF 2025](https://ctf.layer7.kr/)"  
                [![](https://ctftime.org/media/events/white_ver.png){ width="200" align=left }](https://ctf.layer7.kr/)  
                **比赛名称** : [Layer7 CTF 2025](https://ctf.layer7.kr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-15 09:00:00 - 2025-11-16 09:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Layer7 CTF (https://ctftime.org/team/87286)  
                **添加日历** : https://ctftime.org/event/2990.ics  
                
            ??? Quote "[Guardians of the TI](http://ctf.gematik.de/)"  
                [![](https://ctftime.org/media/events/logo_guardians.png){ width="200" align=left }](http://ctf.gematik.de/)  
                **比赛名称** : [Guardians of the TI](http://ctf.gematik.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-14 17:00:00 - 2025-11-15 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : H34lthineer (https://ctftime.org/team/170109)  
                **添加日历** : https://ctftime.org/event/3006.ics  
                
            ??? Quote "[AmateursCTF 2025](https://ctf.amateurs.team/)"  
                [![](){ width="200" align=left }](https://ctf.amateurs.team/)  
                **比赛名称** : [AmateursCTF 2025](https://ctf.amateurs.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-14 08:00:00 - 2025-11-18 08:00:00 UTC+8  
                **比赛权重** : 35.56  
                **赛事主办** : les amateurs (https://ctftime.org/team/166729)  
                **添加日历** : https://ctftime.org/event/2844.ics  
                
            ??? Quote "[POC CTF Final 2025](https://powerofcommunity.net/2025/ctf.html)"  
                [![](https://ctftime.org/media/events/vDP90SY4soKs6q3cKITowqXIE7a0Jy_1.png){ width="200" align=left }](https://powerofcommunity.net/2025/ctf.html)  
                **比赛名称** : [POC CTF Final 2025](https://powerofcommunity.net/2025/ctf.html)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-14 07:00:00 - 2025-11-14 14:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : SAFCSP (https://ctftime.org/team/54707)  
                **添加日历** : https://ctftime.org/event/2956.ics  
                
            ??? Quote "[RootCipher](https://forms.thundercipher.tech/form/949b7b32-ff49-400e-9194-a91a5deeb910)"  
                [![](){ width="200" align=left }](https://forms.thundercipher.tech/form/949b7b32-ff49-400e-9194-a91a5deeb910)  
                **比赛名称** : [RootCipher](https://forms.thundercipher.tech/form/949b7b32-ff49-400e-9194-a91a5deeb910)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-09 21:00:00 - 2025-11-10 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ThunderCipher (https://ctftime.org/team/279782)  
                **添加日历** : https://ctftime.org/event/2991.ics  
                
            ??? Quote "[M*CTF 2025 Junior Quals](https://mctf.mtuci.ru/)"  
                [![](https://ctftime.org/media/events/logo_14.jpg){ width="200" align=left }](https://mctf.mtuci.ru/)  
                **比赛名称** : [M*CTF 2025 Junior Quals](https://mctf.mtuci.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-09 17:00:00 - 2025-11-10 05:00:00 UTC+8  
                **比赛权重** : 36.00  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2995.ics  
                
            ??? Quote "[Cryovault Finals](https://www.isfcr.pes.edu/)"  
                [![](https://ctftime.org/media/events/LOGO_1.png){ width="200" align=left }](https://www.isfcr.pes.edu/)  
                **比赛名称** : [Cryovault Finals](https://www.isfcr.pes.edu/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-09 16:00:00 - 2025-11-10 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ISFCR PESU (https://ctftime.org/team/166645)  
                **添加日历** : https://ctftime.org/event/2985.ics  
                
            ??? Quote "[saarCTF 2025](https://ctf.saarland/)"  
                [![](https://ctftime.org/media/events/saarctf_2025.png){ width="200" align=left }](https://ctf.saarland/)  
                **比赛名称** : [saarCTF 2025](https://ctf.saarland/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2025-11-08 21:00:00 - 2025-11-09 06:00:00 UTC+8  
                **比赛权重** : 97.22  
                **赛事主办** : saarsec (https://ctftime.org/team/15337)  
                **添加日历** : https://ctftime.org/event/2859.ics  
                
            ??? Quote "[Equinor CTF 2025](https://ctf.equinor.com/)"  
                [![](https://ctftime.org/media/events/ept_2.png){ width="200" align=left }](https://ctf.equinor.com/)  
                **比赛名称** : [Equinor CTF 2025](https://ctf.equinor.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-08 17:00:00 - 2025-11-09 03:00:00 UTC+8  
                **比赛权重** : 37.00  
                **赛事主办** : EPT (https://ctftime.org/team/119480)  
                **添加日历** : https://ctftime.org/event/2646.ics  
                
            ??? Quote "[BuckeyeCTF 2025](https://ctf.osucyber.club/)"  
                [![](https://ctftime.org/media/events/buckeyectf-25-logo_1.jpg){ width="200" align=left }](https://ctf.osucyber.club/)  
                **比赛名称** : [BuckeyeCTF 2025](https://ctf.osucyber.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-08 09:00:00 - 2025-11-10 09:00:00 UTC+8  
                **比赛权重** : 50.00  
                **赛事主办** : scriptohio (https://ctftime.org/team/144581)  
                **添加日历** : https://ctftime.org/event/2883.ics  
                
            ??? Quote "[Infobahn CTF 2025](https://2025.infobahnc.tf/)"  
                [![](https://ctftime.org/media/events/mW45GaxJ_400x400.jpg){ width="200" align=left }](https://2025.infobahnc.tf/)  
                **比赛名称** : [Infobahn CTF 2025](https://2025.infobahnc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-08 01:00:00 - 2025-11-10 01:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Infobahn (https://ctftime.org/team/364723)  
                **添加日历** : https://ctftime.org/event/2878.ics  
                
            ??? Quote "[CTF@AC - Finals](https://ctf.ac.upt.ro/)"  
                [![](https://ctftime.org/media/events/2338e2e4033e4bf196b4e6c5f4f9b20d.png){ width="200" align=left }](https://ctf.ac.upt.ro/)  
                **比赛名称** : [CTF@AC - Finals](https://ctf.ac.upt.ro/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-07 23:00:00 - 2025-11-09 17:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : UPT-CTF (https://ctftime.org/team/276942)  
                **添加日历** : https://ctftime.org/event/2921.ics  
                
            ??? Quote "[CSCTF 2025](https://2025.chronos-security.ro/)"  
                [![](https://ctftime.org/media/events/CSCTF25-logo-bg.png){ width="200" align=left }](https://2025.chronos-security.ro/)  
                **比赛名称** : [CSCTF 2025](https://2025.chronos-security.ro/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-07 20:00:00 - 2025-11-09 20:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Chronos Security (https://ctftime.org/team/395297)  
                **添加日历** : https://ctftime.org/event/2980.ics  
                
            ??? Quote "[CSAW CTF Final Round 2025](https://ctf.csaw.io/)"  
                [![](https://ctftime.org/media/events/csaw-stars_1.png){ width="200" align=left }](https://ctf.csaw.io/)  
                **比赛名称** : [CSAW CTF Final Round 2025](https://ctf.csaw.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-07 01:00:00 - 2025-11-08 13:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : NYUSEC (https://ctftime.org/team/439)  
                **添加日历** : https://ctftime.org/event/2982.ics  
                
            ??? Quote "[Ctrl+Space CTF Finals](https://ctrl-space.gg/)"  
                [![](https://ctftime.org/media/events/ctrlspace_1_1.png){ width="200" align=left }](https://ctrl-space.gg/)  
                **比赛名称** : [Ctrl+Space CTF Finals](https://ctrl-space.gg/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-04 17:00:00 - 2025-11-06 19:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ESA (https://ctftime.org/team/391420)  
                **添加日历** : https://ctftime.org/event/2989.ics  
                
            ??? Quote "[Russian CTF Cup 2025 Qualifier](https://ctfcup.ru/)"  
                [![](){ width="200" align=left }](https://ctfcup.ru/)  
                **比赛名称** : [Russian CTF Cup 2025 Qualifier](https://ctfcup.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-02 17:00:00 - 2025-11-03 17:00:00 UTC+8  
                **比赛权重** : 35.29  
                **赛事主办** : ctfcup (https://ctftime.org/team/203499)  
                **添加日历** : https://ctftime.org/event/2993.ics  
                
            ??? Quote "[N1CTF 2025](https://ctf2025.nu1l.com/)"  
                [![](https://ctftime.org/media/events/logo2_5_2.png){ width="200" align=left }](https://ctf2025.nu1l.com/)  
                **比赛名称** : [N1CTF 2025](https://ctf2025.nu1l.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-01 20:00:00 - 2025-11-02 20:00:00 UTC+8  
                **比赛权重** : 94.50  
                **赛事主办** : Nu1L (https://ctftime.org/team/19208)  
                **添加日历** : https://ctftime.org/event/2795.ics  
                
            ??? Quote "[Cryovault Quals](https://www.isfcr.pes.edu/)"  
                [![](){ width="200" align=left }](https://www.isfcr.pes.edu/)  
                **比赛名称** : [Cryovault Quals](https://www.isfcr.pes.edu/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-01 14:30:00 - 2025-11-02 14:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ISFCR PESU (https://ctftime.org/team/166645)  
                **添加日历** : https://ctftime.org/event/2984.ics  
                
            ??? Quote "[Hackloween 2025](https://lobby-ctf.secplayground.com/lobby/a3666ef9-617e-4db3-8bbe-413138e25e76)"  
                [![](https://ctftime.org/media/events/SPG_Hackloween_2025__FB_Profile.png){ width="200" align=left }](https://lobby-ctf.secplayground.com/lobby/a3666ef9-617e-4db3-8bbe-413138e25e76)  
                **比赛名称** : [Hackloween 2025](https://lobby-ctf.secplayground.com/lobby/a3666ef9-617e-4db3-8bbe-413138e25e76)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-01 10:00:00 - 2025-11-02 10:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SECPlayground (https://ctftime.org/team/375409)  
                **添加日历** : https://ctftime.org/event/2914.ics  
                
            ??? Quote "[Haunted Pumpkin CTF '25](https://osintswitzerland.ch/events/haunted-pumpkin-ctf)"  
                [![](https://ctftime.org/media/events/IMG_9346.jpeg){ width="200" align=left }](https://osintswitzerland.ch/events/haunted-pumpkin-ctf)  
                **比赛名称** : [Haunted Pumpkin CTF '25](https://osintswitzerland.ch/events/haunted-pumpkin-ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-11-01 01:00:00 - 2025-11-02 06:59:59 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : OSINT Switzerland (https://ctftime.org/team/391442)  
                **添加日历** : https://ctftime.org/event/2918.ics  
                
            ??? Quote "[V1t CTF 2025](https://ctf.v1t.site/)"  
                [![](https://ctftime.org/media/events/Ban_sao_cua_V1T.png){ width="200" align=left }](https://ctf.v1t.site/)  
                **比赛名称** : [V1t CTF 2025](https://ctf.v1t.site/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-31 21:00:00 - 2025-11-02 21:00:00 UTC+8  
                **比赛权重** : 22.14  
                **赛事主办** : V1t (https://ctftime.org/team/280950)  
                **添加日历** : https://ctftime.org/event/2920.ics  
                
            ??? Quote "[ZeroDay CTF 2025](https://register.zerologon.co.in/)"  
                [![](https://ctftime.org/media/events/IMG-20251021-WA0001.jpg){ width="200" align=left }](https://register.zerologon.co.in/)  
                **比赛名称** : [ZeroDay CTF 2025](https://register.zerologon.co.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-30 21:00:00 - 2025-10-31 21:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Z3r0_l0g0n (https://ctftime.org/team/227457)  
                **添加日历** : https://ctftime.org/event/2988.ics  
                
            ??? Quote "[PH03N1X V1P3R N0V4 CTF](http://pwnctf.ro/)"  
                [![](https://ctftime.org/media/events/CTF_logo_sex-2_1.png){ width="200" align=left }](http://pwnctf.ro/)  
                **比赛名称** : [PH03N1X V1P3R N0V4 CTF](http://pwnctf.ro/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-29 18:00:00 - 2025-11-01 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : PH03N1X V1P3R N0V4 CTF (https://ctftime.org/team/395369)  
                **添加日历** : https://ctftime.org/event/2934.ics  
                
            ??? Quote "[Iran Tech Olympics Hardware Security 2025](https://ctf.olympics.tech/)"  
                [![](https://ctftime.org/media/events/3bfa72e3e10491d8b3bd43a8153aad1e_2.jpg){ width="200" align=left }](https://ctf.olympics.tech/)  
                **比赛名称** : [Iran Tech Olympics Hardware Security 2025](https://ctf.olympics.tech/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-29 14:30:00 - 2025-10-30 02:30:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2930.ics  
                
            ??? Quote "[CipherHunt 2.0](https://cipherhunt.xyz/)"  
                [![](https://ctftime.org/media/events/old-sq_1.jpg){ width="200" align=left }](https://cipherhunt.xyz/)  
                **比赛名称** : [CipherHunt 2.0](https://cipherhunt.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-28 17:30:00 - 2025-10-29 22:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CypherLock (https://ctftime.org/team/356395)  
                **添加日历** : https://ctftime.org/event/3005.ics  
                
            ??? Quote "[Iran Tech Olympics Speed-Run CTF 2025](https://ctf.olympics.tech/)"  
                [![](https://ctftime.org/media/events/3bfa72e3e10491d8b3bd43a8153aad1e_1.jpg){ width="200" align=left }](https://ctf.olympics.tech/)  
                **比赛名称** : [Iran Tech Olympics Speed-Run CTF 2025](https://ctf.olympics.tech/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-28 14:30:00 - 2025-10-28 14:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2931.ics  
                
            ??? Quote "[Iran Tech Olympics Attack-Defense 2025](https://ctf.olympics.tech/)"  
                [![](https://ctftime.org/media/events/3bfa72e3e10491d8b3bd43a8153aad1e.jpg){ width="200" align=left }](https://ctf.olympics.tech/)  
                **比赛名称** : [Iran Tech Olympics Attack-Defense 2025](https://ctf.olympics.tech/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2025-10-27 14:30:00 - 2025-10-28 02:30:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2929.ics  
                
            ??? Quote "[AltayCTF 2025](https://university.altayctf.ru/2025)"  
                [![](https://ctftime.org/media/events/0_2.png){ width="200" align=left }](https://university.altayctf.ru/2025)  
                **比赛名称** : [AltayCTF 2025](https://university.altayctf.ru/2025)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2025-10-26 18:00:00 - 2025-10-27 03:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : SharLike (https://ctftime.org/team/16172)  
                **添加日历** : https://ctftime.org/event/2979.ics  
                
            ??? Quote "[SAS CTF 2025 Finals](https://ctf.thesascon.com/)"  
                [![](https://ctftime.org/media/events/SAS25_new_1.png){ width="200" align=left }](https://ctf.thesascon.com/)  
                **比赛名称** : [SAS CTF 2025 Finals](https://ctf.thesascon.com/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2025-10-26 11:00:00 - 2025-10-26 22:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Drovosec, SAS CREW (https://ctftime.org/team/210132, https://ctftime.org/team/283057)  
                **添加日历** : https://ctftime.org/event/2811.ics  
                
            ??? Quote "[DEADFACE CTF 2025](https://ctf.deadface.io/)"  
                [![](https://ctftime.org/media/events/logo_deadface_ctf_2025-2.png){ width="200" align=left }](https://ctf.deadface.io/)  
                **比赛名称** : [DEADFACE CTF 2025](https://ctf.deadface.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-25 22:00:00 - 2025-10-27 08:00:00 UTC+8  
                **比赛权重** : 35.39  
                **赛事主办** : Cyber Hacktics (https://ctftime.org/team/127017)  
                **添加日历** : https://ctftime.org/event/2912.ics  
                
            ??? Quote "[osu!gaming CTF 2025](https://osugaming.sekai.team/)"  
                [![](https://ctftime.org/media/events/3fb5fab1b0946459c9c33d71e6c5db35.png){ width="200" align=left }](https://osugaming.sekai.team/)  
                **比赛名称** : [osu!gaming CTF 2025](https://osugaming.sekai.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-25 10:00:00 - 2025-10-27 10:00:00 UTC+8  
                **比赛权重** : 21.87  
                **赛事主办** : osu!gaming (https://ctftime.org/team/186954)  
                **添加日历** : https://ctftime.org/event/2801.ics  
                
            ??? Quote "[2025 Qiangwang Challenge on Cyber Mimic Defense Qualification](https://nest.pmlabs.com.cn/#/internationalEliteChallenge)"  
                [![](https://ctftime.org/media/events/wechat_2025-09-26_160854_722_1.png){ width="200" align=left }](https://nest.pmlabs.com.cn/#/internationalEliteChallenge)  
                **比赛名称** : [2025 Qiangwang Challenge on Cyber Mimic Defense Qualification](https://nest.pmlabs.com.cn/#/internationalEliteChallenge)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-25 09:00:00 - 2025-10-26 09:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : LoveFromMimic (https://ctftime.org/team/364644)  
                **添加日历** : https://ctftime.org/event/2952.ics  
                
            ??? Quote "[RSTCON 2025 CTF](https://mctf.io/rstcon25)"  
                [![](https://ctftime.org/media/events/RSTCON-BLK.png){ width="200" align=left }](https://mctf.io/rstcon25)  
                **比赛名称** : [RSTCON 2025 CTF](https://mctf.io/rstcon25)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-25 03:00:00 - 2025-10-26 22:00:00 UTC+8  
                **比赛权重** : 24.00  
                **赛事主办** : RSTCON (https://ctftime.org/team/281202)  
                **添加日历** : https://ctftime.org/event/2865.ics  
                
            ??? Quote "[m0leCon CTF 2026 Teaser](https://ctf.m0lecon.it/)"  
                [![](https://ctftime.org/media/events/ctftime_6_1.png){ width="200" align=left }](https://ctf.m0lecon.it/)  
                **比赛名称** : [m0leCon CTF 2026 Teaser](https://ctf.m0lecon.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-25 01:00:00 - 2025-10-26 01:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : pwnthem0le (https://ctftime.org/team/60467)  
                **添加日历** : https://ctftime.org/event/2946.ics  
                
            ??? Quote "[Web Arena](https://csem.sturtles.in/events/3/)"  
                [![](https://ctftime.org/media/events/Gemini_Generated_Image_j48x6dj48x6dj48x.png){ width="200" align=left }](https://csem.sturtles.in/events/3/)  
                **比赛名称** : [Web Arena](https://csem.sturtles.in/events/3/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-10-18 20:30:15 - 2025-10-19 20:30:15 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Super_Hacker (https://ctftime.org/team/195477)  
                **添加日历** : https://ctftime.org/event/2939.ics  
                
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
