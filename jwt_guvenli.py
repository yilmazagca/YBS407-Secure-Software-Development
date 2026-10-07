# Gerekli: pip install PyJWT python-dotenv
import jwt
import datetime
import os
import logging
from functools import wraps
from typing import Tuple, Optional

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Güvenli SECRET_KEY'i environment variable'dan oku
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("⚠️ Hata: JWT_SECRET_KEY tanımlanmadı veya çok kısa (minimum 32 karakter)")

# Token siyah listesi (logout işlemi için)
BLACKLISTED_TOKENS = set()

def create_jwt(user_id: str, hours: int = 1) -> str:
    """
    Kullanıcı için imzalı JWT oluşturur.
    
    Args:
        user_id: Kullanıcı ID'si
        hours: Token geçerlilik süresi (saat)
    
    Returns:
        JWT token
    
    Raises:
        ValueError: user_id geçerli değilse
    """
    if not user_id or not isinstance(user_id, str) or len(user_id) > 255:
        raise ValueError("user_id boş, string olmalı veya 255 karakterden kısa olmalı")
    
    try:
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours),
            "iat": datetime.datetime.now(datetime.timezone.utc),  # Token oluşturulma zamanı
            "jti": os.urandom(16).hex()  # Unique token ID (token iptal için)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        logger.info(f"Token oluşturuldu: user_id={user_id}")
        return token
    except Exception as e:
        logger.error(f"Token oluşturma hatası: {str(e)}")
        raise


def verify_jwt(token: str) -> Tuple[bool, Optional[str]]:
    """
    JWT token'ı doğrular.
    
    Args:
        token: Doğrulanacak JWT token
    
    Returns:
        Tuple: (başarılı mı, user_id veya None)
    """
    if not token or not isinstance(token, str):
        logger.warning("Geçersiz token formatı")
        return False, None
    
    # Token siyah listede mi kontrol et
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("jti") in BLACKLISTED_TOKENS:
            logger.warning("Logout edilmiş token kullanıldı")
            return False, None
        
        user_id = payload.get("user_id")
        logger.info(f"Token doğrulama başarılı: user_id={user_id}")
        return True, user_id
    
    except jwt.ExpiredSignatureError:
        logger.warning("Token süresi dolmuş")
        return False, None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Geçersiz token: {str(e)}")
        return False, None
    except Exception as e:
        logger.error(f"Token doğrulama hatası: {str(e)}")
        return False, None


def logout_token(token: str) -> bool:
    """Token'ı iptal eder (logout işlemi)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        jti = payload.get("jti")
        if jti:
            BLACKLISTED_TOKENS.add(jti)
            logger.info(f"Token logout edildi")
            return True
    except Exception as e:
        logger.warning(f"Logout hatası: {str(e)}")
    return False


def main():
    """JWT oluşturma ve doğrulama örneği."""
    print("=" * 50)
    print("🔐 Güvenli JWT Uygulaması")
    print("=" * 50)
    
    # 1. Token Oluştur
    test_user_id = "user_12345"
    print(f"\n[1] Giriş - Kullanıcı ID: {test_user_id}")
    
    try:
        token = create_jwt(test_user_id)
        print(f"[✓] Token oluşturuldu:\n{token}\n")
    except ValueError as e:
        print(f"[✗] Hata: {e}")
        return
    
    # 2. Token'ı Doğrula
    print("[2] Token doğrulama...")
    success, user_id = verify_jwt(token)
    
    if success:
        print(f"[✓] Token geçerli! Kullanıcı ID: {user_id}")
    else:
        print("[✗] Token geçersiz veya süresi dolmuş!")
        return
    
    # 3. Logout (Token İptali)
    print("\n[3] Çıkış yapılıyor (logout)...")
    logout_token(token)
    print("[✓] Token iptal edildi")
    
    # 4. İptal Edilmiş Token'ı Tekrar Denemek
    print("\n[4] İptal edilmiş token ile kontrol...")
    success, user_id = verify_jwt(token)
    
    if success:
        print("[✗] GÜVENLIK SORUNU: İptal edilmiş token kabul edildi!")
    else:
        print("[✓] İptal edilmiş token doğru şekilde reddedildi")


if __name__ == "__main__":
    main()
