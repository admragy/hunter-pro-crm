"""
Hunter Pro CRM Ultimate Enterprise - Internationalization (i18n)
Version: 7.0.0
Multi-language support system
"""

from typing import Dict, Optional
from pathlib import Path
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class I18n:
    """Internationalization manager"""
    
    def __init__(self):
        self.default_language = settings.DEFAULT_LANGUAGE
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translation files"""
        # In production, load from JSON files
        # For now, we'll use embedded translations
        
        self.translations = {
            "ar": {
                # Common
                "welcome": "مرحباً",
                "dashboard": "لوحة التحكم",
                "customers": "العملاء",
                "deals": "الصفقات",
                "campaigns": "الحملات",
                "messages": "الرسائل",
                "analytics": "التحليلات",
                "settings": "الإعدادات",
                "logout": "تسجيل الخروج",
                
                # Actions
                "create": "إنشاء",
                "edit": "تعديل",
                "delete": "حذف",
                "save": "حفظ",
                "cancel": "إلغاء",
                "search": "بحث",
                "filter": "تصفية",
                "export": "تصدير",
                "import": "استيراد",
                
                # Status
                "active": "نشط",
                "inactive": "غير نشط",
                "pending": "قيد الانتظار",
                "completed": "مكتمل",
                "failed": "فشل",
                
                # Messages
                "success": "نجح",
                "error": "خطأ",
                "warning": "تحذير",
                "info": "معلومات",
            },
            
            "en": {
                # Common
                "welcome": "Welcome",
                "dashboard": "Dashboard",
                "customers": "Customers",
                "deals": "Deals",
                "campaigns": "Campaigns",
                "messages": "Messages",
                "analytics": "Analytics",
                "settings": "Settings",
                "logout": "Logout",
                
                # Actions
                "create": "Create",
                "edit": "Edit",
                "delete": "Delete",
                "save": "Save",
                "cancel": "Cancel",
                "search": "Search",
                "filter": "Filter",
                "export": "Export",
                "import": "Import",
                
                # Status
                "active": "Active",
                "inactive": "Inactive",
                "pending": "Pending",
                "completed": "Completed",
                "failed": "Failed",
                
                # Messages
                "success": "Success",
                "error": "Error",
                "warning": "Warning",
                "info": "Information",
            },
        }
        
        logger.info(f"✅ Loaded translations for {len(self.translations)} languages")
    
    def translate(
        self,
        key: str,
        language: Optional[str] = None,
        default: Optional[str] = None
    ) -> str:
        """Translate a key to target language"""
        lang = language or self.default_language
        
        if lang not in self.translations:
            lang = self.default_language
        
        return self.translations.get(lang, {}).get(key, default or key)
    
    def t(self, key: str, lang: Optional[str] = None) -> str:
        """Shorthand for translate"""
        return self.translate(key, lang)
    
    def get_language_name(self, code: str) -> str:
        """Get language name from code"""
        names = {
            "ar": "العربية",
            "en": "English",
            "fr": "Français",
            "de": "Deutsch",
            "es": "Español",
        }
        return names.get(code, code)
    
    def is_rtl(self, language: str) -> bool:
        """Check if language is RTL"""
        rtl_languages = ["ar", "he", "fa", "ur"]
        return language in rtl_languages


# Global i18n instance
i18n = I18n()


# Helper function
def translate(key: str, lang: Optional[str] = None) -> str:
    """Global translate function"""
    return i18n.translate(key, lang)


# Alias
t = translate


if __name__ == "__main__":
    # Test translations
    print("🧪 Testing i18n...")
    
    print(f"Arabic: {t('welcome', 'ar')}")
    print(f"English: {t('welcome', 'en')}")
    print(f"Default: {t('dashboard')}")
    print(f"RTL: {i18n.is_rtl('ar')}")
    
    print("✅ i18n tests completed")
