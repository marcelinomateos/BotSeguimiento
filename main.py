import telebot 
import sqlite3
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
#from config import * #importar config
from pacientesBD import * #Importamos pacientes, donde se crea la base de datos


#Instanciar el bot
bot = telebot.TeleBot("7734067796:AAF_2wvdRTR9KQi6jYPOcf-PKyYfSx6eyGk")


temp_data = {}
global usuario_id


################## COMANDOS ##################

#Responde a comando /start
@bot.message_handler(commands= ["iniciar"])
def cmd_start(message):
    #Dar bienvenida al usuario
    bot.reply_to(message, "Hola! Usa el comando /seguimiento para comenzar el seguimiento de tu paciente")

#Registrar Pacientes desde Admin, comando /registrar
@bot.message_handler(commands=["registrar"])
def cmd_registrar(message):
    global usuario_id 
    usuario_id = message.from_user.id
    temp_data[usuario_id] = {}
    bot.reply_to(message, "Ingresa el folio del paciente: ")
    bot.register_next_step_handler(message, obtener_folio)

#Seguimiento de pacientes, comando /seguimiento
@bot.message_handler(commands=["seguimiento"])
def cmd_seguimiento(message):
    bot.send_message(message.chat.id, "Ingrese folio de su paciente")
    bot.register_next_step_handler(message, validar_folio)



################## REGISTRO DE PACIENTES ##################

#Registrar Pacientes desde Admin, comando /registrar
@bot.message_handler(commands=["registrar"])
def cmd_registrar(message):
    usuario_id = message.from_user.id
    temp_data[usuario_id] = {}
    bot.reply_to(message, "Ingresa el folio del paciente: ")
    bot.register_next_step_handler(message, obtener_folio)

#Funcion para obtener el folio
def obtener_folio(message):
    usuario_id = message.from_user.id
    temp_data[usuario_id]['folio'] = message.text
    bot.reply_to(message, "Ingresa el nombre del paciente")
    bot.register_next_step_handler(message, obtener_nombre)

#Funcion para obtener el nombre
def obtener_nombre(message):
    usuario_id = message.from_user.id
    temp_data[usuario_id]['nombre'] = message.text
    bot.reply_to(message, "Ingresa el apellido paterno")
    bot.register_next_step_handler(message, obtener_apellido_paterno)

#Funcion para obtener el apellido paterno
def obtener_apellido_paterno(message):
    usuario_id = message.from_user.id
    temp_data[usuario_id]['apellido_paterno'] = message.text
    bot.reply_to(message, "Ingresa apellido materno")
    bot.register_next_step_handler(message, obtener_apellido_materno)

#Funcion para obtener el apellido materno
def obtener_apellido_materno(message):
    usuario_id = message.from_user.id
    temp_data[usuario_id]['apellido_materno'] = message.text
    bot.reply_to(message, "Ingresa la edad del paciente")
    bot.register_next_step_handler(message, obtener_edad)

#Funcion para obtener la edad
def obtener_edad(message):
    usuario_id = message.from_user.id
    try:
        temp_data[usuario_id]['edad'] = int(message.text)
        bot.reply_to(message, "Ingresa el lugar de procedencia del paciente:")
        bot.register_next_step_handler(message, obtener_procedencia)
    except ValueError:
        bot.reply_to(message, "Por favor, ingresa una edad válida.")
        bot.register_next_step_handler(message, obtener_edad)

#Funcion para obtener la procedencia del paciente
def obtener_procedencia(message):
    usuario_id = message.from_user.id
    temp_data[usuario_id]['lugar_procedencia'] = message.text
    bot.reply_to(message, "Ingresa numero telefonico o de casa")
    bot.register_next_step_handler(message, obtener_numero)

