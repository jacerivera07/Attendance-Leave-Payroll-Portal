from rest_framework import serializers
from .models import Employee, Attendance, Leave, Payroll


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email',
            'department', 'position', 'salary', 'join_date', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_email(self, value):
        """Ensure email is unique"""
        instance = self.instance
        if instance and instance.email == value:
            return value
        
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("Employee with this email already exists.")
        return value


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    working_hours = serializers.ReadOnlyField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'date', 'status',
            'clock_in', 'clock_out', 'working_hours', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate attendance data"""
        # Check if attendance already exists for this employee and date
        employee = data.get('employee')
        date = data.get('date')
        
        if employee and date:
            instance = self.instance
            query = Attendance.objects.filter(employee=employee, date=date)
            
            if instance:
                query = query.exclude(pk=instance.pk)
            
            if query.exists():
                raise serializers.ValidationError(
                    "Attendance record already exists for this employee on this date."
                )
        
        # Validate clock times
        clock_in = data.get('clock_in')
        clock_out = data.get('clock_out')
        
        if clock_out and not clock_in:
            raise serializers.ValidationError("Cannot set clock out without clock in time.")
        
        return data


class LeaveSerializer(serializers.ModelSerializer):
    """Serializer for Leave model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = Leave
        fields = [
            'id', 'employee', 'employee_name', 'leave_type',
            'start_date', 'end_date', 'days', 'status', 'reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate leave dates"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("End date must be after start date.")
        
        return data


class PayrollSerializer(serializers.ModelSerializer):
    """Serializer for Payroll model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    gross_salary = serializers.ReadOnlyField()
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'month', 'year',
            'basic_salary', 'allowances', 'overtime', 'deductions',
            'gross_salary', 'net_salary', 'status', 'processed_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['net_salary', 'processed_date', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate payroll data"""
        month = data.get('month')
        year = data.get('year')
        employee = data.get('employee')
        
        if month and (month < 1 or month > 12):
            raise serializers.ValidationError("Month must be between 1 and 12.")
        
        if year and year < 2000:
            raise serializers.ValidationError("Year must be 2000 or later.")
        
        # Check if payroll already exists for this employee, month, and year
        if employee and month and year:
            instance = self.instance
            query = Payroll.objects.filter(employee=employee, month=month, year=year)
            
            if instance:
                query = query.exclude(pk=instance.pk)
            
            if query.exists():
                raise serializers.ValidationError(
                    "Payroll record already exists for this employee in this month/year."
                )
        
        return data


class ClockInOutSerializer(serializers.Serializer):
    """Serializer for clock in/out operations"""
    employee_id = serializers.IntegerField()
    clock_type = serializers.ChoiceField(choices=['in', 'out'])
    
    def validate_employee_id(self, value):
        """Validate employee exists"""
        if not Employee.objects.filter(id=value).exists():
            raise serializers.ValidationError("Employee not found.")
        return value
