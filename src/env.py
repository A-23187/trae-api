import os

from dotenv import load_dotenv

load_dotenv()

TRAE_APP_ID = str(os.getenv("TRAE_APP_ID"))
TRAE_DEVICE_BRAND = str(os.getenv("TRAE_DEVICE_BRAND"))
TRAE_DEVICE_CPU = str(os.getenv("TRAE_DEVICE_CPU"))
TRAE_DEVICE_ID = str(os.getenv("TRAE_DEVICE_ID"))
TRAE_DEVICE_TYPE = str(os.getenv("TRAE_DEVICE_TYPE"))
TRAE_IDE_TOKEN = str(os.getenv("TRAE_IDE_TOKEN"))
TRAE_IDE_VERSION = str(os.getenv("TRAE_IDE_VERSION"))
TRAE_IDE_VERSION_CODE = str(os.getenv("TRAE_IDE_VERSION_CODE"))
TRAE_IDE_VERSION_TYPE = str(os.getenv("TRAE_IDE_VERSION_TYPE"))
TRAE_MACHINE_ID = str(os.getenv("TRAE_MACHINE_ID"))
TRAE_OS_VERSION = str(os.getenv("TRAE_OS_VERSION"))
