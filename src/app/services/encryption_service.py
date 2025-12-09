"""
Encryption Service for Character Data

Handles encryption and decryption of sensitive character data using Fernet symmetric encryption.
"""

from cryptography.fernet import Fernet
import os
import base64
from typing import Optional


class EncryptionService:
    """Service for encrypting and decrypting sensitive character data"""
    
    def __init__(self):
        """Initialize encryption service with key from environment"""
        encryption_key = os.getenv("CHARACTER_ENCRYPTION_KEY")
        
        if not encryption_key:
            # Generate a new key if not set (for development)
            print("⚠️  WARNING: CHARACTER_ENCRYPTION_KEY not set in environment!")
            print("⚠️  Generating temporary key for this session...")
            encryption_key = Fernet.generate_key().decode()
            print(f"⚠️  Add this to your .env file: CHARACTER_ENCRYPTION_KEY={encryption_key}")
        
        self.cipher = Fernet(encryption_key.encode())
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string
        
        Args:
            data: Plain text string to encrypt
            
        Returns:
            str: Encrypted string (base64 encoded)
        """
        if not data:
            return ""
        
        try:
            encrypted_bytes = self.cipher.encrypt(data.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            print(f"❌ Encryption error: {str(e)}")
            raise ValueError(f"Failed to encrypt data: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt an encrypted string
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
            
        Returns:
            str: Decrypted plain text string
        """
        if not encrypted_data:
            return ""
        
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            print(f"❌ Decryption error: {str(e)}")
            raise ValueError(f"Failed to decrypt data: {str(e)}")
    
    def encrypt_dict(self, data: dict, keys_to_encrypt: list) -> dict:
        """
        Encrypt specific keys in a dictionary
        
        Args:
            data: Dictionary containing data
            keys_to_encrypt: List of keys to encrypt
            
        Returns:
            dict: Dictionary with specified keys encrypted
        """
        encrypted_data = data.copy()
        
        for key in keys_to_encrypt:
            if key in encrypted_data and encrypted_data[key]:
                encrypted_data[key] = self.encrypt(str(encrypted_data[key]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, keys_to_decrypt: list) -> dict:
        """
        Decrypt specific keys in a dictionary
        
        Args:
            data: Dictionary containing encrypted data
            keys_to_decrypt: List of keys to decrypt
            
        Returns:
            dict: Dictionary with specified keys decrypted
        """
        decrypted_data = data.copy()
        
        for key in keys_to_decrypt:
            if key in decrypted_data and decrypted_data[key]:
                try:
                    decrypted_data[key] = self.decrypt(decrypted_data[key])
                except Exception as e:
                    print(f"⚠️  Warning: Could not decrypt key '{key}': {str(e)}")
                    # Keep original value if decryption fails
        
        return decrypted_data


# Global instance
encryption_service = EncryptionService()


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key
    
    Returns:
        str: Base64 encoded encryption key
    """
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    # Test encryption service
    print("🔐 Testing Encryption Service...")
    
    # Generate a test key
    test_key = generate_encryption_key()
    print(f"\n📝 Generated Key: {test_key}")
    print("💡 Add this to your .env file as CHARACTER_ENCRYPTION_KEY")
    
    # Test encryption/decryption
    service = EncryptionService()
    
    test_data = "character_12345"
    encrypted = service.encrypt(test_data)
    decrypted = service.decrypt(encrypted)
    
    print(f"\n✅ Original: {test_data}")
    print(f"🔒 Encrypted: {encrypted}")
    print(f"🔓 Decrypted: {decrypted}")
    print(f"✅ Match: {test_data == decrypted}")
