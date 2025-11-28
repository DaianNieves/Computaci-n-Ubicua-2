import network
import urequests
import time
from machine import UART, Pin
import ujson

SSID = "C4s4R3d"
PASSWORD = "R3dC4542025?$%"
FIREBASE_URL = "https://recolectores-de-datos-p6-default-rtdb.firebaseio.com/sensores.json"

uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))

led = Pin("LED", Pin.OUT)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    print(f"Conectando a {SSID}...")
    
    intentos = 0
    while not wlan.isconnected() and intentos < 20:
        led.toggle()
        time.sleep(0.5)
        intentos += 1
        print(".", end="")
        
    if wlan.isconnected():
        print(f"\n¡Conectado! IP: {wlan.ifconfig()[0]}")
        led.on()
    else:
        print("\nError: No se pudo conectar al WiFi.")
        led.off()

def main():
    conectar_wifi()
    print("--- Sistema Listo: Esperando datos del Arduino ---")
    
    while True:
        try:
            if uart.any():
                data_bytes = uart.readline()
                
                try:
                    texto = data_bytes.decode('utf-8').strip()
                    print(f"\nRecibido del Arduino: {texto}")
                    
                    # Arduino envía: ldr, lm35, mic, hum, temp
                    valores = texto.split(',')
                    
                    if len(valores) == 5:
                        json_data = {
                            "ldr": int(valores[0]),           # Fotoresistencia (entero)
                            "lm35": float(valores[1]),        # LM35 (AHORA ES FLOAT/DECIMAL)
                            "mic": int(valores[2]),           # Micrófono (entero)
                            "humedad": float(valores[3]),     # DHT Humedad (float)
                            "temperatura": float(valores[4]), # DHT Temperatura (float)
                            "timestamp": time.time()          # Tiempo interno (opcional)
                        }
                        
                        print("Subiendo a Firebase...", end="")
                        respuesta = urequests.post(FIREBASE_URL, json=json_data)
                        
                        if respuesta.status_code == 200:
                            print(" ¡OK!")
                        else:
                            print(f" Error: {respuesta.status_code}")
                            
                        respuesta.close()
                        
                    else:
                        print(f"Error de formato: Se esperaban 5 valores, llegaron {len(valores)}")

                except ValueError:
                    print("Error: Uno de los datos no es un número válido.")
                except UnicodeError:
                    print("Error: Trama de datos corrupta (ruido en cables).")
            
        except Exception as e:
            print(f"Error general: {e}")
            wlan = network.WLAN(network.STA_IF)
            if not wlan.isconnected():
                print("WiFi perdido, reconectando...")
                conectar_wifi()
        
        time.sleep_ms(100)

# Ejecutar
if __name__ == "__main__":
    main()