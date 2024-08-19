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
        ??? Quote "[2024年“羊城杯”粤港澳大湾区网络安全大赛](https://2024ycb.dasctf.com/compete/compete?matchCode=87659256dbc7485&competeId=268)"  
            **比赛名称** : [2024年“羊城杯”粤港澳大湾区网络安全大赛](https://2024ycb.dasctf.com/compete/compete?matchCode=87659256dbc7485&competeId=268)  
            **比赛类型** : 个人赛|团队赛 1-4人  
            **报名时间** : 2024年08月01日 18:45 - 2024年08月20日 23:59  
            **比赛时间** : 2024年08月27日 09:00 - 2024年08月28日 09:00  
            **其他说明** : QQ群1：1148320638 QQ群2：696494060 | 研究生、本科、高职、相关企业、党政机关及事业单位和港澳特邀  
            
        ??? Quote "[第八届御网杯信息安全大赛](https://www.hncsisc.com/hncsisc/index.html)"  
            **比赛名称** : [第八届御网杯信息安全大赛](https://www.hncsisc.com/hncsisc/index.html)  
            **比赛类型** : 个人赛 and 团体赛|3人  
            **报名时间** : 2024年07月26日 08:00 - 2024年09月20日 18:00  
            **比赛时间** : 2024年09月21日 00:00 - 2024年10月27日 23:59  
            **其他说明** : 更多信息请前往官网https://www.hncsisc.com 的“赛事活动”查看  
            
        ??? Quote "[NepCTF 2024](暂定)"  
            **比赛名称** : [NepCTF 2024](暂定)  
            **比赛类型** : 个人赛  
            **报名时间** : 2024年07月25日 08:00 - 2024年08月22日 23:59  
            **比赛时间** : 2024年08月23日 00:00 - 2024年08月25日 23:59  
            **其他说明** : QQ群: 560946020  
            
        ??? Quote "[2024年辽宁大学研究生网络安全创新实践大赛](https://mp.weixin.qq.com/s?search_click_id=1419197875279398874-1721064257482-5560857333&__biz=MzkwODY4NjEwMA==&mid=2247483898&idx=2&sn=9e98fa0801ff04680dc13785de62ec59&chksm=c1d81e30983ce3afed49948819b79e7332489d251f75003da001e323b575dc6267a3f9b3c7c3&scene=7&subscene=10000&sessionid=1721062624&clicktime=1721064257&enterid=1721064257&ascene=65&fasttmpl_type=0&fasttmpl_fullversion=7295595-zh_CN-zip&fasttmpl_flag=0&realreporttime=1721064257512&devicetype=android-34&version=28002e34&nettype=WIFI&abtest_cookie=AAACAA==&lang=zh_CN&countrycode=CN&exportkey=n_ChQIAhIQcvD8xBlhKOyhNiXR+sSwhxLiAQIE97dBBAEAAAAAALJPGgdGHkcAAAAOpnltbLcz9gKNyK89dVj05OQmnZhmX5QxbgZxJq2kXOv2MdwjaAf3iVTLVGCcQUSG7VlEEpibGRWcgGV1BZpKtLcneOndlVFC2eMkTtAv8YTngrwgPTc44eKAtyGHcw9azAA/Lyju97FKSOW2D6eW7ZlNCG9gFS8WG6AcsPuxVr7PhVh4jtPz7vGomi56weNGB+8NjPr5ChEwlxJP+UN5C5JA5rUMV2rKtdZBeiASZdqEjpQcPvQmFzF6OVw0NHDUJ/bDftCImrDsZKo=&pass_ticket=kVxbyE61cIHqlon9l8MZfpuGMpxcldPEOp9u/xMr3MOyS4E0APheem2kMNVrm4dm&wx_header=3)"  
            **比赛名称** : [2024年辽宁大学研究生网络安全创新实践大赛](https://mp.weixin.qq.com/s?search_click_id=1419197875279398874-1721064257482-5560857333&__biz=MzkwODY4NjEwMA==&mid=2247483898&idx=2&sn=9e98fa0801ff04680dc13785de62ec59&chksm=c1d81e30983ce3afed49948819b79e7332489d251f75003da001e323b575dc6267a3f9b3c7c3&scene=7&subscene=10000&sessionid=1721062624&clicktime=1721064257&enterid=1721064257&ascene=65&fasttmpl_type=0&fasttmpl_fullversion=7295595-zh_CN-zip&fasttmpl_flag=0&realreporttime=1721064257512&devicetype=android-34&version=28002e34&nettype=WIFI&abtest_cookie=AAACAA==&lang=zh_CN&countrycode=CN&exportkey=n_ChQIAhIQcvD8xBlhKOyhNiXR+sSwhxLiAQIE97dBBAEAAAAAALJPGgdGHkcAAAAOpnltbLcz9gKNyK89dVj05OQmnZhmX5QxbgZxJq2kXOv2MdwjaAf3iVTLVGCcQUSG7VlEEpibGRWcgGV1BZpKtLcneOndlVFC2eMkTtAv8YTngrwgPTc44eKAtyGHcw9azAA/Lyju97FKSOW2D6eW7ZlNCG9gFS8WG6AcsPuxVr7PhVh4jtPz7vGomi56weNGB+8NjPr5ChEwlxJP+UN5C5JA5rUMV2rKtdZBeiASZdqEjpQcPvQmFzF6OVw0NHDUJ/bDftCImrDsZKo=&pass_ticket=kVxbyE61cIHqlon9l8MZfpuGMpxcldPEOp9u/xMr3MOyS4E0APheem2kMNVrm4dm&wx_header=3)  
            **比赛类型** : 团队赛|1-4人  
            **报名时间** : 2024年07月15日 18:41 - 2024年08月31日 23:59  
            **比赛时间** : 2024年08月31日 23:59 - 2024年08月31日 23:59  
            **其他说明** : 仅限辽宁大学研究生 | 参赛队伍需同时参加“华为杯”第三届中国研究生网络安全创新大赛  
            
        ??? Quote "[“华为杯”第三届中国研究生网络安全创新大赛](https://cpipc.acge.org.cn//pw/detail/2c9080188fc20569018fe6375eeb2eb2)"  
            **比赛名称** : [“华为杯”第三届中国研究生网络安全创新大赛](https://cpipc.acge.org.cn//pw/detail/2c9080188fc20569018fe6375eeb2eb2)  
            **比赛类型** : 团队赛|1-4人  
            **报名时间** : 2024年05月06日 00:00 - 2024年09月23日 23:59  
            **比赛时间** : 2024年09月25日 00:00 - 2024年09月25日 23:59  
            **其他说明** : QQ群: 794148708|仅限研究生参加  
            
    === "*即将开始*"
        === "国内赛事"
            ??? Quote "[2024年“羊城杯”粤港澳大湾区网络安全大赛](https://2024ycb.dasctf.com/compete/compete?matchCode=87659256dbc7485&competeId=268)"  
                **比赛名称** : [2024年“羊城杯”粤港澳大湾区网络安全大赛](https://2024ycb.dasctf.com/compete/compete?matchCode=87659256dbc7485&competeId=268)  
                **比赛类型** : 个人赛|团队赛 1-4人  
                **报名时间** : 2024年08月01日 18:45 - 2024年08月20日 23:59  
                **比赛时间** : 2024年08月27日 09:00 - 2024年08月28日 09:00  
                **其他说明** : QQ群1：1148320638 QQ群2：696494060 | 研究生、本科、高职、相关企业、党政机关及事业单位和港澳特邀  
                
            ??? Quote "[第八届御网杯信息安全大赛](https://www.hncsisc.com/hncsisc/index.html)"  
                **比赛名称** : [第八届御网杯信息安全大赛](https://www.hncsisc.com/hncsisc/index.html)  
                **比赛类型** : 个人赛 and 团体赛|3人  
                **报名时间** : 2024年07月26日 08:00 - 2024年09月20日 18:00  
                **比赛时间** : 2024年09月21日 00:00 - 2024年10月27日 23:59  
                **其他说明** : 更多信息请前往官网https://www.hncsisc.com 的“赛事活动”查看  
                
            ??? Quote "[NepCTF 2024](暂定)"  
                **比赛名称** : [NepCTF 2024](暂定)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年07月25日 08:00 - 2024年08月22日 23:59  
                **比赛时间** : 2024年08月23日 00:00 - 2024年08月25日 23:59  
                **其他说明** : QQ群: 560946020  
                
            ??? Quote "[2024年辽宁大学研究生网络安全创新实践大赛](https://mp.weixin.qq.com/s?search_click_id=1419197875279398874-1721064257482-5560857333&__biz=MzkwODY4NjEwMA==&mid=2247483898&idx=2&sn=9e98fa0801ff04680dc13785de62ec59&chksm=c1d81e30983ce3afed49948819b79e7332489d251f75003da001e323b575dc6267a3f9b3c7c3&scene=7&subscene=10000&sessionid=1721062624&clicktime=1721064257&enterid=1721064257&ascene=65&fasttmpl_type=0&fasttmpl_fullversion=7295595-zh_CN-zip&fasttmpl_flag=0&realreporttime=1721064257512&devicetype=android-34&version=28002e34&nettype=WIFI&abtest_cookie=AAACAA==&lang=zh_CN&countrycode=CN&exportkey=n_ChQIAhIQcvD8xBlhKOyhNiXR+sSwhxLiAQIE97dBBAEAAAAAALJPGgdGHkcAAAAOpnltbLcz9gKNyK89dVj05OQmnZhmX5QxbgZxJq2kXOv2MdwjaAf3iVTLVGCcQUSG7VlEEpibGRWcgGV1BZpKtLcneOndlVFC2eMkTtAv8YTngrwgPTc44eKAtyGHcw9azAA/Lyju97FKSOW2D6eW7ZlNCG9gFS8WG6AcsPuxVr7PhVh4jtPz7vGomi56weNGB+8NjPr5ChEwlxJP+UN5C5JA5rUMV2rKtdZBeiASZdqEjpQcPvQmFzF6OVw0NHDUJ/bDftCImrDsZKo=&pass_ticket=kVxbyE61cIHqlon9l8MZfpuGMpxcldPEOp9u/xMr3MOyS4E0APheem2kMNVrm4dm&wx_header=3)"  
                **比赛名称** : [2024年辽宁大学研究生网络安全创新实践大赛](https://mp.weixin.qq.com/s?search_click_id=1419197875279398874-1721064257482-5560857333&__biz=MzkwODY4NjEwMA==&mid=2247483898&idx=2&sn=9e98fa0801ff04680dc13785de62ec59&chksm=c1d81e30983ce3afed49948819b79e7332489d251f75003da001e323b575dc6267a3f9b3c7c3&scene=7&subscene=10000&sessionid=1721062624&clicktime=1721064257&enterid=1721064257&ascene=65&fasttmpl_type=0&fasttmpl_fullversion=7295595-zh_CN-zip&fasttmpl_flag=0&realreporttime=1721064257512&devicetype=android-34&version=28002e34&nettype=WIFI&abtest_cookie=AAACAA==&lang=zh_CN&countrycode=CN&exportkey=n_ChQIAhIQcvD8xBlhKOyhNiXR+sSwhxLiAQIE97dBBAEAAAAAALJPGgdGHkcAAAAOpnltbLcz9gKNyK89dVj05OQmnZhmX5QxbgZxJq2kXOv2MdwjaAf3iVTLVGCcQUSG7VlEEpibGRWcgGV1BZpKtLcneOndlVFC2eMkTtAv8YTngrwgPTc44eKAtyGHcw9azAA/Lyju97FKSOW2D6eW7ZlNCG9gFS8WG6AcsPuxVr7PhVh4jtPz7vGomi56weNGB+8NjPr5ChEwlxJP+UN5C5JA5rUMV2rKtdZBeiASZdqEjpQcPvQmFzF6OVw0NHDUJ/bDftCImrDsZKo=&pass_ticket=kVxbyE61cIHqlon9l8MZfpuGMpxcldPEOp9u/xMr3MOyS4E0APheem2kMNVrm4dm&wx_header=3)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年07月15日 18:41 - 2024年08月31日 23:59  
                **比赛时间** : 2024年08月31日 23:59 - 2024年08月31日 23:59  
                **其他说明** : 仅限辽宁大学研究生 | 参赛队伍需同时参加“华为杯”第三届中国研究生网络安全创新大赛  
                
            ??? Quote "[“华为杯”第三届中国研究生网络安全创新大赛](https://cpipc.acge.org.cn//pw/detail/2c9080188fc20569018fe6375eeb2eb2)"  
                **比赛名称** : [“华为杯”第三届中国研究生网络安全创新大赛](https://cpipc.acge.org.cn//pw/detail/2c9080188fc20569018fe6375eeb2eb2)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年05月06日 00:00 - 2024年09月23日 23:59  
                **比赛时间** : 2024年09月25日 00:00 - 2024年09月25日 23:59  
                **其他说明** : QQ群: 794148708|仅限研究生参加  
                
            ??? Quote "[第四届极客少年挑战赛（决赛）](https://www.cdccs.cn/#/geekYouth)"  
                **比赛名称** : [第四届极客少年挑战赛（决赛）](https://www.cdccs.cn/#/geekYouth)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年07月22日 10:00 - 2024年07月23日 09:00  
                **比赛时间** : 2024年08月23日 10:00 - 2024年08月23日 15:00  
                **其他说明** : QQ群：961713058  
                
            ??? Quote "[第五届“闽盾杯”网络空间安全大塞黑盾全国大学生赛道（决赛）](http://heidunbei.si.net.cn/hdc/cover)"  
                **比赛名称** : [第五届“闽盾杯”网络空间安全大塞黑盾全国大学生赛道（决赛）](http://heidunbei.si.net.cn/hdc/cover)  
                **比赛类型** : 团队赛|3人  
                **报名时间** : 2024年06月26日 10:35 - 2024年06月26日 10:35  
                **比赛时间** : 2024年09月13日 00:00 - 2024年09月13日 23:59  
                **其他说明** : QQ群：676547374 或 566180593  
                
        === "国外赛事"
            ??? Quote "[SekaiCTF 2024](https://ctf.sekai.team/)"  
                [![](https://ctftime.org/media/events/sekai2_SEKAI_CTF_Square_Black_BG.r_1_1.png){ width="200" align=left }](https://ctf.sekai.team/)  
                **比赛名称** : [SekaiCTF 2024](https://ctf.sekai.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-24 00:00:00 - 2024-08-26 00:00:00 UTC+8  
                **比赛权重** : 36.96  
                **赛事主办** : Project Sekai (https://ctftime.org/team/169557)  
                **添加日历** : https://ctftime.org/event/2243.ics  
                
            ??? Quote "[Block Harbor VicOne Automotive CTF - Season 2](https://ctf.blockharbor.io/)"  
                [![](https://ctftime.org/media/events/blockharbor.jpg){ width="200" align=left }](https://ctf.blockharbor.io/)  
                **比赛名称** : [Block Harbor VicOne Automotive CTF - Season 2](https://ctf.blockharbor.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-24 22:00:00 - 2024-09-09 10:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : bhctf (https://ctftime.org/team/251542)  
                **添加日历** : https://ctftime.org/event/2387.ics  
                
            ??? Quote "[Codegate CTF 2024 Finals](http://www.codegate.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://www.codegate.org/)  
                **比赛名称** : [Codegate CTF 2024 Finals](http://www.codegate.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-29 09:00:00 - 2024-08-30 09:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CODEGATE (https://ctftime.org/team/39352)  
                **添加日历** : https://ctftime.org/event/2347.ics  
                
            ??? Quote "[CyberSpace CTF 2024](https://2024.csc.tf/)"  
                [![](https://ctftime.org/media/events/f6b991673b1944e7b199bc978b3f0a15.png){ width="200" align=left }](https://2024.csc.tf/)  
                **比赛名称** : [CyberSpace CTF 2024](https://2024.csc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-31 00:00:00 - 2024-09-02 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CyberSpace (https://ctftime.org/team/116280)  
                **添加日历** : https://ctftime.org/event/2428.ics  
                
            ??? Quote "[CISA ICS CTF 2024](https://ctf.cisaicsctf.com/)"  
                [![](https://ctftime.org/media/events/CTF_Drifveil_Logo_2-1.png){ width="200" align=left }](https://ctf.cisaicsctf.com/)  
                **比赛名称** : [CISA ICS CTF 2024](https://ctf.cisaicsctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-01 01:00:00 - 2024-09-05 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CISA ICSJWG (https://ctftime.org/team/182074)  
                **添加日历** : https://ctftime.org/event/2404.ics  
                
            ??? Quote "[CSAW CTF Qualification Round 2024](https://ctf.csaw.io/)"  
                [![](https://ctftime.org/media/events/CSAW.png){ width="200" align=left }](https://ctf.csaw.io/)  
                **比赛名称** : [CSAW CTF Qualification Round 2024](https://ctf.csaw.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-07 00:00:00 - 2024-09-09 00:00:00 UTC+8  
                **比赛权重** : 21.80  
                **赛事主办** : NYUSEC (https://ctftime.org/team/439)  
                **添加日历** : https://ctftime.org/event/2398.ics  
                
            ??? Quote "[snakeCTF 2024 Quals](https://2024.snakectf.org/)"  
                [![](https://ctftime.org/media/events/LogoCroppable_1.png){ width="200" align=left }](https://2024.snakectf.org/)  
                **比赛名称** : [snakeCTF 2024 Quals](https://2024.snakectf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-07 16:00:00 - 2024-09-08 16:00:00 UTC+8  
                **比赛权重** : 24.79  
                **赛事主办** : MadrHacks (https://ctftime.org/team/114509)  
                **添加日历** : https://ctftime.org/event/2418.ics  
                
            ??? Quote "[MOCA CTF - Finals](https://moca.camp/ctf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://moca.camp/ctf/)  
                **比赛名称** : [MOCA CTF - Finals](https://moca.camp/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-14 00:00:00 - 2024-09-15 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Metro Olografix (https://ctftime.org/team/268425)  
                **添加日历** : https://ctftime.org/event/2294.ics  
                
            ??? Quote "[Securinets CTF Quals 2024](https://ctf.securinets.tn/)"  
                [![](https://ctftime.org/media/events/d82bcfc5f1d83b7cc51c7dd0dbc8f5c6.png){ width="200" align=left }](https://ctf.securinets.tn/)  
                **比赛名称** : [Securinets CTF Quals 2024](https://ctf.securinets.tn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-15 03:00:00 - 2024-09-16 03:00:00 UTC+8  
                **比赛权重** : 95.59  
                **赛事主办** : Securinets (https://ctftime.org/team/5084)  
                **添加日历** : https://ctftime.org/event/2410.ics  
                
            ??? Quote "[Pointer Overflow CTF - 2024](http://pointeroverflowctf.com/)"  
                [![](https://ctftime.org/media/events/poctflogo1transp.png){ width="200" align=left }](http://pointeroverflowctf.com/)  
                **比赛名称** : [Pointer Overflow CTF - 2024](http://pointeroverflowctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-15 20:00:00 - 2025-01-19 20:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : UWSP Pointers (https://ctftime.org/team/231536)  
                **添加日历** : https://ctftime.org/event/2121.ics  
                
            ??? Quote "[PatriotCTF 2024](http://pctf.competitivecyber.club/)"  
                [![](https://ctftime.org/media/events/masoncc_2.png){ width="200" align=left }](http://pctf.competitivecyber.club/)  
                **比赛名称** : [PatriotCTF 2024](http://pctf.competitivecyber.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 06:00:00 - 2024-09-23 06:00:00 UTC+8  
                **比赛权重** : 31.83  
                **赛事主办** : Competitive Cyber at Mason (https://ctftime.org/team/176906)  
                **添加日历** : https://ctftime.org/event/2426.ics  
                
            ??? Quote "[Cyber Jawara International](https://cyberjawara.id/2024)"  
                [![](https://ctftime.org/media/events/067297e97f084c5492331b121d1b0507.png){ width="200" align=left }](https://cyberjawara.id/2024)  
                **比赛名称** : [Cyber Jawara International](https://cyberjawara.id/2024)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 09:59:00 - 2024-09-22 09:59:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : idnsa (https://ctftime.org/team/239714)  
                **添加日历** : https://ctftime.org/event/2411.ics  
                
            ??? Quote "[GMO Cybersecurity Contest - IERAE CTF 2024](https://gmo-cybersecurity.com/event/ieraectf24/)"  
                [![](https://ctftime.org/media/events/ierae-ctf-logo_2_1.png){ width="200" align=left }](https://gmo-cybersecurity.com/event/ieraectf24/)  
                **比赛名称** : [GMO Cybersecurity Contest - IERAE CTF 2024](https://gmo-cybersecurity.com/event/ieraectf24/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 14:00:00 - 2024-09-22 14:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : ierae (https://ctftime.org/team/224122)  
                **添加日历** : https://ctftime.org/event/2441.ics  
                
            ??? Quote "[openECSC 2024 - Final Round](https://open.ecsc2024.it/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://open.ecsc2024.it/)  
                **比赛名称** : [openECSC 2024 - Final Round](https://open.ecsc2024.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 18:00:00 - 2024-09-22 18:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : ECSC2024 (https://ctftime.org/team/283828)  
                **添加日历** : https://ctftime.org/event/2356.ics  
                
            ??? Quote "[21ans LinuxMeetup au Québec](https://www.linuxver.site/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://www.linuxver.site/)  
                **比赛名称** : [21ans LinuxMeetup au Québec](https://www.linuxver.site/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 21:30:00 - 2024-09-22 05:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SummerJedi (https://ctftime.org/team/126955)  
                **添加日历** : https://ctftime.org/event/2422.ics  
                
            ??? Quote "[ASIS CTF Quals 2024](https://asisctf.com/)"  
                [![](https://ctftime.org/media/events/asisctf.jpg){ width="200" align=left }](https://asisctf.com/)  
                **比赛名称** : [ASIS CTF Quals 2024](https://asisctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-09-21 22:00:00 - 2024-09-22 22:00:00 UTC+8  
                **比赛权重** : 66.25  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2211.ics  
                
            ??? Quote "[FAUST CTF 2024](https://2024.faustctf.net/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://2024.faustctf.net/)  
                **比赛名称** : [FAUST CTF 2024](https://2024.faustctf.net/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-09-28 20:00:00 - 2024-09-29 05:00:00 UTC+8  
                **比赛权重** : 93.11  
                **赛事主办** : FAUST (https://ctftime.org/team/550)  
                **添加日历** : https://ctftime.org/event/2351.ics  
                
            ??? Quote "[AltayCTF 2024](https://university.altayctf.ru/2024)"  
                [![](https://ctftime.org/media/events/0_1.png){ width="200" align=left }](https://university.altayctf.ru/2024)  
                **比赛名称** : [AltayCTF 2024](https://university.altayctf.ru/2024)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-10-05 11:00:00 - 2024-10-06 20:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SharLike (https://ctftime.org/team/16172)  
                **添加日历** : https://ctftime.org/event/2376.ics  
                
            ??? Quote "[RuCTF Finals 2024](http://ructf.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://ructf.org/)  
                **比赛名称** : [RuCTF Finals 2024](http://ructf.org/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-10-05 13:00:00 - 2024-10-07 03:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : HackerDom (https://ctftime.org/team/552)  
                **添加日历** : https://ctftime.org/event/2386.ics  
                
            ??? Quote "[BRICS+ CTF Quals 2024](https://brics-ctf.com/)"  
                [![](https://ctftime.org/media/events/logo-2024.png){ width="200" align=left }](https://brics-ctf.com/)  
                **比赛名称** : [BRICS+ CTF Quals 2024](https://brics-ctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-05 18:00:00 - 2024-10-06 18:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : ITMO FSIT (https://ctftime.org/team/264636)  
                **添加日历** : https://ctftime.org/event/2389.ics  
                
            ??? Quote "[TCP1P CTF 2024: Exploring Nusantara's Digital Realm](https://tcp1p.team/tcp1pctf-2024)"  
                [![](https://ctftime.org/media/events/TCP1P-logo.png){ width="200" align=left }](https://tcp1p.team/tcp1pctf-2024)  
                **比赛名称** : [TCP1P CTF 2024: Exploring Nusantara's Digital Realm](https://tcp1p.team/tcp1pctf-2024)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-11 20:00:00 - 2024-10-13 20:00:00 UTC+8  
                **比赛权重** : 24.85  
                **赛事主办** : TCP1P (https://ctftime.org/team/187248)  
                **添加日历** : https://ctftime.org/event/2256.ics  
                
            ??? Quote "[Hackceler8 2024](https://capturetheflag.withgoogle.com/hackceler8)"  
                [![](https://ctftime.org/media/events/HCL8.png){ width="200" align=left }](https://capturetheflag.withgoogle.com/hackceler8)  
                **比赛名称** : [Hackceler8 2024](https://capturetheflag.withgoogle.com/hackceler8)  
                **比赛形式** : Hack quest  
                **比赛时间** : 2024-10-18 08:00:00 - 2024-10-21 07:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Google CTF (https://ctftime.org/team/23929)  
                **添加日历** : https://ctftime.org/event/2379.ics  
                
            ??? Quote "[Hack.lu CTF 2024](https://flu.xxx/)"  
                [![](https://ctftime.org/media/events/logo-small.png){ width="200" align=left }](https://flu.xxx/)  
                **比赛名称** : [Hack.lu CTF 2024](https://flu.xxx/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-19 02:00:00 - 2024-10-21 02:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : FluxFingers (https://ctftime.org/team/551)  
                **添加日历** : https://ctftime.org/event/2438.ics  
                
            ??? Quote "[SAS CTF 2024 Finals](https://ctf.thesascon.com/)"  
                [![](https://ctftime.org/media/events/SAS24_2_1.png){ width="200" align=left }](https://ctf.thesascon.com/)  
                **比赛名称** : [SAS CTF 2024 Finals](https://ctf.thesascon.com/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-10-22 10:00:00 - 2024-10-22 21:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : SAS CREW (https://ctftime.org/team/283057)  
                **添加日历** : https://ctftime.org/event/2435.ics  
                
            ??? Quote "[Russian CTF Cup 2024 Qualifier](https://ctfcup.ru/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctfcup.ru/)  
                **比赛名称** : [Russian CTF Cup 2024 Qualifier](https://ctfcup.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-10-26 20:00:00 - 2024-10-27 20:00:00 UTC+8  
                **比赛权重** : 24.21  
                **赛事主办** : ctfcup (https://ctftime.org/team/203499)  
                **添加日历** : https://ctftime.org/event/2405.ics  
                
            ??? Quote "[Equinor CTF 2024](https://ctf.equinor.com/)"  
                [![](https://ctftime.org/media/events/ept_1.png){ width="200" align=left }](https://ctf.equinor.com/)  
                **比赛名称** : [Equinor CTF 2024](https://ctf.equinor.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 17:00:00 - 2024-11-03 03:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : EPT (https://ctftime.org/team/119480)  
                **添加日历** : https://ctftime.org/event/2292.ics  
                
            ??? Quote "[Platypwn 2024](https://platypwn.ctf.platypwnies.de/)"  
                [![](https://ctftime.org/media/events/Platypwnie.png){ width="200" align=left }](https://platypwn.ctf.platypwnies.de/)  
                **比赛名称** : [Platypwn 2024](https://platypwn.ctf.platypwnies.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-02 22:00:00 - 2024-11-03 22:00:00 UTC+8  
                **比赛权重** : 24.75  
                **赛事主办** : Platypwnies (https://ctftime.org/team/112550)  
                **添加日历** : https://ctftime.org/event/2407.ics  
                
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
                
            ??? Quote "[WP CTF 2024](https://wpctf.it/)"  
                [![](https://ctftime.org/media/events/WP_CTF_logo.png){ width="200" align=left }](https://wpctf.it/)  
                **比赛名称** : [WP CTF 2024](https://wpctf.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-23 16:00:00 - 2024-11-24 00:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : WP CTF (https://ctftime.org/team/303099)  
                **添加日历** : https://ctftime.org/event/2395.ics  
                
            ??? Quote "[BlackHat MEA CTF Final 2024](https://blackhatmea.com/capture-the-flag)"  
                [![](https://ctftime.org/media/events/e0c283c95f7b0db516dae505d31ca20b_3.jpg){ width="200" align=left }](https://blackhatmea.com/capture-the-flag)  
                **比赛名称** : [BlackHat MEA CTF Final 2024](https://blackhatmea.com/capture-the-flag)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-11-26 16:00:00 - 2024-11-28 11:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : SAFCSP (https://ctftime.org/team/54707)  
                **添加日历** : https://ctftime.org/event/2431.ics  
                
            ??? Quote "[snakeCTF 2024 Finals](https://2024.snakectf.org/)"  
                [![](https://ctftime.org/media/events/LogoCroppable_2.png){ width="200" align=left }](https://2024.snakectf.org/)  
                **比赛名称** : [snakeCTF 2024 Finals](https://2024.snakectf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-12-05 16:00:00 - 2024-12-08 16:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : MadrHacks (https://ctftime.org/team/114509)  
                **添加日历** : https://ctftime.org/event/2419.ics  
                
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
                
    === "*正在进行*"
        === "国内赛事"
            ??? Quote "[BaseCTF 2024 高校联合新生赛](https://www.basectf.fun/)"  
                **比赛名称** : [BaseCTF 2024 高校联合新生赛](https://www.basectf.fun/)  
                **比赛类型** : 1-2 人  
                **报名时间** : 2024年08月5日 00:00 - 2024年09月30日 21:00  
                **比赛时间** : 2024年08月15日 09:00 - 2024年09月30日 21:00  
                **其他说明** : QQ 群：530184592 面向新生的比赛，题目分 Week 1 - 7，从入门到挑战循序渐进  
                
            ??? Quote "[2024年浙江省网络安全行业网络安全运维工程师项目职业技能竞赛](https://mp.weixin.qq.com/s/Uf12nfGPFHxz8QMe60cpDA)"  
                **比赛名称** : [2024年浙江省网络安全行业网络安全运维工程师项目职业技能竞赛](https://mp.weixin.qq.com/s/Uf12nfGPFHxz8QMe60cpDA)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年07月08日 10:46 - 2024年07月31日 20:00  
                **比赛时间** : 2024年08月12日 00:00 - 2024年08月22日 15:00  
                **其他说明** : QQ群: 697694051 | 仅限相关岗位在职员工参加  
                
            ??? Quote "[MoeCTF 2024](https://ctf.xidian.edu.cn)"  
                **比赛名称** : [MoeCTF 2024](https://ctf.xidian.edu.cn)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年08月07日 14:23 - 2024年10月14日 21:00  
                **比赛时间** : 2024年08月10日 09:00 - 2024年10月14日 21:00  
                **其他说明** : QQ 群：187536315  
                
            ??? Quote "[第三届江苏大学研究生网络安全创新大赛](https://yjsy.ujs.edu.cn/info/1305/28415.htm)"  
                **比赛名称** : [第三届江苏大学研究生网络安全创新大赛](https://yjsy.ujs.edu.cn/info/1305/28415.htm)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年06月30日 00:00 - 2024年08月30日 23:59  
                **比赛时间** : 2024年06月30日 00:00 - 2024年08月31日 23:59  
                **其他说明** : 仅限研究生  
                
            ??? Quote "[第二届“天网杯”网络安全大赛](https://twcup.cverc.org.cn/twb/twb2024)"  
                **比赛名称** : [第二届“天网杯”网络安全大赛](https://twcup.cverc.org.cn/twb/twb2024)  
                **比赛类型** : 团队赛|不超过5人  
                **报名时间** : 2024年7月15日 00:00 - 2024年7月31日 23:59  
                **比赛时间** : 2024年08月01日 00:00 - 2024年08月20日 23:59  
                **其他说明** : QQ群: 622869531 组委会邮箱: tianwangcup@163.com  
                
        === "国外赛事"
            ??? Quote "[Sydbox CTF: read /etc/CTF](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)"  
                [![](https://ctftime.org){ width="200" align=left }](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)  
                **比赛名称** : [Sydbox CTF: read /etc/CTF](https://git.sr.ht/~alip/syd#ctf-howto-sydbx-capture-the-flag-challenge)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2023-11-16 22:26:32 - 2024-11-16 22:26:32 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Exherbo GNU/Linux (https://ctftime.org/team/275214)  
                **添加日历** : https://ctftime.org/event/2178.ics  
                
    === "*已经结束*"
        === "国内赛事"
            ??? Quote "[“广东通信杯”广东省信息通信行业第四届网络安全技能大赛暨第八届全国职工职业技能大赛网络与信息安全管理员赛项广东省选拔赛](https://gdca.miit.gov.cn/zwgk/tzgg/art/2024/art_c220b24f198346e08bb0074f511a6121.html)"  
                **比赛名称** : [“广东通信杯”广东省信息通信行业第四届网络安全技能大赛暨第八届全国职工职业技能大赛网络与信息安全管理员赛项广东省选拔赛](https://gdca.miit.gov.cn/zwgk/tzgg/art/2024/art_c220b24f198346e08bb0074f511a6121.html)  
                **比赛类型** : 个人赛 and 团队赛|3人  
                **报名时间** : 2024年06月27日 15:42 - 2024年07月15日 23:59  
                **比赛时间** : 2024年08月04日 08:30 - 2024年08月04日 16:30  
                **其他说明** : 仅限在册工作人员参加  
                
            ??? Quote "[2024年南昌市“洪工杯”网络安全行业职工职业技能竞赛](http://61.147.171.109/race/nanchang2024)"  
                **比赛名称** : [2024年南昌市“洪工杯”网络安全行业职工职业技能竞赛](http://61.147.171.109/race/nanchang2024)  
                **比赛类型** : 团队赛|3人  
                **报名时间** : 2024年06月21日 00:00 - 2024年07月21日 23:59  
                **比赛时间** : 2024年07月27日 00:00 - 2024年07月27日 23:59  
                **其他说明** : 初赛QQ群: 787262369  
                
            ??? Quote "[第十七届全国大学生信息安全竞赛创新实践能力赛（总决赛）](http://www.ciscn.cn/announcement/view/350)"  
                **比赛名称** : [第十七届全国大学生信息安全竞赛创新实践能力赛（总决赛）](http://www.ciscn.cn/announcement/view/350)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年07月04日 02:50 - 2024年07月04日 03:50  
                **比赛时间** : 2024年07月20日 00:00 - 2024年07月21日 23:59  
                **其他说明** : QQ群：979328132  
                
            ??? Quote "[第四届极客少年挑战赛（初赛）](https://www.cdccs.cn/#/geekYouth)"  
                **比赛名称** : [第四届极客少年挑战赛（初赛）](https://www.cdccs.cn/#/geekYouth)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年06月19日 00:00 - 2024年07月13日 23:59  
                **比赛时间** : 2024年07月06日 10:00 - 2024年07月20日 12:00  
                **其他说明** : QQ群：961713058  
                
            ??? Quote "[WKCTF 2024](http://110.40.35.73:81/)"  
                **比赛名称** : [WKCTF 2024](http://110.40.35.73:81/)  
                **比赛类型** : 团队赛|1-4人  
                **报名时间** : 2024年07月03日 00:00 - 2024年07月14日 09:00  
                **比赛时间** : 2024年07月14日 10:00 - 2024年07月14日 18:00  
                **其他说明** : QQ群：575413907  
                
            ??? Quote "[CTFshow-西瓜杯CTF](https://ctf.show/)"  
                **比赛名称** : [CTFshow-西瓜杯CTF](https://ctf.show/)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年06月21日 09:30 - 2024年07月05日 19:00  
                **比赛时间** : 2024年07月05日 20:00 - 2024年07月07日 20:00  
                **其他说明** : QQ群：558694708  
                
            ??? Quote "[2024年春秋杯网络安全联赛夏季赛](https://endbm.ichunqiu.com/2024cqgames1)"  
                **比赛名称** : [2024年春秋杯网络安全联赛夏季赛](https://endbm.ichunqiu.com/2024cqgames1)  
                **比赛类型** : 个人赛  
                **报名时间** : 2024年06月04日 00:00 - 2024年07月06日 18:00  
                **比赛时间** : 2024年07月05日 10:00 - 2024年07月06日 16:00  
                **其他说明** : QQ群：277328440  
                
            ??? Quote "[第五届“闽盾杯”网络空间安全大赛（黑盾全国大学生赛道）](http://heidunbei.si.net.cn/hdc/cover)"  
                **比赛名称** : [第五届“闽盾杯”网络空间安全大赛（黑盾全国大学生赛道）](http://heidunbei.si.net.cn/hdc/cover)  
                **比赛类型** : 团队赛|1-3人  
                **报名时间** : 2024年05月21日 00:00 - 2024年06月19日 18:00  
                **比赛时间** : 2024年06月21日 09:00 - 2024年06月21日 17:00  
                **其他说明** : QQ群：566180593  
                
        === "国外赛事"
            ??? Quote "[idekCTF 2024](https://ctf.idek.team/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.idek.team/)  
                **比赛名称** : [idekCTF 2024](https://ctf.idek.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-08-17 08:00:00 - 2024-08-19 08:00:00 UTC+8  
                **比赛权重** : 0  
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
                
            ??? Quote "[pbctf 2024](https://ctf.perfect.blue/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.perfect.blue/)  
                **比赛名称** : [pbctf 2024](https://ctf.perfect.blue/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-07-20 22:00:00 - 2024-07-21 22:00:00 UTC+8  
                **比赛权重** : 55.00  
                **赛事主办** : perfect blue (https://ctftime.org/team/53802)  
                **添加日历** : https://ctftime.org/event/2381.ics  
                
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
                **比赛权重** : 23.34  
                **赛事主办** : OSCTF (https://ctftime.org/team/307415)  
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
                **比赛权重** : 23.88  
                **赛事主办** : Beavers0 (https://ctftime.org/team/269281)  
                **添加日历** : https://ctftime.org/event/2259.ics  
                
            ??? Quote "[DiceCTF 2024 Finals](https://ctf.dicega.ng/)"  
                [![](https://ctftime.org/media/events/dicectf_2_1_1.png){ width="200" align=left }](https://ctf.dicega.ng/)  
                **比赛名称** : [DiceCTF 2024 Finals](https://ctf.dicega.ng/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-06-29 22:00:00 - 2024-07-01 06:00:00 UTC+8  
                **比赛权重** : 0.00  
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
                
            ??? Quote "[Break The Wall - Dystopia 2099](https://breakthewall.hackrocks.com/)"  
                [![](https://ctftime.org/media/events/breakthewall_logo-IrRB.png){ width="200" align=left }](https://breakthewall.hackrocks.com/)  
                **比赛名称** : [Break The Wall - Dystopia 2099](https://breakthewall.hackrocks.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-26 19:00:00 - 2024-07-11 03:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : hackrocks (https://ctftime.org/team/175823)  
                **添加日历** : https://ctftime.org/event/2393.ics  
                
            ??? Quote "[Pacific Hackers Pre-DEFCON CTF & BBQ 2024](https://www.meetup.com/pacifichackers/events/301096276/)"  
                [![](https://ctftime.org/media/events/pacific_hacker_bear.png){ width="200" align=left }](https://www.meetup.com/pacifichackers/events/301096276/)  
                **比赛名称** : [Pacific Hackers Pre-DEFCON CTF & BBQ 2024](https://www.meetup.com/pacifichackers/events/301096276/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-23 03:00:00 - 2024-06-23 10:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Pacific Hackers Association (https://ctftime.org/team/304096)  
                **添加日历** : https://ctftime.org/event/2413.ics  
                
            ??? Quote "[MindBreak 2024 by ESGI](https://forms.gle/PMkTtQ692RGo3SCGA)"  
                [![](https://ctftime.org/media/events/511a7559bf9c4f2a983c12008b53d059.png){ width="200" align=left }](https://forms.gle/PMkTtQ692RGo3SCGA)  
                **比赛名称** : [MindBreak 2024 by ESGI](https://forms.gle/PMkTtQ692RGo3SCGA)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-23 03:00:00 - 2024-06-23 12:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : MindBreakers ESGI (https://ctftime.org/team/280786)  
                **添加日历** : https://ctftime.org/event/2415.ics  
                
            ??? Quote "[İGÜCTF 24'](https://igusiber.com.tr/)"  
                [![](https://ctftime.org/media/events/siber.png){ width="200" align=left }](https://igusiber.com.tr/)  
                **比赛名称** : [İGÜCTF 24'](https://igusiber.com.tr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-22 17:00:00 - 2024-06-23 04:59:59 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Ah Yalan Dünya (https://ctftime.org/team/202267)  
                **添加日历** : https://ctftime.org/event/2394.ics  
                
            ??? Quote "[HACK'OSINT - CTF](https://ctf.hackolyte.fr/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hackolyte.fr/)  
                **比赛名称** : [HACK'OSINT - CTF](https://ctf.hackolyte.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-22 02:00:00 - 2024-06-24 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hack'olyte (https://ctftime.org/team/222944)  
                **添加日历** : https://ctftime.org/event/2392.ics  
                
            ??? Quote "[Google Capture The Flag 2024](https://g.co/ctf)"  
                [![](https://ctftime.org){ width="200" align=left }](https://g.co/ctf)  
                **比赛名称** : [Google Capture The Flag 2024](https://g.co/ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-22 02:00:00 - 2024-06-24 02:00:00 UTC+8  
                **比赛权重** : 99.41  
                **赛事主办** : Google CTF (https://ctftime.org/team/23929)  
                **添加日历** : https://ctftime.org/event/2296.ics  
                
            ??? Quote "[CyberSci Nationals 2024](https://cybersecuritychallenge.ca/)"  
                [![](https://ctftime.org/media/events/c0c445488770d1de63c46986bc92e8e6.png){ width="200" align=left }](https://cybersecuritychallenge.ca/)  
                **比赛名称** : [CyberSci Nationals 2024](https://cybersecuritychallenge.ca/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-21 20:00:00 - 2024-06-23 06:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CyberSciOrganizers (https://ctftime.org/team/157536)  
                **添加日历** : https://ctftime.org/event/2366.ics  
                
            ??? Quote "[Wani CTF 2024](https://wanictf.org/)"  
                [![](https://ctftime.org/media/events/wani_ctf_logo.png){ width="200" align=left }](https://wanictf.org/)  
                **比赛名称** : [Wani CTF 2024](https://wanictf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-21 20:00:00 - 2024-06-23 20:00:00 UTC+8  
                **比赛权重** : 24.99  
                **赛事主办** : Wani Hackase (https://ctftime.org/team/70717)  
                **添加日历** : https://ctftime.org/event/2377.ics  
                
            ??? Quote "[Grey Cat The Flag 2024 Finals](https://ctf.nusgreyhats.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.nusgreyhats.org/)  
                **比赛名称** : [Grey Cat The Flag 2024 Finals](https://ctf.nusgreyhats.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-20 10:00:00 - 2024-06-21 18:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : NUSGreyhats (https://ctftime.org/team/16740)  
                **添加日历** : https://ctftime.org/event/2244.ics  
                
            ??? Quote "[Kryptokaffe CTF 2024](https://www.kryptokaffe.se/)"  
                [![](https://ctftime.org/media/events/kryptokaffe2k24.png){ width="200" align=left }](https://www.kryptokaffe.se/)  
                **比赛名称** : [Kryptokaffe CTF 2024](https://www.kryptokaffe.se/)  
                **比赛形式** : Hack quest  
                **比赛时间** : 2024-06-17 16:00:00 - 2024-07-21 20:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Fikamyndigheten (https://ctftime.org/team/305722)  
                **添加日历** : https://ctftime.org/event/2399.ics  
                
            ??? Quote "[Midnight Sun CTF 2024 Finals](https://play.midnightsunctf.com/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://play.midnightsunctf.com/)  
                **比赛名称** : [Midnight Sun CTF 2024 Finals](https://play.midnightsunctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-15 18:00:00 - 2024-06-16 18:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : HackingForSoju (https://ctftime.org/team/3208)  
                **添加日历** : https://ctftime.org/event/2409.ics  
                
            ??? Quote "[justCTF 2024 teaser](http://2024.justctf.team/)"  
                [![](https://ctftime.org/media/events/logo-ctf_3.png){ width="200" align=left }](http://2024.justctf.team/)  
                **比赛名称** : [justCTF 2024 teaser](http://2024.justctf.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-15 16:00:00 - 2024-06-16 16:00:00 UTC+8  
                **比赛权重** : 77.17  
                **赛事主办** : justCatTheFish (https://ctftime.org/team/33893)  
                **添加日历** : https://ctftime.org/event/2342.ics  
                
            ??? Quote "[vsCTF 2024](https://ctf.viewsource.me/)"  
                [![](https://ctftime.org/media/events/vsctf_2024_2x.png){ width="200" align=left }](https://ctf.viewsource.me/)  
                **比赛名称** : [vsCTF 2024](https://ctf.viewsource.me/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-15 00:00:00 - 2024-06-16 00:00:00 UTC+8  
                **比赛权重** : 34.00  
                **赛事主办** : View Source (https://ctftime.org/team/175828)  
                **添加日历** : https://ctftime.org/event/2248.ics  
                
            ??? Quote "[BrainHack 2024](https://go.gov.sg/dsta-brainhack-signup)"  
                [![](https://ctftime.org/media/events/807b15_524e092c9d7541589d621cd0e9bf6e4bmv2.jpeg){ width="200" align=left }](https://go.gov.sg/dsta-brainhack-signup)  
                **比赛名称** : [BrainHack 2024](https://go.gov.sg/dsta-brainhack-signup)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-12 16:00:00 - 2024-06-14 03:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BrainHack_Organiser (https://ctftime.org/team/287673)  
                **添加日历** : https://ctftime.org/event/2330.ics  
                
            ??? Quote "[Crypto CTF 2024](https://cr.yp.toc.tf/)"  
                [![](https://ctftime.org/media/events/cryptoctf.jpg){ width="200" align=left }](https://cr.yp.toc.tf/)  
                **比赛名称** : [Crypto CTF 2024](https://cr.yp.toc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-08 22:00:00 - 2024-06-09 22:00:00 UTC+8  
                **比赛权重** : 65.62  
                **赛事主办** : ASIS (https://ctftime.org/team/4140)  
                **添加日历** : https://ctftime.org/event/2210.ics  
                
            ??? Quote "[RVCE x IITB x YCF CTF](https://rvctf.tech/)"  
                [![](https://ctftime.org/media/events/rv_logo.jpg){ width="200" align=left }](https://rvctf.tech/)  
                **比赛名称** : [RVCE x IITB x YCF CTF](https://rvctf.tech/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-08 20:30:00 - 2024-06-09 02:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : YCF (https://ctftime.org/team/179685)  
                **添加日历** : https://ctftime.org/event/2385.ics  
                
            ??? Quote "[DIVER OSINT CTF 2024](https://ctfd.diverctf.org/)"  
                [![](https://ctftime.org/media/events/tQF2eZgQ_400x400.jpg){ width="200" align=left }](https://ctfd.diverctf.org/)  
                **比赛名称** : [DIVER OSINT CTF 2024](https://ctfd.diverctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-08 11:00:00 - 2024-06-09 11:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : diver_osint (https://ctftime.org/team/299569)  
                **添加日历** : https://ctftime.org/event/2365.ics  
                
            ??? Quote "[R3CTF/YUANHENGCTF 2024](https://ctf2024.r3kapig.com/)"  
                [![](https://ctftime.org/media/events/r3_logo.png){ width="200" align=left }](https://ctf2024.r3kapig.com/)  
                **比赛名称** : [R3CTF/YUANHENGCTF 2024](https://ctf2024.r3kapig.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-08 10:00:00 - 2024-06-10 10:00:00 UTC+8  
                **比赛权重** : 24.56  
                **赛事主办** : r3kapig (https://ctftime.org/team/58979)  
                **添加日历** : https://ctftime.org/event/2273.ics  
                
            ??? Quote "[ESAIP CTF 2024](https://ctf.esaip.org/)"  
                [![](https://ctftime.org/media/events/Logo_discord.png){ width="200" align=left }](https://ctf.esaip.org/)  
                **比赛名称** : [ESAIP CTF 2024](https://ctf.esaip.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-08 05:00:00 - 2024-06-08 16:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Esaip CTF (https://ctftime.org/team/190938)  
                **添加日历** : https://ctftime.org/event/2382.ics  
                
            ??? Quote "[BCACTF 5.0](https://www.bcactf.com/)"  
                [![](https://ctftime.org/media/events/bcactflogoocean.png){ width="200" align=left }](https://www.bcactf.com/)  
                **比赛名称** : [BCACTF 5.0](https://www.bcactf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-08 04:00:00 - 2024-06-11 04:00:00 UTC+8  
                **比赛权重** : 46.33  
                **赛事主办** : BCACTF (https://ctftime.org/team/81702)  
                **添加日历** : https://ctftime.org/event/2274.ics  
                
            ??? Quote "[Akasec CTF 2024](https://ctf.akasec.club/)"  
                [![](https://ctftime.org/media/events/akasec-ctf-logo_3.jpeg){ width="200" align=left }](https://ctf.akasec.club/)  
                **比赛名称** : [Akasec CTF 2024](https://ctf.akasec.club/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-07 21:37:00 - 2024-06-09 21:37:00 UTC+8  
                **比赛权重** : 23.00  
                **赛事主办** : Akasec (https://ctftime.org/team/107202)  
                **添加日历** : https://ctftime.org/event/2222.ics  
                
            ??? Quote "[DASCTF X HDCTF 2024 Open Competition](https://buuoj.cn/match/matches/204)"  
                [![](https://ctftime.org/media/events/7cb37da3aed536041d1754ecb2083099.jpg){ width="200" align=left }](https://buuoj.cn/match/matches/204)  
                **比赛名称** : [DASCTF X HDCTF 2024 Open Competition](https://buuoj.cn/match/matches/204)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-02 18:00:00 - 2024-06-03 02:00:00 UTC+8  
                **比赛权重** : 1.00  
                **赛事主办** : DASCTF (https://ctftime.org/team/303691)  
                **添加日历** : https://ctftime.org/event/2390.ics  
                
            ??? Quote "[N0PSctf](https://ctf.nops.re/)"  
                [![](https://ctftime.org/media/events/favicon_5.png){ width="200" align=left }](https://ctf.nops.re/)  
                **比赛名称** : [N0PSctf](https://ctf.nops.re/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-01 16:00:00 - 2024-06-03 04:00:00 UTC+8  
                **比赛权重** : 24.28  
                **赛事主办** : NOPS (https://ctftime.org/team/4056)  
                **添加日历** : https://ctftime.org/event/2358.ics  
                
            ??? Quote "[Codegate CTF 2024 Preliminary](http://ctf.codegate.org/)"  
                [![](https://ctftime.org){ width="200" align=left }](http://ctf.codegate.org/)  
                **比赛名称** : [Codegate CTF 2024 Preliminary](http://ctf.codegate.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-01 09:00:00 - 2024-06-02 09:00:00 UTC+8  
                **比赛权重** : 36.58  
                **赛事主办** : CODEGATE (https://ctftime.org/team/39352)  
                **添加日历** : https://ctftime.org/event/2346.ics  
                
            ??? Quote "[Hardwear.io USA 2024 Hardware CTF](https://hwctf.quarkslab.com/)"  
                [![](https://ctftime.org/media/events/logohwcolor_13.png){ width="200" align=left }](https://hwctf.quarkslab.com/)  
                **比赛名称** : [Hardwear.io USA 2024 Hardware CTF](https://hwctf.quarkslab.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-06-01 01:00:00 - 2024-06-02 04:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hardware CTF by Quarkslab (https://ctftime.org/team/274600)  
                **添加日历** : https://ctftime.org/event/2400.ics  
                
            ??? Quote "[Season IV, US Cyber Open](https://www.uscybergames.com/apply-to-play-season-4?hsCtaTracking=b8a9eb7a-183c-4113-a5d4-a4ac7b486e4f%7Cb5c8f25c-5752-4e8f-815b-82cb4d186af1)"  
                [![](https://ctftime.org/media/events/2022-10-USCG_S3_logos_cybergames_1.png){ width="200" align=left }](https://www.uscybergames.com/apply-to-play-season-4?hsCtaTracking=b8a9eb7a-183c-4113-a5d4-a4ac7b486e4f%7Cb5c8f25c-5752-4e8f-815b-82cb4d186af1)  
                **比赛名称** : [Season IV, US Cyber Open](https://www.uscybergames.com/apply-to-play-season-4?hsCtaTracking=b8a9eb7a-183c-4113-a5d4-a4ac7b486e4f%7Cb5c8f25c-5752-4e8f-815b-82cb4d186af1)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-31 19:59:00 - 2024-06-10 07:59:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : PlayCyber (https://ctftime.org/team/165788)  
                **添加日历** : https://ctftime.org/event/2350.ics  
                
            ??? Quote "[GPN CTF 2024](https://ctf.kitctf.de/)"  
                [![](https://ctftime.org/media/events/2acc1e50ba516aa0bc42a61798cfa10d.png){ width="200" align=left }](https://ctf.kitctf.de/)  
                **比赛名称** : [GPN CTF 2024](https://ctf.kitctf.de/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-31 18:00:00 - 2024-06-02 06:00:00 UTC+8  
                **比赛权重** : 31.17  
                **赛事主办** : KITCTF (https://ctftime.org/team/7221)  
                **添加日历** : https://ctftime.org/event/2257.ics  
                
            ??? Quote "[Dreamhack Invitational 2024](https://dreamhack.io/)"  
                [![](https://ctftime.org/media/events/_mini_round_light2x_1.png){ width="200" align=left }](https://dreamhack.io/)  
                **比赛名称** : [Dreamhack Invitational 2024](https://dreamhack.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-27 09:00:00 - 2024-05-27 21:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : Theori (https://ctftime.org/team/250867)  
                **添加日历** : https://ctftime.org/event/2309.ics  
                
            ??? Quote "[Haruulzangi U18 2024 Domestic Finals](http://www.haruulzangi.mn/)"  
                [![](https://ctftime.org/media/events/hz-u18_1_1_1.png){ width="200" align=left }](http://www.haruulzangi.mn/)  
                **比赛名称** : [Haruulzangi U18 2024 Domestic Finals](http://www.haruulzangi.mn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-26 11:00:00 - 2024-05-26 15:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : haruulzangi-organizers (https://ctftime.org/team/266812)  
                **添加日历** : https://ctftime.org/event/2372.ics  
                
            ??? Quote "[AVSS Contest Final 2024](https://avss.geekcon.top/)"  
                [![](https://ctftime.org/media/events/AVSS_1.png){ width="200" align=left }](https://avss.geekcon.top/)  
                **比赛名称** : [AVSS Contest Final 2024](https://avss.geekcon.top/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-25 17:30:00 - 2024-05-26 20:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : GEEKCON (https://ctftime.org/team/255059)  
                **添加日历** : https://ctftime.org/event/2384.ics  
                
            ??? Quote "[RCTF 2024](https://rctf.rois.io/)"  
                [![](https://ctftime.org/media/events/logo_7_1_1.jpg){ width="200" align=left }](https://rctf.rois.io/)  
                **比赛名称** : [RCTF 2024](https://rctf.rois.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-25 09:00:00 - 2024-05-27 09:00:00 UTC+8  
                **比赛权重** : 83.50  
                **赛事主办** : ROIS (https://ctftime.org/team/6476)  
                **添加日历** : https://ctftime.org/event/2374.ics  
                
            ??? Quote "[ångstromCTF 2024](https://angstromctf.com/)"  
                [![](https://ctftime.org/media/events/actf_2.png){ width="200" align=left }](https://angstromctf.com/)  
                **比赛名称** : [ångstromCTF 2024](https://angstromctf.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-25 08:00:00 - 2024-05-28 08:00:00 UTC+8  
                **比赛权重** : 72.06  
                **赛事主办** : ångstromCTF Organizers (https://ctftime.org/team/15734)  
                **添加日历** : https://ctftime.org/event/2375.ics  
                
            ??? Quote "[BTCTF I](https://btcodeclub.vercel.app/)"  
                [![](https://ctftime.org/media/events/Screen_Shot_2024-04-10_at_5.52.43_PM.png){ width="200" align=left }](https://btcodeclub.vercel.app/)  
                **比赛名称** : [BTCTF I](https://btcodeclub.vercel.app/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-25 04:00:00 - 2024-05-27 04:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : btcodeclub (https://ctftime.org/team/278477)  
                **添加日历** : https://ctftime.org/event/2340.ics  
                
            ??? Quote "[L3akCTF 2024](https://ctf.l3ak.team/)"  
                [![](https://ctftime.org/media/events/ctf_final.png){ width="200" align=left }](https://ctf.l3ak.team/)  
                **比赛名称** : [L3akCTF 2024](https://ctf.l3ak.team/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-24 20:00:00 - 2024-05-26 20:00:00 UTC+8  
                **比赛权重** : 24.41  
                **赛事主办** : L3ak (https://ctftime.org/team/220336)  
                **添加日历** : https://ctftime.org/event/2322.ics  
                
            ??? Quote "[AI CTF 2024](https://aictf.phdays.fun/)"  
                [![](https://ctftime.org/media/events/AI_CTF_AI_TRACK_.png){ width="200" align=left }](https://aictf.phdays.fun/)  
                **比赛名称** : [AI CTF 2024](https://aictf.phdays.fun/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-24 17:00:00 - 2024-05-26 05:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : [TechnoPandas] (https://ctftime.org/team/1946)  
                **添加日历** : https://ctftime.org/event/2383.ics  
                
            ??? Quote "[NahamCon CTF 2024](https://ctf.nahamcon.com/)"  
                [![](https://ctftime.org/media/events/NAHAMCON-LOGO_BRANDING_D3_A1_1.png){ width="200" align=left }](https://ctf.nahamcon.com/)  
                **比赛名称** : [NahamCon CTF 2024](https://ctf.nahamcon.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-24 04:00:00 - 2024-05-26 04:00:00 UTC+8  
                **比赛权重** : 41.61  
                **赛事主办** : JustHacking (https://ctftime.org/team/59573)  
                **添加日历** : https://ctftime.org/event/2364.ics  
                
            ??? Quote "[BSides Mumbai CTF 2024](https://ctf.bsidesmumbai.in/)"  
                [![](https://ctftime.org/media/events/Logo_11.png){ width="200" align=left }](https://ctf.bsidesmumbai.in/)  
                **比赛名称** : [BSides Mumbai CTF 2024](https://ctf.bsidesmumbai.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-19 18:30:00 - 2024-05-20 06:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : DarkArmy (https://ctftime.org/team/26569)  
                **添加日历** : https://ctftime.org/event/2369.ics  
                
            ??? Quote "[Hacky'Nov 0x03](https://hackynov.fr/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://hackynov.fr/)  
                **比赛名称** : [Hacky'Nov 0x03](https://hackynov.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 22:00:00 - 2024-05-19 15:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Hacky'Nov (https://ctftime.org/team/178939)  
                **添加日历** : https://ctftime.org/event/2319.ics  
                
            ??? Quote "[HTB Business CTF 2024: The Vault Of Hope](https://ctf.hackthebox.com/event/details/htb-business-ctf-2024-the-vault-of-hope-1474)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.hackthebox.com/event/details/htb-business-ctf-2024-the-vault-of-hope-1474)  
                **比赛名称** : [HTB Business CTF 2024: The Vault Of Hope](https://ctf.hackthebox.com/event/details/htb-business-ctf-2024-the-vault-of-hope-1474)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 21:00:00 - 2024-05-22 21:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : Hack The Box (https://ctftime.org/team/136056)  
                **添加日历** : https://ctftime.org/event/2315.ics  
                
            ??? Quote "[SAS CTF 2024 Quals](https://ctf.thesascon.com/)"  
                [![](https://ctftime.org/media/events/SAS24_2.png){ width="200" align=left }](https://ctf.thesascon.com/)  
                **比赛名称** : [SAS CTF 2024 Quals](https://ctf.thesascon.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 20:00:00 - 2024-05-19 20:00:00 UTC+8  
                **比赛权重** : 20.98  
                **赛事主办** : SAS CREW (https://ctftime.org/team/283057)  
                **添加日历** : https://ctftime.org/event/2299.ics  
                
            ??? Quote "[VulnX CTF 2024](https://vulncon.in/)"  
                [![](https://ctftime.org/media/events/VulnX-Profile_pic.png){ width="200" align=left }](https://vulncon.in/)  
                **比赛名称** : [VulnX CTF 2024](https://vulncon.in/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 18:30:00 - 2024-05-19 18:30:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : VulnX (https://ctftime.org/team/117274)  
                **添加日历** : https://ctftime.org/event/2318.ics  
                
            ??? Quote "[Haruulzangi U18 2024 Domestic Quals](https://u18-2024.haruulzangi.mn/)"  
                [![](https://ctftime.org/media/events/hz-u18_1_1.png){ width="200" align=left }](https://u18-2024.haruulzangi.mn/)  
                **比赛名称** : [Haruulzangi U18 2024 Domestic Quals](https://u18-2024.haruulzangi.mn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 12:00:00 - 2024-05-18 16:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : haruulzangi-organizers (https://ctftime.org/team/266812)  
                **添加日历** : https://ctftime.org/event/2371.ics  
                
            ??? Quote "[TJCTF 2024](https://tjctf.org/)"  
                [![](https://ctftime.org/media/events/logo_96.png){ width="200" align=left }](https://tjctf.org/)  
                **比赛名称** : [TJCTF 2024](https://tjctf.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 02:30:00 - 2024-05-20 02:30:00 UTC+8  
                **比赛权重** : 35.60  
                **赛事主办** : tjcsc (https://ctftime.org/team/53812)  
                **添加日历** : https://ctftime.org/event/2321.ics  
                
            ??? Quote "[Break the Syntax CTF 2024](https://bts2024.wh.edu.pl/)"  
                [![](https://ctftime.org/media/events/logo_99.png){ width="200" align=left }](https://bts2024.wh.edu.pl/)  
                **比赛名称** : [Break the Syntax CTF 2024](https://bts2024.wh.edu.pl/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-18 00:00:00 - 2024-05-19 18:00:00 UTC+8  
                **比赛权重** : 28.30  
                **赛事主办** : PWr Synt@x Err0r (https://ctftime.org/team/88205)  
                **添加日历** : https://ctftime.org/event/2289.ics  
                
            ??? Quote "[Black Cell SecOps 2024 - Online Blue Teaming Jeopardy CTF](https://blackcell.io/ctf/)"  
                [![](https://ctftime.org/media/events/SecOps2024_logo.png){ width="200" align=left }](https://blackcell.io/ctf/)  
                **比赛名称** : [Black Cell SecOps 2024 - Online Blue Teaming Jeopardy CTF](https://blackcell.io/ctf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-17 17:00:00 - 2024-05-20 02:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Black Cell Secops (https://ctftime.org/team/270941)  
                **添加日历** : https://ctftime.org/event/2135.ics  
                
            ??? Quote "[BYUCTF 2024](https://ctfd.cyberjousting.com/)"  
                [![](https://ctftime.org/media/events/cougar.jpg){ width="200" align=left }](https://ctfd.cyberjousting.com/)  
                **比赛名称** : [BYUCTF 2024](https://ctfd.cyberjousting.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-17 08:00:00 - 2024-05-19 08:00:00 UTC+8  
                **比赛权重** : 30.75  
                **赛事主办** : BYU Cyberia (https://ctftime.org/team/155711)  
                **添加日历** : https://ctftime.org/event/2252.ics  
                
            ??? Quote "[openECSC 2024 - Round 3](https://open.ecsc2024.it/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://open.ecsc2024.it/)  
                **比赛名称** : [openECSC 2024 - Round 3](https://open.ecsc2024.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-13 18:00:00 - 2024-05-20 06:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : ECSC2024 (https://ctftime.org/team/283828)  
                **添加日历** : https://ctftime.org/event/2355.ics  
                
            ??? Quote "[CyberSecurityRumble Quals](https://quals.rumble.host/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://quals.rumble.host/)  
                **比赛名称** : [CyberSecurityRumble Quals](https://quals.rumble.host/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-11 21:00:00 - 2024-05-12 21:00:00 UTC+8  
                **比赛权重** : 100.00  
                **赛事主办** : RedRocket (https://ctftime.org/team/48677)  
                **添加日历** : https://ctftime.org/event/2224.ics  
                
            ??? Quote "[San Diego CTF 2024](https://sdc.tf/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://sdc.tf/)  
                **比赛名称** : [San Diego CTF 2024](https://sdc.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-11 07:59:59 - 2024-05-13 07:59:59 UTC+8  
                **比赛权重** : 24.67  
                **赛事主办** : 3 Prongs And a Computer (https://ctftime.org/team/112558)  
                **添加日历** : https://ctftime.org/event/2325.ics  
                
            ??? Quote "[TBTL CTF 2024](https://tbtl.ctfd.io/)"  
                [![](https://ctftime.org/media/events/ctflogo_2.png){ width="200" align=left }](https://tbtl.ctfd.io/)  
                **比赛名称** : [TBTL CTF 2024](https://tbtl.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-11 06:00:00 - 2024-05-13 06:00:00 UTC+8  
                **比赛权重** : 22.17  
                **赛事主办** : TBTL (https://ctftime.org/team/170112)  
                **添加日历** : https://ctftime.org/event/2324.ics  
                
            ??? Quote "[RPCA CTF 2024](https://ctf.rpca.ac.th/)"  
                [![](https://ctftime.org/media/events/RPCACTF2024-Logo_page-0001.jpg){ width="200" align=left }](https://ctf.rpca.ac.th/)  
                **比赛名称** : [RPCA CTF 2024](https://ctf.rpca.ac.th/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-11 01:00:00 - 2024-05-13 01:00:00 UTC+8  
                **比赛权重** : 36.00  
                **赛事主办** : RPCA Cyber Club (https://ctftime.org/team/132960)  
                **添加日历** : https://ctftime.org/event/2352.ics  
                
            ??? Quote "[MireaCTF Finals 2024](https://mireactf.ru/)"  
                [![](https://ctftime.org/media/events/image_2024-04-26_00-28-23_1.png){ width="200" align=left }](https://mireactf.ru/)  
                **比赛名称** : [MireaCTF Finals 2024](https://mireactf.ru/)  
                **比赛形式** : Attack-Defense  
                **比赛时间** : 2024-05-10 16:00:00 - 2024-05-10 22:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : cR4.sh (https://ctftime.org/team/224675)  
                **添加日历** : https://ctftime.org/event/2368.ics  
                
            ??? Quote "[squ1rrel CTF 2024](https://ctf.squ1rrel.dev/)"  
                [![](https://ctftime.org/media/events/squ1rrel.png){ width="200" align=left }](https://ctf.squ1rrel.dev/)  
                **比赛名称** : [squ1rrel CTF 2024](https://ctf.squ1rrel.dev/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-04 23:00:00 - 2024-05-06 11:00:00 UTC+8  
                **比赛权重** : 24.19  
                **赛事主办** : squ1rrel (https://ctftime.org/team/201730)  
                **添加日历** : https://ctftime.org/event/2370.ics  
                
            ??? Quote "[Punk Security DevSecOps Birthday CTF](https://punksecurity.co.uk/ctf)"  
                [![](https://ctftime.org){ width="200" align=left }](https://punksecurity.co.uk/ctf)  
                **比赛名称** : [Punk Security DevSecOps Birthday CTF](https://punksecurity.co.uk/ctf)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-04 17:00:00 - 2024-05-05 05:00:00 UTC+8  
                **比赛权重** : 24.82  
                **赛事主办** : Punk Security (https://ctftime.org/team/212540)  
                **添加日历** : https://ctftime.org/event/2285.ics  
                
            ??? Quote "[BSidesSF 2024 CTF](https://ctf.bsidessf.net/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://ctf.bsidessf.net/)  
                **比赛名称** : [BSidesSF 2024 CTF](https://ctf.bsidessf.net/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-04 08:00:00 - 2024-05-06 07:59:59 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : BSidesSF (https://ctftime.org/team/54737)  
                **添加日历** : https://ctftime.org/event/2357.ics  
                
            ??? Quote "[DEF CON CTF Qualifier 2024](https://nautilus.institute/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://nautilus.institute/)  
                **比赛名称** : [DEF CON CTF Qualifier 2024](https://nautilus.institute/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-04 08:00:00 - 2024-05-06 08:00:00 UTC+8  
                **比赛权重** : 77.38  
                **赛事主办** : Nautilus Institute (https://ctftime.org/team/181536)  
                **添加日历** : https://ctftime.org/event/2229.ics  
                
            ??? Quote "[LakeCTF Finals 23](https://lakectf.epfl.ch/)"  
                [![](https://ctftime.org/media/events/lakeCTFLogo.png){ width="200" align=left }](https://lakectf.epfl.ch/)  
                **比赛名称** : [LakeCTF Finals 23](https://lakectf.epfl.ch/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-03 16:00:00 - 2024-05-04 00:00:00 UTC+8  
                **比赛权重** : 36.00  
                **赛事主办** : polygl0ts (https://ctftime.org/team/53791)  
                **添加日历** : https://ctftime.org/event/2246.ics  
                
            ??? Quote "[MireaCTF Quals 2024](https://spring.mireactf.ru/)"  
                [![](https://ctftime.org/media/events/image_2024-04-26_00-28-23.png){ width="200" align=left }](https://spring.mireactf.ru/)  
                **比赛名称** : [MireaCTF Quals 2024](https://spring.mireactf.ru/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-05-01 16:00:00 - 2024-05-02 00:00:00 UTC+8  
                **比赛权重** : 20.72  
                **赛事主办** : cR4.sh (https://ctftime.org/team/224675)  
                **添加日历** : https://ctftime.org/event/2367.ics  
                
            ??? Quote "[Cybercoliseum Ⅲ](https://cybercoliseum.codeby.games/en)"  
                [![](https://ctftime.org/media/events/logo-cdb.png){ width="200" align=left }](https://cybercoliseum.codeby.games/en)  
                **比赛名称** : [Cybercoliseum Ⅲ](https://cybercoliseum.codeby.games/en)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-28 15:00:00 - 2024-04-30 03:00:00 UTC+8  
                **比赛权重** : 20.95  
                **赛事主办** : Codeby Games (https://ctftime.org/team/299486)  
                **添加日历** : https://ctftime.org/event/2341.ics  
                
            ??? Quote "[CyberSphere CTF - 2024](https://securinets.tn/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://securinets.tn/)  
                **比赛名称** : [CyberSphere CTF - 2024](https://securinets.tn/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-28 05:00:00 - 2024-04-28 17:00:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : Securinets (https://ctftime.org/team/5084)  
                **添加日历** : https://ctftime.org/event/2328.ics  
                
            ??? Quote "[Midnight Flag - Operation BACKSLASH](https://ctfd.midnightflag.fr/)"  
                [![](https://ctftime.org/media/events/logo-3848x3084-upscaled.png){ width="200" align=left }](https://ctfd.midnightflag.fr/)  
                **比赛名称** : [Midnight Flag - Operation BACKSLASH](https://ctfd.midnightflag.fr/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-28 04:00:00 - 2024-04-28 15:00:00 UTC+8  
                **比赛权重** : 37.00  
                **赛事主办** : Midnight Flag - BACKSLASH (https://ctftime.org/team/179110)  
                **添加日历** : https://ctftime.org/event/2295.ics  
                
            ??? Quote "[AirOverflow CTF - 2024](https://ctf.airoverflow.com/)"  
                [![](https://ctftime.org/media/events/Cropped_-_No_Name.png){ width="200" align=left }](https://ctf.airoverflow.com/)  
                **比赛名称** : [AirOverflow CTF - 2024](https://ctf.airoverflow.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 20:00:00 - 2024-04-29 04:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : AirOverFlow (https://ctftime.org/team/140448)  
                **添加日历** : https://ctftime.org/event/2360.ics  
                
            ??? Quote "[THJCC CTF](https://ctf-hobby.scint.org/)"  
                [![](https://ctftime.org/media/events/logo1_4.png){ width="200" align=left }](https://ctf-hobby.scint.org/)  
                **比赛名称** : [THJCC CTF](https://ctf-hobby.scint.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 16:00:00 - 2024-04-29 04:00:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : CakeisTheFake (https://ctftime.org/team/276544)  
                **添加日历** : https://ctftime.org/event/2362.ics  
                
            ??? Quote "[UrchinSec Tanzania National CTF MMXXIV](https://ctf.urchinsec.com/)"  
                [![](https://ctftime.org/media/events/TkH-DDqG_400x400.png){ width="200" align=left }](https://ctf.urchinsec.com/)  
                **比赛名称** : [UrchinSec Tanzania National CTF MMXXIV](https://ctf.urchinsec.com/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 15:30:00 - 2024-04-29 03:30:00 UTC+8  
                **比赛权重** : 25.00  
                **赛事主办** : UrchinSec (https://ctftime.org/team/175663)  
                **添加日历** : https://ctftime.org/event/2327.ics  
                
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
                
            ??? Quote "[UMDCTF 2024](https://umdctf.io/)"  
                [![](https://ctftime.org/media/events/logo_95.png){ width="200" align=left }](https://umdctf.io/)  
                **比赛名称** : [UMDCTF 2024](https://umdctf.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 06:00:00 - 2024-04-29 06:00:00 UTC+8  
                **比赛权重** : 48.92  
                **赛事主办** : UMDCSEC (https://ctftime.org/team/87711)  
                **添加日历** : https://ctftime.org/event/2323.ics  
                
            ??? Quote "[SpringForwardCTF](https://springforward.ctfd.io/)"  
                [![](https://ctftime.org/media/events/NICC-2-green.png){ width="200" align=left }](https://springforward.ctfd.io/)  
                **比赛名称** : [SpringForwardCTF](https://springforward.ctfd.io/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 05:00:00 - 2024-04-29 05:00:00 UTC+8  
                **比赛权重** : 22.40  
                **赛事主办** : G1tc_Gu4rdians (https://ctftime.org/team/202828)  
                **添加日历** : https://ctftime.org/event/2348.ics  
                
            ??? Quote "[Insomni'hack 2024](https://insomnihack.ch/contests/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://insomnihack.ch/contests/)  
                **比赛名称** : [Insomni'hack 2024](https://insomnihack.ch/contests/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-27 00:30:00 - 2024-04-27 11:00:00 UTC+8  
                **比赛权重** : 33.40  
                **赛事主办** : Insomni'hack Team (https://ctftime.org/team/104742)  
                **添加日历** : https://ctftime.org/event/2271.ics  
                
            ??? Quote "[cr3 CTF 2024](https://2024.cr3c.tf/)"  
                [![](https://ctftime.org/media/events/cr3ctf_2024.png){ width="200" align=left }](https://2024.cr3c.tf/)  
                **比赛名称** : [cr3 CTF 2024](https://2024.cr3c.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-26 21:00:00 - 2024-04-28 09:00:00 UTC+8  
                **比赛权重** : 23.96  
                **赛事主办** : cr3.mov (https://ctftime.org/team/242101)  
                **添加日历** : https://ctftime.org/event/2288.ics  
                
            ??? Quote "[D^3CTF 2024](https://d3c.tf/)"  
                [![](https://ctftime.org/media/events/ddd.png){ width="200" align=left }](https://d3c.tf/)  
                **比赛名称** : [D^3CTF 2024](https://d3c.tf/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-26 20:00:00 - 2024-04-28 20:00:00 UTC+8  
                **比赛权重** : 39.40  
                **赛事主办** : D^3CTF Organizers (https://ctftime.org/team/91096)  
                **添加日历** : https://ctftime.org/event/2276.ics  
                
            ??? Quote "[Kernel Kombat](http://18.206.160.227/)"  
                [![](https://ctftime.org/media/events/jeclat.png){ width="200" align=left }](http://18.206.160.227/)  
                **比赛名称** : [Kernel Kombat](http://18.206.160.227/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-24 20:30:00 - 2024-04-25 02:30:00 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : S14y3r (https://ctftime.org/team/282208)  
                **添加日历** : https://ctftime.org/event/2359.ics  
                
            ??? Quote "[THJCC CTF](https://ctf-hobby.scint.org/)"  
                [![](https://ctftime.org/media/events/logo1_3.png){ width="200" align=left }](https://ctf-hobby.scint.org/)  
                **比赛名称** : [THJCC CTF](https://ctf-hobby.scint.org/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-23 10:01:30 - 2024-04-23 10:01:30 UTC+8  
                **比赛权重** : 0.00  
                **赛事主办** : CakeisTheFake (https://ctftime.org/team/276544)  
                **添加日历** : https://ctftime.org/event/2361.ics  
                
            ??? Quote "[openECSC 2024 - Round 2](https://open.ecsc2024.it/)"  
                [![](https://ctftime.org){ width="200" align=left }](https://open.ecsc2024.it/)  
                **比赛名称** : [openECSC 2024 - Round 2](https://open.ecsc2024.it/)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-22 18:00:00 - 2024-04-29 06:00:00 UTC+8  
                **比赛权重** : 0  
                **赛事主办** : ECSC2024 (https://ctftime.org/team/283828)  
                **添加日历** : https://ctftime.org/event/2354.ics  
                
            ??? Quote "[DawgCTF 2024](https://metactf.com/join/dawgctf24)"  
                [![](https://ctftime.org/media/events/ctfTimeLogo_2.png){ width="200" align=left }](https://metactf.com/join/dawgctf24)  
                **比赛名称** : [DawgCTF 2024](https://metactf.com/join/dawgctf24)  
                **比赛形式** : Jeopardy  
                **比赛时间** : 2024-04-21 00:00:00 - 2024-04-22 07:00:00 UTC+8  
                **比赛权重** : 46.57  
                **赛事主办** : UMBC Cyber Dawgs (https://ctftime.org/team/18405)  
                **添加日历** : https://ctftime.org/event/2343.ics  
                
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
