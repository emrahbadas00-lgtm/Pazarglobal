# tools/clean_price.py

import re
from typing import Optional, Dict


def clean_price(price_text: Optional[str]) -> Dict[str, Optional[int]]:
    """
    JS versiyonu ile aynı mantık:
    - Boşsa null döndür
    - Rakam ve virgül dışındakileri sil
    - Virgülü kaldır
    - int'e parse et, NaN ise null
    
    Args:
        price_text: Temizlenecek fiyat metni (örn: "1,250 TL")
        
    Returns:
        Dict içinde clean_price anahtarı ile temizlenmiş fiyat (int veya None)
        Örnek: {"clean_price": 1250} veya {"clean_price": None}
    """
    if not price_text:
        return {"clean_price": None}

    # JS: price_text.replace(/[^\d,]/g, "").replace(",", "")
    # Sadece rakam ve virgül bırak
    cleaned = re.sub(r"[^\d,]", "", price_text)
    # Virgülü kaldır
    cleaned = cleaned.replace(",", "")

    # Boş string kaldıysa None döndür
    if not cleaned:
        return {"clean_price": None}

    try:
        number = int(cleaned, 10)
    except ValueError:
        number = None

    return {"clean_price": number}