#Funcion para guardar el numero y llamar la funcion que guarda en la Base de datos sqlite
def obtener_numero(message):
    usuario_id = message.from_user.id
    try:
        temp_data[usuario_id]['numero'] = int(message.text)

        guardar_en_db(usuario_id)

        bot.reply_to(message, "El registro ha sido completado exitosamente.")
        del temp_data[usuario_id]  # Eliminar los datos temporales

    except ValueError:
        bot.reply_to(message, "Por favor, ingresa un número valido.")
        bot.register_next_step_handler(message, obtener_edad)

def guardar_en_db(usuario_id):
    paciente = temp_data[usuario_id]
    conn = sqlite3.connect('pacientes.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO pacientes (folio, nombre, apellido_paterno, apellido_materno, edad, lugar_procedencia, numero)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (paciente['folio'], paciente['nombre'], paciente['apellido_paterno'], paciente['apellido_materno'], 
          paciente['edad'], paciente['lugar_procedencia'], paciente['numero']))
    
    conn.commit()
    conn.close() # Cerramos la conexión



################## SEGUIMIENTO ##################

#Obtener folio de paciente y avisar si se encuentra registrado
def validar_folio(message):
    folio = message.text
    global usuario_id 
    #
    usuario_id = message.from_user.id
    paciente = verificar_paciente(folio)

    if paciente:
        # Inicializar temp_data para este usuario
        temp_data[usuario_id] = {'folio': folio}
        bot.send_message(message.chat.id, "Paciente encontrado. Iniciando seguimiento.")
        preguntar_temperatura(message)
    else:
        bot.send_message(message.chat.id, "Paciente no encontrado. Por favor verifique el folio.")
#####Inicia Seguimiento#####

# Pregunta sobre la temperatura del paciente
def preguntar_temperatura(message):
    markup = InlineKeyboardMarkup()
    buttons = [
        InlineKeyboardButton("Menor a 36", callback_data="temp_menor_36"),
        InlineKeyboardButton("36 a 37", callback_data="temp_36_37"),
        InlineKeyboardButton("37 a 38", callback_data="temp_37_38"),
        InlineKeyboardButton("38 a 39", callback_data="temp_38_39"),
        InlineKeyboardButton("Mayor a 40", callback_data="temp_mayor_40")
    ]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Ingrese la temperatura de su paciente:", reply_markup=markup)

# Manejar respuestas de temperatura
@bot.callback_query_handler(func=lambda call: call.data.startswith("temp_"))
def respuesta_temperatura(call):
    usuario_id = call.from_user.id

    if call.data == "temp_36_37":
        # Mostrar opciones específicas entre 36.1 y 36.9
        markup = InlineKeyboardMarkup()
        buttons = [InlineKeyboardButton(f"36.{i}", callback_data=f"temp_36.{i}") for i in range(1, 10)]
        markup.add(*buttons)
        bot.edit_message_text("Elija una temperatura más específica:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    if call.data == "temp_menor_36":
        #temp_data[usuario_id]['temperatura'] = call.data.replace("temp_", "").replace("_", " ")
        temp_data[usuario_id]['temperatura'] = 36
        preguntar_vomitos(call.message)
#Temperatura entre 36.1 y 36.9
@bot.callback_query_handler(func=lambda call: call.data.startswith("temp_36."))
def respuesta_temperatura_especifica(call):
    usuario_id = call.from_user.id
    temp_data[usuario_id]['temperatura'] = call.data.replace("temp_", "")
    print (call.data)
    preguntar_vomitos(call.message)

#Preguntar Vomitos
def preguntar_vomitos(message):
    markup = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton("Si", callback_data="vomitos_si"), InlineKeyboardButton("No", callback_data="vomitos_no")]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "¿Su paciente ha presentado vómitos?", reply_markup=markup)

