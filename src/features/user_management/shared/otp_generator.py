from abc import ABC, abstractmethod


class OTPGenerator(ABC):
    @abstractmethod
    def generate_otp(self) -> str:
        """Generate a one-time password (OTP)."""
        pass
