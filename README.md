# random-recipes-bot

## ALPHA 1: working mvp app

* **Все команды через `/<command>`, а не через сообщение.**
* **всплывающие подсказки с командами**
* Подумать, нужны ли условия на валидации. Может быть лучше `try/except`
* validate callback function (Выладиирует callback по классу (CallbackData) и callback.data)
* inline кнопка *использовать* в меню деталей рецепта.
* inline кнопки *Выбрать случайный*, *Добавить* в меню списка рецептов.

## ALPHA 2: module refactoring

* Раскидать все по модулям, сделать красиво
* poetry
* python3.10

## BETA 1: single thread app

* Welcome message
* хостинг
* Возможность делиться рецептом
    * Случайным
    * Списком

## REALISE 1:
* пагинация рецептов
* async mongo
* async fastapi webhook