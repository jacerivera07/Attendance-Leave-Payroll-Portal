from django.contrib import admin
from .models import Employee, Attendance, Leave, Payroll


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'department', 'position', 'salary', 'status', 'join_date']
    list_filter = ['department', 'status', 'join_date']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['-created_at']
    date_hierarchy = 'join_date'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Employment Details', {
            'fields': ('department', 'position', 'salary', 'join_date', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'date', 'status', 'clock_in', 'clock_out', 'working_hours']
    list_filter = ['status', 'date']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Employee & Date', {
            'fields': ('employee', 'date')
        }),
        ('Attendance Details', {
            'fields': ('status', 'clock_in', 'clock_out', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'leave_type', 'start_date', 'end_date', 'days', 'status']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['-created_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Employee', {
            'fields': ('employee',)
        }),
        ('Leave Details', {
            'fields': ('leave_type', 'start_date', 'end_date', 'days', 'reason')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['approve_leaves', 'reject_leaves']
    
    def approve_leaves(self, request, queryset):
        updated = queryset.update(status='Approved')
        self.message_user(request, f'{updated} leave request(s) approved.')
    approve_leaves.short_description = 'Approve selected leave requests'
    
    def reject_leaves(self, request, queryset):
        updated = queryset.update(status='Rejected')
        self.message_user(request, f'{updated} leave request(s) rejected.')
    reject_leaves.short_description = 'Reject selected leave requests'


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'month', 'year', 'basic_salary', 'net_salary', 'status', 'processed_date']
    list_filter = ['status', 'month', 'year']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['-year', '-month', '-created_at']
    
    fieldsets = (
        ('Employee & Period', {
            'fields': ('employee', 'month', 'year')
        }),
        ('Salary Components', {
            'fields': ('basic_salary', 'allowances', 'overtime', 'deductions', 'net_salary')
        }),
        ('Status', {
            'fields': ('status', 'processed_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['net_salary', 'processed_date', 'created_at', 'updated_at']
    
    actions = ['mark_as_processed', 'mark_as_paid']
    
    def mark_as_processed(self, request, queryset):
        updated = queryset.update(status='Processed')
        self.message_user(request, f'{updated} payroll record(s) marked as processed.')
    mark_as_processed.short_description = 'Mark selected as Processed'
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='Paid')
        self.message_user(request, f'{updated} payroll record(s) marked as paid.')
    mark_as_paid.short_description = 'Mark selected as Paid'
