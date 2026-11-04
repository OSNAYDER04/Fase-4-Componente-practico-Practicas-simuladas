from abc import ABC, abstractmethod
from datetime import datetime
import logging
import os

# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS
LOG_FILENAME = "sistema_eventos.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 2. EXCEPCIONES PERSONALIZADAS Y ENCADENAMIENTO
class SoftwareFJError(Exception):
    """Excepción base para todos los errores del sistema."""
    pass

class ClienteInvalidoError(SoftwareFJError):
    """Excepción lanzada cuando los datos del cliente no son válidos."""
    pass

class ServicioNoDisponibleError(SoftwareFJError):
    """Excepción lanzada cuando un servicio presenta fallas o no está disponible."""
    pass

class ReservaInvalidaError(SoftwareFJError):
    """Excepción lanzada ante intentos de reserva incorrectos o no permitidos."""
    pass

# 3. CLASE ABSTRACTA GENERAL (ENTIDAD BASE)
class EntidadSistema(ABC):
    """Clase abstracta que representa entidades generales del sistema."""
    
    def __init__(self, identificador: str):
        self._identificador = identificador

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def obtener_detalle(self) -> str:
        pass

# 4. CLASE CLIENTE (Encapsulación y Validaciones)
class Cliente(EntidadSistema):
    def __init__(self, identificador: str, nombre: str, gmail: str, telefono: str):
        super().__init__(identificador)
        self.nombre = nombre       # Utiliza el setter
        self.gmail = gmail         # Utiliza el setter
        self.telefono = telefono   # Utiliza el setter

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoError(f"Nombre de cliente inválido: '{valor}'. Debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def gmail(self):
        return self.__gmail

    @gmail.setter
    def gmail(self, valor):
        if not valor or "@" not in valor or "." not in valor:
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self.__gmail = valor.strip()

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if not valor or not valor.isdigit() or len(valor) < 8:
            raise ClienteInvalidoError(f"Teléfono inválido: '{valor}'. Debe contener solo dígitos (mínimo 8).")
        self.__telefono = valor

    def obtener_detalle(self) -> str:
        return f"Cliente: {self.__nombre} | gmail: {self.__gmail} | Tel: {self.__telefono}"