#Respuestas sobre vómitos
@bot.callback_query_handler(func=lambda call: call.data.startswith("vomitos_"))
def respuesta_vomitos(call):
    usuario_id = call.from_user.id

    print(f"Datos de temp_data en respuesta_vomito: {temp_data}")
    
    if call.data == "vomitos_si":
        temp_data[usuario_id]['vomitos'] = "Si"
        markup = InlineKeyboardMarkup()
        buttons = [
            InlineKeyboardButton("1 vez por semana", callback_data="frec_1"),
            InlineKeyboardButton("2 veces por semana", callback_data="frec_2"),
            InlineKeyboardButton("3 o más veces por semana", callback_data="frec_3")
        ]
        markup.add(*buttons)
        bot.edit_message_text("¿Con qué frecuencia?", call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        temp_data[usuario_id]['vomitos'] = "No"
        temp_data[usuario_id]['frecuencia_vomitos']  = '0'
        preguntar_respiracion(call.message)

#Frecuencia Vomitos
@bot.callback_query_handler(func=lambda call: call.data.startswith("frec_"))
def respuesta_frecuencia_vomitos(call):
    usuario_id = call.from_user.id
    
    print(f"Datos de temp_data en respuesta_temperatura: {temp_data}")

    temp_data[usuario_id]['frecuencia_vomitos'] = call.data.replace("frec_", "")
    preguntar_respiracion(call.message)

#Preguntar Respiracion
def preguntar_respiracion(message):
    markup = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton("Si", callback_data="resp_si"), InlineKeyboardButton("No", callback_data="resp_no")]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "¿Su paciente presenta problemas para respirar?", reply_markup=markup)

#Respuestas problemas respiracion
@bot.callback_query_handler(func=lambda call: call.data.startswith("resp_"))
def respuesta_respiracion(call):
    usuario_id = call.from_user.id
    print(f"Datos de temp_data en respuesta_respiracion: {temp_data}")
    temp_data[usuario_id]['problemas_respiracion'] = call.data.replace("resp_", "")
    preguntar_dolor_corporal(call.message)

# Pregunta sobre dolor corporal
def preguntar_dolor_corporal(message):
    markup = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton("Si", callback_data="dolor_si"), InlineKeyboardButton("No", callback_data="dolor_no")]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "¿Su paciente presenta dolor corporal?", reply_markup=markup)

#Respuestas dolor corporal
@bot.callback_query_handler(func=lambda call: call.data.startswith('dolor_'))
def respuesta_dolor_corporal(call):
    usuario_id = call.from_user.id
    print(f"Datos de temp_data en respuesta_dolor corporal: {temp_data}")
    if call.data == "dolor_si":
        temp_data[usuario_id]['dolor_corporal'] = "Si"
        preguntar_zona_dolor(call.message)
    else:
        temp_data[usuario_id]['dolor_corporal'] = "No"
        temp_data[usuario_id]['zona_dolor'] = "0"
        temp_data[usuario_id]['intensidad_dolor'] = "0"
        guardar_seguimiento(call.message)

#Preguntar Zona Dolor
def preguntar_zona_dolor(message):
    markup = InlineKeyboardMarkup()
    zonas = ["Cabeza", "Hombros", "Brazos", "Manos", "Pecho", "Estómago", "Piernas", "Pies", "Espalda"]
    buttons =[InlineKeyboardButton(zona, callback_data=f"zona_{zona}") for zona in zonas]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "¿En qué zona del cuerpo se presenta el dolor?", reply_markup=markup)

# Respuestas sobre la zona del dolor
@bot.callback_query_handler(func=lambda call: call.data.startswith("zona_"))
def respuesta_zona_dolor(call):
    usuario_id = call.from_user.id
    print(f"Datos de temp_data en respuesta_zona_dolor: {temp_data}")
    temp_data[usuario_id]['zona_dolor'] = call.data.replace("zona_", "")
    preguntar_intensidad_dolor(call.message)

# Pregunta sobre la intensidad del dolor
def preguntar_intensidad_dolor(message):
    markup = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(str(i), callback_data=f"intensidad_{i}") for i in range(1, 11)]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "¿Con qué intensidad se presenta el dolor? (1 = leve, 10 = El peor dolor de todos)", reply_markup=markup)

