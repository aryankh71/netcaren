# shop/utils.py
from .models import InventoryItem

def generate_barcodes(product, quantity):
    first_letter = product.name[0].upper() if product.name else 'P'
    brand = product.brand.upper() if product.brand else 'UNKNOWN'
    prefix = f"{first_letter}-{brand}-"

    # پیدا کردن آخرین شماره برای این پیشوند (برای جلوگیری از تکرار)
    last_item = InventoryItem.objects.filter(barcode__startswith=prefix).order_by('-barcode').first()
    last_number = 0
    if last_item:
        last_number = int(last_item.barcode.split('-')[-1])

    barcodes = []
    for i in range(1, quantity + 1):
        new_number = last_number + i
        barcode = prefix + f"{new_number:06d}"
        barcodes.append(barcode)

    return barcodes