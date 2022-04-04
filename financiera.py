from asyncore import dispatcher
from telegram import *
from telegram.ext import *
from requests import *
from datetime import datetime
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client as ClientTwilio

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
    auth_token  = "3213ad8991dc85cb5254d856943d384e"
    client = ClientTwilio(account_sid, auth_token)
    for sender in lista_senders:
        message = client.messages \
            .create(
                from_='whatsapp:+16625025249',
                body=f"Hola! Queremos comentarte lo siguiente: Se ha realizado una operación de cambio en PMC. Vendedor: {vendedor} Cliente: {cliente} Tipo: {tipo} Monto: {monto} Cotización: {cotizacion} Fondos USD: Fondos Fondos ARS: Fondos Fecha: {fecha} Saludos!",
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
    monto = string.split(None,3)[1]
    cotizacion = string.split(None,3)[2]
    cliente = string.split(None,3)[3]
    updateSheet(fecha, tipo, vendedor, monto, cotizacion, cliente, "Pilar Mining CO", "Financiera")
    sendTwilio(fecha, tipo, vendedor, monto, cotizacion, cliente)

def ventaCommand(update: Update, context: CallbackContext):
    string = update.message.text
    fecha = datetime.today().strftime('%d-%m-%Y')
    tipo = string.split(None,3)[0][1:]
    vendedor = update.effective_chat.first_name
    monto = string.split(None,3)[1]
    cotizacion = string.split(None,3)[2]
    cliente = string.split(None,3)[3]
    updateSheet(fecha, tipo, vendedor, monto, cotizacion, cliente, "Pilar Mining CO", "Financiera")
    sendTwilio(fecha, tipo, vendedor, monto, cotizacion, cliente)

def updateSheet(fecha, tipo, vendedor, monto, cotizacion, cliente, sheet, worksheet):
    print(f"Fecha: {fecha}, Tipo: {tipo}, Vendedor: {vendedor}, Monto: {monto}, Cotizacion:{cotizacion}, Cliente: {cliente}  ")
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('pilarminingco-c11e8da70b2f.json', scope)
    client = gspread.authorize(creds)
    work_sheet = client.open(sheet)
    sheet_instance = work_sheet.worksheet(worksheet)
    spread = abs((int(getDolarBlue("avg")))-int(cotizacion))
    new_row = (fecha, tipo, vendedor, cliente, monto, cotizacion, int(monto)*int(cotizacion), spread, spread*int(cotizacion),getDolarBlue("buy"),getDolarBlue("sell"))
    sheet_instance.append_row(new_row, value_input_option="USER_ENTERED")
    


dispatcher.add_handler(CommandHandler("start", startCommand))
dispatcher.add_handler(CommandHandler("Compra", compraCommand))
dispatcher.add_handler(CommandHandler("Venta", ventaCommand))

updater.start_polling()