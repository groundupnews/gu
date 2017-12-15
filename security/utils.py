from django.contrib.auth.password_validation import MinimumLengthValidator


class StaffMinimumLengthValidator(MinimumLengthValidator):

        def __init__(self, staff_min_length=14,
                     other_min_length=9):
            self.staff_min_length = staff_min_length
            self.other_min_length = other_min_length

        def validate(self, password, user=None):
            if user and user.is_staff is True:
                self.min_length = self.staff_min_length
            else:
                self.min_length = self.other_min_length
            super().validate(password, user)
