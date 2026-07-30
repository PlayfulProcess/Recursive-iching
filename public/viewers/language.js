/* language.js — the 中文 / EN / both switch, shared by the static viewers.
 *
 * The data convention it reads is GRAMMAR_FORMAT.md, "Languages": an item's `sections`
 * is canonical — for these books, Chinese — and `sections_i18n.<lang>` mirrors its key
 * set exactly. So this file never needs to know which book it is looking at, or what
 * sections that book happens to have. It asks for a key and gets back what to print.
 *
 * The default is 中文, which is the behaviour the viewers had before this existed: the
 * original text is what the reader is offered unless they ask for otherwise. English is
 * James Legge's (1882/1899, public domain) — a Victorian Scot's reading of a Bronze Age
 * manual, offered beside the text rather than in place of it. Both books now have it: the
 * Zhouyi since 2026-07-27, the Ten Wings (his Appendixes I, II, IV and VI) since 07-30.
 *
 * One file rather than a copy per viewer, so the two cannot drift apart.
 */
(function (global) {
  'use strict';

  var KEY = 'recursive-iching:lang';
  var MODES = [
    { id: 'zh',   label: '中文',      hint: 'The books in their own language' },
    { id: 'en',   label: 'EN',        hint: "James Legge's public-domain English (1882/1899)" },
    { id: 'both', label: '中文 + EN', hint: 'The original and the translation together' }
  ];

  function known(id) { return MODES.some(function (m) { return m.id === id; }); }

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }   // file://, private mode
  }

  // A ?lang= in the URL wins (shared links carry their reading), then the last choice,
  // then the original text.
  var mode = new URLSearchParams(location.search).get('lang');
  if (!known(mode)) mode = stored();
  if (!known(mode)) mode = 'zh';

  var subscribers = [];

  function set(next) {
    if (!known(next) || next === mode) return;
    mode = next;
    try { localStorage.setItem(KEY, mode); } catch (e) { /* not fatal — the session still works */ }
    subscribers.forEach(function (fn) { fn(mode); });
  }

  var CSS = '' +
    '.langbar{display:inline-flex;border:1px solid var(--line-soft,#e3dccc);border-radius:999px;' +
      'overflow:hidden;background:var(--surface,#fff);vertical-align:middle}' +
    '.langbar button{border:none;background:transparent;padding:6px 14px;cursor:pointer;' +
      'font-family:inherit;font-size:.85rem;color:var(--ink,#2b2620);line-height:1.3}' +
    '.langbar button.on{background:var(--gold,#9a7322);color:#fff}' +
    '.langbar button:focus-visible{outline:2px solid var(--gold,#9a7322);outline-offset:-2px}' +
    '.lang-note{color:var(--mut,#7a7060);font-size:.78rem;font-style:italic;margin:.2em 0 .6em}' +
    '.lang-en{color:var(--ink,#2b2620)}' +
    '.lang-tag{display:block;font-size:.68rem;letter-spacing:.09em;text-transform:uppercase;' +
      'color:var(--mut,#7a7060);margin:.55em 0 .1em}';

  function injectCss() {
    if (document.getElementById('langbar-css')) return;
    var s = document.createElement('style');
    s.id = 'langbar-css';
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  /* Render the switch into `el` and call `onChange` whenever it moves. */
  function mount(el, onChange) {
    if (!el) return;
    injectCss();
    if (onChange) subscribers.push(onChange);
    function paint() {
      el.innerHTML = '<span class="langbar" role="group" aria-label="Reading language">' +
        MODES.map(function (m) {
          return '<button type="button" data-lang="' + m.id + '" title="' + m.hint + '"' +
            ' aria-pressed="' + (m.id === mode) + '"' +
            (m.id === mode ? ' class="on"' : '') + '>' + m.label + '</button>';
        }).join('') + '</span>';
      Array.prototype.forEach.call(el.querySelectorAll('button'), function (b) {
        b.onclick = function () { set(b.dataset.lang); };
      });
    }
    subscribers.push(paint);
    paint();
  }

  function english(item) {
    return (item && item.sections_i18n && item.sections_i18n.en) || null;
  }

  /* What to print for one section key, in reading order.
     Each entry: { lang: 'zh'|'en', text, tagged } — `tagged` asks the viewer for a small
     language label, which is only useful when both are on screen at once. */
  function passages(item, key) {
    var zh = (item && item.sections && item.sections[key]) || '';
    var en = english(item) ? item.sections_i18n.en[key] : '';
    if (mode === 'en') {
      // No English for this book: fall back to the text rather than print nothing. The
      // article-level note (see `missing`) is what tells the reader why.
      return en ? [{ lang: 'en', text: en, tagged: false }] : [{ lang: 'zh', text: zh, tagged: false }];
    }
    if (mode === 'both' && en) {
      return [{ lang: 'zh', text: zh, tagged: true }, { lang: 'en', text: en, tagged: true }];
    }
    return [{ lang: 'zh', text: zh, tagged: false }];
  }

  /* True when the reader asked for English and this book has none — the viewer should say
     so once, quietly, rather than let the fallback pass for a translation.

     As of 2026-07-30 neither of the books the readers show trips this: the Zhouyi and the
     Ten Wings both carry Legge. It stays for the books still on the rail (Wang Bi, Zhu Xi,
     Wilhelm's German), because the moment one lands is the moment a silent fallback would
     start reading like a translation. */
  function missing(item) {
    return mode !== 'zh' && !english(item);
  }

  var NOTE = 'No public-domain English for this book yet — showing the original.';

  global.Lang = {
    get: function () { return mode; },
    set: set,
    mount: mount,
    passages: passages,
    missing: missing,
    note: NOTE,
    /* For viewers that pull one section out by hand (the Caster) rather than looping. */
    text: function (item, key) {
      return passages(item, key).map(function (p) { return p.text; }).join('\n');
    },
    onChange: function (fn) { subscribers.push(fn); }
  };
})(window);
