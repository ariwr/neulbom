// 전역 상태
let currentUser = null;
let chatHistory = [];
let currentRoomId = null;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', async () => {
    // 토큰이 있으면 프로필 확인
    if (authToken) {
        try {
            currentUser = await authAPI.getProfile();
            updateUI();
        } catch (error) {
            // 토큰이 유효하지 않으면 제거
            setAuthToken(null);
        }
    }
});

// UI 업데이트
function updateUI() {
    const authButtons = document.getElementById('auth-buttons');
    const userInfo = document.getElementById('user-info');
    const userEmail = document.getElementById('user-email');
    const communityBtn = document.getElementById('community-btn');
    const verifyBtn = document.getElementById('verify-btn');
    const postBtn = document.getElementById('post-btn');
    
    if (currentUser) {
        authButtons.style.display = 'none';
        userInfo.style.display = 'flex';
        userEmail.textContent = currentUser.email;
        
        // 등급에 따른 버튼 표시
        if (currentUser.level >= 2) {
            communityBtn.style.display = 'inline-block';
            verifyBtn.style.display = 'inline-block';
            postBtn.style.display = 'inline-block';
            loadCommunityPosts();
        }
    } else {
        authButtons.style.display = 'flex';
        userInfo.style.display = 'none';
        communityBtn.style.display = 'none';
        verifyBtn.style.display = 'none';
        postBtn.style.display = 'none';
    }
}

// 섹션 전환
function showSection(sectionName) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // 커뮤니티 섹션일 때 게시글 로드
    if (sectionName === 'community' && currentUser && currentUser.level >= 2) {
        loadCommunityPosts();
    }
}

// 모달 관리
function showLoginModal() {
    document.getElementById('login-modal').classList.add('active');
}

function showSignupModal() {
    document.getElementById('signup-modal').classList.add('active');
}

function showVerificationModal() {
    document.getElementById('verification-modal').classList.add('active');
}

function showPostModal() {
    document.getElementById('post-modal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    // 에러 메시지 초기화
    const errorDiv = document.getElementById(modalId.replace('-modal', '-error'));
    if (errorDiv) {
        errorDiv.textContent = '';
    }
}

// 모달 외부 클릭 시 닫기
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}

// 로그인 처리
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    
    try {
        await authAPI.login(email, password);
        currentUser = await authAPI.getProfile();
        updateUI();
        closeModal('login-modal');
        document.getElementById('login-form').reset();
    } catch (error) {
        errorDiv.textContent = error.message || '로그인에 실패했습니다.';
    }
}

// 회원가입 처리
async function handleSignup(event) {
    event.preventDefault();
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const passwordConfirm = document.getElementById('signup-password-confirm').value;
    const age = document.getElementById('signup-age').value;
    const region = document.getElementById('signup-region').value;
    const errorDiv = document.getElementById('signup-error');
    
    try {
        const userData = {
            email,
            password,
            password_confirm: passwordConfirm,
        };
        if (age) userData.age = parseInt(age);
        if (region) userData.region = region;
        
        await authAPI.signup(userData);
        currentUser = await authAPI.getProfile();
        updateUI();
        closeModal('signup-modal');
        document.getElementById('signup-form').reset();
        alert('회원가입이 완료되었습니다!');
    } catch (error) {
        errorDiv.textContent = error.message || '회원가입에 실패했습니다.';
    }
}

// 로그아웃
function logout() {
    setAuthToken(null);
    currentUser = null;
    chatHistory = [];
    currentRoomId = null;
    updateUI();
    showSection('chat');
}

