from app.crud.base import CRUDBase
from app.models.analytics import Download
from app.schemas.analytics import DownloadCreate, DownloadUpdate

class CRUDDownload(CRUDBase[Download, DownloadCreate, DownloadUpdate]):
    pass

download = CRUDDownload(Download)
