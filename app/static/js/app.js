// ===== CSRF Token helper =====
function getCsrfToken() {
    const meta = document.querySelector('input[name="csrf_token"]');
    return meta ? meta.value : '';
}

// ===== Like Post (AJAX) =====
function likePost(postId) {
    const btn = document.getElementById(`like-btn-${postId}`);
    const likesEl = document.getElementById(`likes-count-${postId}`);
    const animEl = document.getElementById(`like-anim-${postId}`);

    fetch(`/posts/${postId}/like`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (btn) {
            const icon = btn.querySelector('i');
            if (data.liked) {
                btn.classList.add('liked');
                icon.className = 'fas fa-heart';
                
                // Show burst animation
                createHeartBurst(btn);
                
                // Show success animation
                if (animEl) {
                    animEl.classList.remove('animate');
                    void animEl.offsetWidth;
                    animEl.classList.add('animate');
                }
            } else {
                btn.classList.remove('liked');
                icon.className = 'far fa-heart';
            }
        }
        if (likesEl) {
            likesEl.innerHTML = `<span>${data.likes_count} ta yoqtirish</span>`;
        }
    })
    .catch(err => console.error('Like error:', err));
}

function createHeartBurst(element) {
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    for (let i = 0; i < 8; i++) {
        const heart = document.createElement('i');
        heart.className = 'fas fa-heart heart-particle';
        
        const angle = (i / 8) * Math.PI * 2;
        const velocity = 50 + Math.random() * 50;
        const tx = Math.cos(angle) * velocity;
        const ty = Math.sin(angle) * velocity;
        
        heart.style.left = `${centerX}px`;
        heart.style.top = `${centerY}px`;
        heart.style.setProperty('--tx', `${tx}px`);
        heart.style.setProperty('--ty', `${ty}px`);
        heart.style.position = 'fixed';
        heart.style.zIndex = '9999';
        heart.style.color = '#ef4444';
        heart.style.transition = 'all 0.6s cubic-bezier(0.1, 0.8, 0.3, 1)';
        
        document.body.appendChild(heart);
        
        requestAnimationFrame(() => {
            heart.style.transform = `translate(${tx}px, ${ty}px) scale(1.5)`;
            heart.style.opacity = '0';
        });
        
        setTimeout(() => heart.remove(), 600);
    }
}

// ===== Quick Comment (AJAX) =====
function submitComment(event, postId) {
    event.preventDefault();
    const input = document.getElementById(`comment-input-${postId}`);
    const body = input.value.trim();
    if (!body) return;

    const formData = new FormData();
    formData.append('body', body);
    formData.append('csrf_token', getCsrfToken());

    fetch(`/posts/${postId}/comment`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            input.value = '';
            // Show success feedback
            input.placeholder = 'Izoh qo\'shildi! ✓';
            setTimeout(() => { input.placeholder = 'Izoh qo\'shing...'; }, 2000);
        }
    })
    .catch(err => console.error('Comment error:', err));
}

// ===== Follow/Unfollow (AJAX) =====
function toggleFollow(username, buttonEl) {
    const btn = buttonEl || document.getElementById('follow-btn');
    if (!btn) return;

    // Determine following state based on text or specific class
    const isFollowing = btn.textContent.trim() === 'Kuzatilmoqda';
    const url = isFollowing
        ? `/users/${username}/unfollow`
        : `/users/${username}/follow`;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.following) {
            btn.textContent = 'Kuzatilmoqda';
            btn.classList.add('btn-outline'); // for profile page
            btn.classList.remove('btn-primary'); // for profile page
            btn.classList.remove('primary'); // for post detail
        } else {
            btn.textContent = 'Kuzatish';
            btn.classList.remove('btn-outline'); // for profile page
            btn.classList.add('btn-primary'); // for profile page
            btn.classList.add('primary'); // for post detail
        }
        // Update followers count
        const countEl = document.getElementById('followers-count');
        if (countEl) countEl.textContent = data.followers_count;
    })
    .catch(err => console.error('Follow error:', err));
}

// ===== Save Post (AJAX) =====
function savePost(postId, btn) {
    fetch(`/posts/${postId}/save`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        const icon = btn.querySelector('i');
        if (data.saved) {
            btn.classList.add('saved');
            icon.className = 'fas fa-bookmark';
        } else {
            btn.classList.remove('saved');
            icon.className = 'far fa-bookmark';
        }
    })
    .catch(err => console.error('Save error:', err));
}

// ===== Post Menu Toggle =====
function toggleMenu(btn) {
    const dropdown = btn.nextElementSibling;
    dropdown.classList.toggle('show');

    // Close on outside click
    const close = (e) => {
        if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
            document.removeEventListener('click', close);
        }
    };
    document.addEventListener('click', close);
}

// ===== Auto-dismiss flash messages =====
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-20px)';
            setTimeout(() => msg.remove(), 300);
        }, 4000);
    });
});
