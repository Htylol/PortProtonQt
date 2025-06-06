<div align="center">
  <img src="https://raw.githubusercontent.com/Castro-Fidel/PortWINE/master/data_from_portwine/img/gui/portproton.svg" width="64">
  <h1 align="center">PortProtonQt</h1>
  <p align="center">Проект нацеленный на переписывание PortProton(PortWINE) на PySide</p>
</div>

## В планах

- [X] Адаптировать структуру проекта для поддержки инструментов сборки
- [ ] Добавить возможность управление с геймпада
- [ ] Добавить возможность управление с тачскрина
- [X] Добавить возможность управление с мыши и клавиатуры
- [X] Добавить систему тем [Документация](documentation/theme_guide)
- [X] Вынести все константы такие как уровень закругления карточек в темы (Частично вынесено)
- [X] Добавить метадату для тем (скришоты, описание, домащняя страница и автор)
- [ ] Продумать систему вкладок вместо той что есть сейчас
- [ ] Добавить Gamescope сессию на подобие той что есть в SteamOS
- [ ] Написать адаптивный дизайн
- [X] Брать описание и названия игр с базы данных Steam
- [X] Брать обложки для игр со SteamGridDB или CDN Steam
- [X] Оптимизировать работу со SteamApi что бы ускорить время запуска
- [X] Улучшить функцию поиска SteamApi что бы исправить некорректное определение ID (Graven определается как ENGRAVEN или GRAVENFALL, Spore определается как SporeBound или Spore Valley)
- [ ] Убрать логи со SteamApi в релизной версии потому что логи замедляют код
- [X] Что-то придумать с ограничением SteamApi в 50 тысяч игр за один запрос (иногда туда не попадают нужные игры и остаются без обложки)
- [X] Избавится от любого вызова yad
- [X] Написать свою реализацию запрета ухода в сон, а не использовать ту что в PortProton (Оставим это [PortProton 2.0](https://github.com/Castro-Fidel/PortProton_2.0))
- [X] Написать свою реализацию трея, а не использовать ту что в PortProton
- [X] Добавить в поиск экранную клавиатуру (Реализовавывать собственную клавиатуру слишком затратно, лучше положится на встроенную в DE клавиатуру malit в KDE, gjs-osk в GNOME,Squeekboard в phosh, стимовская в SteamOS и так далее)
- [X] Добавить сортировку карточек по различным критериям (сейчас есть: недавние, кол-во наиграного времени, избранное или по алфавиту)
- [X] Добавить индикацию запуска приложения
- [X] Достичь паритета функционала с Ingame (кроме поддержки нативных игр)
- [ ] Достичь паритета функционала с PortProton
- [X] Добавить возможность изменения названия, описания и обложки через файлы .local/share/PortProtonQT/custom_data/exe_name/{desc,name,cover}
- [X] Добавить встроенное переопределение имени, описания и обложки, например по пути portprotonqt/custom_data [Документация](documentation/metadata_override/)
- [X] Добавить в карточку игры сведения о поддержке геймадов
- [X] Добавить в карточки данные с ProtonDB
- [X] Добавить парсинг ярлыков со Steam
- [X] Добавить на карточку бейдж того что игра со стима
- [X] Добавить поддержку Flatpak и Snap версии Steam
- [X] Выводить данные о самом недавнем пользователе Steam, а не первом попавшемся
- [X] Исправить склонения в детальном выводе времени, например не 3 часов назад, а 3 часа назад
- [X] Добавить перевод через gettext [Документация](documentation/localization_guide)
- [X] Писать описание игр и прочие данные на языке системы
- [X] Добавить недокументированные параметры конфигурации в GUI (time detail_level, games sort_method, games display_filter)
- [X] Добавить систему избранного к карточкам
- [X] Заменить все print на logging
- [ ] Привести все логи к одному языку
- [ ] Стилизовать все элементы без стилей(QMessageBox, QSlider, QDialog)
- [X] Убрать жёсткую привязку путей на стрелочки QComboBox в styles.py
- [X] Исправить частичное применение тем на лету
- [X] Исправить наложение подписей скриншотов при первом перелистывание в полноэкранном режиме

### Установка (debug)

```sh
uv python install 3.10
uv sync
source .venv/bin/activate
```

Запуск производится по команде portprotonqt

### Разработка

В проект встроен линтер (ruff), статический анализатор (pyright) и проверка lock файла, если эти проверки не пройдут PR не будет принят, поэтому перед коммитом введите такую команду

```sh
uv python install 3.10
uv sync --all-extras --dev
source .venv/bin/activate
pre-commit install
```

pre-commit сам запустится при коммите, если вы хотите запустить его вручную введите команду

```sh
pre-commit run --all-files
```

## Авторы

* [Boria138](https://github.com/Boria138) - Программист
* [BlackSnaker](https://github.com/BlackSnaker) - Дизайнер - программист
* [Mikhail Tergoev(Castro-Fidel)](https://github.com/Castro-Fidel) - Автор оригинального проекта PortProton

## Помощники (Контрибьюторы)

Спасибо всем, кто помогает в развитии проекта:

<a href="https://github.com/Boria138/PortProtonQt/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Boria138/PortProtonQt" />
</a>


> [!WARNING]
> Проект находится на стадии WIP (work in progress) корректная работоспособность не гарантирована


> [!WARNING]
> **Будьте осторожны!** Если вы берёте тему не из официального репозитория или надёжного источника, убедитесь, что в её файле `styles.py` нет вредоносного или нежелательного кода. Поскольку `styles.py` — это обычный Python-файл, он может содержать любые инструкции. Всегда проверяйте содержимое чужих тем перед использованием.
