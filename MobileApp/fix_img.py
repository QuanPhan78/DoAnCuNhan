import os

def fix_image_widget(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace CustomImageWidget usage
    old_call_detail = """              child: CustomImageWidget(
                imageUrl: promotion.imageUrl,
                localAsset: promotion.imageAsset ?? 'assets/images/placeholder.png',
              ),"""
    new_call_detail = """              child: CustomImageWidget(
                imageUrl: promotion.imageUrl ?? promotion.imageAsset ?? '',
              ),"""
    content = content.replace(old_call_detail, new_call_detail)
    
    old_call_list = """                                    child: CustomImageWidget(
                                      imageUrl: promo.imageUrl,
                                      localAsset: promo.imageAsset ?? 'assets/images/placeholder.png',
                                    ),"""
    new_call_list = """                                    child: CustomImageWidget(
                                      imageUrl: promo.imageUrl ?? promo.imageAsset ?? '',
                                    ),"""
    content = content.replace(old_call_list, new_call_list)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

fix_image_widget("lib/screens/promotions/promotion_detail_screen.dart")
fix_image_widget("lib/screens/promotions/promotion_list_screen.dart")
print("Fixed CustomImageWidget usage")