/**
 * API Integration Layer for HR Nexus
 * Connects frontend to Django REST API
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// API Helper Functions
const api = {
    // Generic GET request
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    },

    // Generic POST request
    async post(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(JSON.stringify(errorData));
            }
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    },

    // Generic PUT request
    async put(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API PUT Error:', error);
            throw error;
        }
    },

    // Generic PATCH request
    async patch(endpoint, data = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API PATCH Error:', error);
            throw error;
        }
    },

    // Generic DELETE request
    async delete(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'DELETE',
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return true;
        } catch (error) {
            console.error('API DELETE Error:', error);
            throw error;
        }
    }
};

// Employee API
const employeeAPI = {
    getAll: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return api.get(`/employees/${queryString ? '?' + queryString : ''}`);
    },
    getById: (id) => api.get(`/employees/${id}/`),
    create: (data) => api.post('/employees/', data),
    update: (id, data) => api.put(`/employees/${id}/`, data),
    delete: (id) => api.delete(`/employees/${id}/`),
    getStats: () => api.get('/employees/stats/')
};

// Attendance API
const attendanceAPI = {
    getAll: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return api.get(`/attendance/${queryString ? '?' + queryString : ''}`);
    },
    getById: (id) => api.get(`/attendance/${id}/`),
    create: (data) => api.post('/attendance/', data),
    update: (id, data) => api.put(`/attendance/${id}/`, data),
    delete: (id) => api.delete(`/attendance/${id}/`),
    clock: (employeeId, clockType) => api.post('/attendance/clock/', {
        employee_id: employeeId,
        clock_type: clockType
    }),
    getToday: () => api.get('/attendance/today/'),
    getStats: () => api.get('/attendance/stats/')
};

// Leave API
const leaveAPI = {
    getAll: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return api.get(`/leaves/${queryString ? '?' + queryString : ''}`);
    },
    getById: (id) => api.get(`/leaves/${id}/`),
    create: (data) => api.post('/leaves/', data),
    update: (id, data) => api.put(`/leaves/${id}/`, data),
    delete: (id) => api.delete(`/leaves/${id}/`),
    approve: (id) => api.patch(`/leaves/${id}/approve/`),
    reject: (id) => api.patch(`/leaves/${id}/reject/`),
    getPending: () => api.get('/leaves/pending/'),
    getStats: () => api.get('/leaves/stats/')
};

// Payroll API
const payrollAPI = {
    getAll: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return api.get(`/payroll/${queryString ? '?' + queryString : ''}`);
    },
    getById: (id) => api.get(`/payroll/${id}/`),
    create: (data) => api.post('/payroll/', data),
    update: (id, data) => api.put(`/payroll/${id}/`, data),
    delete: (id) => api.delete(`/payroll/${id}/`),
    process: (month, year) => api.post('/payroll/process/', { month, year }),
    getPayslip: (id) => api.get(`/payroll/${id}/payslip/`),
    getStats: (month, year) => api.get(`/payroll/stats/?month=${month}&year=${year}`)
};

// Export for use in main application
window.employeeAPI = employeeAPI;
window.attendanceAPI = attendanceAPI;
window.leaveAPI = leaveAPI;
window.payrollAPI = payrollAPI;
