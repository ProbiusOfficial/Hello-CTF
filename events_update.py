"""赛事数据维护：CTFtime RSS 抓取、国内赛事整理、ICS 日历生成。

数据文件全部在本仓库内：
- docs/Event/json/Global.json   国外赛事（CTFtime RSS）
- docs/Event/json/CN.json       国内赛事（手动 / admin 面板维护）
- docs/Event/json/CN_archive.json  结束超 60 天的国内赛事存档
- docs/Event/calendar/{CN,Global}.ics  日历订阅

注意：feedparser 在 fetch_global() 内部导入，admin 面板不装 feedparser
也能 import 本模块复用国内赛事的时间/状态工具函数。
"""
import hashlib
import json
import os
import re
from datetime import datetime, timedelta

import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "docs", "Event", "json")
CAL_DIR = os.path.join(BASE_DIR, "docs", "Event", "calendar")

GLOBAL_JSON = os.path.join(JSON_DIR, "Global.json")
CN_JSON = os.path.join(JSON_DIR, "CN.json")
CN_ARCHIVE_JSON = os.path.join(JSON_DIR, "CN_archive.json")

RSS_FEEDS = [
    ("https://ctftime.org/event/list/upcoming/rss/", "oncoming"),
    ("https://ctftime.org/event/list/running/rss/", "nowrunning"),
    ("https://ctftime.org/event/list/archive/rss/", "past"),
]

HTTP_TIMEOUT = 30
HTTP_RETRIES = 3
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

ARCHIVE_AFTER_DAYS = 60
CN_TIME_FMT = "%Y年%m月%d日 %H:%M"


# ---------- 国内赛事时间 / 状态工具 ----------

def utc8_now():
    return datetime.utcnow() + timedelta(hours=8)


def parse_cn_time(s):
    """'2026年07月17日 19:00' -> datetime（UTC+8 墙钟时间）。"""
    return datetime.strptime(s, CN_TIME_FMT)


def cn_derived_status(event):
    """由比赛时间推导三档状态：即将开始 / 正在进行 / 已经结束。"""
    now = utc8_now()
    try:
        start = parse_cn_time(event["comp_time_start"])
        end = parse_cn_time(event["comp_time_end"])
    except (ValueError, TypeError, KeyError):
        return "即将开始"
    if now < start:
        return "即将开始"
    if now <= end:
        return "正在进行"
    return "已经结束"


# ---------- 国外赛事：CTFtime RSS ----------

def _fetch_feed(rss_url):
    """requests 拉字节流（UA/超时/重试），返回 bytes；失败返回 None。"""
    import feedparser  # 延迟导入，见模块 docstring

    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            resp = requests.get(
                rss_url,
                headers={"User-Agent": USER_AGENT},
                timeout=HTTP_TIMEOUT,
            )
            resp.raise_for_status()
            return feedparser.parse(resp.content)
        except Exception as e:
            print(f"RSS 获取失败（{attempt}/{HTTP_RETRIES}）{rss_url}: {e}")
    return None


def _parse_global_entry(entry, status):
    start_str = getattr(entry, "start_date", None)
    finish_str = getattr(entry, "finish_date", None)
    if not start_str or not finish_str:
        return None
    start = datetime.strptime(start_str, "%Y%m%dT%H%M%S") + timedelta(hours=8)
    finish = datetime.strptime(finish_str, "%Y%m%dT%H%M%S") + timedelta(hours=8)
    time_range = (
        f'{start.strftime("%Y-%m-%d %H:%M:%S")} - '
        f'{finish.strftime("%Y-%m-%d %H:%M:%S")} UTC+8'
    )

    # 描述里的 [add to calendar] 链接
    add_calendar = None
    description = getattr(entry, "description", "")
    marker = description.find("[add to calendar]")
    if marker != -1:
        link_start = description.rfind('href="', 0, marker) + 6
        link_end = description.find('"', link_start)
        if link_start >= 6 and link_end != -1:
            add_calendar = description[link_start:link_end]
            if add_calendar.startswith("/"):
                add_calendar = "https://ctftime.org" + add_calendar

    try:
        organizers = json.loads(getattr(entry, "organizers", "[]"))
    except (json.JSONDecodeError, TypeError):
        organizers = []
    names = ", ".join(o.get("name", "Unknown") for o in organizers)
    urls = ", ".join(
        f'https://ctftime.org/team/{o["id"]}' for o in organizers if o.get("id")
    )
    organizer_str = f"{names} ({urls})" if names else ""

    logo_url = getattr(entry, "logo_url", "")
    return {
        "比赛名称": getattr(entry, "title", "Unknown Event"),
        "比赛时间": time_range,
        "添加日历": add_calendar,
        "比赛形式": getattr(entry, "format_text", ""),
        "比赛链接": getattr(entry, "url", ""),
        "比赛标志": f"https://ctftime.org{logo_url}" if logo_url else "",
        "比赛权重": getattr(entry, "weight", "0.00"),
        "赛事主办": organizer_str,
        "比赛ID": getattr(entry, "ctf_id", ""),
        "比赛状态": status,
    }


def _fetch_global_feed(rss_url, status):
    feed = _fetch_feed(rss_url)
    if feed is None or not feed.entries:
        print(f"RSS 源无有效内容：{rss_url}")
        return None
    events = []
    for entry in feed.entries:
        try:
            event = _parse_global_entry(entry, status)
            if event:
                events.append(event)
        except Exception as e:
            print(f'跳过无法解析的条目 "{getattr(entry, "title", "Unknown")}": {e}')
    return events


