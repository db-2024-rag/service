document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const chatWindow = document.getElementById('chat-window');
    const sendButton = document.getElementById('send-button');
    const uploadForm = document.getElementById('upload-form');
    const uploadButton = uploadForm.querySelector('button[type="submit"]');
    const historyList = document.getElementById('history-list');
    const clearHistoryButton = document.getElementById('clear-history-button');

    let messageCount = 0; 
    let messages = [];   
    let historyItems = []; 

    loadChatHistory();
    loadHistoryList();

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    function appendMessage(sender, messageContent, isLoading = false, messageId = null) {
        if (messageId === null) {
            messageCount += 1;
            messageId = 'message-' + messageCount;
        } else {
            const count = parseInt(messageId.split('-')[1]);
            if (count > messageCount) {
                messageCount = count;
            }
        }

        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        messageElement.id = messageId; 

        messageElement.classList.add(sender === 'You' ? 'user-message' : 'llm-message');

        const senderElement = document.createElement('div');
        senderElement.className = 'sender';
        senderElement.textContent = sender + ":";

        messageElement.appendChild(senderElement);

        if (sender === 'You' && !isLoading) {
            addToHistory(messageContent, messageId);
        }

        if (Array.isArray(messageContent)) {
            messageContent.forEach((response) => {
                const responseElement = document.createElement('div');
                responseElement.className = 'llm-response-item';

                const textElement = document.createElement('div');
                textElement.className = 'message-text';

                const contentContainer = document.createElement('div');

                if (sender === 'LLM' && !isLoading) {
                    typeTextWithFiles(contentContainer, response.text, response.files || []);
                } else {
                    textElement.textContent = response.text;
                    contentContainer.appendChild(textElement);

                    if (response.files && response.files.length > 0) {
                        const filesElement = document.createElement('div');
                        filesElement.className = 'file-links';
                        response.files.forEach((file) => {
                            const fileLink = document.createElement('a');
                            fileLink.href = '/download/' + encodeURIComponent(file.id) + '/' + encodeURIComponent(file.name);
                            fileLink.textContent = file.name;
                            fileLink.className = 'file-link';
                            filesElement.appendChild(fileLink);
                        });
                        contentContainer.appendChild(filesElement);
                    }
                }

                responseElement.appendChild(contentContainer);
                messageElement.appendChild(responseElement);
            });
        } else {
            const textElement = document.createElement('div');
            textElement.className = 'message-text';

            if (sender === 'LLM' && !isLoading) {
                typeText(textElement, messageContent);
            } else {
                textElement.textContent = messageContent;
            }

            messageElement.appendChild(textElement);
        }

        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        if (!isLoading) {
            messages.push({
                sender: sender,
                content: messageContent,
                messageId: messageId
            });
            saveChatHistory();
        }

        return messageElement; 
    }

    function typeTextWithFiles(container, text, files, index = 0) {
        if (index < text.length) {
            if (!container.querySelector('.message-text')) {
                const textElement = document.createElement('div');
                textElement.className = 'message-text';
                container.appendChild(textElement);
            }
            const textElement = container.querySelector('.message-text');
            textElement.textContent += text.charAt(index);
            setTimeout(() => {
                typeTextWithFiles(container, text, files, index + 1);
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }, 30); 
        } else if (files.length > 0) {
            typeFiles(container, files);
        }
    }

    function typeFiles(container, files, fileIndex = 0, charIndex = 0) {
        if (fileIndex < files.length) {
            if (!container.querySelector('.file-links')) {
                const filesElement = document.createElement('div');
                filesElement.className = 'file-links';
                container.appendChild(filesElement);
            }
            const filesElement = container.querySelector('.file-links');

            if (!filesElement.children[fileIndex]) {
                const fileLink = document.createElement('a');
                fileLink.href = '/download/' + encodeURIComponent(files[fileIndex].id) + '/' + encodeURIComponent(files[fileIndex].name);
                fileLink.className = 'file-link';
                filesElement.appendChild(fileLink);
            }

            const fileLink = filesElement.children[fileIndex];
            fileLink.textContent += files[fileIndex].name.charAt(charIndex);

            if (charIndex < files[fileIndex].name.length - 1) {
                setTimeout(() => {
                    typeFiles(container, files, fileIndex, charIndex + 1);
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                }, 30); 
            } else {
                setTimeout(() => {
                    typeFiles(container, files, fileIndex + 1, 0);
                }, 500); 
            }
        }
    }

    function typeText(element, text, index = 0) {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            setTimeout(() => {
                typeText(element, text, index + 1);
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }, 30); 
        }
    }

    function sendMessage() {
        const message = messageInput.value;
        if (message.trim() === '') {
            return;
        }
        appendMessage('You', message);
        messageInput.value = '';

        sendButton.disabled = true;
        sendButton.textContent = 'Sending...';

        const loadingMessageElement = document.createElement('div');
        loadingMessageElement.className = 'message llm-message loading-message';
        loadingMessageElement.innerHTML = '<em>LLM is thinking...</em>';
        chatWindow.appendChild(loadingMessageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({'message': message}),
        })
        .then(response => response.json())
        .then(data => {
            chatWindow.removeChild(loadingMessageElement);

            appendMessage('LLM', data.responses);

            sendButton.disabled = false;
            sendButton.innerHTML = 'Send<i class="material-icons right">send</i>';
        })
        .catch((error) => {
            console.error('Error:', error);
            chatWindow.removeChild(loadingMessageElement);

            sendButton.disabled = false;
            sendButton.innerHTML = 'Send<i class="material-icons right">send</i>';

            M.toast({html: 'Error sending message.', displayLength: 3000});
        });
    }

    function addToHistory(message, messageId, isLoading = false) {
        const truncatedMessage = message.length > 20 ? message.substring(0, 20) + '...' : message;

        const historyItem = document.createElement('li');
        historyItem.className = 'history-item';
        historyItem.textContent = truncatedMessage;
        historyItem.dataset.messageId = messageId; 

        historyItem.addEventListener('click', function() {
            scrollToMessage(this.dataset.messageId);
        });

        historyList.appendChild(historyItem);

        if (!isLoading) {
            historyItems.push({
                messageId: messageId,
                text: truncatedMessage
            });
            saveHistoryList();
        }
    }

    function scrollToMessage(messageId) {
        const messageElement = document.getElementById(messageId);
        if (messageElement) {
            chatWindow.scrollTop = messageElement.offsetTop - chatWindow.offsetTop;
            messageElement.classList.add('highlighted-message');
            setTimeout(() => {
                messageElement.classList.remove('highlighted-message');
            }, 2000);
        }
    }

    clearHistoryButton.addEventListener('click', clearHistory);

    function clearHistory() {
        if (confirm('Are you sure you want to clear the chat and history?')) {
            chatWindow.innerHTML = '';
            historyList.innerHTML = '';
           
            messageCount = 0;
            messages = [];
            historyItems = [];

            localStorage.removeItem('chatMessages');
            localStorage.removeItem('historyItems');
        }
    }

    function saveChatHistory() {
        localStorage.setItem('chatMessages', JSON.stringify(messages));
    }

    function loadChatHistory() {
        const storedMessages = JSON.parse(localStorage.getItem('chatMessages') || '[]');
        messages = storedMessages;
        messages.forEach((msg) => {
            appendMessage(msg.sender, msg.content, true, msg.messageId);
        });
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            const lastMessageId = lastMessage.messageId;
            const count = parseInt(lastMessageId.split('-')[1]);
            messageCount = count;
        }
    }

    function saveHistoryList() {
        localStorage.setItem('historyItems', JSON.stringify(historyItems));
    }

    function loadHistoryList() {
        const storedHistory = JSON.parse(localStorage.getItem('historyItems') || '[]');
        historyItems = storedHistory;
        historyItems.forEach((item) => {
            const historyItem = document.createElement('li');
            historyItem.className = 'history-item';
            historyItem.textContent = item.text;
            historyItem.dataset.messageId = item.messageId; 

            historyItem.addEventListener('click', function() {
                scrollToMessage(this.dataset.messageId);
            });

            historyList.appendChild(historyItem);
        });
    }

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const fileInput = document.getElementById('file-input');
        const file = fileInput.files[0];

        if (!fileInput.files[0]) {
            M.toast({html: 'Please select a file to upload.', displayLength: 3000});
            return;
        }

        const allowedExtensions = /(\.pdf|\.txt)$/i;
        if (!allowedExtensions.exec(file.name)) {
            showCustomPopup('Invalid file type. Please upload a PDF or TXT file.');
            fileInput.value = '';
            const filePathInput = uploadForm.querySelector('.file-path');
            if (filePathInput) filePathInput.value = '';
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        uploadButton.disabled = true;
        uploadButton.innerHTML = 'Uploading...<i class="material-icons right">file_upload</i>';

        fetch('/upload', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.text())
        .then(data => {
            uploadButton.disabled = false;
            uploadButton.innerHTML = 'Upload<i class="material-icons right">file_upload</i>';

            M.toast({html: 'File uploaded successfully.', displayLength: 3000});

            fileInput.value = '';
            const filePathInput = uploadForm.querySelector('.file-path');
            if (filePathInput) filePathInput.value = '';
        })
        .catch((error) => {
            console.error('Error:', error);
            uploadButton.disabled = false;
            uploadButton.innerHTML = 'Upload<i class="material-icons right">file_upload</i>';

            M.toast({html: 'Error uploading file.', displayLength: 3000});
        });
    });
});
