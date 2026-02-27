from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import gettext
import os

class I18nMiddleware(BaseMiddleware):
    def __init__(self, domain='messages', localedir='locales'):
        self.domain = domain
        self.localedir = localedir
        self.translations = {}
        self.default_language = 'en'
        # Загружаем все доступные языки
        for lang in os.listdir(localedir):
            if os.path.isdir(os.path.join(localedir, lang)):
                try:
                    translation = gettext.translation(domain, localedir, languages=[lang])
                    self.translations[lang] = translation
                except FileNotFoundError:
                    pass

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Определяем язык пользователя
        user_lang = event.from_user.language_code
        if user_lang not in self.translations:
            user_lang = self.default_language
        
        # Получаем функцию перевода
        translation = self.translations.get(user_lang, self.translations[self.default_language])
        gettext_func = translation.gettext
        
        # Сохраняем в data для использования в хендлерах
        data['_'] = gettext_func
        data['lang'] = user_lang
        
        return await handler(event, data)
