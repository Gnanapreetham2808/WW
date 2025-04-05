document.addEventListener("DOMContentLoaded", function () {
    const chatContainer = document.createElement("div");
    chatContainer.classList.add("chat-container");
    chatContainer.innerHTML = `
        <div class="chat-messages"></div>
        <div class="chat-input">
            <input type="text" id="chatTextInput" placeholder="Type a message..." />
            <button id="sendBtn">Send</button>
        </div>
    `;
    document.body.appendChild(chatContainer);

    const messagesDiv = document.querySelector(".chat-messages");
    const chatInput = document.getElementById("chatTextInput");
    const sendBtn = document.getElementById("sendBtn");

    function sendMessage() {
        let userMessage = chatInput.value.trim();
        if (userMessage === "") return;

        appendMessage("You", userMessage);
        chatInput.value = "";

        fetch(window.backendUrl + "/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => response.json())
        .then(data => appendMessage("DNAi", data.reply))
        .catch(error => console.error("Error:", error));
    }

    function appendMessage(sender, text) {
        let messageDiv = document.createElement("div");
        messageDiv.textContent = `${sender}: ${text}`;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") sendMessage();
    });
});