def fetch_global():
    """抓取 CTFtime 三个 RSS 源，合并写入 Global.json。全失败时保留旧文件。"""
    all_events = []
    ok = False
    for rss_url, status in RSS_FEEDS:
        events = _fetch_global_feed(rss_url, status)
        if events is None:
            continue
        ok = True
        all_events.extend(events)
    if not ok:
        print("国外赛事三个源全部失败，保留旧 Global.json")
        return False
    with open(GLOBAL_JSON, "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=4)
        f.write("\n")
    print(f"国外赛事已更新：{len(all_events)} 条")
    return True


# ---------- 国内赛事：归档 / 状态 / 排序 ----------

def maintain_cn():
    """归档结束超 60 天的赛事，刷新 status 字段并排序。"""
    with open(CN_JSON, "r", encoding="utf-8") as f:
        cn = json.load(f)
    try:
        with open(CN_ARCHIVE_JSON, "r", encoding="utf-8") as f:
            archive = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        archive = {"archive": {"result": []}}

    now = utc8_now()
    result = cn["data"]["result"]
    kept = []
    for event in result:
        try:
            end = parse_cn_time(event["comp_time_end"])
        except (ValueError, TypeError, KeyError):
            kept.append(event)  # 时间无法解析的不归档，人工处理
            continue
        if now > end + timedelta(days=ARCHIVE_AFTER_DAYS):
            print(f'{event.get("name", "?")} 已结束超过 {ARCHIVE_AFTER_DAYS} 天，移至存档')
            archive["archive"]["result"].append(event)
        else:
            kept.append(event)

    status_order = {"即将开始": 0, "正在进行": 1, "已经结束": 2}
    for event in kept:
        event["status"] = cn_derived_status(event)
    kept.sort(
        key=lambda e: (
            status_order.get(e["status"], 3),
            e.get("comp_time_start", ""),
        )
    )

    cn["data"]["result"] = kept
    cn["data"]["total"] = len(kept)

    with open(CN_JSON, "w", encoding="utf-8") as f:
        json.dump(cn, f, ensure_ascii=False, indent=4)
        f.write("\n")
    with open(CN_ARCHIVE_JSON, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=4)
        f.write("\n")
    print(f"国内赛事已整理：{len(kept)} 条在列")
    return True


# ---------- ICS 日历 ----------

def _cn_ical_event(event):
    try:
        start = parse_cn_time(event["comp_time_start"]) - timedelta(hours=8)
        finish = parse_cn_time(event["comp_time_end"]) - timedelta(hours=8)
    except (ValueError, TypeError, KeyError) as e:
        print(f'跳过无法生成日历的国内赛事 "{event.get("name", "Unknown")}": {e}')
        return None
    desc = re.sub(r"\s+", "", str(event.get("detail") or ""))
    link = event.get("link", "")
    return {
        "SUMMARY": event["name"],
        "DTSTART": start.strftime("%Y%m%dT%H%M%SZ"),
        "DTEND": finish.strftime("%Y%m%dT%H%M%SZ"),
        "UID": hashlib.md5(event["name"].encode("utf-8")).hexdigest(),
        "DTSTAMP": datetime.now().strftime("%Y%m%dT%H%M%SZ"),
        "URL": link,
        "DESCRIPTION": f"{link} | {desc}",
    }


def _global_ical_event(event):
    try:
        start_str, end_str = event["比赛时间"].replace(" UTC+8", "").split(" - ")
        start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)
        finish = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)
    except (ValueError, TypeError, KeyError) as e:
        print(f'跳过无法生成日历的国外赛事 "{event.get("比赛名称", "Unknown")}": {e}')
        return None
    return {
        "SUMMARY": event["比赛名称"],
        "DTSTART": start.strftime("%Y%m%dT%H%M%SZ"),
        "DTEND": finish.strftime("%Y%m%dT%H%M%SZ"),
        "UID": hashlib.md5(event["比赛名称"].encode("utf-8")).hexdigest(),
        "DTSTAMP": datetime.now().strftime("%Y%m%dT%H%M%SZ"),
        "URL": event["比赛链接"],
        "DESCRIPTION": (
            f'{event["比赛形式"]} | {event["比赛链接"]} | '
            f'比赛ID - {event["比赛ID"]}'
        ),
    }


def _write_ics(path, cal_name, events):
    with open(path, "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\n")
        f.write("VERSION:2.0\n")
        f.write(f"PRODID:-//Hello-CTF//{cal_name}//\n")
        f.write("CALSCALE:GREGORIAN\n")
        f.write(f"X-WR-CALNAME:{cal_name}\n")
        for event in events:
            f.write("BEGIN:VEVENT\n")
            for key, value in event.items():
                f.write(f"{key}:{value}\n")
            f.write("END:VEVENT\n")
        f.write("END:VCALENDAR\n")


def write_ics():
    """由 CN.json / Global.json 生成日历订阅文件。"""
    os.makedirs(CAL_DIR, exist_ok=True)
    try:
        with open(CN_JSON, "r", encoding="utf-8") as f:
            cn = json.load(f)
        cn_events = [
            e for e in (_cn_ical_event(ev) for ev in cn["data"]["result"]) if e
        ]
        _write_ics(os.path.join(CAL_DIR, "CN.ics"), "CN", cn_events)
    except Exception as e:
        print(f"生成 CN.ics 失败：{e}")
        return False
    try:
        with open(GLOBAL_JSON, "r", encoding="utf-8") as f:
            global_events = json.load(f)
        ical_events = [
            e for e in (_global_ical_event(ev) for ev in global_events) if e
        ]
        _write_ics(os.path.join(CAL_DIR, "Global.ics"), "Global", ical_events)
    except Exception as e:
        print(f"生成 Global.ics 失败：{e}")
        return False
    print("ICS 日历已生成")
    return True
