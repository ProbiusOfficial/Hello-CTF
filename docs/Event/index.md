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
        ??? Quote "[第十七届全国大学生信息安全竞赛——创新实践能力赛](http://www.ciscn.cn/)"  
            **比赛名称** : [第十七届全国大学生信息安全竞赛——创新实践能力赛](http://www.ciscn.cn/)  
            **比赛类型** : 团队赛 | 1-4人  
            **报名时间** : 2024年4月12日 00:00 - 2024年5月14日 18:00  
            **比赛时间** : 2024年5月18日 09:00 - 2024年5月19日 18:00  
            **其他说明** : 545083579 (17届信安创新实践赛指导老师群)  327904910 (17届信安创新实践赛学生①群)  191965192 (17届信安创新实践赛学生②群)  566613050 (17届信安创新实践赛学生③群)  570834671 (17届信安创新实践赛学生④群)  
            
        ??? Quote "[第十七届全国大学生信息安全竞赛 - 作品赛](http://www.ciscn.cn/competition/securityCompetition?compet_id=39)"  
            **比赛名称** : [第十七届全国大学生信息安全竞赛 - 作品赛](http://www.ciscn.cn/competition/securityCompetition?compet_id=39)  
            **比赛类型** : 作品赛  
            **报名时间** : 2024年04月07日 23:00 - 2024年06月05日 23:00  
            **比赛时间** : 2024年04月10日 23:00 - 2024年06月05日 23:00  
            **其他说明** : 作品赛，不提供更多信息，如有疑问请前往比赛通知页面 http://www.ciscn.cn/competition/securityCompetition?compet_id=39  
            
        ??? Quote "[第二届数据安全大赛暨首届“数信杯”数据安全大赛](https://shuxinbei.ichunqiu.com/)"  
            **比赛名称** : [第二届数据安全大赛暨首届“数信杯”数据安全大赛](https://shuxinbei.ichunqiu.com/)  
            **比赛类型** : 团队赛|1-3人  
            **报名时间** : 2023年11月15日 00:00 - 2024年04月30日 00:00  
            **比赛时间** : 2024年05月01日 00:00 - 2024年05月02日 00:00  
            **其他说明** : 比赛时间未定  
            
    === "*即将开始*"
        === "国内赛事"
            ??? Quote "[H&NCTF](暂无)"  
                **比赛名称** : [H&NCTF](暂无)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年5月10日 8:00 - 2024年5月13日 18:00  
                **比赛时间** : 2024年5月12日 8:00 - 2024年5月13日 18:00  
                **其他说明** : QQ群：733181790  
                
            ??? Quote "[ISCC 2024](http://www.isclab.org.cn)"  
                **比赛名称** : [ISCC 2024](http://www.isclab.org.cn)  
                **比赛类型** : 个人赛 | 人脉  
                **报名时间** : 2024年04月30日 08:00 - 2024年05月25日 08:00  
                **比赛时间** : 2024年05月01日 08:00 - 2024年05月25日 08:00  
                **其他说明** : QQ群:619577692 / 852601317 邮箱:iscc2004@163.com  
                
            ??? Quote "[第十七届全国大学生信息安全竞赛——创新实践能力赛](http://www.ciscn.cn/)"  
                **比赛名称** : [第十七届全国大学生信息安全竞赛——创新实践能力赛](http://www.ciscn.cn/)  
                **比赛类型** : 团队赛 | 1-4人  
                **报名时间** : 2024年4月12日 00:00 - 2024年5月14日 18:00  
                **比赛时间** : 2024年5月18日 09:00 - 2024年5月19日 18:00  
                **其他说明** : 545083579 (17届信安创新实践赛指导老师群)  327904910 (17届信安创新实践赛学生①群)  191965192 (17届信安创新实践赛学生②群)  566613050 (17届信安创新实践赛学生③群)  570834671 (17届信安创新实践赛学生④群)  
                
            ??? Quote "[第十七届全国大学生信息安全竞赛 - 作品赛](http://www.ciscn.cn/competition/securityCompetition?compet_id=39)"  
                **比赛名称** : [第十七届全国大学生信息安全竞赛 - 作品赛](http://www.ciscn.cn/competition/securityCompetition?compet_id=39)  
                **比赛类型** : 作品赛  
                **报名时间** : 2024年04月07日 23:00 - 2024年06月05日 23:00  
                **比赛时间** : 2024年04月10日 23:00 - 2024年06月05日 23:00  
                **其他说明** : 作品赛，不提供更多信息，如有疑问请前往比赛通知页面 http://www.ciscn.cn/competition/securityCompetition?compet_id=39  
                
            ??? Quote "[第二届数据安全大赛暨首届“数信杯”数据安全大赛](https://shuxinbei.ichunqiu.com/)"  
                **比赛名称** : [第二届数据安全大赛暨首届“数信杯”数据安全大赛](https://shuxinbei.ichunqiu.com/)  
                **比赛类型** : 团队赛|1-3人  
                **报名时间** : 2023年11月15日 00:00 - 2024年04月30日 00:00  
                **比赛时间** : 2024年05月01日 00:00 - 2024年05月02日 00:00  
                **其他说明** : 比赛时间未定  
                
        === "国外赛事"
            ??? Quote "[Midnight Sun CTF 2024 Quals](https://midnightsunctf.com/)"  
                [![](https://ctftime.org/media/events/midnight.png){ width="200" align=left }](https://midnightsunctf.com/)  
                **比赛名称** : [Midnight Sun CTF 2024 Quals](https://midnightsunctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-20 18:00:00 - 2024-04-21 18:00:00 UTC+8  
                **比赛权重** : 35.74  
                **赛事主办** : HackingForSoju (https://ctftime.org/team/3208)  
                **添加日历** : https://ctftime.org/event/2247.ics  
                
            ??? Quote "[Challenge the Cyber - Cyber Chef](https://challengethecyber.nl/)"  
                [![](https://ctftime.org/media/events/12e936bf3a5de410fc3506bfdffb608a.jpg){ width="200" align=left }](https://challengethecyber.nl/)  
                **比赛名称** : [Challenge the Cyber - Cyber Chef](https://challengethecyber.nl/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-20 19:00:00 - 2024-04-21 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Challenge the Cyber (https://ctftime.org/team/181210)  
                **添加日历** : https://ctftime.org/event/2277.ics  
                
            ??? Quote "[cr3 CTF 2024](https://cr3c.tf/)"  
                [![](https://ctftime.org/media/events/cr3ctf_2024.png){ width="200" align=left }](https://cr3c.tf/)  
                **比赛名称** : [cr3 CTF 2024](https://cr3c.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-26 21:00:00 - 2024-04-28 09:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : cr3.mov (https://ctftime.org/team/242101)  
                **添加日历** : https://ctftime.org/event/2288.ics  
                
            ??? Quote "[Insomni'hack 2024](https://insomnihack.ch/contests/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://insomnihack.ch/contests/)  
                **比赛名称** : [Insomni'hack 2024](https://insomnihack.ch/contests/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 00:30:00 - 2024-04-27 11:00:00 UTC+8  
                **比赛权重** : 33.40  
                **赛事主办** : Insomni'hack Team (https://ctftime.org/team/104742)  
                **添加日历** : https://ctftime.org/event/2271.ics  
                
            ??? Quote "[UMDCTF 2024](https://umdctf.io/)"  
                [![](https://ctftime.org/media/events/logo_95.png){ width="200" align=left }](https://umdctf.io/)  
                **比赛名称** : [UMDCTF 2024](https://umdctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 06:00:00 - 2024-04-29 06:00:00 UTC+8  
                **比赛权重** : 48.92  
                **赛事主办** : UMDCSEC (https://ctftime.org/team/87711)  
                **添加日历** : https://ctftime.org/event/2323.ics  
                
            ??? Quote "[HACKTHEON SEJONG 2024 Preliminaries](https://hacktheon.org/)"  
                [![](https://ctftime.org/media/events/CTF_2024.JPG){ width="200" align=left }](https://hacktheon.org/)  
                **比赛名称** : [HACKTHEON SEJONG 2024 Preliminaries](https://hacktheon.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 08:00:00 - 2024-04-27 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Sejong City Hall (https://ctftime.org/team/214900)  
                **添加日历** : https://ctftime.org/event/2286.ics  
                
            ??? Quote "[Dreamhack Invitational Quals 2024](https://dreamhack.io/ctf/518/)"  
                [![](https://ctftime.org/media/events/_mini_round_light2x.png){ width="200" align=left }](https://dreamhack.io/ctf/518/)  
                **比赛名称** : [Dreamhack Invitational Quals 2024](https://dreamhack.io/ctf/518/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 08:00:00 - 2024-04-28 08:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Theori (https://ctftime.org/team/250867)  
                **添加日历** : https://ctftime.org/event/2308.ics  
                
            ??? Quote "[UrchinSec Tanzania National CTF MMXXIV](https://ctf.urchinsec.com/)"  
                [![](https://ctftime.org/media/events/TkH-DDqG_400x400.png){ width="200" align=left }](https://ctf.urchinsec.com/)  
                **比赛名称** : [UrchinSec Tanzania National CTF MMXXIV](https://ctf.urchinsec.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 15:30:00 - 2024-04-29 03:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : UrchinSec (https://ctftime.org/team/175663)  
                **添加日历** : https://ctftime.org/event/2327.ics  
                
            ??? Quote "[Midnight Flag - Operation BACKSLASH]()"  
                [![](https://ctftime.org/media/events/logo-3848x3084-upscaled.png){ width="200" align=left }]()  
                **比赛名称** : [Midnight Flag - Operation BACKSLASH]()  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-28 04:00:00 - 2024-04-28 15:00:00 UTC+8  
                **比赛权重** : 37.00  
                **赛事主办** : Midnight Flag (https://ctftime.org/team/179110)  
                **添加日历** : https://ctftime.org/event/2295.ics  
                
            ??? Quote "[CyberSphere CTF](https://securinets.tn/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://securinets.tn/)  
                **比赛名称** : [CyberSphere CTF](https://securinets.tn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-28 05:00:00 - 2024-04-28 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Securinets (https://ctftime.org/team/5084)  
                **添加日历** : https://ctftime.org/event/2328.ics  
                
            ??? Quote "[Cybercoliseum Ⅲ](https://codeby.games/cybercoliseum)"  
                [![](https://ctftime.org/media/events/logo-cdb.png){ width="200" align=left }](https://codeby.games/cybercoliseum)  
                **比赛名称** : [Cybercoliseum Ⅲ](https://codeby.games/cybercoliseum)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-28 15:00:00 - 2024-04-30 03:00:00 UTC+8  
                **比赛权重** : 20.95  
                **赛事主办** : Codeby Games (https://ctftime.org/team/299486)  
                **添加日历** : https://ctftime.org/event/2341.ics  
                
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
                
            ??? Quote "[Punk Security DevSecOps Birthday CTF](https://punksecurity.co.uk/ctf)"  
                [![](https://ctftime.org){ width="200" align=left }](https://punksecurity.co.uk/ctf)  
                **比赛名称** : [Punk Security DevSecOps Birthday CTF](https://punksecurity.co.uk/ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-04 17:00:00 - 2024-05-05 05:00:00 UTC+8  
                **比赛权重** : 24.82  
                **赛事主办** : Punk Security (https://ctftime.org/team/212540)  
                **添加日历** : https://ctftime.org/event/2285.ics  
                
            ??? Quote "[TBTL CTF 2024](https://tbtl.ctfd.io/)"  
                [![](https://ctftime.org/media/events/ctflogo_2.png){ width="200" align=left }](https://tbtl.ctfd.io/)  
                **比赛名称** : [TBTL CTF 2024](https://tbtl.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-11 06:00:00 - 2024-05-13 06:00:00 UTC+8  
                **比赛权重** : 22.17  
                **赛事主办** : TBTL (https://ctftime.org/team/170112)  
                **添加日历** : https://ctftime.org/event/2324.ics  
                
            ??? Quote "[San Diego CTF 2024](https://sdc.tf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://sdc.tf/)  
                **比赛名称** : [San Diego CTF 2024](https://sdc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-11 07:59:59 - 2024-05-13 07:59:59 UTC+8  
                **比赛权重** : 24.67  
                **赛事主办** : 3 Prongs And a Computer (https://ctftime.org/team/112558)  
                **添加日历** : https://ctftime.org/event/2325.ics  
                
            ??? Quote "[CyberSecurityRumble Quals](https://hacking-meisterschaft.de/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://hacking-meisterschaft.de/)  
                **比赛名称** : [CyberSecurityRumble Quals](https://hacking-meisterschaft.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-11 21:00:00 - 2024-05-12 21:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : RedRocket (https://ctftime.org/team/48677)  
                **添加日历** : https://ctftime.org/event/2224.ics  
                
            ??? Quote "[BYUCTF 2024](https://cyberjousting.com/)"  
                [![](https://ctftime.org/media/events/cougar.jpg){ width="200" align=left }](https://cyberjousting.com/)  
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
                
            ??? Quote "[Break the Syntax CTF 2024](https://bts2024.wh.edu.pl/)"  
                [![](https://ctftime.org/media/events/bts2024_logofill_black.png){ width="200" align=left }](https://bts2024.wh.edu.pl/)  
                **比赛名称** : [Break the Syntax CTF 2024](https://bts2024.wh.edu.pl/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 00:00:00 - 2024-05-19 18:00:00 UTC+8  
                **比赛权重** : 28.30  
                **赛事主办** : PWr Synt@x Err0r (https://ctftime.org/team/88205)  
                **添加日历** : https://ctftime.org/event/2289.ics  
                
            ??? Quote "[TJCTF 2024](https://tjctf.org/)"  
                [![](https://ctftime.org/media/events/logo_96.png){ width="200" align=left }](https://tjctf.org/)  
                **比赛名称** : [TJCTF 2024](https://tjctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 02:30:00 - 2024-05-20 02:30:00 UTC+8  
                **比赛权重** : 35.60  
                **赛事主办** : tjcsc (https://ctftime.org/team/53812)  
                **添加日历** : https://ctftime.org/event/2321.ics  
                
            ??? Quote "[R3CTF/YUANHENGCTF 2024](https://ctf2024.r3kapig.com/)"  
                [![](https://ctftime.org/media/events/r3_logo.png){ width="200" align=left }](https://ctf2024.r3kapig.com/)  
                **比赛名称** : [R3CTF/YUANHENGCTF 2024](https://ctf2024.r3kapig.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 10:00:00 - 2024-05-20 10:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : r3kapig (https://ctftime.org/team/58979)  
                **添加日历** : https://ctftime.org/event/2273.ics  
                
            ??? Quote "[VulnX CTF 2024](https://vulncon.in/)"  
                [![](https://ctftime.org/media/events/VulnX-Profile_pic.png){ width="200" align=left }](https://vulncon.in/)  
                **比赛名称** : [VulnX CTF 2024](https://vulncon.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 18:30:00 - 2024-05-19 18:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : VulnX (https://ctftime.org/team/117274)  
                **添加日历** : https://ctftime.org/event/2318.ics  
                
            ??? Quote "[SAS CTF 2024 Quals](https://ctf.thesascon.com/)"  
                [![](https://ctftime.org/media/events/SAS24_2.png){ width="200" align=left }](https://ctf.thesascon.com/)  
                **比赛名称** : [SAS CTF 2024 Quals](https://ctf.thesascon.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 20:00:00 - 2024-05-19 20:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SAS CREW (https://ctftime.org/team/283057)  
                **添加日历** : https://ctftime.org/event/2299.ics  
                
            ??? Quote "[HTB Business CTF 2024: The Vault Of Hope](https://ctf.hackthebox.com/event/details/htb-business-ctf-2024-the-vault-of-hope-1474)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hackthebox.com/event/details/htb-business-ctf-2024-the-vault-of-hope-1474)  
                **比赛名称** : [HTB Business CTF 2024: The Vault Of Hope](https://ctf.hackthebox.com/event/details/htb-business-ctf-2024-the-vault-of-hope-1474)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 21:00:00 - 2024-05-22 21:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Hack The Box (https://ctftime.org/team/136056)  
                **添加日历** : https://ctftime.org/event/2315.ics  
                
            ??? Quote "[Hacky'Nov 0x03](https://hackynov.fr/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://hackynov.fr/)  
                **比赛名称** : [Hacky'Nov 0x03](https://hackynov.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 22:00:00 - 2024-05-19 15:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hacky'Nov (https://ctftime.org/team/178939)  
                **添加日历** : https://ctftime.org/event/2319.ics  
                
            ??? Quote "[L3akCTF 2024](https://ctf.l3ak.team/)"  
                [![](https://ctftime.org/media/events/ctf_final.png){ width="200" align=left }](https://ctf.l3ak.team/)  
                **比赛名称** : [L3akCTF 2024](https://ctf.l3ak.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-24 20:00:00 - 2024-05-26 20:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : L3ak (https://ctftime.org/team/220336)  
                **添加日历** : https://ctftime.org/event/2322.ics  
                
            ??? Quote "[CrewCTF 2024](https://crewc.tf/)"  
                [![](https://ctftime.org/media/events/THC_new.png){ width="200" align=left }](https://crewc.tf/)  
                **比赛名称** : [CrewCTF 2024](https://crewc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-25 01:00:00 - 2024-05-27 01:00:00 UTC+8  
                **比赛权重** : 26.89  
                **赛事主办** : thehackerscrew (https://ctftime.org/team/85618)  
                **添加日历** : https://ctftime.org/event/2223.ics  
                
            ??? Quote "[Dreamhack Invitational 2024](https://dreamhack.io/)"  
                [![](https://ctftime.org/media/events/_mini_round_light2x_1.png){ width="200" align=left }](https://dreamhack.io/)  
                **比赛名称** : [Dreamhack Invitational 2024](https://dreamhack.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-27 09:00:00 - 2024-05-27 21:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Theori (https://ctftime.org/team/250867)  
                **添加日历** : https://ctftime.org/event/2309.ics  
                
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
                
            ??? Quote "[BCACTF 5.0](https://www.bcactf.com/)"  
                [![](https://ctftime.org/media/events/bcactflogoocean.png){ width="200" align=left }](https://www.bcactf.com/)  
                **比赛名称** : [BCACTF 5.0](https://www.bcactf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-08 04:00:00 - 2024-06-11 04:00:00 UTC+8  
                **比赛权重** : 46.33  
                **赛事主办** : BCACTF (https://ctftime.org/team/81702)  
                **添加日历** : https://ctftime.org/event/2274.ics  
                
            ??? Quote "[Crypto CTF 2024](https://cr.yp.toc.tf/)"  
                [![](https://ctftime.org/media/events/cryptoctf.jpg){ width="200" align=left }](https://cr.yp.toc.tf/)  
                **比赛名称** : [Crypto CTF 2024](https://cr.yp.toc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-08 22:00:00 - 2024-06-09 22:00:00 UTC+8  
                **比赛权重** : 65.62  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2210.ics  
                
            ??? Quote "[BrainHack 2024](https://go.gov.sg/dsta-brainhack-signup)"  
                [![](https://ctftime.org/media/events/807b15_524e092c9d7541589d621cd0e9bf6e4bmv2.jpeg){ width="200" align=left }](https://go.gov.sg/dsta-brainhack-signup)  
                **比赛名称** : [BrainHack 2024](https://go.gov.sg/dsta-brainhack-signup)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-12 16:00:00 - 2024-06-14 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BrainHack_Organiser (https://ctftime.org/team/287673)  
                **添加日历** : https://ctftime.org/event/2330.ics  
                
            ??? Quote "[idekCTF 2024](https://ctf.idek.team/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.idek.team/)  
                **比赛名称** : [idekCTF 2024](https://ctf.idek.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-15 08:00:00 - 2024-06-17 08:00:00 UTC+8  
                **比赛权重** : 35.41  
                **赛事主办** : idek (https://ctftime.org/team/157039)  
                **添加日历** : https://ctftime.org/event/2304.ics  
                
            ??? Quote "[Grey Cat The Flag 2024 Finals](https://ctf.nusgreyhats.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.nusgreyhats.org/)  
                **比赛名称** : [Grey Cat The Flag 2024 Finals](https://ctf.nusgreyhats.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-20 10:00:00 - 2024-06-21 18:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : NUSGreyhats (https://ctftime.org/team/16740)  
                **添加日历** : https://ctftime.org/event/2244.ics  
                
            ??? Quote "[Google Capture The Flag 2024](https://g.co/ctf)"  
                [![](https://ctftime.org){ width="200" align=left }](https://g.co/ctf)  
                **比赛名称** : [Google Capture The Flag 2024](https://g.co/ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-22 02:00:00 - 2024-06-24 02:00:00 UTC+8  
                **比赛权重** : 99.41  
                **赛事主办** : Google CTF (https://ctftime.org/team/23929)  
                **添加日历** : https://ctftime.org/event/2296.ics  
                
            ??? Quote "[MOCA CTF - Qualification](https://moca.camp/ctf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://moca.camp/ctf/)  
                **比赛名称** : [MOCA CTF - Qualification](https://moca.camp/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-22 19:00:00 - 2024-06-23 19:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Metro Olografix (https://ctftime.org/team/268425)  
                **添加日历** : https://ctftime.org/event/2293.ics  
                
            ??? Quote "[UIUCTF 2024](https://uiuc.tf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://uiuc.tf/)  
                **比赛名称** : [UIUCTF 2024](https://uiuc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-29 08:00:00 - 2024-07-01 08:00:00 UTC+8  
                **比赛权重** : 67.51  
                **赛事主办** : SIGPwny (https://ctftime.org/team/27763)  
                **添加日历** : https://ctftime.org/event/2275.ics  
                
            ??? Quote "[DiceCTF 2024 Finals](https://ctf.dicega.ng/)"  
                [![](https://ctftime.org/media/events/dicectf_2_1_1.png){ width="200" align=left }](https://ctf.dicega.ng/)  
                **比赛名称** : [DiceCTF 2024 Finals](https://ctf.dicega.ng/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-06-29 22:00:00 - 2024-07-01 06:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : DiceGang (https://ctftime.org/team/109452)  
                **添加日历** : https://ctftime.org/event/2306.ics  
                
            ??? Quote "[Junior.Crypt.2024 CTF](http://ctf-spcs.mf.grsu.by/)"  
                [![](https://ctftime.org/media/events/logo_NY.jpg){ width="200" align=left }](http://ctf-spcs.mf.grsu.by/)  
                **比赛名称** : [Junior.Crypt.2024 CTF](http://ctf-spcs.mf.grsu.by/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-03 23:00:00 - 2024-07-05 23:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Beavers0 (https://ctftime.org/team/269281)  
                **添加日历** : https://ctftime.org/event/2259.ics  
                
            ??? Quote "[DownUnderCTF 2024](https://play.duc.tf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://play.duc.tf/)  
                **比赛名称** : [DownUnderCTF 2024](https://play.duc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-05 17:30:00 - 2024-07-07 17:30:00 UTC+8  
                **比赛权重** : 68.04  
                **赛事主办** : DownUnderCTF (https://ctftime.org/team/126400)  
                **添加日历** : https://ctftime.org/event/2284.ics  
                
            ??? Quote "[Interlogica CTF2024 - Wastelands](https://ctf.interlogica.it/)"  
                [![](https://ctftime.org/media/events/Untitled_2.png){ width="200" align=left }](https://ctf.interlogica.it/)  
                **比赛名称** : [Interlogica CTF2024 - Wastelands](https://ctf.interlogica.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-05 20:37:00 - 2024-07-08 06:59:59 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Interlogica (https://ctftime.org/team/250899)  
                **添加日历** : https://ctftime.org/event/2301.ics  
                
            ??? Quote "[MOCA CTF - Finals](https://moca.camp/ctf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://moca.camp/ctf/)  
                **比赛名称** : [MOCA CTF - Finals](https://moca.camp/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-14 19:00:00 - 2024-07-15 19:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Metro Olografix (https://ctftime.org/team/268425)  
                **添加日历** : https://ctftime.org/event/2294.ics  
                
            ??? Quote "[corCTF 2024](https://ctf.cor.team/)"  
                [![](https://ctftime.org/media/events/corctflogo_3.png){ width="200" align=left }](https://ctf.cor.team/)  
                **比赛名称** : [corCTF 2024](https://ctf.cor.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-27 08:00:00 - 2024-07-29 08:00:00 UTC+8  
                **比赛权重** : 55.00  
                **赛事主办** : Crusaders of Rust (https://ctftime.org/team/132628)  
                **添加日历** : https://ctftime.org/event/2282.ics  
                
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
                
            ??? Quote "[TCP1P CTF 2024: Exploring Nusantara's Digital Realm](https://tcp1p.github.io/tcp1p-pages/tcp1pctf-2024)"  
                [![](https://ctftime.org/media/events/TCP1P-logo.png){ width="200" align=left }](https://tcp1p.github.io/tcp1p-pages/tcp1pctf-2024)  
                **比赛名称** : [TCP1P CTF 2024: Exploring Nusantara's Digital Realm](https://tcp1p.github.io/tcp1p-pages/tcp1pctf-2024)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-11 20:00:00 - 2024-10-13 20:00:00 UTC+8  
                **比赛权重** : 24.85  
                **赛事主办** : TCP1P (https://ctftime.org/team/187248)  
                **添加日历** : https://ctftime.org/event/2256.ics  
                
            ??? Quote "[Equinor CTF 2024](https://ctf.equinor.com/)"  
                [![](https://ctftime.org/media/events/ept_1.png){ width="200" align=left }](https://ctf.equinor.com/)  
                **比赛名称** : [Equinor CTF 2024](https://ctf.equinor.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 17:00:00 - 2024-11-03 03:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : EPT (https://ctftime.org/team/119480)  
                **添加日历** : https://ctftime.org/event/2292.ics  
                
    === "*正在进行*"
        === "国内赛事"
            ??? Quote "[浙江警察学院平航杯电子数据取证比赛](https://mp.weixin.qq.com/s/ImWNs003Xsh-lruhC_addQ)"  
                **比赛名称** : [浙江警察学院平航杯电子数据取证比赛](https://mp.weixin.qq.com/s/ImWNs003Xsh-lruhC_addQ)  
                **比赛类型** : 团队赛|1-3人  
                **报名时间** : 2024年04月05日 12:00 - 2024年04月15日 12:00  
                **比赛时间** : 2024年04月20日 14:00 - 2024年04月20日 18:00  
                **其他说明** : QQ群：810961465  
                
            ??? Quote "[GEEKCON 2024 国际站AVSS挑战赛](https://mp.weixin.qq.com/s/iA1PQ9ExwVlRN_iOB7INAg)"  
                **比赛名称** : [GEEKCON 2024 国际站AVSS挑战赛](https://mp.weixin.qq.com/s/iA1PQ9ExwVlRN_iOB7INAg)  
                **比赛类型** : 团队赛  
                **报名时间** : 2024年4月15日 00:00 - 2024年4月20日 10:00  
                **比赛时间** : 2024年4月20日 10:00 - 2024年4月22日 10:00  
                **其他说明** : https://discord.gg/dWvBrfwAmF  
                
            ??? Quote "[D^3CTF2024](https://d3c.tf/)"  
                **比赛名称** : [D^3CTF2024](https://d3c.tf/)  
                **比赛类型** : 团队赛 | Jeopardy  
                **报名时间** : 2024年04月07日 09:00 - 2024年04月19日 20:00  
                **比赛时间** : 2024年04月19日 20:00 - 2024年04月21日 20:00  
                **其他说明** : QQ群：317828357  
                
            ??? Quote "[第一届“帕鲁杯”CTF应急响应挑战赛](https://paluctf.runctf.cn/)"  
                **比赛名称** : [第一届“帕鲁杯”CTF应急响应挑战赛](https://paluctf.runctf.cn/)  
                **比赛类型** : 团体赛1-4人  
                **报名时间** : 2024年04月16日 08:00 - 2024年04月19日 08:00  
                **比赛时间** : 2024年04月19日 08:00 - 2024年04月21日 19:00  
                **其他说明** : QQ群：710672599  
                
            ??? Quote "[XYCTF高校新生联合赛 2024](https://www.xyctf.top/)"  
                **比赛名称** : [XYCTF高校新生联合赛 2024](https://www.xyctf.top/)  
                **比赛类型** : 团队赛 | 1-3人  
                **报名时间** : 2024年03月05日 10:00 - 2024年04月01日 09:00  
                **比赛时间** : 2024年04月01日 10:00 - 2024年05月01日 10:00  
                **其他说明** : 赛事群：798794707  
                
        === "国外赛事"
            ??? Quote "[Sydbox CTF: read /etc/CTF](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)"  
                [![](https://ctftime.org){ width="200" align=left }](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)  
                **比赛名称** : [Sydbox CTF: read /etc/CTF](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-16 22:26:32 - 2024-11-16 22:26:32 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Exherbo GNU/Linux (https://ctftime.org/team/275214)  
                **添加日历** : https://ctftime.org/event/2178.ics  
                
            ??? Quote "[SpartanCTF 2024](https://spartan.ctfd.io/)"  
                [![](https://ctftime.org/media/events/zdc_emblem.png){ width="200" align=left }](https://spartan.ctfd.io/)  
                **比赛名称** : [SpartanCTF 2024](https://spartan.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-18 00:00:00 - 2024-04-22 13:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Zero Day Club (https://ctftime.org/team/286318)  
                **添加日历** : https://ctftime.org/event/2313.ics  
                
            ??? Quote "[CTF@CIT 2024](https://ctf.cyber-cit.club/)"  
                [![](https://ctftime.org/media/events/CTF-CIT-ctftime.png){ width="200" align=left }](https://ctf.cyber-cit.club/)  
                **比赛名称** : [CTF@CIT 2024](https://ctf.cyber-cit.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-20 05:00:00 - 2024-04-22 03:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : HACK@CIT (https://ctftime.org/team/287896)  
                **添加日历** : https://ctftime.org/event/2339.ics  
                
            ??? Quote "[UMassCTF 2024](https://ctf.umasscybersec.org/)"  
                [![](https://ctftime.org/media/events/CTF_LOGO_20240401_190034_0000.png){ width="200" align=left }](https://ctf.umasscybersec.org/)  
                **比赛名称** : [UMassCTF 2024](https://ctf.umasscybersec.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-20 06:00:00 - 2024-04-22 06:00:00 UTC+8  
                **比赛权重** : 43.10  
                **赛事主办** : SavedByTheShell (https://ctftime.org/team/78233)  
                **添加日历** : https://ctftime.org/event/2287.ics  
                
            ??? Quote "[CPCTF 2024](https://cpctf.space/)"  
                [![](https://ctftime.org/media/events/624f1650cfdb45fb857a62b9304d4a1c.png){ width="200" align=left }](https://cpctf.space/)  
                **比赛名称** : [CPCTF 2024](https://cpctf.space/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-20 09:00:00 - 2024-04-21 15:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : traP (https://ctftime.org/team/62510)  
                **添加日历** : https://ctftime.org/event/2338.ics  
                
            ??? Quote "[AVSS Contest 2024](https://avss.geekcon.top/)"  
                [![](https://ctftime.org/media/events/AVSS.png){ width="200" align=left }](https://avss.geekcon.top/)  
                **比赛名称** : [AVSS Contest 2024](https://avss.geekcon.top/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-20 10:00:00 - 2024-04-22 10:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : GEEKCON (https://ctftime.org/team/255059)  
                **添加日历** : https://ctftime.org/event/2335.ics  
                
            ??? Quote "[Grey Cat The Flag 2024 Qualifiers](https://ctf.nusgreyhats.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.nusgreyhats.org/)  
                **比赛名称** : [Grey Cat The Flag 2024 Qualifiers](https://ctf.nusgreyhats.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-20 12:00:00 - 2024-04-21 12:00:00 UTC+8  
                **比赛权重** : 22.46  
                **赛事主办** : NUSGreyhats (https://ctftime.org/team/16740)  
                **添加日历** : https://ctftime.org/event/2242.ics  
                
            ??? Quote "[Nexus Elites CTF](https://nexusctf.ycfteam.in/)"  
                [![](https://ctftime.org/media/events/CTF_logo.jpg){ width="200" align=left }](https://nexusctf.ycfteam.in/)  
                **比赛名称** : [Nexus Elites CTF](https://nexusctf.ycfteam.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-20 12:00:00 - 2024-04-21 12:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : YCF (https://ctftime.org/team/179685)  
                **添加日历** : https://ctftime.org/event/2331.ics  
                
    === "*已经结束*"
        === "国内赛事"
            ??? Quote "[第四届红明谷杯（初赛）](https://www.sm.gov.cn/inc/hgbm/)"  
                **比赛名称** : [第四届红明谷杯（初赛）](https://www.sm.gov.cn/inc/hgbm/)  
                **比赛类型** : 团队赛 | 1-3 人  
                **报名时间** : 2024年03月11日 00:00 - 2024年03月31日 00:00  
                **比赛时间** : 2024年04月03日 09:00 - 2024年04月03日 18:00  
                **其他说明** : 赛事交流QQ群：458469559 ；主办单位：数字中国建设峰会组委会 承办单位：福建省数字福建建设领导小组办公室 三明市人民政府  
                
            ??? Quote "[Round#20 Basic WEB个人专场](https://nssctf.cn/contest)"  
                **比赛名称** : [Round#20 Basic WEB个人专场](https://nssctf.cn/contest)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年03月25日 00:00 - 2024年03月30日 13:20  
                **比赛时间** : 2024年03月30日 13:30 - 2024年03月30日 17:30  
                **其他说明** : QQ群：521330139  
                
            ??? Quote "[aliyunCTF2024](https://www.aliyunctf.com/)"  
                **比赛名称** : [aliyunCTF2024](https://www.aliyunctf.com/)  
                **比赛类型** : 团队赛 | 人数暂定  
                **报名时间** : 2024年03月10日 10:00 - 2024年03月23日 09:00  
                **比赛时间** : 2024年03月23日 10:00 - 2024年03月24日 22:00  
                **其他说明** : 赛事官方钉钉群 28800019603  
                
            ??? Quote "[NKCTF2024](https://n0wayback.com/nkctf2024.html)"  
                **比赛名称** : [NKCTF2024](https://n0wayback.com/nkctf2024.html)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年03月10日 10:00 - 2024年03月22日 18:00  
                **比赛时间** : 2024年03月22日 19:00 - 2024年03月23日 19:00  
                **其他说明** : QQ群：630246091  
                
            ??? Quote "[DubheCTF 2024](https://adworld.xctf.org.cn/contest/assess?hash=94938be6-ce42-11ee-ab28-000c29bc20bf)"  
                **比赛名称** : [DubheCTF 2024](https://adworld.xctf.org.cn/contest/assess?hash=94938be6-ce42-11ee-ab28-000c29bc20bf)  
                **比赛类型** : 团队赛 | 1-n  
                **报名时间** : 2024年03月01日 09:00 - 2024年03月16日 08:00  
                **比赛时间** : 2024年03月16日 09:00 - 2024年03月18日 09:00  
                **其他说明** : Discord: https://discord.gg/hq4m3KrVfG QQ群：512066352 本届DubheCTF2024由XCTF联赛的合作单位天枢Dubhe战队组织，由赛宁网安提供技术支持。作为第八届XCTF国际联赛的分站赛，本次比赛将采用在线网络安全夺旗挑战赛的形式，面向全球开放。 此次比赛冠军队伍将直接晋级第八届XCTF总决赛（总决赛具体地点待定，将在确定后通知获得资格的国际和国内队伍）。其他参赛的队伍也将获得积分，来竞争XCTF总决赛的其他席位。  
                
            ??? Quote "[2024第一届VCTF纳新赛](https://ctf.venomsec.com)"  
                **比赛名称** : [2024第一届VCTF纳新赛](https://ctf.venomsec.com)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年03月04日 8:00 - 2024年03月16日 8:00  
                **比赛时间** : 2024年03月16日 8:00 - 2024年03月16日 20:00  
                **其他说明** : 比赛QQ群: 748783131  
                
            ??? Quote "[NSSCTF Round19 密码专项赛](https://www.nssctf.cn/contest)"  
                **比赛名称** : [NSSCTF Round19 密码专项赛](https://www.nssctf.cn/contest)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年03月16日 13:30 - 2024年03月16日 13:30  
                **比赛时间** : 2024年03月16日 13:30 - 2024年03月16日 17:00  
                **其他说明** : QQ群：521330139  
                
            ??? Quote "[第一届“长城杯”信息安全铁人三项赛初赛](http://ccb.itsec.gov.cn/)"  
                **比赛名称** : [第一届“长城杯”信息安全铁人三项赛初赛](http://ccb.itsec.gov.cn/)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2023年12月21日 00:00 - 2024年02月23日 18:00  
                **比赛时间** : 2024年03月10日 09:00 - 2024年03月12日 18:00  
                **其他说明** : 比赛时间2024年3月 未定  
                
            ??? Quote "[青少年CTF擂台挑战赛 2024 #Round 1](https://www.qsnctf.com/#/main/race-center/race-guide?id=11)"  
                **比赛名称** : [青少年CTF擂台挑战赛 2024 #Round 1](https://www.qsnctf.com/#/main/race-center/race-guide?id=11)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年02月05日 00:00 - 2024年02月28日 22:00  
                **比赛时间** : 2024年02月29日 09:00 - 2024年03月01日 22:00  
                **其他说明** : QQ 群号：820016571  
                
            ??? Quote "[HGAME2024网络攻防大赛](https://hgame.vidar.club)"  
                **比赛名称** : [HGAME2024网络攻防大赛](https://hgame.vidar.club)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年01月20日 20:00 - 2024年02月05日 20:00  
                **比赛时间** : 2024年01月29日 20:00 - 2024年02月27日 20:00  
                **其他说明** : QQ群：134591168   适合新手参加  
                
        === "国外赛事"
            ??? Quote "[Incognito 5.0](https://ictf5.ninja/)"  
                [![](https://ctftime.org/media/events/lo.png){ width="200" align=left }](https://ictf5.ninja/)  
                **比赛名称** : [Incognito 5.0](https://ictf5.ninja/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-16 18:00:00 - 2024-04-17 06:00:00 UTC+8  
                **比赛权重** : 21.95  
                **赛事主办** : Byt3Scr4pp3rs (https://ctftime.org/team/57772)  
                **添加日历** : https://ctftime.org/event/2316.ics  
                
            ??? Quote "[Wayne State University - CTF24](https://waynestateuniversity-ctf24.ctfd.io/)"  
                [![](https://ctftime.org/media/events/WSUCyberDefenseClub_1.jpg){ width="200" align=left }](https://waynestateuniversity-ctf24.ctfd.io/)  
                **比赛名称** : [Wayne State University - CTF24](https://waynestateuniversity-ctf24.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-13 21:00:00 - 2024-04-14 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : WayneStateCyber (https://ctftime.org/team/135263)  
                **添加日历** : https://ctftime.org/event/2337.ics  
                
            ??? Quote "[CybHackCTF 2024 Spring](https://event.kibhackctf.ru/)"  
                [![](https://ctftime.org/media/events/logo_98.png){ width="200" align=left }](https://event.kibhackctf.ru/)  
                **比赛名称** : [CybHackCTF 2024 Spring](https://event.kibhackctf.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-13 17:00:00 - 2024-04-14 17:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : CybHackCTF (https://ctftime.org/team/278998)  
                **添加日历** : https://ctftime.org/event/2344.ics  
                
            ??? Quote "[b01lers CTF 2024](https://b01lersc.tf/)"  
                [![](https://ctftime.org/media/events/b01lers-griffen_1.png){ width="200" align=left }](https://b01lersc.tf/)  
                **比赛名称** : [b01lers CTF 2024](https://b01lersc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-13 07:00:00 - 2024-04-15 07:00:00 UTC+8  
                **比赛权重** : 30.80  
                **赛事主办** : b01lers (https://ctftime.org/team/11464)  
                **添加日历** : https://ctftime.org/event/2250.ics  
                
            ??? Quote "[Space Heroes 2024](https://spaceheroes.ctfd.io/)"  
                [![](https://ctftime.org/media/events/moon.png){ width="200" align=left }](https://spaceheroes.ctfd.io/)  
                **比赛名称** : [Space Heroes 2024](https://spaceheroes.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-13 06:00:00 - 2024-04-15 06:00:00 UTC+8  
                **比赛权重** : 24.50  
                **赛事主办** : FITSEC (https://ctftime.org/team/65296)  
                **添加日历** : https://ctftime.org/event/2254.ics  
                
            ??? Quote "[PlaidCTF 2024](https://plaidctf.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://plaidctf.com/)  
                **比赛名称** : [PlaidCTF 2024](https://plaidctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-13 05:00:00 - 2024-04-15 05:00:00 UTC+8  
                **比赛权重** : 95.19  
                **赛事主办** : Plaid Parliament of Pwning (https://ctftime.org/team/284)  
                **添加日历** : https://ctftime.org/event/2245.ics  
                
            ??? Quote "[ShunyaCTF Aarambha](https://shunya.ctf.eng.run/)"  
                [![](https://ctftime.org/media/events/shunyaLogo.png){ width="200" align=left }](https://shunya.ctf.eng.run/)  
                **比赛名称** : [ShunyaCTF Aarambha](https://shunya.ctf.eng.run/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-13 00:30:00 - 2024-04-14 12:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : nCreeps (https://ctftime.org/team/203035)  
                **添加日历** : https://ctftime.org/event/2336.ics  
                
            ??? Quote "[HackPack CTF 2024 - LLM edition](https://hackpack.club/ctf2024/)"  
                [![](https://ctftime.org/media/events/Screenshot_2024-04-05_at_10.29.44.png){ width="200" align=left }](https://hackpack.club/ctf2024/)  
                **比赛名称** : [HackPack CTF 2024 - LLM edition](https://hackpack.club/ctf2024/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-13 00:00:00 - 2024-04-13 23:59:59 UTC+8  
                **比赛权重** : 32.71  
                **赛事主办** : hackpack (https://ctftime.org/team/25905)  
                **添加日历** : https://ctftime.org/event/2333.ics  
                
            ??? Quote "[24@CTF](https://ctf.polycyber.io/)"  
                [![](https://ctftime.org/media/events/Logo_24CTF_2024_1.png){ width="200" align=left }](https://ctf.polycyber.io/)  
                **比赛名称** : [24@CTF](https://ctf.polycyber.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 23:30:00 - 2024-04-08 00:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : PolyCyber (https://ctftime.org/team/212241)  
                **添加日历** : https://ctftime.org/event/2310.ics  
                
            ??? Quote "[THCon 2k24 CTF](http://ctf.thcon.party/)"  
                [![](https://ctftime.org/media/events/logo-desktop.png){ width="200" align=left }](http://ctf.thcon.party/)  
                **比赛名称** : [THCon 2k24 CTF](http://ctf.thcon.party/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 18:00:00 - 2024-04-08 18:00:00 UTC+8  
                **比赛权重** : 23.65  
                **赛事主办** : pony7 (https://ctftime.org/team/20769)  
                **添加日历** : https://ctftime.org/event/2269.ics  
                
            ??? Quote "[DamCTF 2024](https://damctf.xyz/)"  
                [![](https://ctftime.org/media/events/DAM-CTF-2020-Icon_1.png){ width="200" align=left }](https://damctf.xyz/)  
                **比赛名称** : [DamCTF 2024](https://damctf.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 08:00:00 - 2024-04-08 08:00:00 UTC+8  
                **比赛权重** : 47.75  
                **赛事主办** : OSUSEC (https://ctftime.org/team/12858)  
                **添加日历** : https://ctftime.org/event/2262.ics  
                
            ??? Quote "[SwampCTF 2024](https://swampctf.com/)"  
                [![](https://ctftime.org/media/events/swampctf.png){ width="200" align=left }](https://swampctf.com/)  
                **比赛名称** : [SwampCTF 2024](https://swampctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 06:00:00 - 2024-04-08 06:00:00 UTC+8  
                **比赛权重** : 41.41  
                **赛事主办** : Kernel Sanders (https://ctftime.org/team/397)  
                **添加日历** : https://ctftime.org/event/2138.ics  
                
            ??? Quote "[TAMUctf 2024](http://tamuctf.com/)"  
                [![](https://ctftime.org/media/events/TAMUCTF_cmaroon_2.png){ width="200" align=left }](http://tamuctf.com/)  
                **比赛名称** : [TAMUctf 2024](http://tamuctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 06:00:00 - 2024-04-08 06:00:00 UTC+8  
                **比赛权重** : 48.25  
                **赛事主办** : TAMUctf (https://ctftime.org/team/37721)  
                **添加日历** : https://ctftime.org/event/2238.ics  
                
            ??? Quote "[GEEK CTF 2024](https://geekctf.geekcon.top/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://geekctf.geekcon.top/)  
                **比赛名称** : [GEEK CTF 2024](https://geekctf.geekcon.top/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 04:00:00 - 2024-04-15 04:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : GEEKCON (https://ctftime.org/team/255059)  
                **添加日历** : https://ctftime.org/event/2332.ics  
                
            ??? Quote "[RITSEC CTF 2024](https://ctfd.ritsec.club/)"  
                [![](https://ctftime.org/media/events/Ritsec-CTF-2024-r1.jpg){ width="200" align=left }](https://ctfd.ritsec.club/)  
                **比赛名称** : [RITSEC CTF 2024](https://ctfd.ritsec.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-06 00:00:00 - 2024-04-08 00:00:00 UTC+8  
                **比赛权重** : 26.98  
                **赛事主办** : Contagion (https://ctftime.org/team/152691)  
                **添加日历** : https://ctftime.org/event/2291.ics  
                
            ??? Quote "[AmateursCTF 2024](https://ctf.amateurs.team/)"  
                [![](https://ctftime.org/media/events/2d6bd602-ecce-47e6-8f53-b352af222287.915ceb9574bb9759b4dd16bf8a744d25_1.jpeg){ width="200" align=left }](https://ctf.amateurs.team/)  
                **比赛名称** : [AmateursCTF 2024](https://ctf.amateurs.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-05 22:00:00 - 2024-04-10 11:00:00 UTC+8  
                **比赛权重** : 24.54  
                **赛事主办** : les amateurs (https://ctftime.org/team/166729)  
                **添加日历** : https://ctftime.org/event/2226.ics  
                
            ??? Quote "[BelkaCTF #6](https://belkasoft.com/belkactf6/)"  
                [![](https://ctftime.org/media/events/belkactf6_square.jpg){ width="200" align=left }](https://belkasoft.com/belkactf6/)  
                **比赛名称** : [BelkaCTF #6](https://belkasoft.com/belkactf6/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-05 21:00:00 - 2024-04-07 21:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : TODO: security (https://ctftime.org/team/288184)  
                **添加日历** : https://ctftime.org/event/2326.ics  
                
            ??? Quote "[GREP CTF 2.0 - Apogee '24](http://grep.ctf.eng.run/)"  
                [![](https://ctftime.org/media/events/20a7c45b52453060b168055f47ce5352.png){ width="200" align=left }](http://grep.ctf.eng.run/)  
                **比赛名称** : [GREP CTF 2.0 - Apogee '24](http://grep.ctf.eng.run/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-05 20:00:00 - 2024-04-07 08:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BitRaiders (https://ctftime.org/team/286592)  
                **添加日历** : https://ctftime.org/event/2334.ics  
                
            ??? Quote "[UNbreakable International 2024 - Team Phase](https://unr24t-international.cyber-edu.co/)"  
                [![](https://ctftime.org/media/events/g5hqjcGuxmbcMSZ9.png){ width="200" align=left }](https://unr24t-international.cyber-edu.co/)  
                **比赛名称** : [UNbreakable International 2024 - Team Phase](https://unr24t-international.cyber-edu.co/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-05 18:00:00 - 2024-04-07 18:00:00 UTC+8  
                **比赛权重** : 24.83  
                **赛事主办** : bitsentinel (https://ctftime.org/team/280005)  
                **添加日历** : https://ctftime.org/event/2297.ics  
                
            ??? Quote "[HTBLuVA Villach CTF 2024](https://tophack.at/)"  
                [![](https://ctftime.org/media/events/Logos_TopHack-RED-Front.png){ width="200" align=left }](https://tophack.at/)  
                **比赛名称** : [HTBLuVA Villach CTF 2024](https://tophack.at/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-05 17:00:00 - 2024-04-05 23:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : P01s0n3d_Fl4g (https://ctftime.org/team/273774)  
                **添加日历** : https://ctftime.org/event/2317.ics  
                
            ??? Quote "[VolgaCTF 2024 Qualifier](https://q.2024.volgactf.ru/)"  
                [![](https://ctftime.org/media/events/logo-social-yellow_14.png){ width="200" align=left }](https://q.2024.volgactf.ru/)  
                **比赛名称** : [VolgaCTF 2024 Qualifier](https://q.2024.volgactf.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-30 23:00:00 - 2024-03-31 23:00:00 UTC+8  
                **比赛权重** : 35.91  
                **赛事主办** : VolgaCTF.org (https://ctftime.org/team/27094)  
                **添加日历** : https://ctftime.org/event/2200.ics  
                
            ??? Quote "[SummitCTF 2024](https://summitctf.org/)"  
                [![](https://ctftime.org/media/events/default_background_removed.png){ width="200" align=left }](https://summitctf.org/)  
                **比赛名称** : [SummitCTF 2024](https://summitctf.org/)  
                **比赛形式** : Hack quest  
                **比赛时间** : 2024-03-30 21:00:00 - 2024-04-01 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CyberVT (https://ctftime.org/team/173872)  
                **添加日历** : https://ctftime.org/event/2237.ics  
                
            ??? Quote "[CursedCTF 2024 Quals](https://cursedc.tf/)"  
                [![](https://ctftime.org/media/events/Screenshot_2024-01-23_at_11.45.46_AM.png){ width="200" align=left }](https://cursedc.tf/)  
                **比赛名称** : [CursedCTF 2024 Quals](https://cursedc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-30 08:00:00 - 2024-04-01 08:00:00 UTC+8  
                **比赛权重** : 19.50  
                **赛事主办** : cursed (https://ctftime.org/team/199492)  
                **添加日历** : https://ctftime.org/event/2239.ics  
                
            ??? Quote "[UTCTF 2024](https://isss.io/utctf)"  
                [![](https://ctftime.org/media/events/UTCTF2024.png){ width="200" align=left }](https://isss.io/utctf)  
                **比赛名称** : [UTCTF 2024](https://isss.io/utctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-30 07:00:00 - 2024-04-01 07:00:00 UTC+8  
                **比赛权重** : 48.00  
                **赛事主办** : isss (https://ctftime.org/team/69010)  
                **添加日历** : https://ctftime.org/event/2302.ics  
                
            ??? Quote "[HACKFEST'8 QUALS](https://ctf-quals-8.hackfest.tn/)"  
                [![](https://ctftime.org/media/events/HACKFEST_WHITE.png){ width="200" align=left }](https://ctf-quals-8.hackfest.tn/)  
                **比赛名称** : [HACKFEST'8 QUALS](https://ctf-quals-8.hackfest.tn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-24 03:00:00 - 2024-03-24 22:00:00 UTC+8  
                **比赛权重** : 20.73  
                **赛事主办** : HACKFEST TEAM (https://ctftime.org/team/281742)  
                **添加日历** : https://ctftime.org/event/2278.ics  
                
            ??? Quote "[JerseyCTF IV](https://ctf.jerseyctf.com/)"  
                [![](https://ctftime.org/media/events/Asset_39.png){ width="200" align=left }](https://ctf.jerseyctf.com/)  
                **比赛名称** : [JerseyCTF IV](https://ctf.jerseyctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-24 00:00:00 - 2024-03-25 00:00:00 UTC+8  
                **比赛权重** : 21.26  
                **赛事主办** : Highlander Hackers (https://ctftime.org/team/173925)  
                **添加日历** : https://ctftime.org/event/2230.ics  
                
            ??? Quote "[Texas Security Awareness Week 2024](https://csi.utdallas.edu/events/texsaw-2024/)"  
                [![](https://ctftime.org/media/events/texsaw24.png){ width="200" align=left }](https://csi.utdallas.edu/events/texsaw-2024/)  
                **比赛名称** : [Texas Security Awareness Week 2024](https://csi.utdallas.edu/events/texsaw-2024/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-23 23:00:00 - 2024-03-25 06:00:00 UTC+8  
                **比赛权重** : 23.89  
                **赛事主办** : UTD TexSAW (https://ctftime.org/team/220408)  
                **添加日历** : https://ctftime.org/event/2281.ics  
                
            ??? Quote "[Undutmaning 2024](https://undutmaning.se/)"  
                [![](https://ctftime.org/media/events/LOGO_DISCORD.png){ width="200" align=left }](https://undutmaning.se/)  
                **比赛名称** : [Undutmaning 2024](https://undutmaning.se/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-23 20:00:00 - 2024-03-24 04:00:00 UTC+8  
                **比赛权重** : 24.50  
                **赛事主办** : Undutmaning (https://ctftime.org/team/212504)  
                **添加日历** : https://ctftime.org/event/2283.ics  
                
            ??? Quote "[ZeroDays CTF](https://zerodays.ie/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://zerodays.ie/)  
                **比赛名称** : [ZeroDays CTF](https://zerodays.ie/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-23 18:00:00 - 2024-03-24 01:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Ireland without the RE (https://ctftime.org/team/179144)  
                **添加日历** : https://ctftime.org/event/2196.ics  
                
            ??? Quote "[LINE CTF 2024](https://linectf.me/)"  
                [![](https://ctftime.org/media/events/Image_1.jpeg){ width="200" align=left }](https://linectf.me/)  
                **比赛名称** : [LINE CTF 2024](https://linectf.me/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-23 08:00:00 - 2024-03-24 08:00:00 UTC+8  
                **比赛权重** : 49.10  
                **赛事主办** : LINE CTF (https://ctftime.org/team/144094)  
                **添加日历** : https://ctftime.org/event/2119.ics  
                
            ??? Quote "[JUST CTF 2024 Quals](https://www.facebook.com/HackerSpace.JUST/)"  
                [![](https://ctftime.org/media/events/logo_12.jpg){ width="200" align=left }](https://www.facebook.com/HackerSpace.JUST/)  
                **比赛名称** : [JUST CTF 2024 Quals](https://www.facebook.com/HackerSpace.JUST/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-23 02:00:00 - 2024-03-23 10:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HackerSpace_JUST (https://ctftime.org/team/144626)  
                **添加日历** : https://ctftime.org/event/2307.ics  
                
            ??? Quote "[UNbreakable International 2024 - Individual Phase](https://unr24i-international.cyber-edu.co/)"  
                [![](https://ctftime.org/media/events/g5hqjcGuxmbcMSZ9_1.png){ width="200" align=left }](https://unr24i-international.cyber-edu.co/)  
                **比赛名称** : [UNbreakable International 2024 - Individual Phase](https://unr24i-international.cyber-edu.co/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-22 18:00:00 - 2024-03-24 18:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : bitsentinel (https://ctftime.org/team/280005)  
                **添加日历** : https://ctftime.org/event/2298.ics  
                
            ??? Quote "[ApoorvCTF](https://unstop.com/hackathons/capture-the-flag-apoorv-2024-iiit-kottayam-925229)"  
                [![](https://ctftime.org){ width="200" align=left }](https://unstop.com/hackathons/capture-the-flag-apoorv-2024-iiit-kottayam-925229)  
                **比赛名称** : [ApoorvCTF](https://unstop.com/hackathons/capture-the-flag-apoorv-2024-iiit-kottayam-925229)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-22 14:30:00 - 2024-03-24 14:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : r3d_kn1ght5 (https://ctftime.org/team/212248)  
                **添加日历** : https://ctftime.org/event/2312.ics  
                
            ??? Quote "[openECSC 2024 - Round 1](https://open.ecsc2024.it/)"  
                [![](https://ctftime.org/media/events/openECSC.png){ width="200" align=left }](https://open.ecsc2024.it/)  
                **比赛名称** : [openECSC 2024 - Round 1](https://open.ecsc2024.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-18 18:00:00 - 2024-03-25 06:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : ECSC2024 (https://ctftime.org/team/283828)  
                **添加日历** : https://ctftime.org/event/2305.ics  
                
            ??? Quote "[Snowfort 2024](https://snowfort2024.cyberscoring.ca/)"  
                [![](https://ctftime.org/media/events/logo_2024.png){ width="200" align=left }](https://snowfort2024.cyberscoring.ca/)  
                **比赛名称** : [Snowfort 2024](https://snowfort2024.cyberscoring.ca/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-03-16 23:00:00 - 2024-03-17 07:00:00 UTC+8  
                **比赛权重** : 21.25  
                **赛事主办** : Shell We Hack? (https://ctftime.org/team/220236)  
                **添加日历** : https://ctftime.org/event/2260.ics  
                
            ??? Quote "[TuxCTF 2024](https://www.instagram.com/tuxpwners/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://www.instagram.com/tuxpwners/)  
                **比赛名称** : [TuxCTF 2024](https://www.instagram.com/tuxpwners/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-16 17:00:00 - 2024-03-16 22:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : TuxPwners (https://ctftime.org/team/274660)  
                **添加日历** : https://ctftime.org/event/2329.ics  
                
            ??? Quote "[XCTF-DubheCTF 2024](https://dubhectf2024.xctf.org.cn/)"  
                [![](https://ctftime.org/media/events/41eff818a403035f165633e8e89b6111.png){ width="200" align=left }](https://dubhectf2024.xctf.org.cn/)  
                **比赛名称** : [XCTF-DubheCTF 2024](https://dubhectf2024.xctf.org.cn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-16 09:00:00 - 2024-03-18 09:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : 天枢 Dubhe (https://ctftime.org/team/281183)  
                **添加日历** : https://ctftime.org/event/2279.ics  
                
            ??? Quote "[Ethernaut CTF 2024](https://ctf.openzeppelin.com/)"  
                [![](https://ctftime.org/media/events/500x500.png){ width="200" align=left }](https://ctf.openzeppelin.com/)  
                **比赛名称** : [Ethernaut CTF 2024](https://ctf.openzeppelin.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-16 08:00:01 - 2024-03-18 08:00:01 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : OpenZeppelin (https://ctftime.org/team/285917)  
                **添加日历** : https://ctftime.org/event/2314.ics  
                
            ??? Quote "[WolvCTF 2024](https://wolvctf.io/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://wolvctf.io/)  
                **比赛名称** : [WolvCTF 2024](https://wolvctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-16 07:00:00 - 2024-03-18 07:00:00 UTC+8  
                **比赛权重** : 35.25  
                **赛事主办** : wolvsec (https://ctftime.org/team/83621)  
                **添加日历** : https://ctftime.org/event/2240.ics  
                
            ??? Quote "[1753CTF 2024](https://1753ctf.com/)"  
                [![](https://ctftime.org/media/events/badge.png){ width="200" align=left }](https://1753ctf.com/)  
                **比赛名称** : [1753CTF 2024](https://1753ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-16 05:00:00 - 2024-03-17 05:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : 1753c (https://ctftime.org/team/178287)  
                **添加日历** : https://ctftime.org/event/2234.ics  
                
            ??? Quote "[KalmarCTF 2024](http://KalmarC.TF/)"  
                [![](https://ctftime.org/media/events/logo_square_756x756.png){ width="200" align=left }](http://KalmarC.TF/)  
                **比赛名称** : [KalmarCTF 2024](http://KalmarC.TF/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-16 01:00:00 - 2024-03-18 01:00:00 UTC+8  
                **比赛权重** : 24.21  
                **赛事主办** : kalmarunionen (https://ctftime.org/team/114856)  
                **添加日历** : https://ctftime.org/event/2227.ics  
                
            ??? Quote "[Nullcon Berlin HackIM 2024 CTF](https://ctf.nullcon.net/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.nullcon.net/)  
                **比赛名称** : [Nullcon Berlin HackIM 2024 CTF](https://ctf.nullcon.net/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-14 17:30:00 - 2024-03-15 19:00:00 UTC+8  
                **比赛权重** : 20.00  
                **赛事主办** : ENOFLAG (https://ctftime.org/team/1438)  
                **添加日历** : https://ctftime.org/event/2264.ics  
                
            ??? Quote "[Cyber Apocalypse 2024: Hacker Royale](https://ctf.hackthebox.com/event/details/cyber-apocalypse-2024-hacker-royale-1386)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hackthebox.com/event/details/cyber-apocalypse-2024-hacker-royale-1386)  
                **比赛名称** : [Cyber Apocalypse 2024: Hacker Royale](https://ctf.hackthebox.com/event/details/cyber-apocalypse-2024-hacker-royale-1386)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-09 21:00:00 - 2024-03-13 20:59:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Hack The Box (https://ctftime.org/team/136056)  
                **添加日历** : https://ctftime.org/event/2255.ics  
                
            ??? Quote "[vikeCTF 2024](https://ctf.vikesec.ca/)"  
                [![](https://ctftime.org/media/events/vikesec.png){ width="200" align=left }](https://ctf.vikesec.ca/)  
                **比赛名称** : [vikeCTF 2024](https://ctf.vikesec.ca/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-09 08:00:00 - 2024-03-11 08:00:00 UTC+8  
                **比赛权重** : 23.64  
                **赛事主办** : PencilTesters (https://ctftime.org/team/178288)  
                **添加日历** : https://ctftime.org/event/2263.ics  
                
            ??? Quote "[WxMCTF 2024](https://ctf.mcpt.ca/contest/wxmctf)"  
                [![](https://ctftime.org/media/events/Logo_thing_1.png){ width="200" align=left }](https://ctf.mcpt.ca/contest/wxmctf)  
                **比赛名称** : [WxMCTF 2024](https://ctf.mcpt.ca/contest/wxmctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-09 08:00:00 - 2024-03-11 07:00:00 UTC+8  
                **比赛权重** : 23.59  
                **赛事主办** : X Series CTF (https://ctftime.org/team/211390)  
                **添加日历** : https://ctftime.org/event/2179.ics  
                
            ??? Quote "[HSCCTF 2024](https://race.hscsec.cn/home)"  
                [![](https://ctftime.org/media/events/ZLJS-G.png){ width="200" align=left }](https://race.hscsec.cn/home)  
                **比赛名称** : [HSCCTF 2024](https://race.hscsec.cn/home)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-09 05:00:00 - 2024-03-11 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : 红客突击队 (https://ctftime.org/team/119338)  
                **添加日历** : https://ctftime.org/event/2290.ics  
                
            ??? Quote "[HackDay 2024 - Finals](https://www.hackday.fr/)"  
                [![](https://ctftime.org/media/events/CREA_LOGO_Blason_Espion_1.png){ width="200" align=left }](https://www.hackday.fr/)  
                **比赛名称** : [HackDay 2024 - Finals](https://www.hackday.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-09 02:00:00 - 2024-03-10 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : HackDayCTF (https://ctftime.org/team/277562)  
                **添加日历** : https://ctftime.org/event/2267.ics  
                
            ??? Quote "[Shakti CTF](https://ctf.shakticon.com/)"  
                [![](https://ctftime.org/media/events/shaktictf_1_1.png){ width="200" align=left }](https://ctf.shakticon.com/)  
                **比赛名称** : [Shakti CTF](https://ctf.shakticon.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-08 20:30:00 - 2024-03-09 20:30:00 UTC+8  
                **比赛权重** : 24.10  
                **赛事主办** : TeamShakti (https://ctftime.org/team/61083)  
                **添加日历** : https://ctftime.org/event/2268.ics  
                
            ??? Quote "[Pearl CTF](https://play.pearlctf.in/)"  
                [![](https://ctftime.org/media/events/_croppearl_logo_1_of_1.png){ width="200" align=left }](https://play.pearlctf.in/)  
                **比赛名称** : [Pearl CTF](https://play.pearlctf.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-08 20:00:00 - 2024-03-10 07:59:59 UTC+8  
                **比赛权重** : 23.95  
                **赛事主办** : BIT CRIMINALS (https://ctftime.org/team/151727)  
                **添加日历** : https://ctftime.org/event/2231.ics  
                
            ??? Quote "[AthackCTF 2024](https://www.athackctf.com/)"  
                [![](https://ctftime.org/media/events/_hacklogo_v2_720.png){ width="200" align=left }](https://www.athackctf.com/)  
                **比赛名称** : [AthackCTF 2024](https://www.athackctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-02 16:00:00 - 2024-03-04 01:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : athackPrivate (https://ctftime.org/team/278003)  
                **添加日历** : https://ctftime.org/event/2228.ics  
                
            ??? Quote "[GCC CTF 2024](https://gcc-ctf.com/)"  
                [![](https://ctftime.org/media/events/Logo_GCC_White_Font.png){ width="200" align=left }](https://gcc-ctf.com/)  
                **比赛名称** : [GCC CTF 2024](https://gcc-ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-02 04:00:00 - 2024-03-04 04:00:00 UTC+8  
                **比赛权重** : 24.92  
                **赛事主办** : Galette Cidre CTF (https://ctftime.org/team/246488)  
                **添加日历** : https://ctftime.org/event/2251.ics  
                
            ??? Quote "[osu!gaming CTF 2024](https://www.osugaming.lol/)"  
                [![](https://ctftime.org/media/events/unknown_1.png){ width="200" align=left }](https://www.osugaming.lol/)  
                **比赛名称** : [osu!gaming CTF 2024](https://www.osugaming.lol/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-02 01:00:00 - 2024-03-04 01:00:00 UTC+8  
                **比赛权重** : 23.87  
                **赛事主办** : osu!gaming (https://ctftime.org/team/186954)  
                **添加日历** : https://ctftime.org/event/2165.ics  
                
            ??? Quote "[Jeanne d'Hack CTF 2024](https://jeanne-dhack-ctf.univ-rouen.fr/)"  
                [![](https://ctftime.org/media/events/JeannedHackCTF_100_x_100_px1.png){ width="200" align=left }](https://jeanne-dhack-ctf.univ-rouen.fr/)  
                **比赛名称** : [Jeanne d'Hack CTF 2024](https://jeanne-dhack-ctf.univ-rouen.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-01 21:30:00 - 2024-03-03 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Jeanne d'Hack CTF (https://ctftime.org/team/283058)  
                **添加日历** : https://ctftime.org/event/2311.ics  
                
            ??? Quote "[VishwaCTF 2024](https://vishwactf.com/)"  
                [![](https://ctftime.org/media/events/VishwaCTF_3.png){ width="200" align=left }](https://vishwactf.com/)  
                **比赛名称** : [VishwaCTF 2024](https://vishwactf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-03-01 18:30:00 - 2024-03-03 18:29:59 UTC+8  
                **比赛权重** : 33.43  
                **赛事主办** : CyberCellVIIT (https://ctftime.org/team/144677)  
                **添加日历** : https://ctftime.org/event/2272.ics  
                
            ??? Quote "[WEC CTF](https://wecctf.nitk.ac.in/)"  
                [![](https://ctftime.org/media/events/weclogo.png){ width="200" align=left }](https://wecctf.nitk.ac.in/)  
                **比赛名称** : [WEC CTF](https://wecctf.nitk.ac.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-24 20:30:00 - 2024-02-25 20:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Web Club NITK (https://ctftime.org/team/216903)  
                **添加日历** : https://ctftime.org/event/2270.ics  
                
            ??? Quote "[bi0sCTF 2024](https://ctf.bi0s.in/)"  
                [![](https://ctftime.org/media/events/Untitled-removebg-preview_1.png){ width="200" align=left }](https://ctf.bi0s.in/)  
                **比赛名称** : [bi0sCTF 2024](https://ctf.bi0s.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-24 20:00:00 - 2024-02-26 08:00:00 UTC+8  
                **比赛权重** : 79.83  
                **赛事主办** : bi0s (https://ctftime.org/team/662)  
                **添加日历** : https://ctftime.org/event/2117.ics  
                
            ??? Quote "[BraekerCTF](https://github.com/spipm/BraekerCTF_2024_public)"  
                [![](https://ctftime.org/media/events/AI_Robot4.png){ width="200" align=left }](https://github.com/spipm/BraekerCTF_2024_public)  
                **比赛名称** : [BraekerCTF](https://github.com/spipm/BraekerCTF_2024_public)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-23 20:00:00 - 2024-02-25 00:00:00 UTC+8  
                **比赛权重** : 24.70  
                **赛事主办** : Braeker (https://ctftime.org/team/274910)  
                **添加日历** : https://ctftime.org/event/2181.ics  
                
            ??? Quote "[BroncoCTF 2024](http://broncoctf.xyz/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://broncoctf.xyz/)  
                **比赛名称** : [BroncoCTF 2024](http://broncoctf.xyz/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-18 03:00:00 - 2024-02-19 03:00:00 UTC+8  
                **比赛权重** : 23.13  
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
                
            ??? Quote "[Pragyan CTF 2024](https://ctf.pragyan.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.pragyan.org/)  
                **比赛名称** : [Pragyan CTF 2024](https://ctf.pragyan.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-02-16 22:30:00 - 2024-02-17 22:30:00 UTC+8  
                **比赛权重** : 2.80  
                **赛事主办** : Pragyan (https://ctftime.org/team/33867)  
                **添加日历** : https://ctftime.org/event/2266.ics  
                
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
                **比赛权重** : 21.91  
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
                **比赛权重** : 23.33  
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
                **比赛权重** : 24.59  
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
                
            ??? Quote "[HackDay 2024 - Qualifications](https://www.hackday.fr/)"  
                [![](https://ctftime.org/media/events/CREA_LOGO_Blason_Espion.png){ width="200" align=left }](https://www.hackday.fr/)  
                **比赛名称** : [HackDay 2024 - Qualifications](https://www.hackday.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-16 04:00:00 - 2024-01-22 04:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : HackDayCTF (https://ctftime.org/team/277562)  
                **添加日历** : https://ctftime.org/event/2265.ics  
                
            ??? Quote "[UofTCTF 2024](https://ctf.uoftctf.org/)"  
                [![](https://ctftime.org/media/events/ctf_logo_1.png){ width="200" align=left }](https://ctf.uoftctf.org/)  
                **比赛名称** : [UofTCTF 2024](https://ctf.uoftctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-01-14 01:00:00 - 2024-01-15 12:59:00 UTC+8  
                **比赛权重** : 23.81  
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
