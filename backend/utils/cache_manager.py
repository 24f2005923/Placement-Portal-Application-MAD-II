from cache import cache

class CacheManager:
    """Centralized cache invalidation logic to decouple routes from cache rules."""

    @staticmethod
    def invalidate_admin_stats():
        cache.delete('admin:stats')
        cache.delete('admin:activities')

    @staticmethod
    def invalidate_admin_report_stats():
        cache.delete('admin:report_stats')

    @staticmethod
    def invalidate_application(app_id=None):
        """Invalidate caches related to applications."""
        if app_id:
            pass # No specific app cache yet, but pattern applies
        cache.delete_pattern('admin:applications:*')
        cache.delete_pattern('company:applications:*')

    @staticmethod
    def invalidate_student_drive_lists():
        """Invalidate all cached student placement-drive list/search results."""
        cache.delete_pattern('student:drives:*')

    @staticmethod
    def invalidate_application_student(app_id):
        """Invalidate the student-facing caches for the owner of an application."""
        if not app_id:
            return
        from models import db
        from models.application import Application

        app_record = db.session.query(Application).filter(Application.id == app_id).first()
        if app_record and app_record.student:
            CacheManager.invalidate_student(
                student_id=app_record.student.id,
                user_id=app_record.student.user_id,
            )

    @staticmethod
    def invalidate_student(student_id, user_id=None):
        """Invalidate caches related to a student."""
        cache.delete_pattern('admin:students:*')
        cache.delete(f'admin:student:{student_id}')
        if user_id:
            cache.delete(f'student:profile:{user_id}')
            cache.delete(f'student:stats:{user_id}')
            cache.delete_pattern(f'student:drives:{user_id}:*')

    @staticmethod
    def invalidate_company(company_id, user_id=None):
        """Invalidate caches related to a company."""
        cache.delete_pattern('admin:companies:*')
        cache.delete(f'admin:company:{company_id}')
        if user_id:
            cache.delete(f'company:profile:{user_id}')
            cache.delete(f'company:stats:{user_id}')
            cache.delete(f'company:drives:{user_id}')

    @staticmethod
    def invalidate_drive(drive_id, company_user_id=None):
        """Invalidate caches related to a placement drive."""
        cache.delete_pattern('admin:drives:*')
        cache.delete(f'admin:drive:{drive_id}')
        cache.delete_pattern('company:drives:*')
        CacheManager.invalidate_student_drive_lists()
        if company_user_id:
            cache.delete(f'company:drives:{company_user_id}')
            cache.delete(f'company:stats:{company_user_id}')
