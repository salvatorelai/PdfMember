# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.document import Document, Category, Tag  # noqa
from app.models.membership import Membership, RedeemCode, Redemption, Order  # noqa
from app.models.analytics import Download, ReadingHistory  # noqa
from app.models.system import SystemSetting  # noqa
from app.models.token import DownloadToken  # noqa
