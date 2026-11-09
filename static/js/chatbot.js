/**
 * SNEAKER SQUAD - VANILLA JS CHATBOT CLIENT (chatbot.js)
 * -----------------------------------------------------
 * Handles floating widget toggling, message rendering, auto-scrolling,
 * suggestion chips, CSRF tokens, and product cards carousel.
 */

(function() {
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function formatTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  // Lightweight markdown-to-HTML parser for bot replies
  function parseMarkdown(text) {
    if (!text) return '';
    let parsed = text
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Inline Code
      .replace(/`(.*?)`/g, '<code>$1</code>')
      // Links [text](url)
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>')
      // Markdown Tables
      .replace(/\|(.+)\|/g, function(match) {
        if (match.includes('---')) return '';
        const cells = match.split('|').filter(c => c.trim() !== '');
        const row = cells.map(c => `<td style="padding:4px 8px; border:1px solid rgba(255,255,255,0.1);">${c.trim()}</td>`).join('');
        return `<tr style="border-collapse:collapse;">${row}</tr>`;
      })
      // Newlines to <br>
      .replace(/\n/g, '<br>');

    if (parsed.includes('<tr>')) {
      parsed = `<table style="width:100%; border-collapse:collapse; margin:8px 0; font-size:0.8rem; background:rgba(0,0,0,0.25); border-radius:6px; overflow:hidden;">${parsed}</table>`;
    }
    return parsed;
  }

  document.addEventListener('DOMContentLoaded', () => {
    const launcher = document.getElementById('squad-chat-launcher');
    const chatWindow = document.getElementById('squad-chat-window');
    const closeBtn = document.getElementById('squad-chat-close');
    const form = document.getElementById('squad-chat-form');
    const input = document.getElementById('squad-chat-input');
    const body = document.getElementById('squad-chat-body');
    const chips = document.querySelectorAll('.chat-chip');

    if (!launcher || !chatWindow) return;

    // 1. Toggle Chat Window
    launcher.addEventListener('click', () => {
      chatWindow.classList.toggle('active');
      if (chatWindow.classList.contains('active')) {
        setTimeout(() => input && input.focus(), 200);
        scrollToBottom();
      }
    });

    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        chatWindow.classList.remove('active');
      });
    }

    // 2. Suggestion Chips Click
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        const text = chip.getAttribute('data-query') || chip.innerText.trim();
        sendMessage(text);
      });
    });

    // 3. Form Submit
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (text) {
          sendMessage(text);
          input.value = '';
        }
      });
    }

    // Auto-scroll helper
    function scrollToBottom() {
      if (body) {
        body.scrollTop = body.scrollHeight;
      }
    }

    // Append Message to UI
    function appendMessage(sender, htmlContent, products = []) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `chat-msg ${sender}`;

      let productsHTML = '';
      if (products && products.length > 0) {
        const cards = products.map(p => `
          <a href="${p.url}" class="chat-product-card" target="_blank">
            <img src="${p.image}" alt="${p.name}" class="chat-prod-thumb" onerror="this.src='/static/img/shoe-1.jpg'">
            <div class="chat-prod-info">
              <div class="chat-prod-title">${p.name}</div>
              <div class="chat-prod-meta">
                <span class="chat-prod-price">₹${p.price.toLocaleString('en-IN')}</span>
                <span class="chat-prod-rating"><i class="fa-solid fa-star"></i> ${p.rating}</span>
                <span style="color:#94a3b8;">${p.brand}</span>
              </div>
            </div>
            <i class="fa-solid fa-angle-right" style="color:var(--primary); font-size:0.8rem;"></i>
          </a>
        `).join('');
        productsHTML = `<div class="chat-product-carousel">${cards}</div>`;
      }

      msgDiv.innerHTML = `
        <div class="msg-bubble">${htmlContent}${productsHTML}</div>
        <span class="msg-time">${formatTime()}</span>
      `;
      body.appendChild(msgDiv);
      scrollToBottom();
    }

    // Show Typing Indicator
    function showTyping() {
      const typingDiv = document.createElement('div');
      typingDiv.className = 'chat-msg bot typing-indicator-msg';
      typingDiv.id = 'squad-chat-typing';
      typingDiv.innerHTML = `
        <div class="msg-bubble" style="padding:6px 12px;">
          <div class="chat-typing-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      `;
      body.appendChild(typingDiv);
      scrollToBottom();
    }

    function removeTyping() {
      const t = document.getElementById('squad-chat-typing');
      if (t) t.remove();
    }

    // Core Send Message Function
    async function sendMessage(text) {
      if (!text || !text.trim()) return;

      // 1. Render User Message
      appendMessage('user', text.trim());

      // 2. Show Typing Dots
      showTyping();

      try {
        const csrftoken = getCookie('csrftoken') || '';
        const res = await fetch('/chatbot/api/', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
          },
          body: JSON.stringify({ message: text.trim() })
        });

        const data = await res.json();
        removeTyping();

        if (res.ok && data) {
          const parsedText = parseMarkdown(data.text || '');
          appendMessage('bot', parsedText, data.products || []);
        } else {
          appendMessage('bot', '⚠️ Server se connect karne me problem aayi. Kripya dobara try karein.');
        }
      } catch (err) {
        removeTyping();
        appendMessage('bot', '⚠️ Network offline ya slow connection hai. Kripya check karein.');
      }
    }

    // Expose helper globally
    window.squadChatSend = sendMessage;
  });
})();

