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
            ??? Quote "[The Cyber Jawara International 2024](https://international.cyberjawara.pro/)"  
                [![](https://ctftime.org/media/events/73b32f71c82304b9e3df7fe9dedada59-transformed.png){ width="200" align=left }](https://international.cyberjawara.pro/)  
                **比赛名称** : [The Cyber Jawara International 2024](https://international.cyberjawara.pro/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-27 10:00:00 - 2024-10-28 10:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SKSD (https://ctftime.org/team/211952)  
                **添加日历** : https://ctftime.org/event/2552.ics  
                
            ??? Quote "[TuxCTF V2](https://www.instagram.com/tuxpwners/)"  
                [![](https://ctftime.org/media/events/tuxpwners-logo.png){ width="200" align=left }](https://www.instagram.com/tuxpwners/)  
                **比赛名称** : [TuxCTF V2](https://www.instagram.com/tuxpwners/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-29 17:00:00 - 2024-10-29 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : TuxPwners (https://ctftime.org/team/274660)  
                **添加日历** : https://ctftime.org/event/2553.ics  
                
            ??? Quote "[BUET CTF 2024](http://ctf.buetcsefest2024.com/)"  
                [![](https://ctftime.org/media/events/BUET_CTF_2024.png){ width="200" align=left }](http://ctf.buetcsefest2024.com/)  
                **比赛名称** : [BUET CTF 2024](http://ctf.buetcsefest2024.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-31 11:00:00 - 2024-10-31 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BUETSec (https://ctftime.org/team/357430)  
                **添加日历** : https://ctftime.org/event/2525.ics  
                
            ??? Quote "[Hack The Vote 2024](https://hackthe.vote/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://hackthe.vote/)  
                **比赛名称** : [Hack The Vote 2024](https://hackthe.vote/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 07:00:00 - 2024-11-04 07:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : RPISEC (https://ctftime.org/team/572)  
                **添加日历** : https://ctftime.org/event/2498.ics  
                
            ??? Quote "[USC CTF Fall 2024](http://usc.pwn.day/)"  
                [![](https://ctftime.org/media/events/USC_CTF_Logo_Handdrawn.png){ width="200" align=left }](http://usc.pwn.day/)  
                **比赛名称** : [USC CTF Fall 2024](http://usc.pwn.day/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 11:00:00 - 2024-11-04 12:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : 7r0j4npwn135 (https://ctftime.org/team/214221)  
                **添加日历** : https://ctftime.org/event/2543.ics  
                
            ??? Quote "[M*CTF 2024 Junior Quals](https://mctf.mtuci.ru/)"  
                [![](https://ctftime.org/media/events/NbK6tTQdEPQ.jpg){ width="200" align=left }](https://mctf.mtuci.ru/)  
                **比赛名称** : [M*CTF 2024 Junior Quals](https://mctf.mtuci.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 15:00:00 - 2024-11-03 01:00:00 UTC+8  
                **比赛权重** : 24.23  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2535.ics  
                
            ??? Quote "[Equinor CTF 2024](https://ctf.equinor.com/)"  
                [![](https://ctftime.org/media/events/ept_1.png){ width="200" align=left }](https://ctf.equinor.com/)  
                **比赛名称** : [Equinor CTF 2024](https://ctf.equinor.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 17:00:00 - 2024-11-03 03:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : EPT (https://ctftime.org/team/119480)  
                **添加日历** : https://ctftime.org/event/2292.ics  
                
            ??? Quote "[Hackers N' Hops](https://hackersnhops.ctfd.io/)"  
                [![](https://ctftime.org/media/events/HACKERSNHOPS.png){ width="200" align=left }](https://hackersnhops.ctfd.io/)  
                **比赛名称** : [Hackers N' Hops](https://hackersnhops.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 18:00:00 - 2024-11-04 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hackers N' Hops (https://ctftime.org/team/119910)  
                **添加日历** : https://ctftime.org/event/2550.ics  
                
            ??? Quote "[Platypwn 2024](https://platypwn.ctf.platypwnies.de/)"  
                [![](https://ctftime.org/media/events/Platypwnie.png){ width="200" align=left }](https://platypwn.ctf.platypwnies.de/)  
                **比赛名称** : [Platypwn 2024](https://platypwn.ctf.platypwnies.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 22:00:00 - 2024-11-03 22:00:00 UTC+8  
                **比赛权重** : 24.75  
                **赛事主办** : Platypwnies (https://ctftime.org/team/112550)  
                **添加日历** : https://ctftime.org/event/2407.ics  
                
            ??? Quote "[Pacific Hackers Conference 2024](https://www.phack.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://www.phack.org/)  
                **比赛名称** : [Pacific Hackers Conference 2024](https://www.phack.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-03 01:00:00 - 2024-11-03 09:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Pacific Hackers Association (https://ctftime.org/team/304096)  
                **添加日历** : https://ctftime.org/event/2453.ics  
                
            ??? Quote "[AlpacaHack Round 6 (Pwn)](https://alpacahack.com/ctfs/round-6)"  
                [![](https://ctftime.org/media/events/ctftime_7.png){ width="200" align=left }](https://alpacahack.com/ctfs/round-6)  
                **比赛名称** : [AlpacaHack Round 6 (Pwn)](https://alpacahack.com/ctfs/round-6)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-03 11:00:00 - 2024-11-03 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : AlpacaHack (https://ctftime.org/team/312315)  
                **添加日历** : https://ctftime.org/event/2501.ics  
                
            ??? Quote "[RedShift.Eclipse 2 Quals]()"  
                [![](https://ctftime.org/media/events/IMG_5703.JPG){ width="200" align=left }]()  
                **比赛名称** : [RedShift.Eclipse 2 Quals]()  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-03 20:00:00 - 2024-11-04 20:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : o1d_bu7_go1d (https://ctftime.org/team/213673)  
                **添加日历** : https://ctftime.org/event/2541.ics  
                
            ??? Quote "[BlackAlps CTF 2024](https://www.blackalps.ch/ba-24/ctf.php)"  
                [![](https://ctftime.org/media/events/blackalps-v5-logo-black_2.png){ width="200" align=left }](https://www.blackalps.ch/ba-24/ctf.php)  
                **比赛名称** : [BlackAlps CTF 2024](https://www.blackalps.ch/ba-24/ctf.php)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-08 03:15:00 - 2024-11-08 07:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BlackAlps (https://ctftime.org/team/89021)  
                **添加日历** : https://ctftime.org/event/2504.ics  
                
            ??? Quote "[HKCERT CTF 2024](https://ctf.hkcert.org/)"  
                [![](https://ctftime.org/media/events/Screenshot_2024-08-13_100427.png){ width="200" align=left }](https://ctf.hkcert.org/)  
                **比赛名称** : [HKCERT CTF 2024](https://ctf.hkcert.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-08 18:00:00 - 2024-11-10 18:00:00 UTC+8  
                **比赛权重** : 61.22  
                **赛事主办** : HKCERT (https://ctftime.org/team/134746)  
                **添加日历** : https://ctftime.org/event/2455.ics  
                
            ??? Quote "[Metared Argentina CERTUNLP](https://ctf.cert.unlp.edu.ar/)"  
                [![](https://ctftime.org/media/events/unlp.png){ width="200" align=left }](https://ctf.cert.unlp.edu.ar/)  
                **比赛名称** : [Metared Argentina CERTUNLP](https://ctf.cert.unlp.edu.ar/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-08 19:00:00 - 2024-11-09 19:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : CERTUNLP (https://ctftime.org/team/89294)  
                **添加日历** : https://ctftime.org/event/2537.ics  
                
            ??? Quote "[BlueHens CTF 2024](https://bluehens.ctfd.io/)"  
                [![](https://ctftime.org/media/events/UDCTF-logo_2.png){ width="200" align=left }](https://bluehens.ctfd.io/)  
                **比赛名称** : [BlueHens CTF 2024](https://bluehens.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-09 01:00:00 - 2024-11-10 13:00:00 UTC+8  
                **比赛权重** : 34.05  
                **赛事主办** : Blue Hens (https://ctftime.org/team/64660)  
                **添加日历** : https://ctftime.org/event/2512.ics  
                
            ??? Quote "[4T$ CTF](https://ctf.4ts.fr/)"  
                [![](https://ctftime.org/media/events/53b0900ddae2f59936bcc4eafc1458cf.jpg){ width="200" align=left }](https://ctf.4ts.fr/)  
                **比赛名称** : [4T$ CTF](https://ctf.4ts.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-09 02:00:00 - 2024-11-11 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : 4T$ (https://ctftime.org/team/302295)  
                **添加日历** : https://ctftime.org/event/2545.ics  
                
            ??? Quote "[HITCON CTF 2024 Final](http://ctf.hitcon.org/)"  
                [![](https://ctftime.org/media/events/eb3c04d49c017eda197bab74939403eb.jpg){ width="200" align=left }](http://ctf.hitcon.org/)  
                **比赛名称** : [HITCON CTF 2024 Final](http://ctf.hitcon.org/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-11-09 08:00:00 - 2024-11-10 16:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HITCON (https://ctftime.org/team/8299)  
                **添加日历** : https://ctftime.org/event/2523.ics  
                
            ??? Quote "[M*CTF 2024 Quals](https://mctf.mtuci.ru/)"  
                [![](https://ctftime.org/media/events/6sKaJXoc4I4.jpg){ width="200" align=left }](https://mctf.mtuci.ru/)  
                **比赛名称** : [M*CTF 2024 Quals](https://mctf.mtuci.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-09 17:00:00 - 2024-11-10 17:00:00 UTC+8  
                **比赛权重** : 33.59  
                **赛事主办** : BinaryBears (https://ctftime.org/team/36281)  
                **添加日历** : https://ctftime.org/event/2534.ics  
                
            ??? Quote "[Bambi CTF #11](https://bambi11.enoflag.de/)"  
                [![](https://ctftime.org/media/events/reh_1.png){ width="200" align=left }](https://bambi11.enoflag.de/)  
                **比赛名称** : [Bambi CTF #11](https://bambi11.enoflag.de/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-11-09 19:00:00 - 2024-11-10 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ENOFLAG (https://ctftime.org/team/1438)  
                **添加日历** : https://ctftime.org/event/2551.ics  
                
            ??? Quote "[N1CTF 2024](https://ctf2024.nu1l.com/)"  
                [![](https://ctftime.org/media/events/logo2_5_1.png){ width="200" align=left }](https://ctf2024.nu1l.com/)  
                **比赛名称** : [N1CTF 2024](https://ctf2024.nu1l.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-09 20:00:00 - 2024-11-10 20:00:00 UTC+8  
                **比赛权重** : 89.85  
                **赛事主办** : Nu1L (https://ctftime.org/team/19208)  
                **添加日历** : https://ctftime.org/event/2459.ics  
                
            ??? Quote "[EKOPARTY CTF 2024](https://ctf.ekoparty.org/)"  
                [![](https://ctftime.org/media/events/LOGO_eko_2024.png){ width="200" align=left }](https://ctf.ekoparty.org/)  
                **比赛名称** : [EKOPARTY CTF 2024](https://ctf.ekoparty.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-13 21:00:00 - 2024-11-16 03:00:00 UTC+8  
                **比赛权重** : 16.00  
                **赛事主办** : NULL Life (https://ctftime.org/team/321)  
                **添加日历** : https://ctftime.org/event/2507.ics  
                
            ??? Quote "[BlockCTF 2024 (Formerly SquareCTF)](https://squarectf.com/)"  
                [![](https://ctftime.org/media/events/0ed304c3c4dcb6a3e887778f3928e26e.png){ width="200" align=left }](https://squarectf.com/)  
                **比赛名称** : [BlockCTF 2024 (Formerly SquareCTF)](https://squarectf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-14 06:00:00 - 2024-11-15 06:00:00 UTC+8  
                **比赛权重** : 52.43  
                **赛事主办** : Square (https://ctftime.org/team/46747)  
                **添加日历** : https://ctftime.org/event/2517.ics  
                
            ??? Quote "[Die Abenteuer von KIM & TIM Kapt. II - To TI-Mfinity and Beyond](http://ctf.gematik.de/)"  
                [![](https://ctftime.org/media/events/Bild_1.png){ width="200" align=left }](http://ctf.gematik.de/)  
                **比赛名称** : [Die Abenteuer von KIM & TIM Kapt. II - To TI-Mfinity and Beyond](http://ctf.gematik.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-15 17:00:00 - 2024-11-16 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : H34lthineer (https://ctftime.org/team/170109)  
                **添加日历** : https://ctftime.org/event/2481.ics  
                
            ??? Quote "[1337UP LIVE CTF](https://ctf.intigriti.io/)"  
                [![](https://ctftime.org/media/events/intigriti_icon_cmyk_navy.png){ width="200" align=left }](https://ctf.intigriti.io/)  
                **比赛名称** : [1337UP LIVE CTF](https://ctf.intigriti.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-15 19:59:59 - 2024-11-17 07:59:59 UTC+8  
                **比赛权重** : 24.23  
                **赛事主办** : CryptoCat (https://ctftime.org/team/124896)  
                **添加日历** : https://ctftime.org/event/2446.ics  
                
            ??? Quote "[PwnSec CTF 2024](https://ctf.pwnsec.xyz/)"  
                [![](https://ctftime.org/media/events/Logo_12.png){ width="200" align=left }](https://ctf.pwnsec.xyz/)  
                **比赛名称** : [PwnSec CTF 2024](https://ctf.pwnsec.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-15 23:00:00 - 2024-11-16 23:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : PwnSec (https://ctftime.org/team/28797)  
                **添加日历** : https://ctftime.org/event/2454.ics  
                
            ??? Quote "[BRICS+ CTF Finals 2024](https://brics-ctf.com/)"  
                [![](https://ctftime.org/media/events/brics-logo-2024-square.png){ width="200" align=left }](https://brics-ctf.com/)  
                **比赛名称** : [BRICS+ CTF Finals 2024](https://brics-ctf.com/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-11-16 18:00:00 - 2024-11-17 02:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ITMO FSIT (https://ctftime.org/team/264636)  
                **添加日历** : https://ctftime.org/event/2521.ics  
                
            ??? Quote "[Crate-CTF 2024](https://foi.se/cratectf)"  
                [![](https://ctftime.org/media/events/crate-ctf-2024.png){ width="200" align=left }](https://foi.se/cratectf)  
                **比赛名称** : [Crate-CTF 2024](https://foi.se/cratectf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-16 21:00:00 - 2024-11-17 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Crate-CTF (https://ctftime.org/team/352250)  
                **添加日历** : https://ctftime.org/event/2489.ics  
                
            ??? Quote "[GlacierCTF 2024](https://glacierctf.com/)"  
                [![](https://ctftime.org/media/events/3ae6516246966c8d08c81d3bd5451cfa_1.png){ width="200" align=left }](https://glacierctf.com/)  
                **比赛名称** : [GlacierCTF 2024](https://glacierctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-23 02:00:00 - 2024-11-24 02:00:00 UTC+8  
                **比赛权重** : 35.69  
                **赛事主办** : LosFuzzys (https://ctftime.org/team/8323)  
                **添加日历** : https://ctftime.org/event/2402.ics  
                
            ??? Quote "[Hackvens 2024](https://hackvens.fr/)"  
                [![](https://ctftime.org/media/events/Logo_Hackvens.png){ width="200" align=left }](https://hackvens.fr/)  
                **比赛名称** : [Hackvens 2024](https://hackvens.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-23 04:00:00 - 2024-11-23 14:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hackvens (https://ctftime.org/team/194092)  
                **添加日历** : https://ctftime.org/event/2401.ics  
                
            ??? Quote "[SECCON CTF 13 Quals](https://ctf.seccon.jp/)"  
                [![](https://ctftime.org/media/events/seccon_s_7.png){ width="200" align=left }](https://ctf.seccon.jp/)  
                **比赛名称** : [SECCON CTF 13 Quals](https://ctf.seccon.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-23 13:00:00 - 2024-11-24 13:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : SECCON CTF (https://ctftime.org/team/11918)  
                **添加日历** : https://ctftime.org/event/2478.ics  
                
            ??? Quote "[WP CTF 2024](https://wpctf.it/)"  
                [![](https://ctftime.org/media/events/WP_CTF_logo.png){ width="200" align=left }](https://wpctf.it/)  
                **比赛名称** : [WP CTF 2024](https://wpctf.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-23 16:00:00 - 2024-11-24 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : WP CTF (https://ctftime.org/team/303099)  
                **添加日历** : https://ctftime.org/event/2395.ics  
                
            ??? Quote "[CyberSci Regional Qualifiers 2024-25](https://cybersecuritychallenge.ca/)"  
                [![](https://ctftime.org/media/events/9ad26ba791d2c5418b515bd4699ea7e2.png){ width="200" align=left }](https://cybersecuritychallenge.ca/)  
                **比赛名称** : [CyberSci Regional Qualifiers 2024-25](https://cybersecuritychallenge.ca/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-24 00:00:00 - 2024-11-24 07:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CyberSciOrganizers (https://ctftime.org/team/157536)  
                **添加日历** : https://ctftime.org/event/2511.ics  
                
            ??? Quote "[CTFZone 2024 Final](http://ctf.bi.zone/)"  
                [![](https://ctftime.org/media/events/aa86f826480a008ed91d88a917a0c33b.png){ width="200" align=left }](http://ctf.bi.zone/)  
                **比赛名称** : [CTFZone 2024 Final](http://ctf.bi.zone/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-11-24 17:00:00 - 2024-11-25 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BIZone (https://ctftime.org/team/32190)  
                **添加日历** : https://ctftime.org/event/2506.ics  
                
            ??? Quote "[BlackHat MEA CTF Final 2024](https://blackhatmea.com/capture-the-flag)"  
                [![](https://ctftime.org/media/events/e0c283c95f7b0db516dae505d31ca20b_3.jpg){ width="200" align=left }](https://blackhatmea.com/capture-the-flag)  
                **比赛名称** : [BlackHat MEA CTF Final 2024](https://blackhatmea.com/capture-the-flag)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-26 16:00:00 - 2024-11-28 11:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SAFCSP (https://ctftime.org/team/54707)  
                **添加日历** : https://ctftime.org/event/2431.ics  
                
            ??? Quote "[AlpacaHack Round 7 (Web)](https://alpacahack.com/ctfs/round-7)"  
                [![](https://ctftime.org/media/events/ctftime_8.png){ width="200" align=left }](https://alpacahack.com/ctfs/round-7)  
                **比赛名称** : [AlpacaHack Round 7 (Web)](https://alpacahack.com/ctfs/round-7)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-30 11:00:00 - 2024-11-30 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : AlpacaHack (https://ctftime.org/team/312315)  
                **添加日历** : https://ctftime.org/event/2544.ics  
                
            ??? Quote "[HackTM CTF 2024](https://ctf.hacktm.ro/)"  
                [![](https://ctftime.org/media/events/e2b12b3390413f1cf2cdeb7b12e076c6.jpg){ width="200" align=left }](https://ctf.hacktm.ro/)  
                **比赛名称** : [HackTM CTF 2024](https://ctf.hacktm.ro/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-30 20:00:00 - 2024-12-01 20:00:00 UTC+8  
                **比赛权重** : 24.67  
                **赛事主办** : WreckTheLine (https://ctftime.org/team/57908)  
                **添加日历** : https://ctftime.org/event/2452.ics  
                
            ??? Quote "[saarCTF 2024](https://ctf.saarland/)"  
                [![](https://ctftime.org/media/events/e21b4ef017572441617115eaa6bd9823.jpg){ width="200" align=left }](https://ctf.saarland/)  
                **比赛名称** : [saarCTF 2024](https://ctf.saarland/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-11-30 21:00:00 - 2024-12-01 06:00:00 UTC+8  
                **比赛权重** : 98.50  
                **赛事主办** : saarsec (https://ctftime.org/team/15337)  
                **添加日历** : https://ctftime.org/event/2490.ics  
                
            ??? Quote "[snakeCTF 2024 Finals](https://2024.snakectf.org/)"  
                [![](https://ctftime.org/media/events/LogoCroppable_2.png){ width="200" align=left }](https://2024.snakectf.org/)  
                **比赛名称** : [snakeCTF 2024 Finals](https://2024.snakectf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-05 16:00:00 - 2024-12-08 16:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : MadrHacks (https://ctftime.org/team/114509)  
                **添加日历** : https://ctftime.org/event/2419.ics  
                
            ??? Quote "[ISITDTU CTF 2024 Finals](https://ctf.isitdtu.com/)"  
                [![](https://ctftime.org/media/events/index_3.gif){ width="200" align=left }](https://ctf.isitdtu.com/)  
                **比赛名称** : [ISITDTU CTF 2024 Finals](https://ctf.isitdtu.com/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-12-07 10:00:00 - 2024-12-08 19:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ISITDTU (https://ctftime.org/team/8241)  
                **添加日历** : https://ctftime.org/event/2510.ics  
                
            ??? Quote "[RedShift.Eclipse 2 Finals]()"  
                [![](https://ctftime.org/media/events/5202034882946130981.jpg){ width="200" align=left }]()  
                **比赛名称** : [RedShift.Eclipse 2 Finals]()  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-12-07 18:00:00 - 2024-12-08 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : o1d_bu7_go1d (https://ctftime.org/team/213673)  
                **添加日历** : https://ctftime.org/event/2538.ics  
                
            ??? Quote "[DFIR Labs CTF by The DFIR Report](https://thedfirreport.com/services/dfir-labs/ctf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://thedfirreport.com/services/dfir-labs/ctf/)  
                **比赛名称** : [DFIR Labs CTF by The DFIR Report](https://thedfirreport.com/services/dfir-labs/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-08 00:00:00 - 2024-12-08 04:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : The DFIR Report (https://ctftime.org/team/309500)  
                **添加日历** : https://ctftime.org/event/2488.ics  
                
            ??? Quote "[LakeCTF Quals 24-25](https://lakectf.epfl.ch/)"  
                [![](https://ctftime.org/media/events/7fb065c04dbec7e33dfbb1f4456196c7.png){ width="200" align=left }](https://lakectf.epfl.ch/)  
                **比赛名称** : [LakeCTF Quals 24-25](https://lakectf.epfl.ch/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-08 02:00:00 - 2024-12-09 02:00:00 UTC+8  
                **比赛权重** : 36.00  
                **赛事主办** : polygl0ts (https://ctftime.org/team/53791)  
                **添加日历** : https://ctftime.org/event/2502.ics  
                
            ??? Quote "[WannaGame Championship 2024](https://cnsc.uit.edu.vn/ctf/)"  
                [![](https://ctftime.org/media/events/WGC2024_2.png){ width="200" align=left }](https://cnsc.uit.edu.vn/ctf/)  
                **比赛名称** : [WannaGame Championship 2024](https://cnsc.uit.edu.vn/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-13 09:00:00 - 2024-12-14 09:00:00 UTC+8  
                **比赛权重** : 19.80  
                **赛事主办** : Wanna.W1n (https://ctftime.org/team/138431)  
                **添加日历** : https://ctftime.org/event/2515.ics  
                
            ??? Quote "[niteCTF 2024](https://www.nitectf2024.live/)"  
                [![](https://ctftime.org/media/events/WhatsApp_Image_2021-08-06_at_11.28.13_3.jpeg){ width="200" align=left }](https://www.nitectf2024.live/)  
                **比赛名称** : [niteCTF 2024](https://www.nitectf2024.live/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-13 20:00:00 - 2024-12-15 20:00:00 UTC+8  
                **比赛权重** : 29.33  
                **赛事主办** : Cryptonite (https://ctftime.org/team/62713)  
                **添加日历** : https://ctftime.org/event/2461.ics  
                
            ??? Quote "[HTB University CTF 2024: Binary Badlands](https://ctf.hackthebox.com/event/details/university-ctf-2024-binary-badlands-1822)"  
                [![](https://ctftime.org/media/events/htbctf-logo_1.png){ width="200" align=left }](https://ctf.hackthebox.com/event/details/university-ctf-2024-binary-badlands-1822)  
                **比赛名称** : [HTB University CTF 2024: Binary Badlands](https://ctf.hackthebox.com/event/details/university-ctf-2024-binary-badlands-1822)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-13 21:00:00 - 2024-12-16 05:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Hack The Box (https://ctftime.org/team/136056)  
                **添加日历** : https://ctftime.org/event/2539.ics  
                
            ??? Quote "[TSG CTF 2024](https://ctf.tsg.ne.jp/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.tsg.ne.jp/)  
                **比赛名称** : [TSG CTF 2024](https://ctf.tsg.ne.jp/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-14 15:00:00 - 2024-12-15 15:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : TSG (https://ctftime.org/team/16088)  
                **添加日历** : https://ctftime.org/event/2424.ics  
                
            ??? Quote "[Russian CTF Cup 2024 Final](https://ctfcup.ru/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctfcup.ru/)  
                **比赛名称** : [Russian CTF Cup 2024 Final](https://ctfcup.ru/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-12-14 18:00:00 - 2024-12-16 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ctfcup (https://ctftime.org/team/203499)  
                **添加日历** : https://ctftime.org/event/2406.ics  
                
            ??? Quote "[0CTF 2024](https://ctf.0ops.sjtu.cn/)"  
                [![](https://ctftime.org/media/events/0ctf.png){ width="200" align=left }](https://ctf.0ops.sjtu.cn/)  
                **比赛名称** : [0CTF 2024](https://ctf.0ops.sjtu.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-21 10:00:00 - 2024-12-23 10:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : 0ops (https://ctftime.org/team/4419)  
                **添加日历** : https://ctftime.org/event/2448.ics  
                
            ??? Quote "[BackdoorCTF 2024](https://backdoor.infoseciitr.in/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://backdoor.infoseciitr.in/)  
                **比赛名称** : [BackdoorCTF 2024](https://backdoor.infoseciitr.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-22 20:00:00 - 2024-12-23 20:00:00 UTC+8  
                **比赛权重** : 49.48  
                **赛事主办** : InfoSecIITR (https://ctftime.org/team/16691)  
                **添加日历** : https://ctftime.org/event/2540.ics  
                
            ??? Quote "[hxp 38C3 CTF](https://2024.ctf.link/)"  
                [![](https://ctftime.org/media/events/hxp-38c3.png){ width="200" align=left }](https://2024.ctf.link/)  
                **比赛名称** : [hxp 38C3 CTF](https://2024.ctf.link/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-28 04:00:00 - 2024-12-30 04:00:00 UTC+8  
                **比赛权重** : 98.14  
                **赛事主办** : hxp (https://ctftime.org/team/585)  
                **添加日历** : https://ctftime.org/event/2437.ics  
                
            ??? Quote "[ASIS CTF Finals 2024](https://asisctf.com/)"  
                [![](https://ctftime.org/media/events/asis_logo.png){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Finals 2024](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-28 22:00:00 - 2024-12-29 22:00:00 UTC+8  
                **比赛权重** : 92.75  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2403.ics  
                
            ??? Quote "[IrisCTF 2025](https://2025.irisc.tf/)"  
                [![](https://ctftime.org/media/events/IrisSec.png){ width="200" align=left }](https://2025.irisc.tf/)  
                **比赛名称** : [IrisCTF 2025](https://2025.irisc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-04 08:00:00 - 2025-01-06 08:00:00 UTC+8  
                **比赛权重** : 34.30  
                **赛事主办** : IrisSec (https://ctftime.org/team/127034)  
                **添加日历** : https://ctftime.org/event/2503.ics  
                
            ??? Quote "[Cyber League 2025 - Major](https://ctfd.cyberleague.co/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctfd.cyberleague.co/)  
                **比赛名称** : [Cyber League 2025 - Major](https://ctfd.cyberleague.co/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-11 10:00:00 - 2025-01-12 10:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : DIV0-N0H4TS (https://ctftime.org/team/354275)  
                **添加日历** : https://ctftime.org/event/2530.ics  
                
            ??? Quote "[2025 Embedded Capture the Flag](https://ectf.mitre.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ectf.mitre.org/)  
                **比赛名称** : [2025 Embedded Capture the Flag](https://ectf.mitre.org/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2025-01-16 01:00:00 - 2025-04-17 00:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : ectfmitre (https://ctftime.org/team/87292)  
                **添加日历** : https://ctftime.org/event/2542.ics  
                
            ??? Quote "[x3ctf 2025](https://x3c.tf/)"  
                [![](https://ctftime.org/media/events/temp_pfp.png){ width="200" align=left }](https://x3c.tf/)  
                **比赛名称** : [x3ctf 2025](https://x3c.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-01-25 02:00:00 - 2025-01-27 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : x3CTF (https://ctftime.org/team/309820)  
                **添加日历** : https://ctftime.org/event/2467.ics  
                
            ??? Quote "[SpartanCTF 2025](https://spartan.ctfd.io/)"  
                [![](https://ctftime.org/media/events/spctf.png){ width="200" align=left }](https://spartan.ctfd.io/)  
                **比赛名称** : [SpartanCTF 2025](https://spartan.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-02-01 05:00:00 - 2025-02-04 05:00:00 UTC+8  
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
                
            ??? Quote "[N0PSctf](https://www.nops.re/)"  
                [![](https://ctftime.org/media/events/logo-news.png){ width="200" align=left }](https://www.nops.re/)  
                **比赛名称** : [N0PSctf](https://www.nops.re/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2025-05-31 16:00:00 - 2025-06-02 04:00:00 UTC+8  
                **比赛权重** : 24.32  
                **赛事主办** : NOPS (https://ctftime.org/team/4056)  
                **添加日历** : https://ctftime.org/event/2486.ics  
                
    === "*正在进行*"
        === "国内赛事"
    
        === "国外赛事"
            ??? Quote "[Sydbox CTF: read /etc/CTF](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)"  
                [![](https://ctftime.org){ width="200" align=left }](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)  
                **比赛名称** : [Sydbox CTF: read /etc/CTF](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-16 22:26:32 - 2024-11-16 23:26:32 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Exherbo GNU/Linux (https://ctftime.org/team/275214)  
                **添加日历** : https://ctftime.org/event/2178.ics  
                
            ??? Quote "[Pointer Overflow CTF - 2024](http://pointeroverflowctf.com/)"  
                [![](https://ctftime.org/media/events/poctflogo1transp.png){ width="200" align=left }](http://pointeroverflowctf.com/)  
                **比赛名称** : [Pointer Overflow CTF - 2024](http://pointeroverflowctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-15 20:00:00 - 2025-01-19 20:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : UWSP Pointers (https://ctftime.org/team/231536)  
                **添加日历** : https://ctftime.org/event/2121.ics  
                
            ??? Quote "[HeroCTF v6](https://heroctf.fr/)"  
                [![](https://ctftime.org/media/events/HeroCTF_icon_500_1_1.png){ width="200" align=left }](https://heroctf.fr/)  
                **比赛名称** : [HeroCTF v6](https://heroctf.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 05:00:00 - 2024-10-28 07:00:00 UTC+8  
                **比赛权重** : 43.94  
                **赛事主办** : HeroCTF (https://ctftime.org/team/145166)  
                **添加日历** : https://ctftime.org/event/2496.ics  
                
            ??? Quote "[SpookyCTF 2024](https://spookyctf.ctfd.io/)"  
                [![](https://ctftime.org/media/events/Spooky.png){ width="200" align=left }](https://spookyctf.ctfd.io/)  
                **比赛名称** : [SpookyCTF 2024](https://spookyctf.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 07:00:00 - 2024-10-28 07:30:00 UTC+8  
                **比赛权重** : 22.40  
                **赛事主办** : NICC (https://ctftime.org/team/214936)  
                **添加日历** : https://ctftime.org/event/2516.ics  
                
            ??? Quote "[ISITDTU CTF 2024 Quals](https://ctf.isitdtu.com/)"  
                [![](https://ctftime.org/media/events/index_2.gif){ width="200" align=left }](https://ctf.isitdtu.com/)  
                **比赛名称** : [ISITDTU CTF 2024 Quals](https://ctf.isitdtu.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 10:00:00 - 2024-10-27 18:00:00 UTC+8  
                **比赛权重** : 51.00  
                **赛事主办** : ISITDTU (https://ctftime.org/team/8241)  
                **添加日历** : https://ctftime.org/event/2456.ics  
                
            ??? Quote "[UrchinSec Aware CTF](https://ctf.urchinsec.com/)"  
                [![](https://ctftime.org/media/events/URCHINSEC_free-file_1.png){ width="200" align=left }](https://ctf.urchinsec.com/)  
                **比赛名称** : [UrchinSec Aware CTF](https://ctf.urchinsec.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 15:00:00 - 2024-10-28 03:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : UrchinSec (https://ctftime.org/team/175663)  
                **添加日历** : https://ctftime.org/event/2527.ics  
                
            ??? Quote "[Singapore AI CTF](https://www.tech.gov.sg/media/events/singapore-ai-ctf-2024/)"  
                [![](https://ctftime.org/media/events/SG_AI_CTF_FB-Post-4.png){ width="200" align=left }](https://www.tech.gov.sg/media/events/singapore-ai-ctf-2024/)  
                **比赛名称** : [Singapore AI CTF](https://www.tech.gov.sg/media/events/singapore-ai-ctf-2024/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 16:00:00 - 2024-10-28 16:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Singapore AI CTF (https://ctftime.org/team/357504)  
                **添加日历** : https://ctftime.org/event/2546.ics  
                
            ??? Quote "[Russian CTF Cup 2024 Qualifier](https://ctfcup.ru/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctfcup.ru/)  
                **比赛名称** : [Russian CTF Cup 2024 Qualifier](https://ctfcup.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 17:00:00 - 2024-10-27 17:00:00 UTC+8  
                **比赛权重** : 24.21  
                **赛事主办** : ctfcup (https://ctftime.org/team/203499)  
                **添加日历** : https://ctftime.org/event/2405.ics  
                
    === "*已经结束*"
        === "国内赛事"
            ??? Quote "[BRICS+ CTF Quals 2024](https://brics-ctf.com/)"  
                **比赛名称** : [BRICS+ CTF Quals 2024](https://brics-ctf.com/)  
                **比赛类型** : 团队赛  
                **报名时间** : 2024年10月05日 18:00 - 2024年10月06日 18:00  
                **比赛时间** : 2024年10月05日 18:00 - 2024年10月06日 18:00  
                **其他说明** : 初赛将以在线解题赛的形式进行.计划邀请来自金砖国家的15支队伍（每个国家不超过3支队伍）以及总排名前10的最佳队伍参与线上的决赛.同时详情信息请加入discord -> https://discord.gg/3AwqYTvaMw 决赛总奖池7w人民币左右  
                
            ??? Quote "[BaseCTF 2024 高校联合新生赛](https://www.basectf.fun/)"  
                **比赛名称** : [BaseCTF 2024 高校联合新生赛](https://www.basectf.fun/)  
                **比赛类型** : 1-2 人  
                **报名时间** : 2024年08月5日 00:00 - 2024年09月30日 21:00  
                **比赛时间** : 2024年08月15日 09:00 - 2024年09月30日 21:00  
                **其他说明** : QQ 群：530184592 面向新生的比赛，题目分 Week 1 - 7，从入门到挑战循序渐进  
                
            ??? Quote "[“华为杯”第三届中国研究生网络安全创新大赛](https://cpipc.acge.org.cn//pw/detail/2c9080188fc20569018fe6375eeb2eb2)"  
                **比赛名称** : [“华为杯”第三届中国研究生网络安全创新大赛](https://cpipc.acge.org.cn//pw/detail/2c9080188fc20569018fe6375eeb2eb2)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年05月06日 00:00 - 2024年09月23日 23:59  
                **比赛时间** : 2024年09月25日 00:00 - 2024年09月25日 23:59  
                **其他说明** : QQ群: 794148708|仅限研究生参加  
                
            ??? Quote "[第五届“闽盾杯”网络空间安全大塞黑盾全国大学生赛道（决赛）](http://heidunbei.si.net.cn/hdc/cover)"  
                **比赛名称** : [第五届“闽盾杯”网络空间安全大塞黑盾全国大学生赛道（决赛）](http://heidunbei.si.net.cn/hdc/cover)  
                **比赛类型** : 团队赛|3人  
                **报名时间** : 2024年06月26日 10:35 - 2024年06月26日 10:35  
                **比赛时间** : 2024年09月13日 00:00 - 2024年09月13日 23:59  
                **其他说明** : QQ群：676547374 或 566180593  
                
            ??? Quote "[WMCTF 2024](https://wmctf.wm-team.cn/)"  
                **比赛名称** : [WMCTF 2024](https://wmctf.wm-team.cn/)  
                **比赛类型** : 团队赛 | 人数不限  
                **报名时间** : 2024年08月14日 09:00 - 2024年09月09日 09:00  
                **比赛时间** : 2024年09月07日 09:00 - 2024年09月09日 09:00  
                **其他说明** : 有多个联系方式，具体请在赛事网站查看  
                
            ??? Quote "[2024年辽宁大学研究生网络安全创新实践大赛](https://mp.weixin.qq.com/s?search_click_id=1419197875279398874-1721064257482-5560857333&__biz=MzkwODY4NjEwMA==&mid=2247483898&idx=2&sn=9e98fa0801ff04680dc13785de62ec59&chksm=c1d81e30983ce3afed49948819b79e7332489d251f75003da001e323b575dc6267a3f9b3c7c3&scene=7&subscene=10000&sessionid=1721062624&clicktime=1721064257&enterid=1721064257&ascene=65&fasttmpl_type=0&fasttmpl_fullversion=7295595-zh_CN-zip&fasttmpl_flag=0&realreporttime=1721064257512&devicetype=android-34&version=28002e34&nettype=WIFI&abtest_cookie=AAACAA==&lang=zh_CN&countrycode=CN&exportkey=n_ChQIAhIQcvD8xBlhKOyhNiXR+sSwhxLiAQIE97dBBAEAAAAAALJPGgdGHkcAAAAOpnltbLcz9gKNyK89dVj05OQmnZhmX5QxbgZxJq2kXOv2MdwjaAf3iVTLVGCcQUSG7VlEEpibGRWcgGV1BZpKtLcneOndlVFC2eMkTtAv8YTngrwgPTc44eKAtyGHcw9azAA/Lyju97FKSOW2D6eW7ZlNCG9gFS8WG6AcsPuxVr7PhVh4jtPz7vGomi56weNGB+8NjPr5ChEwlxJP+UN5C5JA5rUMV2rKtdZBeiASZdqEjpQcPvQmFzF6OVw0NHDUJ/bDftCImrDsZKo=&pass_ticket=kVxbyE61cIHqlon9l8MZfpuGMpxcldPEOp9u/xMr3MOyS4E0APheem2kMNVrm4dm&wx_header=3)"  
                **比赛名称** : [2024年辽宁大学研究生网络安全创新实践大赛](https://mp.weixin.qq.com/s?search_click_id=1419197875279398874-1721064257482-5560857333&__biz=MzkwODY4NjEwMA==&mid=2247483898&idx=2&sn=9e98fa0801ff04680dc13785de62ec59&chksm=c1d81e30983ce3afed49948819b79e7332489d251f75003da001e323b575dc6267a3f9b3c7c3&scene=7&subscene=10000&sessionid=1721062624&clicktime=1721064257&enterid=1721064257&ascene=65&fasttmpl_type=0&fasttmpl_fullversion=7295595-zh_CN-zip&fasttmpl_flag=0&realreporttime=1721064257512&devicetype=android-34&version=28002e34&nettype=WIFI&abtest_cookie=AAACAA==&lang=zh_CN&countrycode=CN&exportkey=n_ChQIAhIQcvD8xBlhKOyhNiXR+sSwhxLiAQIE97dBBAEAAAAAALJPGgdGHkcAAAAOpnltbLcz9gKNyK89dVj05OQmnZhmX5QxbgZxJq2kXOv2MdwjaAf3iVTLVGCcQUSG7VlEEpibGRWcgGV1BZpKtLcneOndlVFC2eMkTtAv8YTngrwgPTc44eKAtyGHcw9azAA/Lyju97FKSOW2D6eW7ZlNCG9gFS8WG6AcsPuxVr7PhVh4jtPz7vGomi56weNGB+8NjPr5ChEwlxJP+UN5C5JA5rUMV2rKtdZBeiASZdqEjpQcPvQmFzF6OVw0NHDUJ/bDftCImrDsZKo=&pass_ticket=kVxbyE61cIHqlon9l8MZfpuGMpxcldPEOp9u/xMr3MOyS4E0APheem2kMNVrm4dm&wx_header=3)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年07月15日 18:41 - 2024年08月31日 23:59  
                **比赛时间** : 2024年08月31日 23:59 - 2024年08月31日 23:59  
                **其他说明** : 仅限辽宁大学研究生 | 参赛队伍需同时参加“华为杯”第三届中国研究生网络安全创新大赛  
                
            ??? Quote "[第三届江苏大学研究生网络安全创新大赛](https://yjsy.ujs.edu.cn/info/1305/28415.htm)"  
                **比赛名称** : [第三届江苏大学研究生网络安全创新大赛](https://yjsy.ujs.edu.cn/info/1305/28415.htm)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年06月30日 00:00 - 2024年08月30日 23:59  
                **比赛时间** : 2024年06月30日 00:00 - 2024年08月31日 23:59  
                **其他说明** : 仅限研究生  
                
            ??? Quote "[2024年“羊城杯”粤港澳大湾区网络安全大赛](https://2024ycb.dasctf.com/compete/compete?matchCode=87659256dbc7485&competeId=268)"  
                **比赛名称** : [2024年“羊城杯”粤港澳大湾区网络安全大赛](https://2024ycb.dasctf.com/compete/compete?matchCode=87659256dbc7485&competeId=268)  
                **比赛类型** : 个人赛|团队赛 1-4人  
                **报名时间** : 2024年08月01日 18:45 - 2024年08月20日 23:59  
                **比赛时间** : 2024年08月27日 09:00 - 2024年08月28日 09:00  
                **其他说明** : QQ群1：1148320638 QQ群2：696494060 | 研究生、本科、高职、相关企业、党政机关及事业单位和港澳特邀  
                
            ??? Quote "[MoeCTF 2024](https://ctf.xidian.edu.cn)"  
                **比赛名称** : [MoeCTF 2024](https://ctf.xidian.edu.cn)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年08月07日 14:23 - 2024年10月14日 21:00  
                **比赛时间** : 2024年08月10日 09:00 - 2024年10月14日 21:00  
                **其他说明** : QQ 群：187536315  
                
            ??? Quote "[GEEKGAME 2024](https://geekgame.pku.edu.cn)"  
                **比赛名称** : [GEEKGAME 2024](https://geekgame.pku.edu.cn)  
                **比赛类型** : 线上Jeopardy解题赛  
                **报名时间** : 2024年10月06日 12:00 - 2024年10月11日 11:59  
                **比赛时间** : 2024年10月12日 12:00 - 2024年10月19日 12:00  
                **其他说明** : 第四届北京大学信息安全综合能力竞赛GEEKGAME 2024由北京大学学生 Linux 俱乐部主办，比赛时间为2024年10月12日至10月19日，采用个人线上赛的模式，选手可加入QQ群133986617获取更多信息。  
                
            ??? Quote "[2024'源鲁杯'高校网络安全技能大赛](https://ctf.yuanloo.com/)"  
                **比赛名称** : [2024'源鲁杯'高校网络安全技能大赛](https://ctf.yuanloo.com/)  
                **比赛类型** : 个人线上赛  
                **报名时间** : 2024年09月01日 09:00 - 2024年10月23日 15:00  
                **比赛时间** : 2024年10月10日 09:00 - 2024年10月23日 15:00  
                **其他说明** : QQ群:437096728 更多信息请前往赛事官网 https://ctf.yuanloo.com/  
                
        === "国外赛事"
            ??? Quote "[EngimaXplore2.0 2024](https://unstop.com/hackathons/engimaxplore-20-ctf-tantrafiesta24-iiit-nagpur-1153719)"  
                [![](https://ctftime.org){ width="200" align=left }](https://unstop.com/hackathons/engimaxplore-20-ctf-tantrafiesta24-iiit-nagpur-1153719)  
                **比赛名称** : [EngimaXplore2.0 2024](https://unstop.com/hackathons/engimaxplore-20-ctf-tantrafiesta24-iiit-nagpur-1153719)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-24 20:29:59 - 2024-10-25 20:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Crispr_iiitn (https://ctftime.org/team/270138)  
                **添加日历** : https://ctftime.org/event/2524.ics  
                
            ??? Quote "[Z3R0 D4Y CTF](https://ctf.zerologon.co.in/)"  
                [![](https://ctftime.org/media/events/Logo.c1dfc2e2d63945110c8d.png){ width="200" align=left }](https://ctf.zerologon.co.in/)  
                **比赛名称** : [Z3R0 D4Y CTF](https://ctf.zerologon.co.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-24 17:00:00 - 2024-10-25 05:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Z3r0_l0g0n (https://ctftime.org/team/227457)  
                **添加日历** : https://ctftime.org/event/2529.ics  
                
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
                **比赛权重** : 0  
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
                **比赛权重** : 0  
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
                **比赛权重** : 0  
                **赛事主办** : Google CTF (https://ctftime.org/team/23929)  
                **添加日历** : https://ctftime.org/event/2379.ics  
                
            ??? Quote "[Africa battleCTF 2024 prequal](https://qualifier.bugpwn.com/)"  
                [![](https://ctftime.org/media/events/banner_1.png){ width="200" align=left }](https://qualifier.bugpwn.com/)  
                **比赛名称** : [Africa battleCTF 2024 prequal](https://qualifier.bugpwn.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-18 08:00:00 - 2024-10-20 08:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : BUG PWN (https://ctftime.org/team/182428)  
                **添加日历** : https://ctftime.org/event/2531.ics  
                
            ??? Quote "[CTF MetaRed Mexico Anuies-TIC 2024](https://ctfd.anuies.mx/)"  
                [![](https://ctftime.org/media/events/ctf_2024_1.jpg){ width="200" align=left }](https://ctfd.anuies.mx/)  
                **比赛名称** : [CTF MetaRed Mexico Anuies-TIC 2024](https://ctfd.anuies.mx/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-15 23:00:00 - 2024-10-16 11:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : UV-CSIRT (https://ctftime.org/team/166955)  
                **添加日历** : https://ctftime.org/event/2482.ics  
                
            ??? Quote "[Breach Bytes 2.0](https://unstop.com/hackathons/breach-bytes-20-shri-vile-parle-kelavani-mandals-dwarkadas-j-sanghvi-college-of-engineering-djsce-mumbai-1171442)"  
                [![](https://ctftime.org/media/events/BREACH_BYTES_2.0_Logo_1.png){ width="200" align=left }](https://unstop.com/hackathons/breach-bytes-20-shri-vile-parle-kelavani-mandals-dwarkadas-j-sanghvi-college-of-engineering-djsce-mumbai-1171442)  
                **比赛名称** : [Breach Bytes 2.0](https://unstop.com/hackathons/breach-bytes-20-shri-vile-parle-kelavani-mandals-dwarkadas-j-sanghvi-college-of-engineering-djsce-mumbai-1171442)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-15 10:30:00 - 2024-10-15 21:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : The dangers of my heart (https://ctftime.org/team/300150)  
                **添加日历** : https://ctftime.org/event/2526.ics  
                
            ??? Quote "[GITEX GLOBAL CTF](https://gitex.ctf.ae/)"  
                [![](https://ctftime.org/media/events/New_Project_17.png){ width="200" align=left }](https://gitex.ctf.ae/)  
                **比赛名称** : [GITEX GLOBAL CTF](https://gitex.ctf.ae/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-14 15:00:00 - 2024-10-15 20:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CTF.ae (https://ctftime.org/team/151875)  
                **添加日历** : https://ctftime.org/event/2522.ics  
                
            ??? Quote "[SLAY CTF 2024](https://zl-slay.vercel.app/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://zl-slay.vercel.app/)  
                **比赛名称** : [SLAY CTF 2024](https://zl-slay.vercel.app/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-14 11:30:00 - 2024-10-14 23:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : W07v3R1n (https://ctftime.org/team/239616)  
                **添加日历** : https://ctftime.org/event/2547.ics  
                
            ??? Quote "[Securinets CTF Quals 2024](https://ctf.securinets.tn/)"  
                [![](https://ctftime.org/media/events/d82bcfc5f1d83b7cc51c7dd0dbc8f5c6_1.png){ width="200" align=left }](https://ctf.securinets.tn/)  
                **比赛名称** : [Securinets CTF Quals 2024](https://ctf.securinets.tn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-13 03:00:00 - 2024-10-14 03:00:00 UTC+8  
                **比赛权重** : 95.59  
                **赛事主办** : Securinets (https://ctftime.org/team/5084)  
                **添加日历** : https://ctftime.org/event/2520.ics  
                
            ??? Quote "[NoHat CTF 2024](https://play.pwnx.io/#/event/40b08dba-3140-4cae-89da-6db9c0d8e5a0)"  
                [![](https://ctftime.org){ width="200" align=left }](https://play.pwnx.io/#/event/40b08dba-3140-4cae-89da-6db9c0d8e5a0)  
                **比赛名称** : [NoHat CTF 2024](https://play.pwnx.io/#/event/40b08dba-3140-4cae-89da-6db9c0d8e5a0)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-13 00:00:00 - 2024-10-14 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : PWNX (https://ctftime.org/team/179989)  
                **添加日历** : https://ctftime.org/event/2518.ics  
                
            ??? Quote "[Blue Water CTF 2024](https://bw.ctf.ing/)"  
                [![](https://ctftime.org/media/events/4872c3c168bd1cdeb5dc564bb3a0416f.png){ width="200" align=left }](https://bw.ctf.ing/)  
                **比赛名称** : [Blue Water CTF 2024](https://bw.ctf.ing/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-12 22:00:00 - 2024-10-14 10:00:00 UTC+8  
                **比赛权重** : 82.00  
                **赛事主办** : 💦​ (https://ctftime.org/team/205897)  
                **添加日历** : https://ctftime.org/event/2479.ics  
                
            ??? Quote "[Haus der Flaggen/Flag Heist](https://laokoon-security.com/ctf2024)"  
                [![](https://ctftime.org/media/events/HausDerFlaggen_Plakat_1080_x_1080_px.png){ width="200" align=left }](https://laokoon-security.com/ctf2024)  
                **比赛名称** : [Haus der Flaggen/Flag Heist](https://laokoon-security.com/ctf2024)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-12 16:00:00 - 2024-10-13 02:00:00 UTC+8  
                **比赛权重** : 21.00  
                **赛事主办** : Laokoon SecurITy (https://ctftime.org/team/201667)  
                **添加日历** : https://ctftime.org/event/2436.ics  
                
            ??? Quote "[AlpacaHack Round 5 (Crypto)](https://alpacahack.com/ctfs/round-5)"  
                [![](https://ctftime.org/media/events/ctftime_6.png){ width="200" align=left }](https://alpacahack.com/ctfs/round-5)  
                **比赛名称** : [AlpacaHack Round 5 (Crypto)](https://alpacahack.com/ctfs/round-5)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-12 11:00:00 - 2024-10-12 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : AlpacaHack (https://ctftime.org/team/312315)  
                **添加日历** : https://ctftime.org/event/2500.ics  
                
            ??? Quote "[TCP1P CTF 2024: Exploring Nusantara's Digital Realm](https://ctf.tcp1p.team/)"  
                [![](https://ctftime.org/media/events/Asset_10.jpg){ width="200" align=left }](https://ctf.tcp1p.team/)  
                **比赛名称** : [TCP1P CTF 2024: Exploring Nusantara's Digital Realm](https://ctf.tcp1p.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-11 20:00:00 - 2024-10-13 20:00:00 UTC+8  
                **比赛权重** : 24.85  
                **赛事主办** : TCP1P (https://ctftime.org/team/187248)  
                **添加日历** : https://ctftime.org/event/2256.ics  
                
            ??? Quote "[Kernel Kombat](https://zl-slay.vercel.app/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://zl-slay.vercel.app/)  
                **比赛名称** : [Kernel Kombat](https://zl-slay.vercel.app/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-06 14:46:54 - 2024-10-06 14:46:54 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : S14y3r (https://ctftime.org/team/282208)  
                **添加日历** : https://ctftime.org/event/2528.ics  
                
            ??? Quote "[TU Delft CTF 2024](https://ctf.ewi.tudelft.nl/)"  
                [![](https://ctftime.org/media/events/fddd624d58320dba5f40c75a47d72974.jpg){ width="200" align=left }](https://ctf.ewi.tudelft.nl/)  
                **比赛名称** : [TU Delft CTF 2024](https://ctf.ewi.tudelft.nl/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-05 18:00:00 - 2024-10-06 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : TU Delft CTF Team (https://ctftime.org/team/134822)  
                **添加日历** : https://ctftime.org/event/2487.ics  
                
            ??? Quote "[BRICS+ CTF Quals 2024](https://brics-ctf.com/)"  
                [![](https://ctftime.org/media/events/logo-2024.png){ width="200" align=left }](https://brics-ctf.com/)  
                **比赛名称** : [BRICS+ CTF Quals 2024](https://brics-ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-05 18:00:00 - 2024-10-06 18:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ITMO FSIT (https://ctftime.org/team/264636)  
                **添加日历** : https://ctftime.org/event/2389.ics  
                
            ??? Quote "[IRON CTF 2024](https://ctf.1nf1n1ty.team/)"  
                [![](https://ctftime.org/media/events/ironCTF.png){ width="200" align=left }](https://ctf.1nf1n1ty.team/)  
                **比赛名称** : [IRON CTF 2024](https://ctf.1nf1n1ty.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-05 13:30:00 - 2024-10-06 13:30:00 UTC+8  
                **比赛权重** : 24.65  
                **赛事主办** : 1nf1n1ty (https://ctftime.org/team/151859)  
                **添加日历** : https://ctftime.org/event/2497.ics  
                
            ??? Quote "[RuCTF Finals 2024](http://ructf.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://ructf.org/)  
                **比赛名称** : [RuCTF Finals 2024](http://ructf.org/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-10-05 13:00:00 - 2024-10-07 03:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : HackerDom (https://ctftime.org/team/552)  
                **添加日历** : https://ctftime.org/event/2386.ics  
                
            ??? Quote "[AlpacaHack Round 4 (Rev)](https://alpacahack.com/ctfs/round-4)"  
                [![](https://ctftime.org/media/events/ctftime_5.png){ width="200" align=left }](https://alpacahack.com/ctfs/round-4)  
                **比赛名称** : [AlpacaHack Round 4 (Rev)](https://alpacahack.com/ctfs/round-4)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-05 11:00:00 - 2024-10-05 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : AlpacaHack (https://ctftime.org/team/312315)  
                **添加日历** : https://ctftime.org/event/2499.ics  
                
            ??? Quote "[AltayCTF 2024](https://university.altayctf.ru/2024)"  
                [![](https://ctftime.org/media/events/0_1.png){ width="200" align=left }](https://university.altayctf.ru/2024)  
                **比赛名称** : [AltayCTF 2024](https://university.altayctf.ru/2024)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-10-05 11:00:00 - 2024-10-06 20:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : SharLike (https://ctftime.org/team/16172)  
                **添加日历** : https://ctftime.org/event/2376.ics  
                
            ??? Quote "[Hack Havoc 2.0](https://ctf.cybermaterial.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.cybermaterial.com/)  
                **比赛名称** : [Hack Havoc 2.0](https://ctf.cybermaterial.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-04 21:59:48 - 2024-10-25 21:59:48 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Hack Havoc (https://ctftime.org/team/316395)  
                **添加日历** : https://ctftime.org/event/2532.ics  
                
            ??? Quote "[FAUST CTF 2024](https://2024.faustctf.net/)"  
                [![](https://ctftime.org/media/events/faust2024_1.png){ width="200" align=left }](https://2024.faustctf.net/)  
                **比赛名称** : [FAUST CTF 2024](https://2024.faustctf.net/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-09-28 20:00:00 - 2024-09-29 05:00:00 UTC+8  
                **比赛权重** : 93.11  
                **赛事主办** : FAUST (https://ctftime.org/team/550)  
                **添加日历** : https://ctftime.org/event/2351.ics  
                
            ??? Quote "[justCTF 2024 finals](https://2024finals.justctf.team/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://2024finals.justctf.team/)  
                **比赛名称** : [justCTF 2024 finals](https://2024finals.justctf.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-28 18:00:00 - 2024-09-29 18:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : justCatTheFish (https://ctftime.org/team/33893)  
                **添加日历** : https://ctftime.org/event/2484.ics  
                
            ??? Quote "[Capture the Flag Competition in TON 2024](https://ctf.tonbit.xyz/)"  
                [![](https://ctftime.org/media/events/TonBit.png){ width="200" align=left }](https://ctf.tonbit.xyz/)  
                **比赛名称** : [Capture the Flag Competition in TON 2024](https://ctf.tonbit.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-28 09:00:00 - 2024-09-29 09:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BitsLab (https://ctftime.org/team/331124)  
                **添加日历** : https://ctftime.org/event/2509.ics  
                
            ??? Quote "[SCTF 2024](https://adworld.xctf.org.cn/contest/assess?hash=4124a446-65a9-11ef-a39a-000c297261bb)"  
                [![](https://ctftime.org/media/events/syclover_2.jpg){ width="200" align=left }](https://adworld.xctf.org.cn/contest/assess?hash=4124a446-65a9-11ef-a39a-000c297261bb)  
                **比赛名称** : [SCTF 2024](https://adworld.xctf.org.cn/contest/assess?hash=4124a446-65a9-11ef-a39a-000c297261bb)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-28 09:00:00 - 2024-09-30 09:00:00 UTC+8  
                **比赛权重** : 37.00  
                **赛事主办** : Syclover (https://ctftime.org/team/455)  
                **添加日历** : https://ctftime.org/event/2483.ics  
                
            ??? Quote "[BuckeyeCTF 2024](https://pwnoh.io/)"  
                [![](https://ctftime.org/media/events/logo-black-square.jpeg){ width="200" align=left }](https://pwnoh.io/)  
                **比赛名称** : [BuckeyeCTF 2024](https://pwnoh.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-28 04:00:00 - 2024-09-30 04:00:00 UTC+8  
                **比赛权重** : 50.91  
                **赛事主办** : scriptohio (https://ctftime.org/team/144581)  
                **添加日历** : https://ctftime.org/event/2449.ics  
                
            ??? Quote "[Season IV, US Cyber Games Flag Fest CTF](https://www.uscybergames.com/season-4-draft-experience#ctf)"  
                [![](https://ctftime.org/media/events/2022-10-USCG_S3_logos_cybergames_1_1.png){ width="200" align=left }](https://www.uscybergames.com/season-4-draft-experience#ctf)  
                **比赛名称** : [Season IV, US Cyber Games Flag Fest CTF](https://www.uscybergames.com/season-4-draft-experience#ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-28 02:00:00 - 2024-10-06 11:59:58 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : PlayCyber (https://ctftime.org/team/165788)  
                **添加日历** : https://ctftime.org/event/2472.ics  
                
            ??? Quote "[DefCamp Capture the Flag (D-CTF) 2024 Quals](https://dctf24-quals.cyber-edu.co/)"  
                [![](https://ctftime.org/media/events/w5NGLTFBTZWXGg8lLPAeyg-Photoroom.png){ width="200" align=left }](https://dctf24-quals.cyber-edu.co/)  
                **比赛名称** : [DefCamp Capture the Flag (D-CTF) 2024 Quals](https://dctf24-quals.cyber-edu.co/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-27 18:00:00 - 2024-09-29 17:00:00 UTC+8  
                **比赛权重** : 33.56  
                **赛事主办** : CCSIR.org (https://ctftime.org/team/9831)  
                **添加日历** : https://ctftime.org/event/2480.ics  
                
            ??? Quote "[Haruulzangi CTF 2024 Finals](https://dashboard.haruulzangi.mn/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://dashboard.haruulzangi.mn/)  
                **比赛名称** : [Haruulzangi CTF 2024 Finals](https://dashboard.haruulzangi.mn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-26 12:00:00 - 2024-09-26 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : haruulzangi-organizers (https://ctftime.org/team/266812)  
                **添加日历** : https://ctftime.org/event/2494.ics  
                
            ??? Quote "[H7CTF International](https://ctf.h7tex.com/)"  
                [![](https://ctftime.org/media/events/1_3.png){ width="200" align=left }](https://ctf.h7tex.com/)  
                **比赛名称** : [H7CTF International](https://ctf.h7tex.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-26 11:30:00 - 2024-09-27 19:30:00 UTC+8  
                **比赛权重** : 23.41  
                **赛事主办** : H7Tex (https://ctftime.org/team/281844)  
                **添加日历** : https://ctftime.org/event/2491.ics  
                
            ??? Quote "[Haruulzangi CTF 2024 Round 2](https://dashboard.haruulzangi.mn/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://dashboard.haruulzangi.mn/)  
                **比赛名称** : [Haruulzangi CTF 2024 Round 2](https://dashboard.haruulzangi.mn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-22 12:00:00 - 2024-09-22 16:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : haruulzangi-organizers (https://ctftime.org/team/266812)  
                **添加日历** : https://ctftime.org/event/2493.ics  
                
            ??? Quote "[ASIS CTF Quals 2024](https://asisctf.com/)"  
                [![](https://ctftime.org/media/events/asisctf.jpg){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Quals 2024](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 22:00:00 - 2024-09-22 22:00:00 UTC+8  
                **比赛权重** : 66.25  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2211.ics  
                
            ??? Quote "[21ans LinuxMeetup au Québec](https://www.linuxver.site/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://www.linuxver.site/)  
                **比赛名称** : [21ans LinuxMeetup au Québec](https://www.linuxver.site/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 21:30:00 - 2024-09-22 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SummerJedi (https://ctftime.org/team/126955)  
                **添加日历** : https://ctftime.org/event/2422.ics  
                
            ??? Quote "[openECSC 2024 - Final Round](https://open.ecsc2024.it/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://open.ecsc2024.it/)  
                **比赛名称** : [openECSC 2024 - Final Round](https://open.ecsc2024.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 18:00:00 - 2024-09-22 18:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : ECSC2024 (https://ctftime.org/team/283828)  
                **添加日历** : https://ctftime.org/event/2356.ics  
                
            ??? Quote "[GMO Cybersecurity Contest - IERAE CTF 2024](https://gmo-cybersecurity.com/event/ieraectf24/)"  
                [![](https://ctftime.org/media/events/ierae-ctf-logo_2_1.png){ width="200" align=left }](https://gmo-cybersecurity.com/event/ieraectf24/)  
                **比赛名称** : [GMO Cybersecurity Contest - IERAE CTF 2024](https://gmo-cybersecurity.com/event/ieraectf24/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 14:00:00 - 2024-09-22 14:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ierae (https://ctftime.org/team/224122)  
                **添加日历** : https://ctftime.org/event/2441.ics  
                
            ??? Quote "[Cyber Jawara International](https://cyberjawara.id/2024)"  
                [![](https://ctftime.org/media/events/067297e97f084c5492331b121d1b0507.png){ width="200" align=left }](https://cyberjawara.id/2024)  
                **比赛名称** : [Cyber Jawara International](https://cyberjawara.id/2024)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 09:59:00 - 2024-09-22 09:59:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : idnsa (https://ctftime.org/team/239714)  
                **添加日历** : https://ctftime.org/event/2411.ics  
                
            ??? Quote "[BlazCTF 2024](https://ctf.blaz.ai/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.blaz.ai/)  
                **比赛名称** : [BlazCTF 2024](https://ctf.blaz.ai/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 09:00:00 - 2024-09-23 09:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : FuzzLand (https://ctftime.org/team/270659)  
                **添加日历** : https://ctftime.org/event/2492.ics  
                
            ??? Quote "[PatriotCTF 2024](http://pctf.competitivecyber.club/)"  
                [![](https://ctftime.org/media/events/masoncc_2.png){ width="200" align=left }](http://pctf.competitivecyber.club/)  
                **比赛名称** : [PatriotCTF 2024](http://pctf.competitivecyber.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 06:00:00 - 2024-09-23 06:00:00 UTC+8  
                **比赛权重** : 31.83  
                **赛事主办** : Competitive Cyber at Mason (https://ctftime.org/team/176906)  
                **添加日历** : https://ctftime.org/event/2426.ics  
                
            ??? Quote "[VolgaCTF 2024 Final](https://volgactf.ru/en/volgactf-2024/final/)"  
                [![](https://ctftime.org/media/events/logo-social-yellow_15.png){ width="200" align=left }](https://volgactf.ru/en/volgactf-2024/final/)  
                **比赛名称** : [VolgaCTF 2024 Final](https://volgactf.ru/en/volgactf-2024/final/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-09-19 14:00:00 - 2024-09-19 23:00:00 UTC+8  
                **比赛权重** : 73.80  
                **赛事主办** : VolgaCTF.org (https://ctftime.org/team/27094)  
                **添加日历** : https://ctftime.org/event/2432.ics  
                
            ??? Quote "[AlpacaHack Round 3 (Crypto)](https://alpacahack.com/ctfs/round-3)"  
                [![](https://ctftime.org/media/events/dark_512_1.png){ width="200" align=left }](https://alpacahack.com/ctfs/round-3)  
                **比赛名称** : [AlpacaHack Round 3 (Crypto)](https://alpacahack.com/ctfs/round-3)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-15 11:00:00 - 2024-09-15 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : AlpacaHack (https://ctftime.org/team/312315)  
                **添加日历** : https://ctftime.org/event/2466.ics  
                
            ??? Quote "[KubanCTF Qualifier 2024](https://kubanctf.ru/signUp)"  
                [![](https://ctftime.org/media/events/0f5e680946259ad6bbdf28ccb33b74e9.png){ width="200" align=left }](https://kubanctf.ru/signUp)  
                **比赛名称** : [KubanCTF Qualifier 2024](https://kubanctf.ru/signUp)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-14 15:00:00 - 2024-09-14 23:00:00 UTC+8  
                **比赛权重** : 16.37  
                **赛事主办** : Codeby Games (https://ctftime.org/team/299486)  
                **添加日历** : https://ctftime.org/event/2464.ics  
                
            ??? Quote "[jailCTF 2024](https://ctf.pyjail.club/)"  
                [![](https://ctftime.org/media/events/jailctf150.png){ width="200" align=left }](https://ctf.pyjail.club/)  
                **比赛名称** : [jailCTF 2024](https://ctf.pyjail.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-14 04:00:00 - 2024-09-17 04:00:00 UTC+8  
                **比赛权重** : 24.88  
                **赛事主办** : jailctf (https://ctftime.org/team/311088)  
                **添加日历** : https://ctftime.org/event/2450.ics  
                
            ??? Quote "[RSTCON 2024 CTF (Online/Hybrid)](https://metactf.com/join/rstcon24)"  
                [![](https://ctftime.org/media/events/rstcon.png){ width="200" align=left }](https://metactf.com/join/rstcon24)  
                **比赛名称** : [RSTCON 2024 CTF (Online/Hybrid)](https://metactf.com/join/rstcon24)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-14 03:45:00 - 2024-09-16 00:45:00 UTC+8  
                **比赛权重** : 24.00  
                **赛事主办** : RSTCON (https://ctftime.org/team/281202)  
                **添加日历** : https://ctftime.org/event/2427.ics  
                
            ??? Quote "[m0leCon CTF 2025 Teaser](https://ctf.m0lecon.it/)"  
                [![](https://ctftime.org/media/events/ctftime_2025.png){ width="200" align=left }](https://ctf.m0lecon.it/)  
                **比赛名称** : [m0leCon CTF 2025 Teaser](https://ctf.m0lecon.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-14 01:00:00 - 2024-09-15 01:00:00 UTC+8  
                **比赛权重** : 80.00  
                **赛事主办** : pwnthem0le (https://ctftime.org/team/60467)  
                **添加日历** : https://ctftime.org/event/2440.ics  
                
            ??? Quote "[MOCA CTF - Finals](https://moca.camp/ctf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://moca.camp/ctf/)  
                **比赛名称** : [MOCA CTF - Finals](https://moca.camp/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-14 00:00:00 - 2024-09-15 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Metro Olografix (https://ctftime.org/team/268425)  
                **添加日历** : https://ctftime.org/event/2294.ics  
                
            ??? Quote "[Haruulzangi CTF 2024 Qualifier](https://dashboard.haruulzangi.mn/)"  
                [![](https://ctftime.org/media/events/zangi_2.png){ width="200" align=left }](https://dashboard.haruulzangi.mn/)  
                **比赛名称** : [Haruulzangi CTF 2024 Qualifier](https://dashboard.haruulzangi.mn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-13 12:00:00 - 2024-09-13 12:00:00 UTC+8  
                **比赛权重** : 23.33  
                **赛事主办** : haruulzangi-organizers (https://ctftime.org/team/266812)  
                **添加日历** : https://ctftime.org/event/2476.ics  
                
            ??? Quote "[COMPFEST CTF 2024](https://ctf-mirror.compfest.id/)"  
                [![](https://ctftime.org/media/events/Group_49363.png){ width="200" align=left }](https://ctf-mirror.compfest.id/)  
                **比赛名称** : [COMPFEST CTF 2024](https://ctf-mirror.compfest.id/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-08 08:00:00 - 2024-09-09 08:00:00 UTC+8  
                **比赛权重** : 43.00  
                **赛事主办** : CSUI (https://ctftime.org/team/70551)  
                **添加日历** : https://ctftime.org/event/2463.ics  
                
            ??? Quote "[DFIR Labs CTF by The DFIR Report](https://thedfirreport.com/services/dfir-labs/ctf/)"  
                [![](https://ctftime.org/media/events/image_31.png){ width="200" align=left }](https://thedfirreport.com/services/dfir-labs/ctf/)  
                **比赛名称** : [DFIR Labs CTF by The DFIR Report](https://thedfirreport.com/services/dfir-labs/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-08 00:00:00 - 2024-09-08 04:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : The DFIR Report (https://ctftime.org/team/309500)  
                **添加日历** : https://ctftime.org/event/2451.ics  
                
            ??? Quote "[Urmia CTF 2024](https://uctf.ir/)"  
                [![](https://ctftime.org/media/events/NewLogo_1.jpg){ width="200" align=left }](https://uctf.ir/)  
                **比赛名称** : [Urmia CTF 2024](https://uctf.ir/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-07 20:00:00 - 2024-09-09 20:00:00 UTC+8  
                **比赛权重** : 24.27  
                **赛事主办** : UCG (https://ctftime.org/team/255103)  
                **添加日历** : https://ctftime.org/event/2460.ics  
                
            ??? Quote "[snakeCTF 2024 Quals](https://2024.snakectf.org/)"  
                [![](https://ctftime.org/media/events/LogoCroppable_1.png){ width="200" align=left }](https://2024.snakectf.org/)  
                **比赛名称** : [snakeCTF 2024 Quals](https://2024.snakectf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-07 16:00:00 - 2024-09-08 16:00:00 UTC+8  
                **比赛权重** : 24.79  
                **赛事主办** : MadrHacks (https://ctftime.org/team/114509)  
                **添加日历** : https://ctftime.org/event/2418.ics  
                
            ??? Quote "[HackTheDrone CTF Qualifier](http://hackthedrone.org/eng/ctf.php)"  
                [![](https://ctftime.org/media/events/hackthedrone.png){ width="200" align=left }](http://hackthedrone.org/eng/ctf.php)  
                **比赛名称** : [HackTheDrone CTF Qualifier](http://hackthedrone.org/eng/ctf.php)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-07 12:00:00 - 2024-09-08 12:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HackTheDrone (https://ctftime.org/team/337463)  
                **添加日历** : https://ctftime.org/event/2474.ics  
                
            ??? Quote "[WMCTF2024](https://wmctf.wm-team.cn/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://wmctf.wm-team.cn/)  
                **比赛名称** : [WMCTF2024](https://wmctf.wm-team.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-07 09:00:00 - 2024-09-09 09:00:00 UTC+8  
                **比赛权重** : 53.88  
                **赛事主办** : W&M (https://ctftime.org/team/54666)  
                **添加日历** : https://ctftime.org/event/2457.ics  
                
            ??? Quote "[CSAW CTF Qualification Round 2024](https://ctf.csaw.io/)"  
                [![](https://ctftime.org/media/events/CSAW.png){ width="200" align=left }](https://ctf.csaw.io/)  
                **比赛名称** : [CSAW CTF Qualification Round 2024](https://ctf.csaw.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-07 00:00:00 - 2024-09-09 00:00:00 UTC+8  
                **比赛权重** : 21.80  
                **赛事主办** : NYUSEC (https://ctftime.org/team/439)  
                **添加日历** : https://ctftime.org/event/2398.ics  
                
            ??? Quote "[BlackHat MEA CTF Qualification 2024](https://blackhatmea.com/capture-the-flag)"  
                [![](https://ctftime.org/media/events/e0c283c95f7b0db516dae505d31ca20b_2.jpg){ width="200" align=left }](https://blackhatmea.com/capture-the-flag)  
                **比赛名称** : [BlackHat MEA CTF Qualification 2024](https://blackhatmea.com/capture-the-flag)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-01 18:00:00 - 2024-09-02 17:59:59 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : SAFCSP (https://ctftime.org/team/54707)  
                **添加日历** : https://ctftime.org/event/2430.ics  
                
            ??? Quote "[AlpacaHack Round 2 (Web)](https://alpacahack.com/ctfs/round-2)"  
                [![](https://ctftime.org/media/events/dark_512.png){ width="200" align=left }](https://alpacahack.com/ctfs/round-2)  
                **比赛名称** : [AlpacaHack Round 2 (Web)](https://alpacahack.com/ctfs/round-2)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-01 11:00:00 - 2024-09-01 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : AlpacaHack (https://ctftime.org/team/312315)  
                **添加日历** : https://ctftime.org/event/2465.ics  
                
            ??? Quote "[CISA ICS CTF 2024](https://ctf.cisaicsctf.com/)"  
                [![](https://ctftime.org/media/events/CTF_Drifveil_Logo-1.png){ width="200" align=left }](https://ctf.cisaicsctf.com/)  
                **比赛名称** : [CISA ICS CTF 2024](https://ctf.cisaicsctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-01 01:00:00 - 2024-09-05 00:00:00 UTC+8  
                **比赛权重** : 24.89  
                **赛事主办** : CISA ICSJWG (https://ctftime.org/team/182074)  
                **添加日历** : https://ctftime.org/event/2404.ics  
                
            ??? Quote "[CyberSpace CTF 2024](https://2024.csc.tf/)"  
                [![](https://ctftime.org/media/events/f6b991673b1944e7b199bc978b3f0a15.png){ width="200" align=left }](https://2024.csc.tf/)  
                **比赛名称** : [CyberSpace CTF 2024](https://2024.csc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-31 00:00:00 - 2024-09-02 00:00:00 UTC+8  
                **比赛权重** : 24.83  
                **赛事主办** : CyberSpace (https://ctftime.org/team/116280)  
                **添加日历** : https://ctftime.org/event/2428.ics  
                
            ??? Quote "[Flagyard HITBSecConf Single Player CTF](https://conference.hitb.org/hitbsecconf2024bkk/capture-the-flag/)"  
                [![](https://ctftime.org/media/events/4ea2d58d-116d-427d-ad8b-4625d48cbec9.jpg){ width="200" align=left }](https://conference.hitb.org/hitbsecconf2024bkk/capture-the-flag/)  
                **比赛名称** : [Flagyard HITBSecConf Single Player CTF](https://conference.hitb.org/hitbsecconf2024bkk/capture-the-flag/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-29 12:00:00 - 2024-08-30 19:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : SAFCSP (https://ctftime.org/team/54707)  
                **添加日历** : https://ctftime.org/event/2475.ics  
                
            ??? Quote "[Codegate CTF 2024 Finals](http://www.codegate.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://www.codegate.org/)  
                **比赛名称** : [Codegate CTF 2024 Finals](http://www.codegate.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-29 09:00:00 - 2024-08-30 09:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CODEGATE (https://ctftime.org/team/39352)  
                **添加日历** : https://ctftime.org/event/2347.ics  
                
            ??? Quote "[Automotive CTF Japan 2024](https://vicone.com/jp/automotive-ctf)"  
                [![](https://ctftime.org/media/events/7471ff863b474b2db4fdb2f0b8086302.png){ width="200" align=left }](https://vicone.com/jp/automotive-ctf)  
                **比赛名称** : [Automotive CTF Japan 2024](https://vicone.com/jp/automotive-ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-25 08:00:00 - 2024-09-10 07:59:59 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : VicOne Japan (https://ctftime.org/team/314349)  
                **添加日历** : https://ctftime.org/event/2473.ics  
                
            ??? Quote "[Cygenix CTF](https://cygenixctf.ycfteam.in/)"  
                [![](https://ctftime.org/media/events/cygenix.png){ width="200" align=left }](https://cygenixctf.ycfteam.in/)  
                **比赛名称** : [Cygenix CTF](https://cygenixctf.ycfteam.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-24 22:30:00 - 2024-08-25 22:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : YCF (https://ctftime.org/team/179685)  
                **添加日历** : https://ctftime.org/event/2468.ics  
                
            ??? Quote "[Block Harbor VicOne Automotive CTF - Season 2](https://ctf.blockharbor.io/)"  
                [![](https://ctftime.org/media/events/blockharbor.jpg){ width="200" align=left }](https://ctf.blockharbor.io/)  
                **比赛名称** : [Block Harbor VicOne Automotive CTF - Season 2](https://ctf.blockharbor.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-24 22:00:00 - 2024-09-09 10:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : bhctf (https://ctftime.org/team/251542)  
                **添加日历** : https://ctftime.org/event/2387.ics  
                
            ??? Quote "[DASCTF2024 August Back-to-School Season](https://buuoj.cn/match/matches/209)"  
                [![](https://ctftime.org/media/events/Dingtalk_20240814101134.jpg){ width="200" align=left }](https://buuoj.cn/match/matches/209)  
                **比赛名称** : [DASCTF2024 August Back-to-School Season](https://buuoj.cn/match/matches/209)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-24 18:00:00 - 2024-08-25 02:00:00 UTC+8  
                **比赛权重** : 20.00  
                **赛事主办** : DASCTF (https://ctftime.org/team/303691)  
                **添加日历** : https://ctftime.org/event/2458.ics  
                
            ??? Quote "[SekaiCTF 2024](https://ctf.sekai.team/)"  
                [![](https://ctftime.org/media/events/sekai2_SEKAI_CTF_Square_Black_BG.r_1_1.png){ width="200" align=left }](https://ctf.sekai.team/)  
                **比赛名称** : [SekaiCTF 2024](https://ctf.sekai.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-24 00:00:00 - 2024-08-26 00:00:00 UTC+8  
                **比赛权重** : 36.96  
                **赛事主办** : Project Sekai (https://ctftime.org/team/169557)  
                **添加日历** : https://ctftime.org/event/2243.ics  
                
            ??? Quote "[idekCTF 2024](https://ctf.idek.team/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.idek.team/)  
                **比赛名称** : [idekCTF 2024](https://ctf.idek.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-17 08:00:00 - 2024-08-19 08:00:00 UTC+8  
                **比赛权重** : 52.30  
                **赛事主办** : idek (https://ctftime.org/team/157039)  
                **添加日历** : https://ctftime.org/event/2304.ics  
                
            ??? Quote "[Lexington Informatics Tournament CTF 2024](https://lit.lhsmathcs.org/)"  
                [![](https://ctftime.org/media/events/square_CTFtime_LIT_1.png){ width="200" align=left }](https://lit.lhsmathcs.org/)  
                **比赛名称** : [Lexington Informatics Tournament CTF 2024](https://lit.lhsmathcs.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-10 23:00:00 - 2024-08-13 11:59:59 UTC+8  
                **比赛权重** : 46.25  
                **赛事主办** : LIT CTF (https://ctftime.org/team/157660)  
                **添加日历** : https://ctftime.org/event/2444.ics  
                
            ??? Quote "[CTFZone 2024 Quals](https://ctf.bi.zone/)"  
                [![](https://ctftime.org/media/events/b98226ad9a255846e456617d99bde1de.png){ width="200" align=left }](https://ctf.bi.zone/)  
                **比赛名称** : [CTFZone 2024 Quals](https://ctf.bi.zone/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-10 17:00:00 - 2024-08-11 17:00:00 UTC+8  
                **比赛权重** : 73.82  
                **赛事主办** : BIZone (https://ctftime.org/team/32190)  
                **添加日历** : https://ctftime.org/event/2408.ics  
                
            ??? Quote "[DEF CON CTF 2024](https://nautilus.institute/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://nautilus.institute/)  
                **比赛名称** : [DEF CON CTF 2024](https://nautilus.institute/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-08-10 00:00:00 - 2024-08-12 04:00:00 UTC+8  
                **比赛权重** : 35.00  
                **赛事主办** : Nautilus Institute (https://ctftime.org/team/181536)  
                **添加日历** : https://ctftime.org/event/2462.ics  
                
            ??? Quote "[PECAN+ CTF 2024](https://pecanplus.ecusdf.org/)"  
                [![](https://ctftime.org/media/events/Pecan_Logo_Transparent_1.png){ width="200" align=left }](https://pecanplus.ecusdf.org/)  
                **比赛名称** : [PECAN+ CTF 2024](https://pecanplus.ecusdf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-04 09:00:00 - 2024-08-04 13:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : PECAN+ (https://ctftime.org/team/250009)  
                **添加日历** : https://ctftime.org/event/2439.ics  
                
            ??? Quote "[n00bzCTF 2024](https://ctf.n00bzunit3d.xyz/)"  
                [![](https://ctftime.org/media/events/logo_ascii_1.png){ width="200" align=left }](https://ctf.n00bzunit3d.xyz/)  
                **比赛名称** : [n00bzCTF 2024](https://ctf.n00bzunit3d.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-03 09:00:00 - 2024-08-05 09:00:00 UTC+8  
                **比赛权重** : 24.23  
                **赛事主办** : n00bzUnit3d (https://ctftime.org/team/152491)  
                **添加日历** : https://ctftime.org/event/2378.ics  
                
            ??? Quote "[CrewCTF 2024](https://2024.crewc.tf/)"  
                [![](https://ctftime.org/media/events/THC_new.png){ width="200" align=left }](https://2024.crewc.tf/)  
                **比赛名称** : [CrewCTF 2024](https://2024.crewc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-03 01:00:00 - 2024-08-05 01:00:00 UTC+8  
                **比赛权重** : 26.89  
                **赛事主办** : thehackerscrew (https://ctftime.org/team/85618)  
                **添加日历** : https://ctftime.org/event/2223.ics  
                
            ??? Quote "[Arab Security Cyber Wargames 2024 Qualifications](https://www.ascyberwargames.com/ascwgs2024/)"  
                [![](https://ctftime.org/media/events/Image20230709224223.png){ width="200" align=left }](https://www.ascyberwargames.com/ascwgs2024/)  
                **比赛名称** : [Arab Security Cyber Wargames 2024 Qualifications](https://www.ascyberwargames.com/ascwgs2024/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-02 21:00:00 - 2024-08-03 21:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Arab Security Cyber Wargames (https://ctftime.org/team/127553)  
                **添加日历** : https://ctftime.org/event/2434.ics  
                
            ??? Quote "[TFC CTF 2024](https://ctf.thefewchosen.com/)"  
                [![](https://ctftime.org/media/events/discord_logo_3.png){ width="200" align=left }](https://ctf.thefewchosen.com/)  
                **比赛名称** : [TFC CTF 2024](https://ctf.thefewchosen.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-02 19:00:00 - 2024-08-04 19:00:00 UTC+8  
                **比赛权重** : 41.68  
                **赛事主办** : The Few Chosen (https://ctftime.org/team/140885)  
                **添加日历** : https://ctftime.org/event/2423.ics  
                
            ??? Quote "[SCAN 2024 Digital Asset Tracing Challenge](https://scanctf2024.ctfd.io/)"  
                [![](https://ctftime.org/media/events/Logo_blue2x.png){ width="200" align=left }](https://scanctf2024.ctfd.io/)  
                **比赛名称** : [SCAN 2024 Digital Asset Tracing Challenge](https://scanctf2024.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-30 08:00:00 - 2024-07-31 08:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : D Asset Inc. (https://ctftime.org/team/310109)  
                **添加日历** : https://ctftime.org/event/2442.ics  
                
            ??? Quote "[corCTF 2024](https://ctf.cor.team/)"  
                [![](https://ctftime.org/media/events/corctflogo_3.png){ width="200" align=left }](https://ctf.cor.team/)  
                **比赛名称** : [corCTF 2024](https://ctf.cor.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-27 08:00:00 - 2024-07-29 08:00:00 UTC+8  
                **比赛权重** : 55.00  
                **赛事主办** : Crusaders of Rust (https://ctftime.org/team/132628)  
                **添加日历** : https://ctftime.org/event/2282.ics  
                
            ??? Quote "[DeadSec CTF 2024](https://deadsec.ctf.ae/)"  
                [![](https://ctftime.org/media/events/Picture1_1.png){ width="200" align=left }](https://deadsec.ctf.ae/)  
                **比赛名称** : [DeadSec CTF 2024](https://deadsec.ctf.ae/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-27 04:00:00 - 2024-07-28 16:00:00 UTC+8  
                **比赛权重** : 23.96  
                **赛事主办** : DeadSec (https://ctftime.org/team/19339)  
                **添加日历** : https://ctftime.org/event/2353.ics  
                
            ??? Quote "[Aptos Code Collision CTF 2024](https://ctf.aptosfoundation.org/)"  
                [![](https://ctftime.org/media/events/AptosProfilePic.png){ width="200" align=left }](https://ctf.aptosfoundation.org/)  
                **比赛名称** : [Aptos Code Collision CTF 2024](https://ctf.aptosfoundation.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-26 20:00:00 - 2024-07-28 20:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Aptos (https://ctftime.org/team/307766)  
                **添加日历** : https://ctftime.org/event/2433.ics  
                
            ??? Quote "[BDSec CTF 2024](https://bdsec-ctf.com/)"  
                [![](https://ctftime.org/media/events/brand-logo_1.png){ width="200" align=left }](https://bdsec-ctf.com/)  
                **比赛名称** : [BDSec CTF 2024](https://bdsec-ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-20 23:00:00 - 2024-07-21 23:00:00 UTC+8  
                **比赛权重** : 16.00  
                **赛事主办** : Knight Squad (https://ctftime.org/team/141739)  
                **添加日历** : https://ctftime.org/event/2421.ics  
                
            ??? Quote "[ENOWARS 8](https://8.enowars.com/)"  
                [![](https://ctftime.org/media/events/enowars8.png){ width="200" align=left }](https://8.enowars.com/)  
                **比赛名称** : [ENOWARS 8](https://8.enowars.com/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-07-20 20:00:00 - 2024-07-21 05:00:00 UTC+8  
                **比赛权重** : 98.89  
                **赛事主办** : ENOFLAG (https://ctftime.org/team/1438)  
                **添加日历** : https://ctftime.org/event/2412.ics  
                
            ??? Quote "[MOCA CTF - Quals](https://play.pwnx.io/#/event/fb765f39-bc6f-46b9-a7bc-823bc261323a)"  
                [![](https://ctftime.org){ width="200" align=left }](https://play.pwnx.io/#/event/fb765f39-bc6f-46b9-a7bc-823bc261323a)  
                **比赛名称** : [MOCA CTF - Quals](https://play.pwnx.io/#/event/fb765f39-bc6f-46b9-a7bc-823bc261323a)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-20 17:00:00 - 2024-07-21 17:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Metro Olografix (https://ctftime.org/team/268425)  
                **添加日历** : https://ctftime.org/event/2293.ics  
                
            ??? Quote "[DASCTF 2024 Summer Challenge](https://buuoj.cn/match/matches/207)"  
                [![](https://ctftime.org/media/events/Dingtalk_20240709141420.jpg){ width="200" align=left }](https://buuoj.cn/match/matches/207)  
                **比赛名称** : [DASCTF 2024 Summer Challenge](https://buuoj.cn/match/matches/207)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-20 10:00:00 - 2024-07-20 18:00:00 UTC+8  
                **比赛权重** : 20.00  
                **赛事主办** : DASCTF (https://ctftime.org/team/303691)  
                **添加日历** : https://ctftime.org/event/2429.ics  
                
            ??? Quote "[ImaginaryCTF 2024](https://2024.imaginaryctf.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://2024.imaginaryctf.org/)  
                **比赛名称** : [ImaginaryCTF 2024](https://2024.imaginaryctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-20 03:00:00 - 2024-07-22 03:00:00 UTC+8  
                **比赛权重** : 49.81  
                **赛事主办** : ImaginaryCTF (https://ctftime.org/team/131529)  
                **添加日历** : https://ctftime.org/event/2396.ics  
                
            ??? Quote "[CatTheQuest](https://catthequest.com/)"  
                [![](https://ctftime.org/media/events/DALL_E-2024-03-21-18.10-removebg-preview.png){ width="200" align=left }](https://catthequest.com/)  
                **比赛名称** : [CatTheQuest](https://catthequest.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-15 08:00:00 - 2024-07-21 08:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : CatTheFlag (https://ctftime.org/team/306432)  
                **添加日历** : https://ctftime.org/event/2414.ics  
                
            ??? Quote "[OSCTF](https://ctf.os.ftp.sh/)"  
                [![](https://ctftime.org/media/events/os_ctf_logo.png){ width="200" align=left }](https://ctf.os.ftp.sh/)  
                **比赛名称** : [OSCTF](https://ctf.os.ftp.sh/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-13 08:30:00 - 2024-07-14 00:30:00 UTC+8  
                **比赛权重** : 23.10  
                **赛事主办** : BlitzHack (https://ctftime.org/team/307415)  
                **添加日历** : https://ctftime.org/event/2416.ics  
                
            ??? Quote "[HITCON CTF 2024 Quals](https://ctf2024.hitcon.org/)"  
                [![](https://ctftime.org/media/events/hitcon-ctf_monotone_black.png){ width="200" align=left }](https://ctf2024.hitcon.org/)  
                **比赛名称** : [HITCON CTF 2024 Quals](https://ctf2024.hitcon.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-12 22:00:00 - 2024-07-14 22:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : HITCON (https://ctftime.org/team/8299)  
                **添加日历** : https://ctftime.org/event/2345.ics  
                
            ??? Quote "[Interlogica CTF2024 - Wastelands](https://ctf.interlogica.ninja/)"  
                [![](https://ctftime.org/media/events/Untitled_2.png){ width="200" align=left }](https://ctf.interlogica.ninja/)  
                **比赛名称** : [Interlogica CTF2024 - Wastelands](https://ctf.interlogica.ninja/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-05 20:37:00 - 2024-07-08 06:59:59 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Interlogica (https://ctftime.org/team/250899)  
                **添加日历** : https://ctftime.org/event/2301.ics  
                
            ??? Quote "[DownUnderCTF 2024](https://play.duc.tf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://play.duc.tf/)  
                **比赛名称** : [DownUnderCTF 2024](https://play.duc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-05 17:30:00 - 2024-07-07 17:30:00 UTC+8  
                **比赛权重** : 68.04  
                **赛事主办** : DownUnderCTF (https://ctftime.org/team/126400)  
                **添加日历** : https://ctftime.org/event/2284.ics  
                
            ??? Quote "[Junior.Crypt.2024 CTF](http://ctf-spcs.mf.grsu.by/)"  
                [![](https://ctftime.org/media/events/logo_NY.jpg){ width="200" align=left }](http://ctf-spcs.mf.grsu.by/)  
                **比赛名称** : [Junior.Crypt.2024 CTF](http://ctf-spcs.mf.grsu.by/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-03 23:00:00 - 2024-07-05 23:00:00 UTC+8  
                **比赛权重** : 22.95  
                **赛事主办** : Beavers0 (https://ctftime.org/team/269281)  
                **添加日历** : https://ctftime.org/event/2259.ics  
                
            ??? Quote "[DiceCTF 2024 Finals](https://ctf.dicega.ng/)"  
                [![](https://ctftime.org/media/events/dicectf_2_1_1.png){ width="200" align=left }](https://ctf.dicega.ng/)  
                **比赛名称** : [DiceCTF 2024 Finals](https://ctf.dicega.ng/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-06-29 22:00:00 - 2024-07-01 06:00:00 UTC+8  
                **比赛权重** : 20.00  
                **赛事主办** : DiceGang (https://ctftime.org/team/109452)  
                **添加日历** : https://ctftime.org/event/2306.ics  
                
            ??? Quote "[UIUCTF 2024](http://2024.uiuc.tf/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://2024.uiuc.tf/)  
                **比赛名称** : [UIUCTF 2024](http://2024.uiuc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-29 08:00:00 - 2024-07-01 08:00:00 UTC+8  
                **比赛权重** : 67.51  
                **赛事主办** : SIGPwny (https://ctftime.org/team/27763)  
                **添加日历** : https://ctftime.org/event/2275.ics  
                
            ??? Quote "[The Hacker Conclave](http://ctf.thehackerconclave.es/)"  
                [![](https://ctftime.org/media/events/conclave.png){ width="200" align=left }](http://ctf.thehackerconclave.es/)  
                **比赛名称** : [The Hacker Conclave](http://ctf.thehackerconclave.es/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-27 16:00:00 - 2024-06-27 19:00:00 UTC+8  
                **比赛权重** : 19.60  
                **赛事主办** : C0ncl4v3 (https://ctftime.org/team/303692)  
                **添加日历** : https://ctftime.org/event/2397.ics  
                
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
