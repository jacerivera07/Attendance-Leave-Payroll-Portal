/**
 * Employee Dashboard JavaScript
 * Handles all employee-specific functionality
 */

// Current employee data
let currentEmployee = null;
let currentUser = null;
let myAttendance = [];
let myLeaves = [];
let myPayroll = [];

// Authentication Check
function checkAuth() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (!token || !user) {
        window.location.href = '/login';
        return null;
    }
    
    const userData = JSON.parse(user);
    
    // Check if user is employee role
    if (userData.role !== 'employee') {
        // Redirect admin to admin dashboard
        window.location.href = '/';
        return null;
    }
    
    return userData;
}

// Load User Info
async function loadUserInfo() {
    currentUser = checkAuth();
    if (!currentUser) return;
    
    // Update user display
    const initials = (currentUser.first_name?.[0] || '') + (currentUser.last_name?.[0] || '');
    document.getElementById('user-initials').textContent = initials || currentUser.username?.[0]?.toUpperCase() || '?';
    document.getElementById('user-name').textContent = currentUser.first_name && currentUser.last_name 
        ? `${currentUser.first_name} ${currentUser.last_name}` 
        : currentUser.username;
    document.getElementById('user-role').textContent = 'Employee';
    
    // Load employee profile
    await loadEmployeeProfile();
}

// Load Employee Profile
async function loadEmployeeProfile() {
    const token = localStorage.getItem('token');
    const headers = {
        'Authorization': 'Token ' + token
    };

    try {
        // Get all employees and find current user's employee record
        const response = await fetch(API_BASE_URL + '/employees/', { headers });
        if (response.ok) {
            const data = await response.json();
            const employees = data.results || data;
            
            // Find employee by email matching user email
            currentEmployee = employees.find(emp => emp.email === currentUser.email);
            
            if (currentEmployee) {
                console.log('Current employee loaded:', currentEmployee);
                loadMyData();
            } else {
                console.error('Employee profile not found');
                alert('Employee profile not found. Please contact administrator.');
            }
        }
    } catch (error) {
        console.error('Error loading employee profile:', error);
    }
}

// Load My Data
async function loadMyData() {
    if (!currentEmployee) return;
    
    const token = localStorage.getItem('token');
    const headers = {
        'Authorization': 'Token ' + token
    };

    try {
        // Load my attendance
        const attResponse = await fetch(API_BASE_URL + '/attendance/?employee=' + currentEmployee.id, { headers });
        if (attResponse.ok) {
            const attData = await attResponse.json();
            myAttendance = (attData.results || attData).map(att => ({
                id: att.id,
                employeeId: att.employee,
                date: att.date,
                status: att.status,
                clockIn: att.clock_in,
                clockOut: att.clock_out,
                notes: att.notes || ''
            }));
            console.log('Loaded my attendance:', myAttendance.length);
        }

        // Load my leaves
        const leaveResponse = await fetch(API_BASE_URL + '/leaves/?employee=' + currentEmployee.id, { headers });
        if (leaveResponse.ok) {
            const leaveData = await leaveResponse.json();
            myLeaves = (leaveData.results || leaveData).map(leave => ({
                id: leave.id,
                employeeId: leave.employee,
                type: leave.leave_type,
                startDate: leave.start_date,
                endDate: leave.end_date,
                days: leave.days,
                status: leave.status,
                reason: leave.reason || ''
            }));
            console.log('Loaded my leaves:', myLeaves.length);
        }

        // Load my payroll
        const payrollResponse = await fetch(API_BASE_URL + '/payroll/?employee=' + currentEmployee.id, { headers });
        if (payrollResponse.ok) {
            const payrollData = await payrollResponse.json();
            myPayroll = payrollData.results || payrollData;
            console.log('Loaded my payroll:', myPayroll.length);
        }

        // Refresh dashboard after loading data
        refreshDashboard();
        
    } catch (error) {
        console.error('Error loading my data:', error);
    }
}

// Logout Function
async function handleLogout() {
    if (!confirm('Are you sure you want to logout?')) return;
    
    const token = localStorage.getItem('token');
    
    try {
        await fetch(API_BASE_URL + '/auth/logout/', {
            method: 'POST',
            headers: {
                'Authorization': 'Token ' + token,
                'Content-Type': 'application/json'
            }
        });
    } catch (error) {
        console.error('Logout error:', error);
    }
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

// Clock
function updateClock() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString('en-US', { hour12: false });
    document.getElementById('current-date').textContent = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
}
setInterval(updateClock, 1000);
updateClock();

