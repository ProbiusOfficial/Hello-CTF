"""Hello-CTF 数据更新脚本。

负责赛事数据维护，全部数据在本仓库内生成：
- 国外赛事：直接抓取 CTFtime RSS -> docs/Event/json/Global.json
- 国内赛事：归档 / 状态刷新 / 排序 -> docs/Event/json/CN.json(+CN_archive.json)
- 日历订阅：docs/Event/calendar/{CN,Global}.ics

单个环节失败只告警不中断。注意国内网络可能访问不了 ctftime.org，
此时国外赛事保留旧数据，由 GitHub Action 的每日任务更新。
"""
import events_update


def main():
    for label, func in [
        ("国外赛事抓取", events_update.fetch_global),
        ("国内赛事整理", events_update.maintain_cn),
        ("ICS 日历生成", events_update.write_ics),
    ]:
        try:
            func()
        except Exception as e:
            print(f"{label}失败：{e}")


if __name__ == "__main__":
    main()
