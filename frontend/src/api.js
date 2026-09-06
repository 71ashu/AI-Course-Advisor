/**
 * API client for AI Course Advisor backend.
 * Uses fetch with credentials for session-based auth.
 */

const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const isFormData = options.body instanceof FormData;
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: 'include',
    headers: {
      // Let the browser set the multipart Content-Type (with boundary) itself.
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...options.headers,
    },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed: ${res.status}`);
  }
  return data;
}

export const api = {
  // Auth
  register: (data) => request('/auth/register', {
    method: 'POST',
    body: data instanceof FormData ? data : JSON.stringify(data),
  }),
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  forgotPassword: (data) => request('/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  resetPassword: (data) => request('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  me: () => request('/auth/me'),

  // Profile
  getProfile: () => request('/profile'),
  updateProfile: (data) => request('/profile', { method: 'PUT', body: JSON.stringify(data) }),

  // Courses
  getCourses: () => request('/courses'),
  getPrograms: () => request('/programs'),

  // Advisor
  getRecommendations: (query, history = []) => request('/recommend', {
    method: 'POST',
    body: JSON.stringify({ query, history }),
  }),
  getProgress: () => request('/progress'),

  // Prerequisite Graph
  getPrerequisitePath: (target) => request(`/prerequisite-path?target=${encodeURIComponent(target)}`),
  getPrerequisiteGraph: () => request('/prerequisite-graph'),

  // Onboarding
  submitOnboarding: (data) => request('/onboarding', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};
