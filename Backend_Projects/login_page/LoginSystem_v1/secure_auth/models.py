from django.db import models

class UserAccount(models.Model):
    # 1. Core Profile Details (Collected on page 1)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    
    # 2. Temporary Security Code Field
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    
    # 3. Permanent Security Password Field (Blank at first, hashed and saved at the very end)
    password_hash = models.CharField(max_length=255, blank=True, null=True)
    
    # 4. Operational Flow State Trackers (Both default to False)
    email_verified = models.BooleanField(default=False)
    active_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} \n{self.last_name} \n{self.email} \nVerified: {self.email_verified} \nActive: {self.active_status} \n"