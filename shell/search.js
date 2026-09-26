/* ============================================================
   Hello-CTF 全站搜索 shell/search.js（首页 / 文档页 / 独立页共用）
   数据源：mkdocs 构建产物 /search/search_index.json（懒加载，仅首次打开时拉取）
   匹配：AND 子串匹配 + 标题加权（对中文天然友好，不依赖英文分词）
   用法：引入脚本后自动注册 Ctrl+K / Cmd+K；调用 ShellSearch.open() 打开。
   ============================================================ */
(function () {
  "use strict";

  var CSS = `
  .hs-mask{position:fixed;inset:0;z-index:100;background:rgba(15,23,42,.42);
    -webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);
    display:flex;justify-content:center;align-items:flex-start;padding:12vh 16px 16px;
    animation:hs-fade .14s ease}
  @keyframes hs-fade{from{opacity:0}to{opacity:1}}
  .hs-box{width:min(640px,100%);background:var(--paper,#fff);border:1px solid var(--line,#e6eaf1);
    border-radius:16px;box-shadow:0 24px 60px -20px rgba(15,23,42,.4);overflow:hidden;
    animation:hs-pop .16s ease}
  @keyframes hs-pop{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
  .hs-inputrow{display:flex;align-items:center;gap:10px;padding:14px 18px;
    border-bottom:1px solid var(--line,#e6eaf1)}
  .hs-inputrow .p{font-family:var(--mono,monospace);color:var(--accent,#2563eb);font-weight:700}
  .hs-input{flex:1;border:none;outline:none;background:transparent;color:var(--ink,#0f172a);
    font:15px/1.5 var(--sans,sans-serif)}
  .hs-input::placeholder{color:var(--ink-3,#94a3b8)}
  .hs-kbd{font-family:var(--mono,monospace);font-size:10.5px;color:var(--ink-3,#94a3b8);
    border:1px solid var(--line,#e6eaf1);border-radius:6px;padding:2px 7px}
  .hs-list{max-height:52vh;overflow-y:auto;scrollbar-width:thin}
  .hs-item{display:block;padding:11px 18px;border-bottom:1px dashed var(--line,#e6eaf1);cursor:pointer;text-decoration:none}
  .hs-item:last-child{border-bottom:none}
  .hs-item.sel,.hs-item:hover{background:var(--wash,#f8fafc)}
  .hs-item .t{font-weight:700;font-size:14px;color:var(--ink,#0f172a)}
  .hs-item .loc{font-family:var(--mono,monospace);font-size:10.5px;color:var(--ink-3,#94a3b8);margin-top:1px}
  .hs-item .s{font-size:12.5px;color:var(--ink-2,#475569);margin-top:3px;line-height:1.6}
  .hs-item mark{background:linear-gradient(transparent 60%,var(--hl,#bfdbfe) 60%);color:inherit;padding:0}
  .hs-empty{padding:22px 18px;font-size:13px;color:var(--ink-3,#94a3b8);text-align:center}
  .hs-foot{display:flex;gap:14px;padding:8px 18px;border-top:1px solid var(--line,#e6eaf1);
    font-family:var(--mono,monospace);font-size:10.5px;color:var(--ink-3,#94a3b8)}
  `;

  var index = null;      /* [{location, title, text}]，text 已去 HTML */
  var loading = null;
  var modal = null, input = null, list = null;
  var sel = 0, results = [];

  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function loadIndex() {
    if (index) return Promise.resolve(index);
    if (loading) return loading;
    loading = fetch("/search/search_index.json")
      .then(function (r) { return r.json(); })
      .then(function (d) {
        index = d.docs.map(function (x) {
          return {
            location: x.location,
            title: x.title || "",
            text: (x.text || "").replace(/<[^>]*>/g, " ").replace(/\s+/g, " ")
          };
        });
        return index;
      });
    return loading;
  }

  function search(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    var res = [];
    for (var i = 0; i < index.length; i++) {
      var doc = index[i];
      var t = doc.title.toLowerCase(), x = doc.text.toLowerCase();
      var score = 0, first = -1, ok = true;
      for (var j = 0; j < terms.length; j++) {
        var term = terms[j];
        var ti = t.indexOf(term), xi = x.indexOf(term);
        if (ti < 0 && xi < 0) { ok = false; break; }
        if (ti >= 0) score += 100 - Math.min(ti, 50);
        if (xi >= 0) {
          score += 10;
          if (first < 0 || xi < first) first = xi;
        }
      }
      if (!ok) continue;
      if (doc.location.indexOf("#") < 0) score += 3;   /* 页面级结果略优先于小节 */
      res.push({ doc: doc, score: score, first: first < 0 ? 0 : first });
    }
    res.sort(function (a, b) { return b.score - a.score; });
    return res.slice(0, 12);
  }

  function highlight(text, terms) {
    var out = esc(text);
    terms.forEach(function (term) {
      if (!term) return;
      var re = new RegExp("(" + term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
      out = out.replace(re, "<mark>$1</mark>");
    });
    return out;
  }

  function snippet(doc, terms, first) {
    var start = Math.max(0, first - 50);
    var s = doc.text.slice(start, start + 160);
    if (start > 0) s = "…" + s;
    if (start + 160 < doc.text.length) s += "…";
    return highlight(s, terms);
  }

  function render(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) {
      list.innerHTML = '<div class="hs-empty">输入关键词，搜索全部教程内容</div>';
      results = [];
      return;
    }
    results = search(q);
    sel = 0;
    if (!results.length) {
      list.innerHTML = '<div class="hs-empty">没有找到「' + esc(q) + '」相关内容</div>';
      return;
    }
    list.innerHTML = results.map(function (r, i) {
      return '<a class="hs-item' + (i === sel ? " sel" : "") + '" data-i="' + i + '" href="/' + r.doc.location + '">' +
        '<div class="t">' + highlight(r.doc.title, terms) + "</div>" +
        '<div class="loc">/' + esc(r.doc.location.split("#")[0]) + "</div>" +
        '<div class="s">' + snippet(r.doc, terms, r.first) + "</div>" +
      "</a>";
    }).join("");
  }

  function move(d) {
    if (!results.length) return;
    sel = (sel + d + results.length) % results.length;
    list.querySelectorAll(".hs-item").forEach(function (el, i) {
      el.classList.toggle("sel", i === sel);
    });
    var el = list.querySelector(".hs-item.sel");
    if (el) el.scrollIntoView({ block: "nearest" });
  }

  function open() {
    if (modal) { input.focus(); input.select(); return; }
    if (!document.getElementById("hs-style")) {
      var st = document.createElement("style");
      st.id = "hs-style";
      st.textContent = CSS;
      document.head.appendChild(st);
    }
    modal = document.createElement("div");
    modal.className = "hs-mask";
    modal.innerHTML =
      '<div class="hs-box">' +
        '<div class="hs-inputrow"><span class="p">/</span>' +
          '<input class="hs-input" placeholder="搜索知识点，如 SQL注入 / ROP / 隐写 …" autocomplete="off" spellcheck="false">' +
          '<span class="hs-kbd">ESC</span></div>' +
        '<div class="hs-list"><div class="hs-empty">索引加载中…</div></div>' +
        '<div class="hs-foot"><span>↑↓ 选择</span><span>↵ 打开</span><span>ESC 关闭</span><span style="margin-left:auto">Ctrl+K 全局唤起</span></div>' +
      "</div>";
    document.body.appendChild(modal);
    input = modal.querySelector(".hs-input");
    list = modal.querySelector(".hs-list");
    input.focus();

    loadIndex().then(function () {
      if (!input.value) list.innerHTML = '<div class="hs-empty">输入关键词，搜索全部教程内容</div>';
      else render(input.value);
    }).catch(function () {
      list.innerHTML = '<div class="hs-empty">搜索索引加载失败</div>';
    });

    input.addEventListener("input", function () {
      if (index) render(input.value);
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") {
        var el = list.querySelector(".hs-item.sel");
        if (el) window.location.href = el.getAttribute("href");
      }
    });
    modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
  }

  function close() {
    if (modal) { modal.remove(); modal = null; input = null; list = null; results = []; }
  }

  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      open();
    } else if (e.key === "Escape") {
      close();
    }
  });

  window.ShellSearch = { open: open, close: close };
})();
