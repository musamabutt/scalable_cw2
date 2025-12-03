// static/script.js

document.addEventListener("DOMContentLoaded", () => {
    // Attach like handlers
    document.querySelectorAll(".like-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const videoId = btn.dataset.videoId;
        try {
          const res = await fetch(`/like/${videoId}`, { method: 'POST' });
          const data = await res.json();
          if (data.likes !== undefined) {
            btn.querySelector(".like-count").innerText = data.likes;
            // update text more visibly
            btn.classList.add("liked");
          } else if (data.error) {
            alert(data.error);
          }
        } catch (err) {
          console.error(err);
          alert("Could not like video (network error).");
        }
      });
    });
  
    // No need to bind comment forms here because they use inline onsubmit handler addComment(...)
  });
  
  // addComment called from inline form onsubmit
  async function addComment(event, videoId) {
    event.preventDefault();
    const form = event.target;
    const input = form.querySelector('input[name="content"]');
    const content = input.value.trim();
    if (!content) {
      alert("Comment cannot be empty");
      return;
    }
  
    const formData = new FormData();
    formData.append('content', content);
  
    try {
      const res = await fetch(`/comment/${videoId}`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data && !data.error) {
        // add the new comment to the DOM (use username returned by server)
        const commentList = form.closest(".comments-block").querySelector(".comment-list");
        const div = document.createElement('div');
        div.className = 'comment';
        const username = data.username || data.user_id || "Unknown";
        div.innerHTML = `<strong>${escapeHtml(username)}</strong>: <span class="comment-text">${escapeHtml(data.content)}</span>`;
        commentList.appendChild(div);
        input.value = '';
      } else {
        alert(data.error || "Could not add comment");
      }
    } catch (err) {
      console.error(err);
      alert("Network error when submitting comment.");
    }
  }
  
  // small helper to avoid XSS in inserted strings
  function escapeHtml(unsafe) {
    return unsafe
         .replaceAll('&', "&amp;")
         .replaceAll('<', "&lt;")
         .replaceAll('>', "&gt;")
         .replaceAll('"', "&quot;")
         .replaceAll("'", "&#039;");
  }
  