// Professional Styling Auto-Injection Script
// This script automatically applies professional styling to pages that haven't been updated yet

(function() {
    'use strict';

    // Check if professional styling is already loaded
    if (document.querySelector('link[href*="professional_style.css"]') ||
        document.querySelector('.ql-header') ||
        (document.body && document.body.classList.contains('professional-styled'))) {
        return; // Already has professional styling
    }

    // Apply immediate dark theme to prevent white flash
    applyImmediateDarkTheme();

    // Inject professional CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/static/professional_style.css';
    if (document.head) {
        document.head.appendChild(link);
    }

    // Inject unified QR Legends theme CSS
    const unifiedTheme = document.createElement('style');
    unifiedTheme.innerHTML = `
        /* === QRLegends Unified Theme (Dark/Light) === */
        :root{
          --ql-bg: #0b1724;
          --ql-panel: #0f2340;
          --ql-card: #102846;
          --ql-text: #f0f4ff;
          --ql-sub: #c5d1e8;
          --ql-primary: #3b82f6;
          --ql-success: #22c55e;
          --ql-warning: #f59e0b;
          --ql-danger: #ef4444;
          --ql-accent: #6366f1;
          --ql-border: rgba(255,255,255,.2);
          --ql-surface: rgba(255,255,255,.1);
        }

        html,body{height:100%;}
        body{
          margin:0;
          background: radial-gradient(1200px 600px at 60% -100px, #123a86 0%, #0e2242 45%, #081b2e 100%) fixed !important;
          color: var(--ql-text) !important;
          font-family: Inter, ui-sans-serif, system-ui, Arial, sans-serif;
          line-height: 1.45;
          min-height: 100vh;
        }

        .ql-header{
          position: sticky; top:0; z-index:1000;
          background: rgba(8,27,46,.7);
          backdrop-filter: blur(6px);
          border-bottom: 1px solid var(--ql-border);
        }

        .ql-header-inner{
          display:flex; align-items:center; justify-content:space-between;
          max-width:1200px; margin:0 auto; padding:14px 20px;
        }

        .ql-title{display:flex; align-items:center; gap:10px;}
        .ql-h1{font-size:1.25rem; margin:0; letter-spacing:.2px; color: var(--ql-text);}
        .ql-nav{display:flex; gap:8px; flex-wrap:wrap;}

        .ql-btn{
          display:inline-block; padding:8px 12px; border-radius:10px; text-decoration:none;
          color:var(--ql-text); background: var(--ql-surface); border: 1px solid var(--ql-border);
          box-shadow: 0 1px 0 rgba(255,255,255,.05) inset, 0 4px 14px rgba(0,0,0,.2);
          transition: transform .08s ease, background .2s ease, border-color .2s ease;
        }

        .ql-btn:hover{
          transform: translateY(-1px);
          background: rgba(255,255,255,.12);
          color: var(--ql-text);
          text-decoration: none;
        }

        .ql-secondary{
          background: linear-gradient(180deg, rgba(59,130,246,.25), rgba(59,130,246,.12));
          border-color: rgba(59,130,246,.35);
        }

        .ql-container{ max-width:1200px; margin:22px auto; padding:0 20px; }

        .ql-card{
          background: linear-gradient(180deg, rgba(22,41,78,.9), rgba(14,30,59,.92));
          border: 1px solid var(--ql-border);
          box-shadow: 0 10px 30px rgba(2,8,23,.45), 0 1px 0 rgba(255,255,255,.06) inset;
          border-radius:16px; padding:16px;
          margin-bottom: 20px;
        }

        .ql-card h2{
          font-size:1.05rem; margin:0 0 10px 0; color: #e8f0ff; letter-spacing:.2px; font-weight: 600;
        }
        
        .ql-card h3, .ql-card h4{
          color: #dce6ff; font-weight: 600;
        }
        
        .ql-card p, .ql-card label, .ql-card span{
          color: #e0e9ff;
        }

        /* Override any white backgrounds */
        .container, .main-content, .page-content {
          background: rgba(45, 55, 72, 0.8) !important;
          backdrop-filter: blur(10px);
          border-radius: 16px;
          padding: 24px;
          margin: 20px auto;
          max-width: 1200px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.3);
          border: 1px solid rgba(99, 102, 241, 0.2);
        }

        .professional-styled { background: var(--ql-bg) !important; }
    `;
    if (document.head) {
        document.head.appendChild(unifiedTheme);
    }

    // Wait for CSS to load, then apply enhancements
    link.onload = function() {
        applyProfessionalEnhancements();
    };

    // Apply enhancements immediately if CSS is already loaded
    setTimeout(() => {
        applyProfessionalEnhancements();
    }, 100);

    function applyImmediateDarkTheme() {
        // Mark body as professionally styled to prevent white flash
        if (document.body) {
            document.body.classList.add('professional-styled');

            // Apply immediate dark background
            document.body.style.background = 'radial-gradient(1200px 600px at 60% -100px, #123a86 0%, #0e2242 45%, #081b2e 100%) fixed';
            document.body.style.color = '#f0f4ff';
            document.body.style.minHeight = '100vh';
            document.body.style.fontFamily = 'Inter, ui-sans-serif, system-ui, Arial, sans-serif';
        }

        // Fix any existing white containers
        const whiteElements = document.querySelectorAll('*');
        whiteElements.forEach(el => {
            if (el) {
                const bgColor = window.getComputedStyle(el).backgroundColor;
                if (bgColor === 'rgb(255, 255, 255)' || bgColor === 'white' || bgColor === '#ffffff') {
                    el.style.background = 'rgba(45, 55, 72, 0.8)';
                    el.style.color = '#f0f4ff';
                }
            }
        });
    }

    function applyProfessionalEnhancements() {
        // Create professional navigation if it doesn't exist
        createProfessionalNavigation();

        // Enhance page containers
        enhanceContainers();

        // Enhance page headers
        enhancePageHeaders();

        // Enhance buttons
        enhanceButtons();

        // Enhance forms
        enhanceForms();

        // Enhance cards
        enhanceCards();

        // Enhance tables
        enhanceTables();
        
        // Enhance text visibility
        enhanceTextVisibility();

        console.log('✅ Professional styling enhancements applied');
    }

    function createProfessionalNavigation() {
        // Only add if no navigation exists
        if (!document.querySelector('.top-nav, .nav-header, .header, .ql-header')) {
            const nav = document.createElement('header');
            nav.className = 'ql-header';
            nav.innerHTML = `
                <div class="ql-header-inner">
                    <div class="ql-title">
                        <span class="ql-logo">🟦</span>
                        <h1 class="ql-h1">QR LEGENDS</h1>
                    </div>
                    <nav class="ql-nav">
                        <a class="ql-btn ql-secondary" href="/main_dashboard">🏠 Dashboard</a>
                        <a class="ql-btn" href="/order_picking">📦 Order Picking</a>
                        <a class="ql-btn" href="/inbound_hub">⬅️ Inbound</a>
                        <a class="ql-btn" href="/outbound_hub">➡️ Outbound</a>
                        <a class="ql-btn" href="/inventory">📊 Inventory</a>
                    </nav>
                </div>
            `;
            if (document.body) {
                document.body.prepend(nav);
                // Add padding to body to account for fixed header
                document.body.style.paddingTop = '70px';
            }
        }
    }

    function enhanceContainers() {
        const containers = document.querySelectorAll('.container, .main-content, body > div:first-child');
        containers.forEach(container => {
            if (container && !container.classList.contains('ql-container')) {
                container.classList.add('qr-legends-enhanced'); // Changed class for clarity as per original thought, original code had .ql-container.
                container.style.background = 'rgba(45, 55, 72, 0.8)';
                container.style.backdropFilter = 'blur(10px)';
                container.style.borderRadius = '16px';
                container.style.padding = '24px';
                container.style.margin = '20px auto';
                container.style.maxWidth = '1200px';
                container.style.boxShadow = '0 8px 32px rgba(0,0,0,0.3)';
                container.style.border = '1px solid rgba(99, 102, 241, 0.2)';
            }
        });
    }

    function enhancePageHeaders() {
        const headers = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        headers.forEach(header => {
            if (header && !header.closest('.ql-header') && !header.closest('.page-header')) {
                header.style.color = '#e8f0ff';
                header.style.fontWeight = '700';
                if (header.tagName === 'H1') {
                    header.style.fontSize = '1.75rem';
                    header.style.marginBottom = '20px';
                } else if (header.tagName === 'H2') {
                    header.style.fontSize = '1.5rem';
                    header.style.marginBottom = '16px';
                } else if (header.tagName === 'H3') {
                    header.style.fontSize = '1.25rem';
                    header.style.marginBottom = '12px';
                }
            }
        });
    }

    function enhanceButtons() {
        const buttons = document.querySelectorAll('button, .button, input[type="submit"], a[class*="btn"]');
        buttons.forEach(button => {
            if (button && !button.classList.contains('ql-btn') && !button.closest('.ql-header')) {
                button.style.background = 'linear-gradient(180deg, rgba(59,130,246,.35), rgba(59,130,246,.2))';
                button.style.border = '1px solid rgba(59,130,246,.5)';
                button.style.color = '#f0f4ff';
                button.style.padding = '8px 12px';
                button.style.borderRadius = '10px';
                button.style.transition = 'all 0.2s ease';
                button.style.cursor = 'pointer';
                button.style.fontWeight = '600';
            }
        });
    }

    function enhanceForms() {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input) {
                input.style.background = 'rgba(255,255,255,.12)';
                input.style.border = '1px solid rgba(255,255,255,.25)';
                input.style.color = '#f0f4ff';
                input.style.padding = '10px 12px';
                input.style.borderRadius = '8px';
                input.style.fontWeight = '500';
            }
        });

        const labels = document.querySelectorAll('label');
        labels.forEach(label => {
            if (label) {
                label.style.color = '#e8f0ff';
                label.style.marginBottom = '8px';
                label.style.display = 'block';
                label.style.fontWeight = '600';
            }
        });
        
        const paragraphs = document.querySelectorAll('p');
        paragraphs.forEach(p => {
            if (p) {
                p.style.color = '#dce6ff';
            }
        });
    }

    function enhanceCards() {
        const cards = document.querySelectorAll('.card, .feature-card, .widget-card, .section');
        cards.forEach(card => {
            if (card) {
                card.style.background = 'linear-gradient(180deg, rgba(22,41,78,.9), rgba(14,30,59,.92))';
                card.style.border = '1px solid rgba(255,255,255,.12)';
                card.style.borderRadius = '16px';
                card.style.padding = '16px';
                card.style.marginBottom = '20px';
                card.style.boxShadow = '0 10px 30px rgba(2,8,23,.45)';
            }
        });
    }

    function enhanceTables() {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            if (table) {
                table.style.background = 'rgba(45, 55, 72, 0.8)';
                table.style.color = '#dbe8ff';
                table.style.borderRadius = '8px';
                table.style.overflow = 'hidden';

                const ths = table.querySelectorAll('th');
                ths.forEach(th => {
                    if (th) {
                        th.style.background = 'rgba(99, 102, 241, 0.3)';
                        th.style.color = '#dbe8ff';
                        th.style.padding = '12px';
                    }
                });

                const tds = table.querySelectorAll('td');
                tds.forEach(td => {
                    if (td) {
                        td.style.padding = '10px 12px';
                        td.style.borderBottom = '1px solid rgba(255,255,255,.12)';
                        td.style.color = '#e8f0ff';
                    }
                });
            }
        });
    }
    
    // Enhance all text visibility
    function enhanceTextVisibility() {
        const allText = document.querySelectorAll('span, div, a, li');
        allText.forEach(el => {
            if (el && el.textContent.trim()) {
                const currentColor = window.getComputedStyle(el).color;
                // If text is too dim, brighten it
                if (currentColor.includes('rgb')) {
                    el.style.color = '#e0e9ff';
                }
            }
        });
    }
})();

// Auto-apply on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        // Script will auto-run when loaded
    });
}