# Manejar respuestas sobre la intensidad del dolor
@bot.callback_query_handler(func=lambda call: call.data.startswith("intensidad_"))
def respuesta_intensidad_dolor(call):
    usuario_id = call.from_user.id
    print(f"Datos de temp_data en respuesta_intensidad_dolor: {temp_data}")
    temp_data[usuario_id]['intensidad_dolor'] = int(call.data.replace("intensidad_", ""))
    guardar_seguimiento(call.message)

#Guardar seguimiento en la BD
def guardar_seguimiento(message):
    global usuario_id
    #usuario_id = message.from_user.id if message.from_user.id else None

    print(f"Usuario_id: {usuario_id}")
    print(f"temp_data: {temp_data}")
    # Verificar si se obtuvo un usuario_id válido
    if usuario_id is None:
        bot.send_message(message.chat.id, "Error: No se pudo identificar al usuario.")
        return

    # Verificar si el usuario_id existe en temp_data
    if usuario_id not in temp_data:
        bot.send_message(message.chat.id, "Ocurrió un error. No se encontraron los datos de seguimiento.")
        return
    
    seguimiento = temp_data[usuario_id]
    folio = seguimiento['folio']
    fecha = datetime.now().strftime('%Y-%m-%d')
    hora = datetime.now().strftime('%H:%M:%S')
    temperatura = seguimiento['temperatura']
    vomitos = seguimiento.get('vomitos', '')
    frecuencia_vomitos = seguimiento.get('frecuencia_vomitos', '')
    problemas_respiracion = seguimiento.get('problemas_respiracion', '')
    dolor_corporal = seguimiento.get('dolor_corporal', '')
    zona_dolor = seguimiento.get('zona_dolor', '')
    intensidad_dolor = seguimiento.get('intensidad_dolor', None)

    if not temperatura:
        bot.send_message(message.chat.id, "Error: Falta la temperatura del paciente.")
        print("Error: Falta la temperatura")
        return
    
    if not vomitos:
        bot.send_message(message.chat.id, "Error: Falta la vomitos del paciente.")
        print("Error: Falta la vomitos")
        return
    
    if not frecuencia_vomitos:
        bot.send_message(message.chat.id, "Error: Falta la frecuencia vomitos del paciente.")
        print("Error: Falta la frecuencia vomitos")
        return
    
    if not problemas_respiracion:
        bot.send_message(message.chat.id, "Error:  problemas respiracion del paciente.")
        print("Error: Faltan problemas respiracion")
        return
    
    if not dolor_corporal:
        bot.send_message(message.chat.id, "Error: Falta la dolor_corporal del paciente.")
        print("Error: Falta la dolor_corporal")
        return
    
    if not zona_dolor:
        bot.send_message(message.chat.id, "Error: zona_dolor del paciente.")
        print("Error: zona_dolor")
        return
    
    if not intensidad_dolor:
        bot.send_message(message.chat.id, "Error: Falta la intensidad_dolor del paciente.")
        print("Error: Falta la intensidad_dolor")
        return
    
    
    # Insertar los datos en la tabla seguimientos
    conn = sqlite3.connect('pacientes.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO seguimientos (folio, fecha, hora, temperatura, vomitos, frecuencia_vomitos, problemas_respiracion, dolor_corporal, zona_dolor, intensidad_dolor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (folio, fecha, hora, temperatura, vomitos, frecuencia_vomitos, problemas_respiracion, dolor_corporal, zona_dolor, intensidad_dolor))

    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, "Seguimiento guardado con éxito.")

################## FUNCIONES UTILES ##################

#Verifica que un paciente se encuentre en la tabla pacientes
def verificar_paciente(folio):
    conn = sqlite3.connect('pacientes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pacientes WHERE folio = ?', (folio,))
    paciente = cursor.fetchone()
    conn.close() # Cerramos la conexión
    return paciente

if __name__ == '__main__':
    print('Iniciando')
    bot.infinity_polling()