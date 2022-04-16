from asyncore import dispatcher
from telegram import *
from telegram.ext import *
from requests import *
from datetime import datetime
import gspread
import requests
import os
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client as ClientTwilio


if "DOCKER" in os.environ['ENVIRONMENT']:
    credenciales = 'app/pilarminingco-c11e8da70b2f.json'
if "TEST" in os.environ['ENVIRONMENT']:
    credenciales = 'pilarminingco-c11e8da70b2f.json'
if "PROD" in os.environ['ENVIRONMENT']:
    credenciales = '/home/PMC/AutomatismosPMC/pilarminingco-c11e8da70b2f.json'

class operacion:
    def __init__(self, fecha, tipo, vendedor, monto, cotizacion, cliente ):
        self.fecha = fecha
        self.tipo = tipo
        self.vendedor = vendedor
        self.monto = monto
        self.cotizacion = cotizacion
        self.cliente = cliente

updater = Updater(token="5124513220:AAGh3zhe36hP7dt9iMBzomiKWiyV4o47VHc")
dispatcher = updater.dispatcher

def sendTwilio(fecha, tipo, vendedor, monto, cotizacion, cliente):
    lista_senders=['5491130252911','5491121708911']
    account_sid = "AC7567d2dee446b304d2e30b9f277656a6"
    auth_token  = "bbcc1a2a7511d55fb8e6b7bae24cade5"
    client = ClientTwilio(account_sid, auth_token)
    for sender in lista_senders:
        message = client.messages \
            .create(
                from_='whatsapp:+16625025249',
                body=f"Hola! Queremos comentarte lo siguiente: \nSe ha realizado una operación de cambio en PMC. \nVendedor: {vendedor} - Cliente: {cliente} \nTipo: {tipo} Monto: {monto} Cotización: {cotizacion} \n*Fondos USD: Fondos Fondos ARS: Fondos* \nFecha: {fecha} \nSaludos!",
                to=f'whatsapp:+{sender}'
            )

def getDolarBlue(operacion):
    response = requests.get("https://api.bluelytics.com.ar/v2/latest").json()
    if "buy" in operacion:
        return response["blue"]["value_buy"]
    if "sell" in operacion:
        return response["blue"]["value_sell"]
    if "avg" in operacion:
        return response["blue"]["value_avg"]


def startCommand(update: Update, context: CallbackContext):
    print(update.effective_chat)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bienvenido utilice /compra monto cotizacion nombre \nEJEMPLO: /compra 500 197 Juan Perez\nEJEMPLO: /venta 500 201 Juan Perez")

def compraCommand(update: Update, context: CallbackContext):
    string = update.message.text
    fecha = datetime.today().strftime('%d-%m-%Y')
    tipo = string.split(None,3)[0][1:]
    vendedor = update.effective_chat.first_name
    monto = string.split(None,3)[1].replace(",",".")
    cotizacion = string.split(None,3)[2].replace(",",".")
    cliente = string.split(None,3)[3]
    sendResponse(monto, cotizacion, update,context)
    updateSheet(fecha, tipo, vendedor, monto, cotizacion, cliente, "Pilar Mining CO", "Financiera",update,context)
    sendTwilio(fecha, tipo, vendedor, monto, cotizacion, cliente)

def ventaCommand(update: Update, context: CallbackContext):
    string = update.message.text
    fecha = datetime.today().strftime('%d-%m-%Y')
    tipo = string.split(None,3)[0][1:]
    vendedor = update.effective_chat.first_name
    monto = string.split(None,3)[1].replace(",",".")
    cotizacion = string.split(None,3)[2].replace(",",".")
    cliente = string.split(None,3)[3]
    sendResponse(monto, cotizacion, update,context)
    updateSheet(fecha, tipo, vendedor, monto, cotizacion, cliente, "Pilar Mining CO", "Financiera",update,context)
    sendTwilio(fecha, tipo, vendedor, monto, cotizacion, cliente)

