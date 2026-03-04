from ai.student_data_loader import StudentDataLoader
from api.config import settings

_loader = None

def get_data_loader() -> StudentDataLoader:
    """
    Shared StudentDataLoader instance.
    - USE_DATABASE overrides data source when set
    - Otherwise MOCK_MODE=True uses JSON
    """
    global _loader
    if _loader is None:
        _loader = StudentDataLoader(
            data_file=settings.STUDENTS_FILE,
            use_database=settings.USE_DATABASE,
        )
    return _loader
