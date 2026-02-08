from ai.student_data_loader import StudentDataLoader
from api.config import settings

_loader = None

def get_data_loader() -> StudentDataLoader:
    """
    Shared StudentDataLoader instance.
    - MOCK_MODE=True  => JSON ашиглана
    - MOCK_MODE=False => Database ашиглана (чи одоохондоо JSON гэж байсан)
    """
    global _loader
    if _loader is None:
        _loader = StudentDataLoader(use_database=not settings.MOCK_MODE)
    return _loader