// Mobile Menu Toggle
function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-overlay');
    sidebar.classList.toggle('-translate-x-full');
    overlay.classList.toggle('hidden');
}

// View Switching
function switchView(viewName) {
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
    document.getElementById(`view-${viewName}`).classList.remove('hidden');
    
    document.querySelectorAll('.sidebar-link').forEach(el => el.classList.remove('active'));
    document.getElementById(`nav-${viewName}`).classList.add('active');
    
    if (window.innerWidth < 1024) {
        toggleMobileMenu();
    }

    if (viewName === 'dashboard') refreshDashboard();
    if (viewName === 'attendance') loadMyAttendance();
    if (viewName === 'leave') renderMyLeaves();
    if (viewName === 'payroll') renderMyPayroll();
    if (viewName === 'profile') renderMyProfile();
    
    lucide.createIcons();
}

// Modal Functions
function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
    lucide.createIcons();
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// Dashboard Functions
function refreshDashboard() {
    if (!currentEmployee) return;
    
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    // Filter attendance for current month
    const monthAttendance = myAttendance.filter(a => {
        const date = new Date(a.date);
        return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
    });
    
    const presentDays = monthAttendance.filter(a => a.status === 'Present' || a.status === 'Late').length;
    const absentDays = monthAttendance.filter(a => a.status === 'Absent').length;
    const workingDays = 22; // Assumed working days per month
    const attendanceRate = workingDays > 0 ? Math.round((presentDays / workingDays) * 100) : 0;
    
    // Filter leaves for current year
    const yearLeaves = myLeaves.filter(l => {
        const date = new Date(l.startDate);
        return date.getFullYear() === currentYear && l.status === 'Approved';
    });
    const leavesTaken = yearLeaves.reduce((sum, l) => sum + l.days, 0);
    
    // Update stats
    document.getElementById('stat-days-present').textContent = presentDays;
    document.getElementById('stat-days-absent').textContent = absentDays;
    document.getElementById('stat-leaves-taken').textContent = leavesTaken;
    document.getElementById('stat-attendance-rate').textContent = `${attendanceRate}%`;
    
    // Recent attendance table
    const recentAttendance = myAttendance.slice(-7).reverse();
    const recentTable = document.getElementById('recent-attendance-table');
    recentTable.innerHTML = recentAttendance.map(a => `
        <tr class="hover:bg-gray-50">
            <td class="px-4 py-3 text-gray-600">${a.date}</td>
            <td class="px-4 py-3"><span class="px-2 py-1 rounded-full text-xs font-medium status-${a.status.toLowerCase().replace(' ', '-')}">${a.status}</span></td>
            <td class="px-4 py-3 text-gray-600">${a.clockIn || '-'}</td>
            <td class="px-4 py-3 text-gray-600">${a.clockOut || '-'}</td>
        </tr>
    `).join('');
    
    // My leaves list
    const pendingLeaves = myLeaves.filter(l => l.status === 'Pending');
    document.getElementById('pending-leaves-count').textContent = pendingLeaves.length;
    
    const leavesList = document.getElementById('my-leaves-list');
    if (pendingLeaves.length === 0) {
        leavesList.innerHTML = '<p class="text-gray-500 text-center py-4 text-sm">No pending requests</p>';
    } else {
        leavesList.innerHTML = pendingLeaves.slice(0, 3).map(l => `
            <div class="p-3 bg-gray-50 rounded-xl">
                <div class="flex items-center gap-2 mb-1">
                    <i data-lucide="clock" class="w-4 h-4 text-yellow-600"></i>
                    <p class="font-medium text-sm">${l.type}</p>
                </div>
                <p class="text-xs text-gray-500">${l.startDate} to ${l.endDate}</p>
                <p class="text-xs text-gray-500 mt-1">${l.days} days • Pending</p>
            </div>
        `).join('');
    }
    
    lucide.createIcons();
}

