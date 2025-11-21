const API_BASE = '/api';

export const curationApi = {
  getQueue: async (status = 'pending', page = 1, limit = 20) => {
    const response = await fetch(
      `${API_BASE}/curation/queue?status=${status}&page=${page}&limit=${limit}`
    );
    return response.json();
  },

  getCuration: async (id) => {
    const response = await fetch(`${API_BASE}/curation/${id}`);
    return response.json();
  },

  claim: async (id, reviewerId) => {
    const response = await fetch(`${API_BASE}/curation/${id}/claim`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId })
    });
    return response.json();
  },

  approve: async (id, reviewerId) => {
    const response = await fetch(`${API_BASE}/curation/${id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId })
    });
    return response.json();
  },

  reject: async (id, reviewerId, feedback) => {
    const response = await fetch(`${API_BASE}/curation/${id}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId, feedback })
    });
    return response.json();
  },

  requestRevision: async (id, reviewerId, feedback) => {
    const response = await fetch(`${API_BASE}/curation/${id}/revise`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId, feedback })
    });
    return response.json();
  },

  release: async (id, reviewerId) => {
    const response = await fetch(`${API_BASE}/curation/${id}/release`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId })
    });
    return response.json();
  },

  getAuditLogs: async (id) => {
    const response = await fetch(`${API_BASE}/curation/${id}/audit`);
    return response.json();
  }
};

export const questionApi = {
  generate: async (topic, difficulty = 'medium') => {
    const response = await fetch(
      `${API_BASE}/questions/generate?topic=${encodeURIComponent(topic)}&difficulty=${difficulty}`,
      { method: 'POST' }
    );
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
    return response.json();
  },

  getApproved: async (topic = null) => {
    const url = topic 
      ? `${API_BASE}/questions/approved?topic=${encodeURIComponent(topic)}`
      : `${API_BASE}/questions/approved`;
    const response = await fetch(url);
    return response.json();
  }
};

export const analyticsApi = {
  getCurationAnalytics: async (days = 7) => {
    const response = await fetch(`${API_BASE}/analytics/curation?days=${days}`);
    return response.json();
  }
};
