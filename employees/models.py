from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with role-based access"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    class Meta:
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_employee_user(self):
        return self.role == 'employee'


class Employee(models.Model):
    """Employee model for storing employee information"""
    
    DEPARTMENT_CHOICES = [
        ('Engineering', 'Engineering'),
        ('Design', 'Design'),
        ('Marketing', 'Marketing'),
        ('HR', 'HR'),
        ('Sales', 'Sales'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending Setup'),
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    join_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['department']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.department}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Attendance(models.Model):
    """Attendance model for tracking employee attendance"""
    
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Half Day', 'Half Day'),
        ('On Leave', 'On Leave'),
    ]
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['status']),
        ]
        verbose_name_plural = 'Attendance Records'
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.status}"
    
    @property
    def working_hours(self):
        """Calculate working hours"""
        if self.clock_in and self.clock_out:
            from datetime import datetime, timedelta
            clock_in_dt = datetime.combine(self.date, self.clock_in)
            clock_out_dt = datetime.combine(self.date, self.clock_out)
            
            if clock_out_dt < clock_in_dt:
                clock_out_dt += timedelta(days=1)
            
            diff = clock_out_dt - clock_in_dt
            hours = diff.total_seconds() / 3600
            return round(hours, 2)
        return 0


class Leave(models.Model):
    """Leave model for managing employee leave requests"""
    
    LEAVE_TYPE_CHOICES = [
        ('Vacation', 'Vacation'),
        ('Sick Leave', 'Sick Leave'),
        ('Personal', 'Personal'),
        ('Work From Home', 'Work From Home'),
        ('Unpaid', 'Unpaid Leave'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['employee', 'status']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def save(self, *args, **kwargs):
        """Calculate days if not provided"""
        if not self.days:
            delta = self.end_date - self.start_date
            self.days = delta.days + 1
        super().save(*args, **kwargs)


class Payroll(models.Model):
    """Payroll model for managing employee salary payments"""
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processed', 'Processed'),
        ('Paid', 'Paid'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payroll_records'
    )
    month = models.IntegerField(validators=[MinValueValidator(1)])
    year = models.IntegerField(validators=[MinValueValidator(2000)])
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    processed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', '-month', '-created_at']
        unique_together = ['employee', 'month', 'year']
        indexes = [
            models.Index(fields=['month', 'year']),
            models.Index(fields=['employee', 'month', 'year']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.month}/{self.year} - ${self.net_salary}"
    
    def save(self, *args, **kwargs):
        """Calculate net salary before saving"""
        self.net_salary = (
            self.basic_salary + 
            self.allowances + 
            self.overtime - 
            self.deductions
        )
        if self.status == 'Processed' and not self.processed_date:
            self.processed_date = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def gross_salary(self):
        """Calculate gross salary"""
        return self.basic_salary + self.allowances + self.overtime



class PayrollPeriod(models.Model):
    """Payroll Period model for bi-monthly cutoff management"""
    
    PERIOD_CHOICES = [
        ('first_half', '1st-15th'),
        ('second_half', '16th-End of Month'),
    ]
    
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Processing', 'Processing'),
        ('Closed', 'Closed'),
    ]
    
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    month = models.IntegerField(validators=[MinValueValidator(1)])
    year = models.IntegerField(validators=[MinValueValidator(2000)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', '-month', '-start_date']
        unique_together = ['period_type', 'month', 'year']
        indexes = [
            models.Index(fields=['month', 'year']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.get_period_type_display()} - {self.month}/{self.year}"
    
    @property
    def period_name(self):
        """Get formatted period name"""
        from datetime import datetime
        month_name = datetime(self.year, self.month, 1).strftime('%B')
        return f"{month_name} {self.year} ({self.get_period_type_display()})"
    
    @property
    def days_count(self):
        """Calculate number of days in period"""
        delta = self.end_date - self.start_date
        return delta.days + 1


class WorkSchedule(models.Model):
    """Work Schedule model for managing employee work days per cutoff period"""
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='work_schedules'
    )
    payroll_period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='work_schedules'
    )
    work_days = models.JSONField(
        default=list,
        help_text="List of dates (YYYY-MM-DD) when employee should work"
    )
    rest_days = models.JSONField(
        default=list,
        help_text="List of dates (YYYY-MM-DD) when employee is off"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payroll_period__year', '-payroll_period__month']
        unique_together = ['employee', 'payroll_period']
        indexes = [
            models.Index(fields=['employee', 'payroll_period']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_period.period_name}"
    
    @property
    def total_work_days(self):
        """Count total work days"""
        return len(self.work_days) if self.work_days else 0
    
    @property
    def total_rest_days(self):
        """Count total rest days"""
        return len(self.rest_days) if self.rest_days else 0
