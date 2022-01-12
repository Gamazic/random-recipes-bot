# random-recipes-bot
Preview:
![Preview](tg_app_screenshots/random-recipes-bot-alpha-v0.1.jpg)

# requirements
* `.env` file
* `poetry`


# Roadmap

## ALPHA 1: working mvp app
- [X] Все команды через `/<command>`, а не через сообщение.
- [X] всплывающие подсказки с командами
- [X] Подумать, нужны ли условия на валидации. Может быть лучше `try/except`
- [X] validate callback function (Выладирует callback по классу (CallbackData) и callback.data)
- [X] inline кнопка *использовать* в меню деталей рецепта.
- [X] inline кнопки *Выбрать случайный*, *Добавить*, *Обнулить все* в меню списка рецептов.

## ALPHA 2: module refactoring
- [X] Все стринги вроде 'delete', 'action' вынести в константы либо еще как то хранить.
- [X] Раскидать все по модулям, сделать красиво
- [X] poetry
- [ ] Documentation

## BETA 1: single thread app
- [ ] Делать некликабельными/удалять неактуальные inline keyboard
- [ ] обработка всевозможных исключений (например, когда кликаешь по уже удаленному рецепту в старом inline keyboard)
- [ ] Переработать логику бота. Убрать лишние возможности, дублирующие возможности.

## BETA 2: async app
- [ ] async mongo
- [ ] async fastapi webhook

## REALISE 1:
- [ ] Welcome message
- [ ] хостинг
- [ ] пагинация рецептов
- [ ] final refactoring

# FEATURES:
- [ ] Возможность делиться рецептом
    - [ ] Случайным
    - [ ] Списком