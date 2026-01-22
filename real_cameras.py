"""
Camera Spoofer - Listas de Câmeras
Contém padrões para detectar câmeras virtuais e nomes de câmeras reais para substituição.
"""

# Padrões para identificar câmeras virtuais (case-insensitive)
VIRTUAL_CAMERA_PATTERNS = [
    # OBS Studio
    "obs virtual camera",
    "obs-camera",
    "obs virtual",
    
    # NDI (NewTek Network Device Interface)
    "newtek ndi video",
    "ndi virtual input",
    "ndi webcam input",
    "ndi video",
    
    # vMix
    "vmix video",
    "vmix video virtual webcam",
    "vmix virtual",
    
    # ManyCam
    "manycam virtual webcam",
    "manycam",
    
    # XSplit
    "xsplit vcam",
    "xsplit broadcaster",
    
    # Snap Camera
    "snap camera",
    "snapcamera",
    
    # SplitCam
    "splitcam video driver",
    "splitcam",
    
    # CyberLink YouCam
    "cyberlink youcam",
    "youcam",
    
    # Prism Live Studio
    "prism live studio",
    "prism live",
    
    # e2eSoft VCam
    "e2esoft vcam",
    "e2esoft ivcam",
    "vcam",
    
    # EpocCam
    "epoccam camera",
    "epoccam",
    
    # AlterCam
    "altercam virtual webcam",
    "altercam",
    
    # DroidCam
    "droidcam source",
    "droidcam",
    
    # iVCam
    "ivcam",
    
    # CamTwist
    "camtwist",
    
    # Outros
    "virtual camera",
    "virtual webcam",
    "fake camera",
    "screen capture",
    "capture card",
]

# Nomes de câmeras reais para substituição (apenas as mais populares)
REAL_CAMERA_NAMES = {
    "Logitech": [
        "Logitech HD Webcam C920",
        "Logitech HD Pro Webcam C922",
        "Logitech BRIO 4K Ultra HD Webcam",
        "Logitech StreamCam",
    ],
    "Microsoft": [
        "Microsoft LifeCam HD-3000",
        "Microsoft LifeCam Studio",
        "Microsoft Modern Webcam",
    ],
    "Dell": [
        "Dell UltraSharp Webcam",
        "Dell Pro Webcam WB5023",
    ],
    "HP": [
        "HP TrueVision HD Camera",
        "HP 960 4K Streaming Webcam",
    ],
    "Lenovo": [
        "Lenovo Integrated Camera",
        "Lenovo 500 FHD Webcam",
    ],
    "Outras": [
        "Razer Kiyo",
        "Elgato Facecam",
        "OBSBOT Tiny 2",
        "Insta360 Link",
        "ASUS ROG Eye",
    ],
}

def get_all_real_camera_names() -> list:
    """Retorna lista plana com todos os nomes de câmeras reais."""
    all_names = []
    for brand_names in REAL_CAMERA_NAMES.values():
        all_names.extend(brand_names)
    return all_names

def get_real_cameras_by_brand() -> dict:
    """Retorna dicionário de câmeras reais organizadas por marca."""
    return REAL_CAMERA_NAMES.copy()

def is_virtual_camera(camera_name: str) -> bool:
    """
    Verifica se o nome da câmera corresponde a uma câmera virtual conhecida.
    
    Args:
        camera_name: Nome da câmera para verificar
        
    Returns:
        True se for uma câmera virtual, False caso contrário
    """
    if not camera_name:
        return False
    
    camera_lower = camera_name.lower()
    
    for pattern in VIRTUAL_CAMERA_PATTERNS:
        if pattern in camera_lower:
            return True
    
    return False

def get_suggested_name(original_name: str = None) -> str:
    """
    Retorna um nome de câmera real sugerido.
    Por padrão, sugere Logitech C920 por ser a mais comum.
    
    Args:
        original_name: Nome original da câmera (não usado atualmente)
        
    Returns:
        Nome sugerido de câmera real
    """
    # Logitech C920 é a webcam mais popular do mundo
    return "Logitech HD Webcam C920"
