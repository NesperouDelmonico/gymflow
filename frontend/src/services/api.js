// src/services/api.js
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const membershipsApi = {
  list:   ()         => api.get("/memberships/"),
  create: (data)     => api.post("/memberships/", data),
  update: (id, data) => api.put(`/memberships/${id}`, data),
  delete: (id)       => api.delete(`/memberships/${id}`),
  mine:   ()         => api.get("/memberships/my"),
};

export const plansApi = {
  list: () => api.get("/plans/"),
};

export const usersApi = {
  list: () => api.get("/users/"),
};

export default api;
