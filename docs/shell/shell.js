/* ============================================================
   Hello-CTF 共享外壳 shell.js
   用法：<script src="/shell/shell.js"></script>
         <script>Shell.mount({ active: "home" });</script>
   负责：注入图标 sprite、挂载侧边栏 + 项目动态面板 + 移动端按钮、
         主题切换、收起态、红点未读、导航翻页。
   页面级逻辑（日历、卡片等）由页面自己实现。
   ============================================================ */
(function () {
  "use strict";

  /* 全站导航定义（单一事实来源；增删入口只改这里） */
  const NAV = [
    { cap: "文档主体 · DOCS" },
    { key: "home",       icon: "i-home",     label: "首页",     href: "/",                        idx: "01" },
    { key: "start",      icon: "i-flag",     label: "开始阅读", href: "/contents/",                 idx: "02" },
    { key: "directions", icon: "i-globe",    label: "方向一览", href: "/sidebar/directions.html", idx: "03" },
    { cap: "工具 · TOOLS" },
    { key: "tools",      icon: "i-toolbox",  label: "工具一览", href: "/sidebar/tools.html" },
    { cap: "技能 · SKILL" },
    { key: "skill",      icon: "i-tree",     label: "技能树",   href: "/sidebar/ctf-skill.html" },
    { cap: "赛事 · EVENTS" },
    { key: "events",     icon: "i-calendar", label: "赛事日历", href: "/sidebar/events.html" },
    { key: "archives",   icon: "i-archive",  label: "历史比赛", href: "/sidebar/archives.html" },
    { cap: "其他 · MORE" },
    { key: "feedback",   icon: "i-users",    label: "反馈与群聊", href: "/sidebar/feedback.html" },
    { key: "about",      icon: "i-zap",      label: "关于",     href: "/hc-preface/about/" }
  ];

  function icon(id, cls) {
    return '<svg class="' + (cls || "ic") + '"><use href="#' + id + '"/></svg>';
  }

  const FEED_PANEL_HTML =
    '<div class="feed-panel" id="feedPanel" hidden>' +
      '<div class="fp-cap">ANNOUNCEMENTS · 公告</div>' +
      '<div id="fpAnnounce"><div class="fp-item">加载中…</div></div>' +
      '<div class="fp-cap" style="padding-top:14px">GIT LOG · 项目更新动态</div>' +
      '<div id="fpCommits"><div class="fp-item">加载中…</div></div>' +
      '<div class="fp-note"># 公告来自 index_content.json · 动态来自 GitHub commits</div>' +
    '</div>';

  function buildSidebar(active) {
    const items = NAV.map(item => {
      if (item.cap) return '<div class="nav-cap">' + item.cap + "</div>";
      const on = item.key === active ? " on" : "";
      const ext = item.ext ? ' target="_blank" rel="noopener"' : "";
      const idx = item.idx ? '<span class="idx">' + item.idx + "</span>" : "";
      return '<a class="nav-item' + on + '" href="' + item.href + '"' + ext + '>' +
        icon(item.icon) + item.label + idx + "</a>";
    }).join("\n");

    return '' +
    '<button class="menu-btn" id="menuBtn" aria-label="菜单">☰</button>' +
    '<div class="overlay" id="overlay"></div>' +
    '<aside class="sidebar" id="sidebar">' +
      '<a class="logo" href="/"><span class="mark">' + icon("i-flag") + '</span>Hello<em>CTF</em></a>' +
      '<a class="nav-item" id="searchToggle" style="cursor:pointer">' + icon("i-search") + '搜索 <span class="idx">Ctrl+K</span></a>' +
      '<a class="nav-item" id="feedToggle">' + icon("i-mega") + '项目动态 <span class="feed-badge" id="feedBadge" hidden>0</span></a>' +
      '<div class="nav-wrap"><nav class="nav" id="navScroll">' + items + '</nav>' +
      '<button class="nav-btn up" id="navUp" hidden aria-label="向上翻">' + icon("i-chev-up") + '</button>' +
      '<button class="nav-btn down" id="navDown" hidden aria-label="向下翻">' + icon("i-chev-down") + '</button></div>' +
      '<div class="side-foot">' +
        '<button class="theme-btn collapse-btn" id="collapseBtn"><svg class="ic" id="collapseIcon"><use href="#i-arrow"/></svg><span id="collapseLabel">收起侧边栏</span></button>' +
        '<button class="theme-btn" id="themeBtn"><svg class="ic" id="themeIcon"><use href="#i-moon"/></svg><span id="themeLabel">切换深色模式</span></button>' +
      '</div>' +
    '</aside>' +
    FEED_PANEL_HTML;
  }

  /* ---------- 图标 sprite 注入（sessionStorage 缓存，二次访问零延迟） ---------- */
  function insertSvg(svg) {
    const holder = document.createElement("div");
    holder.style.display = "none";
    holder.setAttribute("aria-hidden", "true");
    holder.innerHTML = svg;
    document.body.prepend(holder);
  }
  function injectIcons() {
    try {
      const cached = sessionStorage.getItem("hc-icons");
      if (cached) { insertSvg(cached); return Promise.resolve(); }
    } catch (e) {}
    return fetch("/shell/icons.svg")
      .then(r => r.text())
      .then(svg => {
        insertSvg(svg);
        try { sessionStorage.setItem("hc-icons", svg); } catch (e) {}
      })
      .catch(() => {});
  }

  /* ---------- 行为 ---------- */
  function wireTheme() {
    const btn = document.getElementById("themeBtn");
    const label = document.getElementById("themeLabel");
    const iconUse = document.querySelector("#themeIcon use");
    const saved = localStorage.getItem("hc-theme");
    if (saved === "dark") apply("dark");
    btn.onclick = () => apply(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
    function apply(t) {
      document.documentElement.dataset.theme = t;
      /* Tailwind darkMode:'class' 桥接：独立页（tools/skill/archives 等）跟随切换 */
      document.documentElement.classList.toggle("dark", t === "dark");
      localStorage.setItem("hc-theme", t);
      iconUse.setAttribute("href", t === "dark" ? "#i-sun" : "#i-moon");
      label.textContent = t === "dark" ? "切换浅色模式" : "切换深色模式";
      /* 与 mkdocs-material 的 palette 联动（文档页注入时） */
      if (window.__md_palette_sync) window.__md_palette_sync(t);
      /* 广播主题变化（giscus 等外部组件监听） */
      document.dispatchEvent(new CustomEvent("hc-theme-change", { detail: t }));
    }
  }

  function wireRail() {
    document.querySelectorAll(".nav-item").forEach(item => {
      const t = Array.from(item.childNodes).find(n => n.nodeType === 3 && n.textContent.trim());
      if (t) item.dataset.label = t.textContent.trim();
    });
    if (localStorage.getItem("hc-rail") === "1") document.body.classList.add("rail");
    document.getElementById("collapseBtn").onclick = () => {
      document.body.classList.toggle("rail");
      localStorage.setItem("hc-rail", document.body.classList.contains("rail") ? "1" : "0");
    };
  }

  function wireNavScroll() {
    const nav = document.getElementById("navScroll");
    const up = document.getElementById("navUp");
    const down = document.getElementById("navDown");
    function update() {
      up.hidden = nav.scrollTop <= 4;
      down.hidden = nav.scrollTop + nav.clientHeight >= nav.scrollHeight - 4;
    }
    if (!nav.dataset.wired) {   /* 幂等：文档树注入后会再次调用来重算 */
      nav.dataset.wired = "1";
      up.onclick = () => nav.scrollBy({ top: -220, behavior: "smooth" });
      down.onclick = () => nav.scrollBy({ top: 220, behavior: "smooth" });
      nav.addEventListener("scroll", update);
      window.addEventListener("resize", update);
    }
    update();
  }

  function wireMobile() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");
    document.getElementById("menuBtn").onclick = () => { sidebar.classList.add("open"); overlay.classList.add("show"); };
    overlay.onclick = () => { sidebar.classList.remove("open"); overlay.classList.remove("show"); };
  }

  function wireFeed(toggleSel) {
    const feedPanel = document.getElementById("feedPanel");
    const feedBadge = document.getElementById("feedBadge");
    let feedTotal = 0;
    function refreshBadge() {
      const seen = +(localStorage.getItem("hc-feed-seen") || 0);
      const unread = Math.max(0, feedTotal - seen);
      feedBadge.hidden = unread <= 0;
      feedBadge.textContent = unread;
    }
    refreshBadge();

    (async function loadFeed() {
      let total = 0;
      try {
        const data = await (await fetch("/index_content.json")).json();
        const lines = (data.announcement || "").split("\n").map(s => s.trim()).filter(Boolean).slice(0, 4);
        document.getElementById("fpAnnounce").innerHTML = lines.length
          ? lines.map(s =>
              '<div class="fp-item">' +
              s.replace(/\[([^\]]+)\]\([^)]*\)/g, "$1").replace(/[⭐🌟#*]/g, "").trim() +
              "</div>"
            ).join("")
          : '<div class="fp-item">暂无公告</div>';
        total += lines.length;
      } catch (e) {
        document.getElementById("fpAnnounce").innerHTML = '<div class="fp-item">公告加载失败</div>';
      }
      try {
        const commits = await (await fetch("https://api.github.com/repos/ProbiusOfficial/Hello-CTF/commits?per_page=5")).json();
        if (!Array.isArray(commits)) throw new Error("rate limited");
        document.getElementById("fpCommits").innerHTML = commits.map(c => {
          const msg = c.commit.message.split("\n")[0];
          const d = new Date(c.commit.committer.date);
          const date = String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
          return '<div class="fp-item"><span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + msg + '</span><span class="date">' + date + "</span></div>";
        }).join("");
        total += commits.length;
      } catch (e) {
        document.getElementById("fpCommits").innerHTML = '<div class="fp-item">commit 动态加载失败（可能无外网或被限流）</div>';
      }
      feedTotal = total;
      refreshBadge();
    })();

    const toggle = document.querySelector(toggleSel || "#feedToggle");
    if (toggle) toggle.onclick = () => {
      feedPanel.hidden = !feedPanel.hidden;
      if (!feedPanel.hidden) {
        localStorage.setItem("hc-feed-seen", feedTotal);
        feedBadge.hidden = true;
      }
    };
    document.addEventListener("click", e => {
      if (!feedPanel.hidden && !e.target.closest("#feedPanel") && !e.target.closest(toggleSel || "#feedToggle"))
        feedPanel.hidden = true;
    });
    document.addEventListener("keydown", e => { if (e.key === "Escape") feedPanel.hidden = true; });
  }

  /* ---------- 挂载入口 ---------- */
  window.Shell = {
    /* 完整外壳：侧边栏 + 项目动态（首页 / 独立页用） */
    mount(opts) {
      opts = opts || {};
      /* 先同步挂载侧栏骨架（图标 sprite 随后补齐），消除页面切换时的侧栏闪烁 */
      const frag = document.createElement("template");
      frag.innerHTML = buildSidebar(opts.active || "");
      document.body.prepend(frag.content);
      wireTheme();
      wireRail();
      wireNavScroll();
      wireMobile();
      wireFeed("#feedToggle");
      var st = document.getElementById("searchToggle");
      if (st && window.ShellSearch) st.onclick = function () { window.ShellSearch.open(); };
      injectIcons();
      document.body.classList.add("shell-mounted");
    },
    /* 仅项目动态面板：挂到页面里已有的按钮上（mkdocs 文档页头部用） */
    mountFeed(toggleSel) {
      injectIcons().then(() => {
        if (!document.getElementById("feedPanel")) {
          const frag = document.createElement("template");
          frag.innerHTML = FEED_PANEL_HTML;
          document.body.appendChild(frag.content);
        }
        wireFeed(toggleSel || "#feedToggle");
      });
    }
  };
})();
