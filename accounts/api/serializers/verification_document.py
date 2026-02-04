from rest_framework import serializers
from accounts.models.verification_document import VerificationDocument


class VerificationDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for VerificationDocument model.
    """
    reviewed_by_email = serializers.EmailField(source='reviewed_by.email', read_only=True, allow_null=True)
    
    class Meta:
        model = VerificationDocument
        fields = [
            'uuid', 
            'document_url', 
            'document_type', 
            'status',
            'rejection_reason',
            'reviewed_by_email',
            'reviewed_at',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'reviewed_by_email', 'reviewed_at']


class VerificationDocumentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating verification documents.
    Accepts either a document URL (string) or document data.
    """
    document_url = serializers.URLField(required=False, allow_blank=True)
    document_type = serializers.CharField(required=False, allow_blank=True, max_length=100)
    
    def validate(self, attrs):
        """
        Validate that at least document_url is provided.
        """
        if not attrs.get('document_url'):
            raise serializers.ValidationError({
                'document_url': 'Document URL is required.'
            })
        return attrs


class VerificationDocumentApproveSerializer(serializers.Serializer):
    """
    Serializer for approving verification documents.
    No additional fields required.
    """
    pass  # No additional fields required for approval


class VerificationDocumentRejectSerializer(serializers.Serializer):
    """
    Serializer for rejecting verification documents.
    """
    rejection_reason = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="Reason for rejecting the document"
    )