def subimosCommand(update: Update, context: CallbackContext):
    string = update.message.text
    fecha = datetime.today().strftime('%d-%m-%Y')
    tipo = string.split(None,3)[0][1:]
    vendedor = update.effective_chat.first_name
    monto = string.split(None,3)[1].replace(",",".")
    cotizacion = string.split(None,3)[2].replace(",",".")
    cliente = string.split(None,3)[3]
    sendResponse(monto, cotizacion, update,context)
    updateSheet(fecha, tipo, vendedor, monto, cotizacion, cliente, "Pilar Mining CO", "Financiera",update,context)
    sendTwilio(fecha, tipo, vendedor, monto, cotizacion, cliente)


def bajamosCommand(update: Update, context: CallbackContext):
    string = update.message.text
    fecha = datetime.today().strftime('%d-%m-%Y')
    tipo = string.split(None,3)[0][1:]
    vendedor = update.effective_chat.first_name
    monto = string.split(None,3)[1].replace(",",".")
    cotizacion = string.split(None,3)[2].replace(",",".")
    cliente = string.split(None,3)[3]
    sendResponse(monto, cotizacion, update,context)
    updateSheet(fecha, tipo, vendedor, monto, cotizacion, cliente, "Pilar Mining CO", "Financiera",update,context)
    sendTwilio(fecha, tipo, vendedor, monto, cotizacion, cliente)

def sendResponse(monto, cotizacion, update,context):
    if "compra" in "tipo":
        billete = float(monto) * float(cotizacion)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Compramos USD {str(monto)} - Entregamos ARS ${billete}")
    if "venta" in "tipo":
        billete = float(monto) * float(cotizacion)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Compramos ARS {str(monto)} - Entregamos USD {billete}")
    if "subimos" in "tipo":
        billete = float(monto) - (float(monto) * float(cotizacion)/100)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Subimos USDT {str(monto)} - Entregamos USD {billete}")    
    if "bajamos" in "tipo":
        billete = float(monto) - (float(monto) * float(cotizacion)/100)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Bajamos USDT {str(monto)} - Entregamos USDT {billete}")

def updateSheet(fecha, tipo, vendedor, monto, cotizacion, cliente, sheet, worksheet,update,context):
    print(f"Fecha: {fecha}, Tipo: {tipo}, Vendedor: {vendedor}, Monto: {monto}, Cotizacion:{cotizacion}, Cliente: {cliente}  ")
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credenciales, scope)
    client = gspread.authorize(creds)
    work_sheet = client.open(sheet)
    sheet_instance = work_sheet.worksheet(worksheet)
    if (tipo == "compra"):
        spread = (float(getDolarBlue("avg")))-float(cotizacion)
    if (tipo == "venta"):
        spread = (float(cotizacion)-float(getDolarBlue("avg")))
    ganancia = spread*float(monto)
    if "compra" or "venta" in tipo:
        new_row = (fecha, tipo, vendedor, cliente, monto, cotizacion, float(monto)*float(cotizacion), spread, ganancia,getDolarBlue("buy"),getDolarBlue("sell"),getDolarBlue("avg"))
    if "subida" or "bajada" in tipo:
        new_row = (fecha, tipo, vendedor, cliente, monto, cotizacion, float(monto)*float(cotizacion), spread, ganancia,getDolarBlue("buy"),getDolarBlue("sell"),getDolarBlue("avg"), cotizacion)
    sheet_instance.append_row(new_row, value_input_option="USER_ENTERED")
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Transaccion cargada con exito - Ganancia ${ganancia}")




dispatcher.add_handler(CommandHandler("start", startCommand))
dispatcher.add_handler(CommandHandler("Compra", compraCommand))
dispatcher.add_handler(CommandHandler("Venta", ventaCommand))
dispatcher.add_handler(CommandHandler("subimos", subimosCommand))
dispatcher.add_handler(CommandHandler("bajamos", bajamosCommand))


updater.start_polling()