// 챗봇 메시지 전송
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 사용자 메시지 표시
    addChatMessage(message, 'user');
    input.value = '';
    
    try {
        const response = await chatAPI.sendMessage(message, chatHistory, currentRoomId);
        
        // 봇 응답 표시
        addChatMessage(response.reply, 'bot');
        
        // 위기 감지 알림
        if (response.is_crisis) {
            showCrisisAlert(response.crisis_info);
        }
        
        // 히스토리 업데이트
        chatHistory.push(
            { role: 'user', content: message },
            { role: 'assistant', content: response.reply }
        );
        
        // room_id가 반환되면 저장
        if (response.room_id) {
            currentRoomId = response.room_id;
        }
    } catch (error) {
        addChatMessage('죄송합니다. 오류가 발생했습니다.', 'bot');
        console.error('챗봇 오류:', error);
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

function addChatMessage(message, type) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.innerHTML = `<div class="message-content">${escapeHtml(message)}</div>`;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showCrisisAlert(crisisInfo) {
    const alertDiv = document.getElementById('crisis-alert');
    alertDiv.innerHTML = `
        <strong>위기 상황 감지</strong><br>
        ${crisisInfo.message || '전문가의 도움이 필요해 보입니다.'}<br>
        ${crisisInfo.phone ? `전화: ${crisisInfo.phone}` : ''}
    `;
    alertDiv.style.display = 'block';
}

// 복지 정보 검색
async function searchWelfare() {
    const keyword = document.getElementById('welfare-keyword').value;
    const region = document.getElementById('welfare-region').value;
    const age = document.getElementById('welfare-age').value;
    const resultsDiv = document.getElementById('welfare-results');
    
    resultsDiv.innerHTML = '<p>검색 중...</p>';
    
    try {
        const results = await welfareAPI.search(keyword, region, age || null);
        
        if (results.length === 0) {
            resultsDiv.innerHTML = '<p>검색 결과가 없습니다.</p>';
            return;
        }
        
        resultsDiv.innerHTML = results.map(welfare => `
            <div class="welfare-card">
                <h3>${escapeHtml(welfare.title)}</h3>
                <p>${escapeHtml(welfare.summary || '')}</p>
                ${welfare.source_link ? `<a href="${welfare.source_link}" target="_blank">자세히 보기</a>` : ''}
                ${currentUser && currentUser.level >= 2 ? `
                    <button class="btn btn-outline bookmark-btn" onclick="bookmarkWelfare(${welfare.id})">
                        북마크
                    </button>
                ` : ''}
            </div>
        `).join('');
    } catch (error) {
        resultsDiv.innerHTML = `<p class="error-message">검색 중 오류가 발생했습니다: ${error.message}</p>`;
    }
}

async function bookmarkWelfare(welfareId) {
    try {
        await welfareAPI.bookmark(welfareId);
        alert('북마크에 추가되었습니다.');
    } catch (error) {
        alert('북마크 추가에 실패했습니다: ' + error.message);
    }
}

// 커뮤니티 심사 제출
async function handleVerification(event) {
    event.preventDefault();
    const content = document.getElementById('verification-content').value;
    const errorDiv = document.getElementById('verification-error');
    
    try {
        const result = await communityAPI.verify(content);
        closeModal('verification-modal');
        document.getElementById('verification-form').reset();
        
        // 사용자 정보 갱신
        if (result.status === 'approved') {
            currentUser = await authAPI.getProfile();
            updateUI();
            alert('심사가 승인되었습니다! 커뮤니티에 입장하실 수 있습니다.');
        } else if (result.status === 'rejected') {
            alert('심사가 거절되었습니다: ' + (result.reason || '심사 기준에 맞지 않습니다.'));
        } else {
            alert('심사가 제출되었습니다. 검토 후 결과를 알려드리겠습니다.');
        }
    } catch (error) {
        errorDiv.textContent = error.message || '제출에 실패했습니다.';
    }
}

// 게시글 작성
async function handlePostCreate(event) {
    event.preventDefault();
    const title = document.getElementById('post-title').value;
    const content = document.getElementById('post-content').value;
    const errorDiv = document.getElementById('post-error');
    
    try {
        await communityAPI.createPost(title, content);
        closeModal('post-modal');
        document.getElementById('post-form').reset();
        loadCommunityPosts();
        alert('게시글이 작성되었습니다.');
    } catch (error) {
        errorDiv.textContent = error.message || '작성에 실패했습니다.';
    }
}

// 커뮤니티 게시글 로드
async function loadCommunityPosts() {
    const postsDiv = document.getElementById('community-posts');
    
    if (!currentUser || currentUser.level < 2) {
        postsDiv.innerHTML = '<p>커뮤니티는 Level 2 (일반 회원) 이상만 이용할 수 있습니다.</p>';
        return;
    }
    
    try {
        const posts = await communityAPI.getPosts();
        // API가 배열을 직접 반환하므로 items 체크 불필요
        
        if (!posts || posts.length === 0) {
            postsDiv.innerHTML = '<p>게시글이 없습니다.</p>';
            return;
        }
        
        postsDiv.innerHTML = posts.map(post => `
            <div class="post-card">
                <h3>${escapeHtml(post.title)}</h3>
                <p>${escapeHtml(post.content)}</p>
                <div class="post-meta">
                    작성일: ${new Date(post.created_at).toLocaleString('ko-KR')} | 
                    조회수: ${post.view_count || 0} | 
                    좋아요: ${post.like_count || 0} | 
                    댓글: ${post.comment_count || 0}
                </div>
            </div>
        `).join('');
    } catch (error) {
        postsDiv.innerHTML = `<p class="error-message">게시글을 불러오는 중 오류가 발생했습니다: ${error.message}</p>`;
    }
}

// HTML 이스케이프
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

