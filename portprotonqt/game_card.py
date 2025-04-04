from PySide6 import QtCore, QtGui, QtWidgets
import portprotonqt.themes.standart.styles as default_styles
from portprotonqt.image_utils import load_pixmap, round_corners
from portprotonqt.localization import _
from portprotonqt.config_utils import read_favorites, save_favorites
from portprotonqt.theme_manager import ThemeManager
from portprotonqt.config_utils import read_theme_from_config

class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.Signal()

    def __init__(self, *args, icon=None, icon_size=16, icon_space=5, **kwargs):
        """
        Поддерживаются вызовы:
          - ClickableLabel("текст", parent=...) – первый аргумент строка,
          - ClickableLabel(parent, text="...") – если первым аргументом передается родитель.

        Аргументы:
          icon: QIcon или None – иконка, которая будет отрисована вместе с текстом.
          icon_size: int – размер иконки (ширина и высота).
          icon_space: int – отступ между иконкой и текстом.
        """
        if args and isinstance(args[0], str):
            text = args[0]
            parent = kwargs.get("parent", None)
            super().__init__(text, parent)
        elif args and isinstance(args[0], QtWidgets.QWidget):
            parent = args[0]
            text = kwargs.get("text", "")
            super().__init__(parent)
            self.setText(text)
        else:
            text = ""
            parent = kwargs.get("parent", None)
            super().__init__(text, parent)

        self._icon = icon
        self._icon_size = icon_size
        self._icon_space = icon_space
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def setIcon(self, icon):
        """Устанавливает иконку и перерисовывает виджет."""
        self._icon = icon
        self.update()

    def icon(self):
        """Возвращает текущую иконку."""
        return self._icon

    def paintEvent(self, event):
        """Переопределяем отрисовку: рисуем иконку и текст в одном лейбле."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        rect = self.contentsRect()
        alignment = self.alignment()

        icon_size = self._icon_size
        spacing = self._icon_space

        icon_rect = QtCore.QRect()
        text_rect = QtCore.QRect()
        text = self.text()

        if self._icon:
            # Получаем QPixmap нужного размера
            pixmap = self._icon.pixmap(icon_size, icon_size)
            icon_rect = QtCore.QRect(0, 0, icon_size, icon_size)
            icon_rect.moveTop(rect.top() + (rect.height() - icon_size) // 2)
        else:
            pixmap = None

        fm = QtGui.QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()
        total_width = text_width + (icon_size + spacing if pixmap else 0)

        if alignment & QtCore.Qt.AlignHCenter:
            x = rect.left() + (rect.width() - total_width) // 2
        elif alignment & QtCore.Qt.AlignRight:
            x = rect.right() - total_width
        else:
            x = rect.left()

        y = rect.top() + (rect.height() - text_height) // 2

        if pixmap:
            icon_rect.moveLeft(x)
            text_rect = QtCore.QRect(x + icon_size + spacing, y, text_width, text_height)
        else:
            text_rect = QtCore.QRect(x, y, text_width, text_height)

        option = QtWidgets.QStyleOption()
        option.initFrom(self)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, option, painter, self)

        if pixmap:
            painter.drawPixmap(icon_rect, pixmap)
        self.style().drawItemText(
            painter,
            text_rect,
            alignment,
            self.palette(),
            self.isEnabled(),
            text,
            self.foregroundRole(),
        )

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
            event.accept()
        else:
            super().mousePressEvent(event)

class GameCard(QtWidgets.QFrame):
    def __init__(self, name, description, cover_path, appid, controller_support, exec_line,
                 last_launch, formatted_playtime, protondb_tier, last_launch_ts, playtime_seconds, steam_game,
                 select_callback, theme=None, card_width=250, parent=None):
        super().__init__(parent)
        self.name = name
        self.description = description
        self.cover_path = cover_path
        self.appid = appid
        self.controller_support = controller_support
        self.exec_line = exec_line
        self.last_launch = last_launch
        self.formatted_playtime = formatted_playtime
        self.protondb_tier = protondb_tier
        self.steam_game = steam_game
        self.last_launch_ts = last_launch_ts
        self.playtime_seconds = playtime_seconds

        self.select_callback = select_callback
        self.theme_manager = ThemeManager()
        self.theme = theme if theme is not None else default_styles

        self.current_theme_name = read_theme_from_config()

        # Дополнительное пространство для анимации
        extra_margin = 20
        self.setFixedSize(card_width + extra_margin, int(card_width * 1.6) + extra_margin)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setStyleSheet(self.theme.GAME_CARD_WINDOW_STYLE)

        # Параметры анимации обводки
        self._borderWidth = 2
        self._gradientAngle = 0.0
        self._hovered = False

        # Анимации
        self.thickness_anim = QtCore.QPropertyAnimation(self, b"borderWidth")
        self.thickness_anim.setDuration(300)
        self.gradient_anim = None
        self.pulse_anim = None

        # Флаг для отслеживания подключения слота startPulseAnimation
        self._isPulseAnimationConnected = False

        # Тень
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QtGui.QColor(0, 0, 0, 150))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        # Отступы, чтобы анимация не перекрывалась
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(extra_margin // 2, extra_margin // 2, extra_margin // 2, extra_margin // 2)
        layout.setSpacing(5)

        # Контейнер обложки
        coverWidget = QtWidgets.QWidget()
        coverWidget.setFixedSize(card_width, int(card_width * 1.2))
        coverLayout = QtWidgets.QStackedLayout(coverWidget)
        coverLayout.setContentsMargins(0, 0, 0, 0)
        coverLayout.setStackingMode(QtWidgets.QStackedLayout.StackAll)

        # Обложка
        coverLabel = QtWidgets.QLabel()
        coverLabel.setFixedSize(card_width, int(card_width * 1.2))
        pixmap = load_pixmap(cover_path, card_width, int(card_width * 1.2)) if cover_path else load_pixmap("", card_width, int(card_width * 1.2))
        pixmap = round_corners(pixmap, 15)
        coverLabel.setPixmap(pixmap)
        coverLabel.setStyleSheet(self.theme.COVER_LABEL_STYLE)
        coverLayout.addWidget(coverLabel)

        # Значок избранного (звёздочка) в левом верхнем углу обложки
        self.favoriteLabel = ClickableLabel(coverWidget)
        self.favoriteLabel.setFixedSize(*self.theme.favoriteLabelSize)
        self.favoriteLabel.move(8, 8)  # позиция: 8 пикселей от левого и верхнего края
        self.favoriteLabel.clicked.connect(self.toggle_favorite)
        # Определяем статус избранного по имени игры
        self.is_favorite = self.name in read_favorites()
        self.update_favorite_icon()
        self.favoriteLabel.raise_()

        # ProtonDB бейдж
        tier_text = self.getProtonDBText(protondb_tier)
        if tier_text:
            icon_filename = self.getProtonDBIconFilename(protondb_tier)
            icon = self.theme_manager.get_icon(icon_filename, self.current_theme_name)
            self.protondbLabel = ClickableLabel(
                tier_text,
                icon=icon,
                parent=coverWidget,
                icon_size=16,    # размер иконки
                icon_space=5     # отступ между иконкой и текстом
            )
            self.protondbLabel.setStyleSheet(self.theme.get_protondb_badge_style(protondb_tier))
            protondb_visible = True
        else:
            self.protondbLabel = ClickableLabel(
                "",
                parent=coverWidget,
                icon_size=16,
                icon_space=5
            )
            self.protondbLabel.setVisible(False)
            protondb_visible = False

        # Steam бейдж
        steam_icon = self.theme_manager.get_icon("steam.svg", self.current_theme_name)
        self.steamLabel = ClickableLabel(
            "Steam",
            icon=steam_icon,
            parent=coverWidget,
            icon_size=16,
            icon_space=5
        )
        self.steamLabel.setStyleSheet(self.theme.STEAM_BADGE_STYLE)
        steam_visible = (str(steam_game).lower() == "true")
        self.steamLabel.setVisible(steam_visible)

        # Расположение бейджей
        right_margin = 8
        badge_spacing = 5
        top_y = 10
        if steam_visible and protondb_visible:
            steam_width = self.steamLabel.width()
            steam_x = card_width - steam_width - right_margin
            self.steamLabel.move(steam_x, top_y)

            protondb_width = self.protondbLabel.width()
            protondb_x = card_width - protondb_width - right_margin
            protondb_y = top_y + self.steamLabel.height() + badge_spacing
            self.protondbLabel.move(protondb_x, protondb_y)
        elif steam_visible:
            steam_width = self.steamLabel.width()
            steam_x = card_width - steam_width - right_margin
            self.steamLabel.move(steam_x, top_y)
        elif protondb_visible:
            protondb_width = self.protondbLabel.width()
            protondb_x = card_width - protondb_width - right_margin
            self.protondbLabel.move(protondb_x, top_y)

        self.protondbLabel.raise_()
        self.steamLabel.raise_()
        self.protondbLabel.clicked.connect(self.open_protondb_report)
        self.steamLabel.clicked.connect(self.open_steam_page)

        layout.addWidget(coverWidget)

        # Название игры
        nameLabel = QtWidgets.QLabel(name)
        nameLabel.setAlignment(QtCore.Qt.AlignCenter)
        nameLabel.setStyleSheet(self.theme.GAME_CARD_NAME_LABEL_STYLE)
        layout.addWidget(nameLabel)

    def getProtonDBText(self, tier):
        if not tier:
            return ""
        translations = {
            "platinum": _("Platinum"),
            "gold": _("Gold"),
            "silver":  _("Silver"),
            "bronze": _("Bronze"),
            "borked": _("Borked"),
            "pending":  _("Pending")
        }
        return translations.get(tier.lower(), "")

    def getProtonDBIconFilename(self, tier):
        """
        Возвращает имя файла иконки в зависимости от уровня protondb.
        Для примера:
          - Для platinum и gold — 'platinum-gold.svg'
          - Для silver и bronze — 'silver-bronze.svg'
          - Для borked и pending — 'broken.svg'
        """
        tier = tier.lower()
        if tier in ("platinum", "gold"):
            return "platinum-gold.svg"
        elif tier in ("silver", "bronze"):
            return "silver-bronze.svg"
        elif tier in ("borked", "pending"):
            return "broken.svg"
        return ""

    def open_protondb_report(self):
        url = QtCore.QUrl(f"https://www.protondb.com/app/{self.appid}")
        QtGui.QDesktopServices.openUrl(url)

    def open_steam_page(self):
        url = QtCore.QUrl(f"steam://store/{self.appid}")
        QtGui.QDesktopServices.openUrl(url)

    def update_favorite_icon(self):
        """
        Обновляет отображение значка избранного.
        Если игра избранная – отображается заполненная звезда (★),
        иначе – пустая (☆).
        """
        if self.is_favorite:
            self.favoriteLabel.setText("★")
        else:
            self.favoriteLabel.setText("☆")
        self.favoriteLabel.setStyleSheet(self.theme.FAVORITE_LABEL_STYLE)

    def toggle_favorite(self):
        """
        Переключает статус избранного для данной игры и сохраняет изменения в конфиге.
        """
        favorites = read_favorites()
        if self.is_favorite:
            if self.name in favorites:
                favorites.remove(self.name)
            self.is_favorite = False
        else:
            if self.name not in favorites:
                favorites.append(self.name)
            self.is_favorite = True
        save_favorites(favorites)
        self.update_favorite_icon()

    def getBorderWidth(self):
        return self._borderWidth

    def setBorderWidth(self, value):
        self._borderWidth = value
        self.update()

    borderWidth = QtCore.Property(int, getBorderWidth, setBorderWidth)

    def getGradientAngle(self):
        return self._gradientAngle

    def setGradientAngle(self, value):
        self._gradientAngle = value
        self.update()

    gradientAngle = QtCore.Property(float, getGradientAngle, setGradientAngle)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        pen = QtGui.QPen()
        pen.setWidth(self._borderWidth)
        if self._hovered:
            center = self.rect().center()
            gradient = QtGui.QConicalGradient(center, self._gradientAngle)
            gradient.setColorAt(0, QtGui.QColor("#00fff5"))
            gradient.setColorAt(0.33, QtGui.QColor("#FF5733"))
            gradient.setColorAt(0.66, QtGui.QColor("#9B59B6"))
            gradient.setColorAt(1, QtGui.QColor("#00fff5"))
            pen.setBrush(QtGui.QBrush(gradient))
        else:
            pen.setColor(QtGui.QColor(0, 0, 0, 0))

        painter.setPen(pen)
        radius = 18
        rect = self.rect().adjusted(
            self._borderWidth / 2,
            self._borderWidth / 2,
            -self._borderWidth / 2,
            -self._borderWidth / 2
        )
        painter.drawRoundedRect(rect, radius, radius)

    def startPulseAnimation(self):
        if not self._hovered:
            return
        self.pulse_anim = QtCore.QPropertyAnimation(self, b"borderWidth")
        self.pulse_anim.setDuration(800)
        self.pulse_anim.setLoopCount(0)
        self.pulse_anim.setKeyValueAt(0, 8)
        self.pulse_anim.setKeyValueAt(0.5, 10)
        self.pulse_anim.setKeyValueAt(1, 8)
        self.pulse_anim.start()

    def enterEvent(self, event):
        self._hovered = True
        self.thickness_anim.stop()
        if self._isPulseAnimationConnected:
            self.thickness_anim.finished.disconnect(self.startPulseAnimation)
            self._isPulseAnimationConnected = False
        self.thickness_anim.setEasingCurve(QtCore.QEasingCurve.OutBack)
        self.thickness_anim.setStartValue(self._borderWidth)
        self.thickness_anim.setEndValue(8)
        self.thickness_anim.finished.connect(self.startPulseAnimation)
        self._isPulseAnimationConnected = True
        self.thickness_anim.start()

        self.gradient_anim = QtCore.QPropertyAnimation(self, b"gradientAngle")
        self.gradient_anim.setDuration(3000)
        self.gradient_anim.setStartValue(360)
        self.gradient_anim.setEndValue(0)
        self.gradient_anim.setLoopCount(-1)
        self.gradient_anim.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        if self.gradient_anim:
            self.gradient_anim.stop()
            self.gradient_anim = None

        self.thickness_anim.stop()
        if self._isPulseAnimationConnected:
            self.thickness_anim.finished.disconnect(self.startPulseAnimation)
            self._isPulseAnimationConnected = False

        if self.pulse_anim:
            self.pulse_anim.stop()
            self.pulse_anim = None

        self.thickness_anim.setEasingCurve(QtCore.QEasingCurve.InBack)
        self.thickness_anim.setStartValue(self._borderWidth)
        self.thickness_anim.setEndValue(2)
        self.thickness_anim.start()

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.select_callback(
            self.name,
            self.description,
            self.cover_path,
            self.appid,
            self.controller_support,
            self.exec_line,
            self.last_launch,
            self.formatted_playtime,
            self.protondb_tier
        )

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.select_callback(
                self.name,
                self.description,
                self.cover_path,
                self.appid,
                self.controller_support,
                self.exec_line,
                self.last_launch,
                self.formatted_playtime,
                self.protondb_tier
            )
        else:
            super().keyPressEvent(event)
