from aiogram import Router

from .system.start import router as start_router
from .content.info import router as info_router
from .content.compare import router as compare_router
from .quiz.quiz import router as quiz_router
from .system.stats import router as stats_router
from .system.leaderboard import router as leaderboard_router
from .system.feedback import router as feedback_router
from .system.menu import router as menu_router

router = Router()
router.include_router(start_router)
router.include_router(info_router)
router.include_router(compare_router)
router.include_router(quiz_router)
router.include_router(stats_router)
router.include_router(leaderboard_router)
router.include_router(feedback_router)
router.include_router(menu_router)
