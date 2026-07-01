class DomainError(Exception):
    """Базовый класс доменных ошибок сервисного слоя."""


class LotNotFoundError(DomainError):
    def __init__(self, lot_id: int) -> None:
        self.lot_id = lot_id
        super().__init__(f"Лот {lot_id} не найден")


class LotSetNotFoundError(DomainError):
    def __init__(self, set_id: int) -> None:
        self.set_id = set_id
        super().__init__(f"Набор лотов {set_id} не найден")


class LotNotAvailableError(DomainError):
    """Лот не в статусе «в продаже» — бронировать нельзя."""

    def __init__(self, lot_id: int) -> None:
        self.lot_id = lot_id
        super().__init__(f"Лот {lot_id} недоступен для брони")


class InvalidCredentialsError(DomainError):
    def __init__(self) -> None:
        super().__init__("Неверный логин или пароль")
