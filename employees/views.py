from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, date, timedelta
from .models import Employee, Attendance, Leave, Payroll
from .serializers import (
    EmployeeSerializer, AttendanceSerializer,
    LeaveSerializer, PayrollSerializer, ClockInOutSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Employee CRUD operations
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    
    def get_queryset(self):
        """Filter employees by department or search query"""
        queryset = Employee.objects.all()
        
        # Filter by department
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department=department)
        
        # Search by name or email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get employee statistics"""
        total = Employee.objects.count()
        active = Employee.objects.filter(status='Active').count()
        pending = Employee.objects.filter(status='Pending').count()
        by_department = Employee.objects.values('department').annotate(
            count=Count('id')
        )
        
        return Response({
            'total': total,
            'active': active,
            'pending': pending,
            'by_department': list(by_department)
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending employees awaiting admin setup"""
        pending_employees = Employee.objects.filter(status='Pending')
        serializer = self.get_serializer(pending_employees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def activate(self, request, pk=None):
        """Activate an employee after admin completes setup"""
        employee = self.get_object()
        employee.status = 'Active'
        employee.save()
        return Response(
            EmployeeSerializer(employee).data,
            status=status.HTTP_200_OK
        )


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Attendance CRUD operations
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    
    def get_queryset(self):
        """Filter attendance by date or employee"""
        queryset = Attendance.objects.select_related('employee').all()
        
        # Filter by date
        date_param = self.request.query_params.get('date', None)
        if date_param:
            queryset = queryset.filter(date=date_param)
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee', None)
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def clock(self, request):
        """Handle clock in/out operations"""
        serializer = ClockInOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        employee_id = serializer.validated_data['employee_id']
        clock_type = serializer.validated_data['clock_type']
        
        employee = Employee.objects.get(id=employee_id)
        today = date.today()
        now = timezone.now().time()
        
        # Get or create attendance record for today
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'status': 'Present',
                'clock_in': now if clock_type == 'in' else None
            }
        )
        
        if clock_type == 'in':
            if not created and attendance.clock_in:
                return Response(
                    {'error': 'Already clocked in today'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            attendance.clock_in = now
            # Determine if late (after 9 AM)
            if now.hour >= 9:
                attendance.status = 'Late'
            else:
                attendance.status = 'Present'
        else:  # clock out
            if not attendance.clock_in:
                return Response(
                    {'error': 'Must clock in first'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            attendance.clock_out = now
        
        attendance.save()
        
        return Response(
            AttendanceSerializer(attendance).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's attendance"""
        today = date.today()
        attendance = Attendance.objects.filter(date=today).select_related('employee')
        serializer = self.get_serializer(attendance, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get attendance statistics"""
        today = date.today()
        today_attendance = Attendance.objects.filter(date=today)
        
        total_employees = Employee.objects.filter(status='Active').count()
        present = today_attendance.filter(
            Q(status='Present') | Q(status='Late')
        ).count()
        absent = total_employees - present
        on_leave = today_attendance.filter(status='On Leave').count()
        
        return Response({
            'date': today,
            'total_employees': total_employees,
            'present': present,
            'absent': absent,
            'on_leave': on_leave,
            'attendance_rate': round((present / total_employees * 100) if total_employees > 0 else 0, 2)
        })


class LeaveViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Leave CRUD operations
    """
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    
    def get_queryset(self):
        """Filter leaves by status or employee"""
        queryset = Leave.objects.select_related('employee').all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee', None)
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Approve a leave request"""
        leave = self.get_object()
        leave.status = 'Approved'
        leave.save()
        return Response(
            LeaveSerializer(leave).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """Reject a leave request"""
        leave = self.get_object()
        leave.status = 'Rejected'
        leave.save()
        return Response(
            LeaveSerializer(leave).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending leave requests"""
        pending_leaves = Leave.objects.filter(status='Pending').select_related('employee')
        serializer = self.get_serializer(pending_leaves, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get leave statistics"""
        total = Leave.objects.count()
        approved = Leave.objects.filter(status='Approved').count()
        pending = Leave.objects.filter(status='Pending').count()
        rejected = Leave.objects.filter(status='Rejected').count()
        
        return Response({
            'total': total,
            'approved': approved,
            'pending': pending,
            'rejected': rejected
        })


class PayrollViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payroll CRUD operations
    """
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    
    def get_queryset(self):
        """Filter payroll by month/year or employee"""
        queryset = Payroll.objects.select_related('employee').all()
        
        # Filter by month and year
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        if month and year:
            queryset = queryset.filter(month=month, year=year)
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee', None)
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def process(self, request):
        """Process payroll for a specific month/year"""
        month = request.data.get('month')
        year = request.data.get('year')
        
        if not month or not year:
            return Response(
                {'error': 'Month and year are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        employees = Employee.objects.filter(status='Active')
        payroll_records = []
        
        for employee in employees:
            # Check if payroll already exists
            existing = Payroll.objects.filter(
                employee=employee,
                month=month,
                year=year
            ).first()
            
            if existing:
                continue
            
            # Calculate attendance for the month
            start_date = date(int(year), int(month), 1)
            if int(month) == 12:
                end_date = date(int(year) + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(int(year), int(month) + 1, 1) - timedelta(days=1)
            
            attendance_records = Attendance.objects.filter(
                employee=employee,
                date__range=[start_date, end_date]
            )
            
            # Calculate working days (assuming 22 working days per month)
            working_days = 22
            present_days = attendance_records.filter(
                Q(status='Present') | Q(status='Late')
            ).count()
            
            # Calculate deductions for absent days
            daily_rate = float(employee.salary) / working_days
            absent_days = working_days - present_days
            deductions = daily_rate * absent_days
            
            # Calculate overtime
            overtime_hours = 0
            for record in attendance_records:
                if record.working_hours > 8:
                    overtime_hours += (record.working_hours - 8)
            
            overtime_pay = overtime_hours * 25  # $25 per hour
            
            # Calculate allowances (10% of basic salary)
            allowances = float(employee.salary) * 0.1
            
            # Create payroll record
            payroll = Payroll.objects.create(
                employee=employee,
                month=month,
                year=year,
                basic_salary=employee.salary,
                allowances=allowances,
                overtime=overtime_pay,
                deductions=deductions,
                status='Processed'
            )
            payroll_records.append(payroll)
        
        serializer = self.get_serializer(payroll_records, many=True)
        return Response(
            {
                'message': f'Processed payroll for {len(payroll_records)} employees',
                'payroll': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def payslip(self, request, pk=None):
        """Generate payslip data for a specific payroll record"""
        payroll = self.get_object()
        
        payslip_data = {
            'employee': {
                'name': payroll.employee.full_name,
                'email': payroll.employee.email,
                'department': payroll.employee.department,
                'position': payroll.employee.position,
                'employee_id': f"EMP-{str(payroll.employee.id).zfill(4)}"
            },
            'period': {
                'month': payroll.month,
                'year': payroll.year,
                'pay_date': payroll.processed_date or timezone.now()
            },
            'earnings': {
                'basic_salary': float(payroll.basic_salary),
                'allowances': float(payroll.allowances),
                'overtime': float(payroll.overtime),
                'gross_salary': float(payroll.gross_salary)
            },
            'deductions': {
                'total': float(payroll.deductions)
            },
            'net_salary': float(payroll.net_salary)
        }
        
        return Response(payslip_data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get payroll statistics"""
        month = request.query_params.get('month', date.today().month)
        year = request.query_params.get('year', date.today().year)
        
        monthly_payroll = Payroll.objects.filter(month=month, year=year)
        total_payroll = monthly_payroll.aggregate(
            total=Sum('net_salary')
        )['total'] or 0
        
        return Response({
            'month': month,
            'year': year,
            'total_payroll': float(total_payroll),
            'processed_count': monthly_payroll.filter(status='Processed').count(),
            'pending_count': monthly_payroll.filter(status='Pending').count()
        })
