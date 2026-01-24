from aiogram import Router

from .start import router as start_router
from .info import router as info_router
from .quiz import router as quiz_router
from .stats import router as stats_router
from .feedback import router as feedback_router

router = Router()
router.include_router(start_router)
router.include_router(info_router)
router.include_router(quiz_router)
router.include_router(stats_router)
router.include_router(feedback_router)
