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
    datefmt="%Y-%m-%d %H:%M:%S" # Esta línea de código se utiliza para definir el formato en el que se mostrará la fecha y la hora dentro del archivo de registros (.log).
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

# ==========================================
# 5. CLASE ABSTRACTA SERVICIO Y DERIVADOS
# ==========================================
class Servicio(EntidadSistema, ABC):
    """Clase abstracta base que define la estructura general de cualquier servicio."""

    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, disponible: bool = True):
        # Inicializa el identificador heredado de EntidadSistema y los atributos del servicio
        super().__init__(identificador)
        self.nombre_servicio = nombre_servicio
        self.costo_base = costo_base
        self.disponible = disponible

    @property
    def costo_base(self):
        # Getter que permite consultar el atributo privado __costo_base de forma segura
        return self.__costo_base

    @costo_base.setter
    def costo_base(self, valor):
        # Setter que valida que el costo base no sea negativo antes de asignarlo
        if valor < 0:
            raise ServicioNoDisponibleError("El costo base no puede ser negativo.")
        self.__costo_base = float(valor)

    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        """Método polimórfico obligatorio para calcular costos en las clases hijas."""
        pass

    @abstractmethod
    def describir(self) -> str:
        """Método polimórfico obligatorio para describir cada tipo de servicio."""
        pass

    def obtener_detalle(self) -> str:
        # Retorna una cadena formateada con el nombre del servicio y su costo base
        return f"Servicio: {self.nombre_servicio} | Costo Base: ${self.__costo_base:.2f}"


# Servicio 1: Reserva de Salas
class ReservaSalas(Servicio):
    """Clase derivada de Servicio especializada en el alquiler y reserva de salas."""

    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, capacidad: int):
        # Llama al constructor de Servicio y añade la capacidad de personas de la sala
        super().__init__(identificador, nombre_servicio, costo_base)
        self.capacidad = capacidad

    # Método sobrecargado mediante argumentos opcionales / condicionales
    def calcular_costo(self, horas: float = 1.0, aplicar_impuesto: bool = True, descuento_porcentaje: float = 0.0) -> float:
        # Calcula el costo total validando horas, aplicando descuentos opcionales e IVA del 19%
        try:
            if horas <= 0:
                raise ValueError("Las horas de reserva deben ser mayores a cero.")
            
            subtotal = self.costo_base * horas
            if descuento_porcentaje > 0:
                subtotal -= subtotal * (descuento_porcentaje / 100)
            
            if aplicar_impuesto:
                subtotal *= 1.19  # IVA 19%
            return round(subtotal, 2)
        except Exception as e:
            # Encadena cualquier error de cálculo dentro de la excepción personalizada del sistema
            raise ServicioNoDisponibleError(f"Error al calcular costo de sala: {e}") from e

    def describir(self) -> str:
        # Sobrescribe el método abstracto incluyendo la capacidad específica de la sala
        return f"[Sala de Reuniones] Capacidad: {self.capacidad} personas. {self.obtener_detalle()}"
    # 6. CLASE RESERVA (Gestión integral y bloques try/except/else/finally)
class Reserva:
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, cantidad_tiempo: float):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad_tiempo = cantidad_tiempo
        self.estado = "Creada"  # Creada, Confirmada, Cancelada, Procesada

    def confirmar_reserva(self, **kwargs):
        """Implementa bloques try/except/else/finally y manejo robusto."""
        logging.info(f"Iniciando procesamiento de reserva {self.id_reserva}...")
        try:
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self.servicio.nombre_servicio}' no se encuentra disponible.")
            
            # Cálculo del costo usando polimorfismo
            if isinstance(self.servicio, ReservaSalas):
                self.costo_final = self.servicio.calcular_costo(horas=self.cantidad_tiempo, **kwargs)
            elif isinstance(self.servicio, AlquilerEquipos):
                self.costo_final = self.servicio.calcular_costo(dias=int(self.cantidad_tiempo), **kwargs)
            elif isinstance(self.servicio, AsesoriaEspecializada):
                self.costo_final = self.servicio.calcular_costo(sesiones=int(self.cantidad_tiempo), **kwargs)
            else:
                raise ReservaInvalidaError("Tipo de servicio desconocido para procesar la reserva.")
            
            self.estado = "Confirmada"
            
        except (ServicioNoDisponibleError, ReservaInvalidaError, ValueError) as e:
            self.estado = "Fallida"
            logging.error(f"Error controlado en reserva {self.id_reserva}: {e}")
            raise ReservaInvalidaError(f"No se pudo confirmar la reserva {self.id_reserva}") from e
        
        else:
            # Se ejecuta solo si NO hubo excepciones
            logging.info(f"Reserva {self.id_reserva} confirmada con éxito. Costo total: ${self.costo_final}")
            print(f" -> [ÉXITO] Reserva {self.id_reserva} procesada correctamente para {self.cliente.nombre}. Total: ${self.costo_final}")
            
        finally:
            # Se ejecuta siempre (auditoría / cierre de operación)
            logging.info(f"Transacción de reserva {self.id_reserva} finalizada. Estado actual: {self.estado}\n")

    def cancelar_reserva(self):
        if self.estado == "Cancelada":
            print(f" -> [AVISO] La reserva {self.id_reserva} ya estaba cancelada.")
            return
        self.estado = "Cancelada"
        logging.warning(f"La reserva {self.id_reserva} ha sido cancelada por el usuario.")
        print(f" -> [CANCELADA] La reserva {self.id_reserva} se canceló exitosamente.")
