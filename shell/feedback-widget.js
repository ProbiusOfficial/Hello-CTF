/* ============================================================
   Hello-CTF 全站反馈小喇叭 feedback-widget.js
   自挂载：shell 页面由 shell.js 注入，mkdocs 文档页由 extra_javascript 引入。
   右下角小喇叭 → 弹出反馈框，自动带上当前页面 URL，提交到消息收集器。
   明暗主题自适应（跟随站点主题，实时监听切换）。
   ============================================================ */
(function () {
  "use strict";
  if (window.__hcFbWidget) return; // 防重复挂载
  window.__hcFbWidget = true;

  var ENDPOINT = "https://helloctfmsg.cyclens.tech/api/submit";

  var css = `
  #hc-fb-btn {
    position: fixed; right: 22px; bottom: 22px; z-index: 9999;
    width: 46px; height: 46px; border-radius: 50%; border: none; cursor: pointer;
    background: #0f172a; color: #fff; box-shadow: 0 10px 24px -8px rgba(15,23,42,.4);
    display: flex; align-items: center; justify-content: center;
    transition: transform .15s ease, box-shadow .15s ease, background .2s, color .2s;
  }
  #hc-fb-btn:hover { transform: translateY(-2px) scale(1.05); }
  #hc-fb-btn svg { width: 20px; height: 20px; }
  #hc-fb-panel {
    --fb-bg: #ffffff; --fb-fg: #0f172a; --fb-muted: #64748b;
    --fb-field: #f1f5f9; --fb-line: #e2e8f0; --fb-accent: #2563eb;
    position: fixed; right: 22px; bottom: 80px; z-index: 9999;
    width: 360px; max-width: calc(100vw - 44px);
    background: var(--fb-bg); color: var(--fb-fg);
    border: 1px solid var(--fb-line); border-radius: 14px;
    box-shadow: 0 18px 48px -14px rgba(15,23,42,.28);
    padding: 16px; font-family: Inter, system-ui, sans-serif;
    transition: background .2s, color .2s, border-color .2s;
  }
  #hc-fb-panel.dark {
    --fb-bg: #0f172a; --fb-fg: #e2e8f0; --fb-muted: #94a3b8;
    --fb-field: #1e293b; --fb-line: #334155; --fb-accent: #60a5fa;
    box-shadow: 0 18px 48px -12px rgba(0,0,0,.6);
  }
  #hc-fb-panel .t { font-size: 14px; font-weight: 700; margin-bottom: 4px; }
  #hc-fb-panel .pg {
    font-size: 11px; color: var(--fb-muted); margin-bottom: 10px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  #hc-fb-panel textarea {
    width: 100%; min-height: 130px; resize: vertical; box-sizing: border-box;
    font: inherit; font-size: 13.5px; line-height: 1.6;
    background: var(--fb-field); color: var(--fb-fg);
    border: 1px solid var(--fb-line); border-radius: 8px; padding: 9px 11px; outline: none;
    transition: border-color .15s, background .2s, color .2s;
  }
  #hc-fb-panel textarea:focus { border-color: var(--fb-accent); }
  #hc-fb-panel .ops { display: flex; align-items: center; gap: 8px; margin-top: 10px; }
  #hc-fb-panel .send {
    font: inherit; font-size: 13px; font-weight: 700; cursor: pointer;
    background: var(--fb-accent); color: #fff; border: none; border-radius: 8px; padding: 7px 16px;
  }
  #hc-fb-panel .send[disabled] { opacity: .5; cursor: not-allowed; }
  #hc-fb-panel .cancel {
    font: inherit; font-size: 13px; cursor: pointer;
    background: none; color: var(--fb-muted); border: none; padding: 7px 8px;
  }
  #hc-fb-panel .st { font-size: 12px; margin-left: auto; }
  #hc-fb-panel .st.ok { color: #16a34a; }
  #hc-fb-panel .st.err { color: #dc2626; }
  #hc-fb-panel.dark .st.ok { color: #4ade80; }
  #hc-fb-panel.dark .st.err { color: #f87171; }
  `;

  /* 站点主题判定：shell 页面暗色时才设 data-theme，Material 文档页用 data-md-color-scheme。
     不做系统主题回退——站点自身有明确主题控制，默认即亮色。 */
  function siteIsDark() {
    var el = document.documentElement;
    if (el.dataset.theme) return el.dataset.theme === "dark";
    if (el.dataset.mdColorScheme) return el.dataset.mdColorScheme === "slate";
    if (document.body && document.body.dataset.mdColorScheme) {
      return document.body.dataset.mdColorScheme === "slate";
    }
    return false;
  }

  function mount() {
    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);

    var btn = document.createElement("button");
    btn.id = "hc-fb-btn";
    btn.title = "反馈 / 勘误";
    btn.setAttribute("aria-label", "反馈");
    btn.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="M3 11l18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/></svg>';
    document.body.appendChild(btn);

    var panel = document.createElement("div");
    panel.id = "hc-fb-panel";
    panel.hidden = true;
    panel.innerHTML =
      '<div class="t">反馈 / 勘误</div>' +
      '<div class="pg" id="hc-fb-page"></div>' +
      '<textarea id="hc-fb-text" placeholder="这页哪里有问题、想说什么，直接写…"></textarea>' +
      '<div class="ops">' +
        '<button class="send" id="hc-fb-send">发送</button>' +
        '<button class="cancel" id="hc-fb-cancel">取消</button>' +
        '<span class="st" id="hc-fb-st"></span>' +
      "</div>";
    document.body.appendChild(panel);

    /* 主题跟随：面板换肤；按钮保持固定深色（站点视觉锚点，不随主题变） */
    function syncTheme() {
      panel.classList.toggle("dark", siteIsDark());
    }
    syncTheme();
    new MutationObserver(syncTheme).observe(document.documentElement, {
      attributes: true, attributeFilter: ["data-theme", "data-md-color-scheme"],
    });

    var text = panel.querySelector("#hc-fb-text");
    var st = panel.querySelector("#hc-fb-st");
    var send = panel.querySelector("#hc-fb-send");

    btn.onclick = function () {
      panel.hidden = !panel.hidden;
      if (!panel.hidden) {
        panel.querySelector("#hc-fb-page").textContent =
          "当前页面：" + document.title;
        st.textContent = "";
        text.focus();
      }
    };
    panel.querySelector("#hc-fb-cancel").onclick = function () {
      panel.hidden = true;
    };

    send.onclick = async function () {
      var v = text.value.trim();
      if (!v) {
        st.className = "st err";
        st.textContent = "先写点内容";
        return;
      }
      send.disabled = true;
      st.className = "st";
      st.textContent = "发送中…";
      try {
        var res = await fetch(ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            type: "feedback",
            title: "页面反馈 · " + document.title,
            content: v + "\n\n———\n页面：" + location.href,
          }),
        });
        if (!res.ok) throw new Error("HTTP " + res.status);
        text.value = "";
        st.className = "st ok";
        st.textContent = "已收到，感谢！";
        setTimeout(function () { panel.hidden = true; }, 1200);
      } catch (e) {
        st.className = "st err";
        st.textContent = "发送失败，请稍后再试";
      } finally {
        send.disabled = false;
      }
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
