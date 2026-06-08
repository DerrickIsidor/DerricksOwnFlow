/**
 * DerricksOwnFlow — Shared Navigation
 *
 * This file injects the cross-page world-switcher nav bar into every page.
 * It only needs to exist in ONE place — update this file to change the nav
 * on ALL four pages at once.
 *
 * HOW TO USE ON A PAGE:
 *   1. Add this before your closing </body> tag:
 *      <script src="assets/shared.js"></script>
 *
 *   2. Call initSharedNav() in your page's script:
 *      initSharedNav('home');   // or 'flow', 'dj', 'data'
 *
 *   3. For light-themed pages (dataflow), pass the theme:
 *      initSharedNav('data', { theme: 'light' });
 *
 * HOW TO ADD A NEW WORLD:
 *   Add an entry to the WORLDS array below, then add initSharedNav('your-id')
 *   to the new page. That's it.
 */

(function () {

  // ── WORLD DEFINITIONS ─────────────────────────────────────────────────────
  // Edit this array to change nav labels, links, or accent colors.
  var WORLDS = [
    { id: 'home', label: 'Derrick.',  href: 'index.html',             color: '#F2E8D9' },
    { id: 'flow', label: 'Own Flow',  href: 'derricks-own-flow.html', color: '#EF7B2B' },
    { id: 'dj',   label: 'DJ Flow',   href: 'dj-flow.html',           color: '#D4FF00' },
    { id: 'data', label: 'DataFlow',  href: 'dataflow.html',          color: '#1A6BFF' },
  ];

  // Theme presets — extend if you add new page themes
  var THEMES = {
    dark:       { background: 'rgba(10,8,6,0.88)',    border: 'rgba(242,232,217,0.08)' },
    dark_warm:  { background: 'rgba(26,18,8,0.92)',   border: 'rgba(242,232,217,0.07)' },
    dark_black: { background: 'rgba(8,8,8,0.92)',     border: 'rgba(212,255,0,0.08)'   },
    light:      { background: 'rgba(250,250,248,0.94)', border: 'rgba(44,43,39,0.08)'  },
  };

  // Which theme each world uses by default
  var DEFAULT_THEMES = {
    home: 'dark',
    flow: 'dark_warm',
    dj:   'dark_black',
    data: 'light',
  };

  /**
   * Inject the world-switcher nav bar immediately after the page's <nav>.
   *
   * @param {string} activeId  — ID of the current world: 'home'|'flow'|'dj'|'data'
   * @param {object} opts      — Optional overrides
   *   opts.theme      — 'dark'|'dark_warm'|'dark_black'|'light' (auto-detected if omitted)
   *   opts.background — Raw CSS background string (overrides theme)
   *   opts.border     — Raw CSS border-color string (overrides theme)
   */
  function initSharedNav(activeId, opts) {
    opts = opts || {};

    var themeName = opts.theme || DEFAULT_THEMES[activeId] || 'dark';
    var preset    = THEMES[themeName] || THEMES.dark;
    var bg        = opts.background || preset.background;
    var border    = opts.border     || preset.border;

    var bar = document.createElement('div');
    bar.id  = 'world-nav';
    bar.setAttribute('style', [
      'position:sticky',
      'top:60px',
      'z-index:90',
      'width:100%',
      'background:' + bg,
      'border-bottom:0.5px solid ' + border,
      'display:flex',
      'align-items:center',
      'justify-content:center',
      'gap:32px',
      'padding:10px 40px',
      'backdrop-filter:blur(12px)',
    ].join(';') + ';');

    WORLDS.forEach(function (w) {
      var isActive = (w.id === activeId);

      var a = document.createElement('a');
      a.href = (opts.basePath || '') + w.href;
      a.setAttribute('style', [
        'display:flex',
        'align-items:center',
        'gap:6px',
        'text-decoration:none',
        'font-family:system-ui,-apple-system,sans-serif',
        'font-size:11px',
        'font-weight:500',
        'letter-spacing:0.12em',
        'text-transform:uppercase',
        'color:' + w.color,
        'opacity:' + (isActive ? '1' : '0.45'),
        'transition:opacity 0.2s',
      ].join(';') + ';');

      a.addEventListener('mouseover', function () { this.style.opacity = '1'; });
      a.addEventListener('mouseout',  function () { this.style.opacity = isActive ? '1' : '0.45'; });

      var dot = document.createElement('span');
      dot.setAttribute('style', [
        'width:6px',
        'height:6px',
        'border-radius:50%',
        'background:' + w.color,
        'display:inline-block',
        'opacity:' + (isActive ? '1' : '0.35'),
        'flex-shrink:0',
      ].join(';') + ';');

      a.appendChild(dot);
      a.appendChild(document.createTextNode(w.label));
      bar.appendChild(a);
    });

    var mainNav = document.querySelector('nav');
    if (mainNav) {
      mainNav.insertAdjacentElement('afterend', bar);
    } else {
      document.body.insertBefore(bar, document.body.firstChild);
    }
  }

  window.initSharedNav = initSharedNav;

})();
