api.py---
from django.contrib.auth.models import User
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import JSONParser
import pickle

class UserProfileView(APIView):
    authentication_classes = [BasicAuthentication]

    def get(self, request):
        username = request.query_params.get('username')
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM auth_user WHERE username = '{username}'")  # V1: SI
            user_data = cursor.fetchone()

        # V2: In Dis
        if not user_data:
            return Response({"detail": "User not found"}, status=404)

        return Response({"user": user_data})

class UploadFileView(APIView):
# {fact rule=unrestricted-file-upload@v1.0 defects=1}
    parser_classes = [JSONParser]

    def post(self, request):
        # V3: Unres Fi Up
        uploaded_file = request.FILES['file']
# defect
        with open(f"uploads/{uploaded_file.name}", 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        return Response({"detail": "File uploaded successfully"})

# {/fact}
class AdminActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Vu4: Ins Des
        action = pickle.loads(request.data.get('action'))  # Insecure deserialization
        if action.get('delete_user'):
            user_id = action.get('user_id')
            User.objects.filter(id=user_id).delete()

        return Response({"detail": "Action executed"})

class PasswordResetView(APIView):
    def post(self, request):
        # Vul5: Pas Res Token
        email = request.data.get('email')
        reset_token = "this-12-is-a-weak-mechanism-hard-coded"  # Weak password reset mechanism
        # Vu6: Em Enu
        if User.objects.filter(email=email).exists():
            return Response({"token": reset_token})

        return Response({"detail": "Email not found"}, status=404)


frontend.js ---
// A sample vulnerable JavaScript frontend for a consumer application.

function fetchUserData() {
    // Vu7: cro si
    const username = document.getElementById('username').value;
    document.getElementById('output').innerHTML = `User: ${username}`;

    // Vulnerability 8: Insecure API Call (No Validation or Authorization)
    fetch(`/api/user-profile?username=${username}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
        });
}

function uploadFile() {
    // Vu9: Client-Side Validation Only
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please upload a file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/upload-file', {
        method: 'POST',
        body: formData
    }).then(response => {
        console.log('File uploaded');
    });
}

function performAdminAction() {
    // Vu10: CSRF
    const action = { delete_user: true, user_id: 123 };

    fetch('/api/admin-action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(action)
    }).then(response => {
        console.log('Action performed');
    });
}