# 7. SIMULACIÓN DE 10 OPERACIONES (Válidas e Inválidas)
# ==========================================
def ejecutar_simulacion():
    print("==================================================")
    print(" INICIANDO SIMULACIÓN DE OPERACIONES - SOFTWARE FJ")
    print("==================================================\n")

    # Instanciación de Servicios Base
    sala_vip = ReservaSalas("S001", "Sala Ejecutiva A", 50.0, capacidad=10)
    equipo_mac = AlquilerEquipos("E001", "MacBook Pro M3", 25.0, tipo_equipo="Portátil")
    asesoria_tec = AsesoriaEspecializada("A001", "Consultoría en Arquitectura Software", 120.0, especialista="Dra. Ana Pérez")

    operaciones = [
        # Operación 1: Registro de Cliente Válido y Reserva Exitosa (Sala de Reuniones)
        lambda: (
            print("1. [Operación Válida] Creando cliente y reservando sala..."),
            cli := Cliente("C001", "Carlos Mendoza", "carlos.mendoza@gmail.com", "3001234567"),
            res := Reserva("R-001", cli, sala_vip, cantidad_tiempo=3.0),
            res.confirmar_reserva(aplicar_impuesto=True, descuento_porcentaje=10.0)
        ),

        # Operación 2: Error por Datos Inválidos en Cliente (Nombre muy corto)
        lambda: (
            print("2. [Operación Inválida] Intentando crear cliente con nombre corto..."),
            Cliente("C002", "Jo", "jo@gmail.com", "3119876543")
        ),

        # Operación 3: Alquiler de Equipo Exitoso
        lambda: (
            print("3. [Operación Válida] Alquiler de equipo informático..."),
            cli := Cliente("C003", "María Gómez", "maria.gomez@gmail.com", "3204567890"),
            res := Reserva("R-002", cli, equipo_mac, cantidad_tiempo=5.0),
            res.confirmar_reserva(seguro_adicional=True)
        ),

        # Operación 4: Error por Correo Electrónico Inválido
        lambda: (
            print("4. [Operación Inválida] Creando cliente con correo malformado..."),
            Cliente("C004", "Esteban Quito", "esteban-email.com", "3154567891")
        ),

        # Operación 5: Asesoría Especializada Exitosa (Con Urgencia Alta)
        lambda: (
            print("5. [Operación Válida] Solicitando asesoría especializada urgente..."),
            cli := Cliente("C005", "Lucia Fernandez", "lucia.f@gmail.com", "3187654321"),
            res := Reserva("R-003", cli, asesoria_tec, cantidad_tiempo=2.0),
            res.confirmar_reserva(nivel_urgencia="alto")
        ),

# Operación 6: Validación de excepción ante duración inválida (tiempo igual a cero)
        lambda: (
            print("6. [Operación Inválida] Reserva con duración inválida (cero horas)..."),
            # Se instancia un cliente con datos válidos
            cli := Cliente("C006", "Pedro Picapiedra", "pedro@gmail.com", "3011112222"),
            # Se intenta crear y confirmar una reserva con 0 horas para disparar ReservaInvalidaError
            res := Reserva("R-004", cli, sala_vip, cantidad_tiempo=0.0),
            res.confirmar_reserva()
        ),

        # Operación 7: Flujo válido de creación y posterior cancelación de una reserva
        lambda: (
            print("7. [Operación Válida] Cancelación de reserva previamente creada..."),
            # Se registra un nuevo cliente válido en el sistema
            cli := Cliente("C007", "Sofía Vergara", "sofia@gmail.com", "3023334444"),
            # Se crea la reserva asociando correctamente al cliente (cli) y el servicio (equipo_mac)
            res := Reserva("R-005", cli, equipo_mac, cantidad_tiempo=2.0),
            # Se ejecuta el método de cancelación para cambiar el estado de la reserva
            res.cancelar_reserva()
        ),
    # Operación 8: Error por Teléfono con caracteres alfabéticos
        lambda: (
            print("8. [Operación Inválida] Cliente con teléfono que contiene letras..."),
            Cliente("C008", "Raúl Castro", "raul@gmail.com", "300ABC4567")
        ),

        # Operación 9: Intento de reserva en un servicio marcado como No Disponible
        lambda: (
            print("9. [Operación Inválida] Reservando un servicio fuera de servicio..."),
            setattr(sala_vip, "disponible", False), # Inhabilitamos el servicio
            cli := Cliente("C009", "Andrea Rincón", "andrea@gmail.com", "3109998877"),
            res := Reserva("R-006", cli, sala_vip, cantidad_tiempo=1.0),
            res.confirmar_reserva()
        ),

        # Operación 10: Operación Válida Final (Restaurando disponibilidad y haciendo nueva reserva)
        lambda: (
            print("10. [Operación Válida] Restaurando servicio y generando reserva normal..."),
            setattr(sala_vip, "disponible", True),
            cli := Cliente("C010", "Gabriel García", "gabriel@gmail.com", "3145556677"),
            res := Reserva("R-007", cli, sala_vip, cantidad_tiempo=2.5),
            res.confirmar_reserva(aplicar_impuesto=True, descuento_porcentaje=5.0)
        )
    ]
# Ejecutor iterativo con manejo global para garantizar que el sistema nunca colapse
    for i, op in enumerate(operaciones, 1):
        print(f"\n--- Ejecutando Operación {i} ---")
        try:
            op()
        except SoftwareFJError as se:
            print(f" -> [CONTROLADOR DE EXCEPCIÓN PERSONALIZADA]: {se}")
        except Exception as ex:
            print(f" -> [ERROR INESPERADO CAPTURADO]: {ex}")
        print("-" * 50)

    print(f"\nSimulación finalizada. Todos los eventos y errores fueron registrados en '{LOG_FILENAME}'.")

if __name__ == "__main__":
    ejecutar_simulacion()    
