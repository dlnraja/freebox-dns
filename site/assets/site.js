(function () {
  'use strict';

  /* Mobile nav toggle */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* Mermaid init (only when diagrams present) */
  if (typeof mermaid !== 'undefined' && document.querySelector('.mermaid')) {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'base',
      themeVariables: {
        primaryColor: '#E8F4F2',
        primaryTextColor: '#0B3D3A',
        primaryBorderColor: '#0B3D3A',
        lineColor: '#145751',
        secondaryColor: '#ffffff',
        tertiaryColor: '#d4ebe6',
        fontFamily: '"Source Sans 3", system-ui, sans-serif'
      },
      flowchart: { curve: 'basis', padding: 16 }
    });
  }
})();
