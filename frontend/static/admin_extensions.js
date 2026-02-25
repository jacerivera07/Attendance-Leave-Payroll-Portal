/**
 * Admin Dashboard Extensions
 * Additional features for employee management
 */

// Load pending employees count
async function loadPendingEmployees() {
    const token = localStorage.getItem('token');
    const headers = token ? { 'Authorization': `Token ${token}` } : {};

    try {
        const response = await fetch(API_BASE_URL + '/employees/', { headers });
        if (response.ok) {
            const data = await response.json();
            const allEmployees = data.results || data;
            
            // Filter pending employees
            const pendingEmployees = allEmployees.filter(emp => emp.status === 'Pending');
            const pendingCount = pendingEmployees.length;
            
            // Update pending count badge
            const badge = document.getElementById('pending-badge');
            if (badge) {
                badge.textContent = pendingCount;
                if (pendingCount > 0) {
                    badge.classList.remove('hidden');
                } else {
                    badge.classList.add('hidden');
                }
            }
            
            return pendingEmployees;
        }
    } catch (error) {
        console.error('Error loading pending employees:', error);
    }
    return [];
}

// View pending employees
async function viewPendingEmployees() {
    const pendingEmps = await loadPendingEmployees();
    
    if (pendingEmps.length === 0) {
        alert('No pending employees to process! 🎉\n\nAll employees have been activated.');
        return;
    }
    
    // Show notification message
    const message = `You have ${pendingEmps.length} new employee${pendingEmps.length > 1 ? 's' : ''} waiting to be processed!`;
    
    // Create notification banner
    const banner = document.createElement('div');
    banner.className = 'bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4 rounded-lg';
    banner.innerHTML = `
        <div class="flex items-center gap-3">
            <i data-lucide="alert-circle" class="w-6 h-6 text-yellow-600"></i>
            <div>
                <p class="font-medium text-yellow-800">${message}</p>
                <p class="text-sm text-yellow-700 mt-1">Click "Setup Profile" to configure their details and activate their accounts.</p>
            </div>
        </div>
    `;
    
    // Insert banner before employee table
    const employeesView = document.getElementById('view-employees');
    const existingBanner = employeesView.querySelector('.bg-yellow-50.border-l-4');
    if (existingBanner) {
        existingBanner.remove();
    }
    const whiteBox = employeesView.querySelector('.bg-white');
    if (whiteBox) {
        employeesView.insertBefore(banner, whiteBox);
    }
    lucide.createIcons();
    
    // Filter to show only pending employees
    document.getElementById('employee-search').value = '';
    document.getElementById('department-filter').value = '';
    
    // Render only pending employees in the table
    const table = document.getElementById('employees-table');
    table.innerHTML = pendingEmps.map(emp => {
        return `
            <tr class="hover:bg-yellow-50 bg-yellow-50 border-l-4 border-yellow-400">
                <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-white font-bold">
                            ${emp.first_name[0]}${emp.last_name[0]}
                        </div>
                        <div>
                            <p class="font-medium text-gray-900">${emp.first_name} ${emp.last_name}</p>
                            <p class="text-sm text-gray-500">${emp.email}</p>
                            <span class="inline-flex items-center gap-1 text-xs text-yellow-700 font-medium mt-1">
                                <i data-lucide="clock" class="w-3 h-3"></i>
                                Awaiting Setup
                            </span>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600">${emp.department}</td>
                <td class="px-6 py-4 text-sm text-gray-600">${emp.position}</td>
                <td class="px-6 py-4 text-sm font-medium text-gray-900">₱${parseFloat(emp.salary).toLocaleString()}</td>
                <td class="px-6 py-4 text-sm text-gray-600">${emp.join_date}</td>
                <td class="px-6 py-4">
                    <span class="px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700 border border-yellow-300">
                        ${emp.status}
                    </span>
                </td>
                <td class="px-6 py-4">
                    <button onclick="openEditEmployee(${emp.id})" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium flex items-center gap-2">
                        <i data-lucide="settings" class="w-4 h-4"></i>
                        Setup Profile
                    </button>
                </td>
            </tr>
        `;
    }).join('');
    
    lucide.createIcons();
    
    // Switch to employees view if not already there
    switchView('employees');
}

// Open edit employee modal
async function openEditEmployee(employeeId) {
    // Try to get employee from global employees array first
    let employee = null;
    if (typeof employees !== 'undefined') {
        employee = employees.find(e => e.id === employeeId);
    }
    
    if (!employee) {
        // If not in global array, fetch from API
        const token = localStorage.getItem('token');
        try {
            const response = await fetch(API_BASE_URL + '/employees/' + employeeId + '/', {
                headers: { 'Authorization': 'Token ' + token }
            });
            if (response.ok) {
                const data = await response.json();
                employee = {
                    id: data.id,
                    firstName: data.first_name,
                    lastName: data.last_name,
                    email: data.email,
                    department: data.department,
                    position: data.position,
                    salary: data.salary,
                    joinDate: data.join_date,
                    status: data.status
                };
            }
        } catch (error) {
            console.error('Error fetching employee:', error);
            alert('Failed to load employee data');
            return;
        }
    }
    
    if (!employee) {
        alert('Employee not found');
        return;
    }
    
    // Populate form
    document.getElementById('edit-employee-id').value = employee.id;
    document.getElementById('edit-firstName').value = employee.firstName;
    document.getElementById('edit-lastName').value = employee.lastName;
    document.getElementById('edit-email').value = employee.email;
    document.getElementById('edit-department').value = employee.department;
    document.getElementById('edit-position').value = employee.position;
    document.getElementById('edit-salary').value = employee.salary;
    document.getElementById('edit-joinDate').value = employee.joinDate;
    document.getElementById('edit-status').value = employee.status;
    
    // Show modal
    openModal('edit-employee-modal');
}

// Handle edit employee form submission
async function handleEditEmployee(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const employeeId = formData.get('employeeId');
    
    const updatedEmployee = {
        first_name: formData.get('firstName'),
        last_name: formData.get('lastName'),
        email: formData.get('email'),
        department: formData.get('department'),
        position: formData.get('position'),
        salary: parseFloat(formData.get('salary')),
        join_date: formData.get('joinDate'),
        status: formData.get('status')
    };
    
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(API_BASE_URL + '/employees/' + employeeId + '/', {
            method: 'PUT',
            headers: {
                'Authorization': 'Token ' + token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedEmployee)
        });
        
        if (response.ok) {
            closeModal('edit-employee-modal');
            
            // If status changed to Active, show success message
            if (updatedEmployee.status === 'Active') {
                alert('✅ Employee profile activated successfully!\n\nThe employee can now access their dashboard.');
            } else {
                alert('✅ Employee updated successfully!');
            }
            
            // Reload data
            await loadDataFromAPI();
            await loadPendingEmployees();
            renderEmployees();
        } else {
            const error = await response.json();
            alert('Failed to update employee: ' + JSON.stringify(error));
        }
    } catch (error) {
        console.error('Update error:', error);
        alert('Failed to update employee');
    }
}

// Initialize on page load
if (typeof window !== 'undefined') {
    // Hook into the main loadDataFromAPI function
    window.addEventListener('DOMContentLoaded', () => {
        const originalLoadDataFromAPI = window.loadDataFromAPI;
        if (originalLoadDataFromAPI) {
            window.loadDataFromAPI = async function() {
                await originalLoadDataFromAPI();
                await loadPendingEmployees();
            };
        }
        
        // Load pending employees on initial load
        setTimeout(() => {
            loadPendingEmployees();
        }, 1000);
    });
}
