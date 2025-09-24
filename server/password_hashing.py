# password_hashing.py


# type: ignore
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import logging


# Create a logger for this module
logger = logging.getLogger(__name__)

# Set up the password hasher with security settings
# This creates a tool that will turn passwords into scrambled text
password_hasher = PasswordHasher(
    time_cost=3, # How many times to repeat the scrambling (more = safer but slower)
    memory_cost=65536, # How much computer memory to use (64MB - more = safer but slower)
    parallelism=4, # How many computer cores to use at the same time
    hash_len=32, # How long the scrambled password should be (32 characters)
    salt_len=16 # How long the random salt (= unique identifier) should be (16 characters)
)

def hash_password(password):
    """
    Turn a plain text password into a scrambled version that can be safely stored
    """
    try:
        # Use the hasher to turn the plain password into scrambled text
        hashed = password_hasher.hash(password)
        logger.debug("Password hashed successfully")
        # Return the scrambled password
        return hashed
    except Exception as e:
        logger.error(f"Failed to hash password | error={str(e)}")
        # Stop the program and show the error
        raise


def verify_password(password, hashed_password):
    """
    Check if a plain text password matches a scrambled password from the database
    """
    try:
        # Check if the plain password matches the scrambled password
        password_hasher.verify(hashed_password, password)
        logger.debug("Password verification successful")
        # Passwords match
        return True
    # Passwords don't match
    except VerifyMismatchError:
        logger.debug("Password verification failed - password mismatch")
        return False
    # Something else went wrong
    except Exception as e:
        logger.error(f"Password verification failed with error | error={str(e)}")
        return False