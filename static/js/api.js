// API 클라이언트
const API_BASE_URL = window.location.origin;

// 토큰 관리
let authToken = localStorage.getItem('authToken');

function setAuthToken(token) {
    authToken = token;
    if (token) {
        localStorage.setItem('authToken', token);
    } else {
        localStorage.removeItem('authToken');
    }
}

function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json',
    };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    return headers;
}

// API 호출 함수
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        ...options,
        headers: {
            ...getAuthHeaders(),
            ...options.headers,
        },
    };

    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '요청 실패');
        }
        
        return data;
    } catch (error) {
        console.error('API 호출 오류:', error);
        throw error;
    }
}

// 인증 API
const authAPI = {
    signup: async (userData) => {
        return apiCall('/api/auth/signup', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    },
    
    login: async (email, password) => {
        const data = await apiCall('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        setAuthToken(data.access_token);
        return data;
    },
    
    getProfile: async () => {
        return apiCall('/api/users/me');
    },
    
    updateProfile: async (profileData) => {
        return apiCall('/api/users/me', {
            method: 'PUT',
            body: JSON.stringify(profileData),
        });
    },
};

// 챗봇 API
const chatAPI = {
    sendMessage: async (message, history = [], roomId = null) => {
        const params = roomId ? `?room_id=${roomId}` : '';
        return apiCall(`/api/chat/message${params}`, {
            method: 'POST',
            body: JSON.stringify({ message, history }),
        });
    },
    
    getRooms: async () => {
        return apiCall('/api/chat/rooms');
    },
    
    createRoom: async (title) => {
        return apiCall('/api/chat/rooms', {
            method: 'POST',
            body: JSON.stringify({ title }),
        });
    },
};

// 복지 정보 API
const welfareAPI = {
    search: async (keyword = '', region = '', age = null) => {
        const params = new URLSearchParams();
        if (keyword) params.append('keyword', keyword);
        if (region) params.append('region', region);
        if (age) params.append('age', age);
        
        return apiCall(`/api/welfare/search?${params.toString()}`);
    },
    
    bookmark: async (welfareId) => {
        return apiCall(`/api/welfare/${welfareId}/bookmark`, {
            method: 'POST',
        });
    },
    
    getBookmarks: async () => {
        return apiCall('/api/users/bookmarks/welfare');
    },
};

// 커뮤니티 API
const communityAPI = {
    verify: async (content) => {
        return apiCall('/api/community/verify', {
            method: 'POST',
            body: JSON.stringify({ text: content }),
        });
    },
    
    getPosts: async () => {
        return apiCall('/api/community/posts');
    },
    
    createPost: async (title, content) => {
        return apiCall('/api/community/posts', {
            method: 'POST',
            body: JSON.stringify({ title, content, category: 'free' }),
        });
    },
};

