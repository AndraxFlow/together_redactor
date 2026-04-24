import axios from "axios";
import { getToken } from "./storage";

const apiBaseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
});

apiClient.interceptors.request.use((config) => {
  const token = getToken();

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});