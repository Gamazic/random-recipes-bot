# random-recipes-bot

## ALPHA 1: working mvp app

* **Все команды через `/<command>`, а не через сообщение.**
* **всплывающие подсказки с командами**
* **Подумать, нужны ли условия на валидации. Может быть лучше `try/except`**
* **validate callback function (Выладирует callback по классу (CallbackData) и callback.data)**
* **inline кнопка *использовать* в меню деталей рецепта.**
* inline кнопки *Выбрать случайный*, *Добавить*, *Обнулить все* в меню списка рецептов.

## ALPHA 2: module refactoring

* Все стринги вроде 'delete', 'action' вынести в константы либо еще как то хранить.
* Раскидать все по модулям, сделать красиво
* poetry
* python3.10

## BETA 1: single thread app

* Welcome message
* хостинг
* обработка всевозможных исключений (например, когда кликаешь по уже удаленному рецепту в старом inline keyboard)
* Возможность делиться рецептом
    * Случайным
    * Списком

## REALISE 1:
* Делать некликабельными/удалять неактуальные inline keyboard
* пагинация рецептов
* async mongo
* async fastapi webhook