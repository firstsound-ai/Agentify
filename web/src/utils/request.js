import axios from 'axios';

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
});


request.interceptors.request.use(config => {
//   const token = localStorage.getItem('token');
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
  return config;
}, error => {
  return Promise.reject(error);
});


request.interceptors.response.use(response => {
  return response.data;
}, error => {
  console.error('API Error:', error);
  return Promise.reject(error);
});

export default request;