// My Attendance Functions
function loadMyAttendance() {
    if (!currentEmployee) return;
    
    const dateInput = document.getElementById('attendance-date');
    if (!dateInput.value) {
        // Set to current month start
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        dateInput.valueAsDate = firstDay;
    }
    
    const table = document.getElementById('attendance-table');
    
    // Sort by date descending
    const sortedAttendance = [...myAttendance].sort((a, b) => new Date(b.date) - new Date(a.date));
    
    table.innerHTML = sortedAttendance.map(record => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 text-sm text-gray-600">${record.date}</td>
            <td class="px-6 py-4">
                <span class="px-3 py-1 rounded-full text-xs font-medium status-${record.status.toLowerCase().replace(' ', '-')}">${record.status}</span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600">${record.clockIn || '-'}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${record.clockOut || '-'}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${calculateWorkingHours(record.clockIn, record.clockOut)}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${record.notes || '-'}</td>
        </tr>
    `).join('');
}

function calculateWorkingHours(clockIn, clockOut) {
    if (!clockIn || !clockOut) return '-';
    const [inH, inM] = clockIn.split(':').map(Number);
    const [outH, outM] = clockOut.split(':').map(Number);
    const diff = (outH * 60 + outM) - (inH * 60 + inM);
    const hours = Math.floor(diff / 60);
    const mins = diff % 60;
    return `${hours}h ${mins}m`;
}

// Clock In/Out Functions
function setClockType(type) {
    document.getElementById('clock-type').value = type;
    document.getElementById('btn-clock-in').classList.toggle('border-green-500', type === 'in');
    document.getElementById('btn-clock-in').classList.toggle('text-green-600', type === 'in');
    document.getElementById('btn-clock-in').classList.toggle('border-gray-200', type !== 'in');
    document.getElementById('btn-clock-in').classList.toggle('text-gray-600', type !== 'in');
    
    document.getElementById('btn-clock-out').classList.toggle('border-red-500', type === 'out');
    document.getElementById('btn-clock-out').classList.toggle('text-red-600', type === 'out');
    document.getElementById('btn-clock-out').classList.toggle('border-gray-200', type !== 'out');
    document.getElementById('btn-clock-out').classList.toggle('text-gray-600', type !== 'out');
}

async function handleClockSubmit(e) {
    e.preventDefault();
    
    if (!currentEmployee) {
        alert('Employee profile not loaded');
        return;
    }
    
    const type = document.getElementById('clock-type').value;
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(API_BASE_URL + '/attendance/clock/', {
            method: 'POST',
            headers: {
                'Authorization': 'Token ' + token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                employee_id: currentEmployee.id,
                clock_type: type
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(`Successfully clocked ${type}!`);
            closeModal('clock-modal');
            
            // Reload data
            await loadMyData();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to clock in/out');
        }
    } catch (error) {
        console.error('Clock error:', error);
        alert('Failed to clock in/out');
    }
}

// My Leaves Functions
function renderMyLeaves() {
    if (!currentEmployee) return;
    
    // Update stats
    document.getElementById('leave-total').textContent = myLeaves.length;
    document.getElementById('leave-approved').textContent = myLeaves.filter(l => l.status === 'Approved').length;
    document.getElementById('leave-pending').textContent = myLeaves.filter(l => l.status === 'Pending').length;
    document.getElementById('leave-rejected').textContent = myLeaves.filter(l => l.status === 'Rejected').length;
    
    // Render table
    const table = document.getElementById('leave-table');
    const sortedLeaves = [...myLeaves].sort((a, b) => new Date(b.startDate) - new Date(a.startDate));
    
    table.innerHTML = sortedLeaves.map(leave => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 text-sm text-gray-600">${leave.type}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${leave.startDate}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${leave.endDate}</td>
            <td class="px-6 py-4 text-sm text-gray-600">${leave.days} days</td>
            <td class="px-6 py-4">
                <span class="px-3 py-1 rounded-full text-xs font-medium status-${leave.status.toLowerCase()}">${leave.status}</span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-600">${leave.reason || '-'}</td>
        </tr>
    `).join('');
    
    lucide.createIcons();
}

