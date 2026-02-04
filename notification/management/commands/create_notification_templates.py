from django.core.management.base import BaseCommand
from notification.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Create default notification templates for Vanguard app'

    def handle(self, *args, **options):
        templates = [
            # Intel-related notifications
            {
                'name': 'INTEL_COMMENT',
                'notification_type': 'INTEL_COMMENT',
                'title_template': '💬 New Comment on Your Intel',
                'body_template': '{commenter_first_name} commented on your intel report',
                'icon': 'comment_icon',
                'sound': 'default',
                'priority': 'normal'
            },
            {
                'name': 'INTEL_LIKE',
                'notification_type': 'INTEL_LIKE',
                'title_template': '👍 New Like on Your Intel',
                'body_template': '{liker_first_name} liked your intel report',
                'icon': 'like_icon',
                'sound': 'default',
                'priority': 'normal'
            },
            {
                'name': 'INTEL_STATUS_UPDATE',
                'notification_type': 'INTEL_STATUS_UPDATE',
                'title_template': '📋 Intel Status Updated',
                'body_template': 'Your intel report status changed from {old_status} to {new_status}',
                'icon': 'status_icon',
                'sound': 'default',
                'priority': 'normal'
            },
            
            # Exchange-related notifications
            {
                'name': 'EXCHANGE_APPROVED',
                'notification_type': 'EXCHANGE_APPROVED',
                'title_template': '🎉 Exchange Approved!',
                'body_template': 'Congratulations! Your exchange "{org_name}" has been approved and is now live.',
                'icon': 'approval_icon',
                'sound': 'success_sound',
                'priority': 'high'
            },
            {
                'name': 'EXCHANGE_REJECTED',
                'notification_type': 'EXCHANGE_REJECTED',
                'title_template': '❌ Exchange Rejected',
                'body_template': 'Your exchange "{org_name}" has been rejected. Reason: {reason}',
                'icon': 'rejection_icon',
                'sound': 'default',
                'priority': 'high'
            },
            {
                'name': 'EXCHANGE_UNDER_REVIEW',
                'notification_type': 'EXCHANGE_UNDER_REVIEW',
                'title_template': '📝 Exchange Under Review',
                'body_template': 'Your exchange "{org_name}" has been submitted and is under review.',
                'icon': 'review_icon',
                'sound': 'default',
                'priority': 'normal'
            },
            
            # System notifications
            {
                'name': 'SYSTEM_WELCOME',
                'notification_type': 'SYSTEM',
                'title_template': '🎊 Welcome to Vanguard!',
                'body_template': 'Welcome to Vanguard! Start by completing your profile and exploring the community.',
                'icon': 'app_icon',
                'sound': 'default',
                'priority': 'normal'
            },
            {
                'name': 'SYSTEM_UPDATE',
                'notification_type': 'SYSTEM',
                'title_template': '📢 System Update',
                'body_template': 'Important system update: {message}',
                'icon': 'system_icon',
                'sound': 'default',
                'priority': 'normal'
            },
            {
                'name': 'PROFILE_VERIFICATION_APPROVED',
                'notification_type': 'PROFILE_VERIFICATION',
                'title_template': '✅ Profile Verification Approved',
                'body_template': 'Congratulations! Your profile has been verified.',
                'icon': 'verified_icon',
                'sound': 'success_sound',
                'priority': 'high'
            },
            {
                'name': 'PROFILE_VERIFICATION_REJECTED',
                'notification_type': 'PROFILE_VERIFICATION',
                'title_template': '❌ Profile Verification Failed',
                'body_template': 'Your profile verification was unsuccessful. Please review and resubmit.',
                'icon': 'warning_icon',
                'sound': 'default',
                'priority': 'normal'
            },
            {
                'name': 'ROLE_REQUEST_APPROVED',
                'notification_type': 'ROLE_REQUEST_UPDATE',
                'title_template': '🎉 Role Request Approved',
                'body_template': 'Your request to become a {role} has been approved!',
                'icon': 'role_icon',
                'sound': 'success_sound',
                'priority': 'high'
            },
            {
                'name': 'ROLE_REQUEST_REJECTED',
                'notification_type': 'ROLE_REQUEST_UPDATE',
                'title_template': '❌ Role Request Rejected',
                'body_template': 'Your request to become a {role} has been rejected. Reason: {reason}',
                'icon': 'role_icon',
                'sound': 'default',
                'priority': 'normal'
            },
            {
                'name': 'WARNING_NOTIFICATION',
                'notification_type': 'SYSTEM',
                'title_template': '⚠️ Account Warning',
                'body_template': 'Your account has received a warning: {message}',
                'icon': 'warning_icon',
                'sound': 'alert_sound',
                'priority': 'high'
            }
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                # Update existing template
                for key, value in template_data.items():
                    if key != 'name':  # Don't update the name
                        setattr(template, key, value)
                template.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary:\n'
                f'Created: {created_count} templates\n'
                f'Updated: {updated_count} templates\n'
                f'Total: {len(templates)} templates processed'
            )
        )
