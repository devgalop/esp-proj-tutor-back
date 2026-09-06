import secrets
from src.features.user_management.shared.otp_generator import OTPGenerator


class SimpleOTPGenerator(OTPGenerator):

    def generate_otp(self) -> str:
        otp = secrets.token_hex(3)
        return otp.upper()
