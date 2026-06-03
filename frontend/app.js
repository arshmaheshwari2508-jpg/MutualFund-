        const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
            ? 'http://127.0.0.1:8000' 
            : 'https://my-backend-app.up.railway.app';

        const chatForm = document.getElementById('chat-form');
        const chatInput = document.getElementById('chat-input');
        const messagesContainer = document.getElementById('messages-container');
        const chatFeed = document.getElementById('chat-feed');
        const typingIndicator = document.getElementById('typing-indicator');

        window.onload = async () => {
            const statusDot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');
            const lastUpdated = document.getElementById('last-updated');

            try {
                const response = await fetch(`${API_BASE_URL}/api/health`);
                if (response.ok) {
                    statusDot.className = 'w-2.5 h-2.5 rounded-full bg-emerald-500 pulse-dot';
                    statusText.innerText = 'Connected';
                    const date = new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
                    lastUpdated.innerText = `Last updated from Groww sources: ${date}`;
                } else {
                    throw new Error();
                }
            } catch (err) {
                statusDot.className = 'w-2.5 h-2.5 rounded-full bg-[#f85149]';
                statusText.innerText = 'Service Unavailable';
                lastUpdated.innerText = 'Offline Mode - Cached Data Only';
            }
        };

        function formatText(text) {
            // Handle markdown links [Title](url)
            let formatted = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="text-primary font-bold hover:underline">$1</a>');
            // Handle line breaks
            formatted = formatted.replace(/\n/g, '<br>');
            return formatted;
        }

        function scrollToBottom() {
            chatFeed.scrollTo({
                top: chatFeed.scrollHeight,
                behavior: 'smooth'
            });
        }

        function createMessage(content, isUser = false) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[85%] animate-slide-up w-full self-${isUser ? 'end' : 'start'}`;
            
            const innerDiv = document.createElement('div');
            innerDiv.className = isUser 
                ? 'bg-[#2f81f7] text-white px-5 py-4 rounded-2xl rounded-tr-none shadow-lg' 
                : 'glass-panel px-5 py-4 rounded-2xl rounded-tl-none';
            
            innerDiv.innerHTML = `<p class="text-body-md leading-relaxed">${formatText(content)}</p>`;
            
            const meta = document.createElement('span');
            meta.className = 'text-label-md text-on-surface-variant mt-2 px-1';
            meta.innerText = `${isUser ? 'You' : 'Assistant'} • Just now`;
            
            msgDiv.appendChild(innerDiv);
            msgDiv.appendChild(meta);
            
            if (isUser) msgDiv.style.marginLeft = 'auto';

            messagesContainer.appendChild(msgDiv);
            scrollToBottom();
        }

        async function handleChat(query) {
            if (!query.trim()) return;

            // Add user message
            createMessage(query, true);
            chatInput.value = '';

            // Show typing indicator
            typingIndicator.classList.remove('hidden');
            scrollToBottom();

            try {
                const response = await fetch(`${API_BASE_URL}/api/query`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });

                const data = await response.json();
                typingIndicator.classList.add('hidden');

                // FIX: API returns { "response": ... } not { "answer": ... }
                if (data && data.response) {
                    createMessage(data.response);
                } else if (data && data.answer) {
                    createMessage(data.answer);
                } else {
                    createMessage("I'm sorry, I couldn't retrieve the specific facts for that query. Please try asking about a specific HDFC mutual fund's NAV or load structure.");
                }
            } catch (err) {
                typingIndicator.classList.add('hidden');
                createMessage("Technical connection error. Please ensure the backend service is operational. Note: I am only permitted to provide factual, verified data.");
            }
        }

        chatForm.onsubmit = (e) => {
            e.preventDefault();
            handleChat(chatInput.value);
        };

        function sendQuickQuery(query) {
            handleChat(query);
        }