async function handleLeaveRequest(e) {
    e.preventDefault();
    
    if (!currentEmployee) {
        alert('Employee profile not loaded');
        return;
    }
    
    const formData = new FormData(e.target);
    const start = new Date(formData.get('startDate'));
    const end = new Date(formData.get('endDate'));
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    
    const leaveData = {
        employee: currentEmployee.id,
        leave_type: formData.get('type'),
        start_date: formData.get('startDate'),
        end_date: formData.get('endDate'),
        days: diffDays,
        reason: formData.get('reason')
    };
    
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(API_BASE_URL + '/leaves/', {
            method: 'POST',
            headers: {
                'Authorization': 'Token ' + token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(leaveData)
        });
        
        if (response.ok) {
            alert('Leave request submitted successfully!');
            closeModal('request-leave-modal');
            e.target.reset();
            
            // Reload data
            await loadMyData();
        } else {
            const error = await response.json();
            alert('Failed to submit leave request: ' + JSON.stringify(error));
        }
    } catch (error) {
        console.error('Leave request error:', error);
        alert('Failed to submit leave request');
    }
}

// My Payroll Functions
function renderMyPayroll() {
    if (!currentEmployee) return;
    
    const table = document.getElementById('payroll-table');
    const sortedPayroll = [...myPayroll].sort((a, b) => {
        if (b.year !== a.year) return b.year - a.year;
        return b.month - a.month;
    });
    
    if (sortedPayroll.length === 0) {
        table.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-500">No payroll records found</td></tr>';
        return;
    }
    
    table.innerHTML = sortedPayroll.map(payroll => {
        const monthName = new Date(payroll.year, payroll.month - 1, 1).toLocaleString('default', { month: 'long' });
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 text-sm font-medium text-gray-900">${monthName} ${payroll.year}</td>
                <td class="px-6 py-4 text-sm text-gray-600">{parseFloat(payroll.basic_salary).toLocaleString()}</td>
                <td class="px-6 py-4 text-sm text-green-600">+{parseFloat(payroll.allowances).toLocaleString()}</td>
                <td class="px-6 py-4 text-sm text-green-600">+{parseFloat(payroll.overtime).toLocaleString()}</td>
                <td class="px-6 py-4 text-sm text-red-600">-{parseFloat(payroll.deductions).toLocaleString()}</td>
                <td class="px-6 py-4 text-sm font-bold text-gray-900">{parseFloat(payroll.net_salary).toLocaleString()}</td>
                <td class="px-6 py-4">
                    <button onclick="viewMyPayslip(${payroll.id})" class="p-2 bg-indigo-100 text-indigo-600 rounded-lg hover:bg-indigo-200 transition-colors">
                        <i data-lucide="eye" class="w-4 h-4"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
    
    lucide.createIcons();
}

async function viewMyPayslip(payrollId) {
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(API_BASE_URL + '/payroll/' + payrollId + '/payslip/', {
            headers: {
                'Authorization': 'Token ' + token
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayPayslip(data);
        } else {
            alert('Failed to load payslip');
        }
    } catch (error) {
        console.error('Payslip error:', error);
        alert('Failed to load payslip');
    }
}

function displayPayslip(data) {
    const monthName = new Date(data.period.year, data.period.month - 1, 1).toLocaleString('default', { month: 'long' });
    
    const payslipHtml = `
        <div class="text-center mb-6 border-b-2 border-gray-100 pb-4">
            <h2 class="text-2xl font-bold text-indigo-900">HR NEXUS</h2>
            <p class="text-gray-600">Payslip for ${monthName} ${data.period.year}</p>
        </div>
        
        <div class="grid grid-cols-2 gap-6 mb-6">
            <div>
                <h4 class="font-bold text-gray-900 mb-2">Employee Details</h4>
                <p class="text-sm text-gray-600"><strong>Name:</strong> ${data.employee.name}</p>
                <p class="text-sm text-gray-600"><strong>Department:</strong> ${data.employee.department}</p>
                <p class="text-sm text-gray-600"><strong>Position:</strong> ${data.employee.position}</p>
                <p class="text-sm text-gray-600"><strong>Employee ID:</strong> ${data.employee.employee_id}</p>
            </div>
            <div class="text-right">
                <h4 class="font-bold text-gray-900 mb-2">Payment Details</h4>
                <p class="text-sm text-gray-600"><strong>Pay Date:</strong> ${new Date(data.period.pay_date).toLocaleDateString()}</p>
                <p class="text-sm text-gray-600"><strong>Bank:</strong> Sample Bank</p>
            </div>
        </div>
        
        <table class="w-full mb-6">
            <thead>
                <tr class="bg-gray-50">
                    <th class="text-left py-2 px-4 border-b">Description</th>
                    <th class="text-right py-2 px-4 border-b">Amount (₱)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="py-2 px-4 border-b">Basic Salary</td>
                    <td class="text-right py-2 px-4 border-b">₱${data.earnings.basic_salary.toLocaleString()}</td>
                </tr>
                <tr>
                    <td class="py-2 px-4 border-b">Allowances</td>
                    <td class="text-right py-2 px-4 border-b text-green-600">+₱${data.earnings.allowances.toLocaleString()}</td>
                </tr>
                <tr>
                    <td class="py-2 px-4 border-b">Overtime</td>
                    <td class="text-right py-2 px-4 border-b text-green-600">+₱${data.earnings.overtime.toLocaleString()}</td>
                </tr>
                <tr class="bg-gray-50 font-semibold">
                    <td class="py-2 px-4 border-b">Gross Salary</td>
                    <td class="text-right py-2 px-4 border-b">₱${data.earnings.gross_salary.toLocaleString()}</td>
                </tr>
                <tr>
                    <td class="py-2 px-4 border-b">Deductions</td>
                    <td class="text-right py-2 px-4 border-b text-red-600">-₱${data.deductions.total.toLocaleString()}</td>
                </tr>
                <tr class="bg-indigo-50 font-bold text-indigo-900 text-lg">
                    <td class="py-3 px-4">NET SALARY</td>
                    <td class="text-right py-3 px-4">₱${data.net_salary.toLocaleString()}</td>
                </tr>
            </tbody>
        </table>
        
        <div class="border-t-2 border-gray-100 pt-4 text-center text-sm text-gray-500">
            <p>This is a computer-generated payslip and does not require signature.</p>
            <p class="mt-1">For queries, contact HR at hr@company.com</p>
        </div>
    `;
    
    document.getElementById('payslip-content').innerHTML = payslipHtml;
    openModal('payslip-modal');
}

function printPayslip() {
    const content = document.getElementById('payslip-content').innerHTML;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>Payslip</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <style>
                    body { font-family: 'Inter', sans-serif; padding: 20px; }
                    @media print { body { padding: 0; } }
                </style>
            </head>
            <body>
                ${content}
            </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 250);
}

// My Profile Functions
function renderMyProfile() {
    if (!currentEmployee) return;
    
    const initials = currentEmployee.first_name[0] + currentEmployee.last_name[0];
    document.getElementById('profile-initials').textContent = initials;
    document.getElementById('profile-name').textContent = `${currentEmployee.first_name} ${currentEmployee.last_name}`;
    document.getElementById('profile-position').textContent = currentEmployee.position;
    document.getElementById('profile-department').textContent = currentEmployee.department;
    document.getElementById('profile-join-date').textContent = currentEmployee.join_date;
    document.getElementById('profile-status').textContent = currentEmployee.status;
    
    document.getElementById('profile-first-name').textContent = currentEmployee.first_name;
    document.getElementById('profile-last-name').textContent = currentEmployee.last_name;
    document.getElementById('profile-email').textContent = currentEmployee.email;
    document.getElementById('profile-emp-id').textContent = `EMP-${String(currentEmployee.id).padStart(4, '0')}`;
    
    // Calculate stats
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    const monthAttendance = myAttendance.filter(a => {
        const date = new Date(a.date);
        return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
    });
    
    const presentDays = monthAttendance.filter(a => a.status === 'Present' || a.status === 'Late').length;
    const absentDays = monthAttendance.filter(a => a.status === 'Absent').length;
    const workingDays = 22;
    const attendanceRate = workingDays > 0 ? Math.round((presentDays / workingDays) * 100) : 0;
    
    const yearLeaves = myLeaves.filter(l => {
        const date = new Date(l.startDate);
        return date.getFullYear() === currentYear && l.status === 'Approved';
    });
    const leavesTaken = yearLeaves.reduce((sum, l) => sum + l.days, 0);
    
    document.getElementById('profile-stat-present').textContent = presentDays;
    document.getElementById('profile-stat-absent').textContent = absentDays;
    document.getElementById('profile-stat-leaves').textContent = leavesTaken;
    document.getElementById('profile-stat-rate').textContent = `${attendanceRate}%`;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', async function() {
    await loadUserInfo();
    lucide.createIcons();
});

