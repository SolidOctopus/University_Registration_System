document.getElementById("message-form").addEventListener("submit", function(event) {
    event.preventDefault();
    const messageInput = document.getElementById("message-input");
    const content = messageInput.value.trim();
    if (!content) return;

    const formData = new FormData();
    formData.append("content", content);

    const userId = document.querySelector('.chat-header').getAttribute('data-user-id');
    if (!userId) return;

    fetch(`/messages/send/${userId}/`, {
        method: "POST",
        body: formData,
        headers: {"X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value}
    }).then(response => {
        if (response.ok) {
            messageInput.value = "";
            loadMessages();
        }
    });
});

function loadMessages() {
    const chatMessages = document.querySelector(".chat-messages");
    fetch(window.location.href)
        .then(res => res.text())
        .then(html => {
            const doc = new DOMParser().parseFromString(html, "text/html");
            chatMessages.innerHTML = doc.querySelector(".chat-messages").innerHTML;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
}

// New Conversation Modal logic
document.getElementById('new-convo-btn').addEventListener('click', () => {
    document.getElementById('new-convo-modal').style.display = 'block';
    document.getElementById('modal-overlay').style.display = 'block';
});

// Allow users to close the modal
document.getElementById('modal-overlay').addEventListener('click', closeModal);
document.getElementById('close-modal-btn').addEventListener('click', () => {
    document.getElementById('new-convo-modal').style.display = 'none';
    document.getElementById('modal-overlay').style.display = 'none';
});
