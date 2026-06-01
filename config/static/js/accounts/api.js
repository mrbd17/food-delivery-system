function getCookie(name) {
  return document.cookie
    .split("; ")
    .find(row => row.startsWith(name + "="))
    ?.split("=")[1];
}

const csrfToken = getCookie("csrftoken");

const api = axios.create({
  baseURL: "/api",
  timeout: 10000,
  withCredentials: true,
  headers: {
    "X-CSRFToken": csrfToken,
    "X-Requested-With": "XMLHttpRequest",
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error", error);

    if (error.response?.status === 401) {
      window.location.href = `/accounts/login/?next=${window.location.pathname}`;
    }

    return Promise.reject(error);
  }
);

export default api;