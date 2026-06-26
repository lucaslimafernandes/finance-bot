import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)

from asgiref.sync import sync_to_async

from accounts.models import User
from finances.models import Transaction

from services.ai_service import AIService
from services.finance_service import FinanceService


# ==========================
# USER
# ==========================

@sync_to_async
def create_user(telegram_user):

    return User.objects.get_or_create(
        telegram_id=telegram_user.id,
        defaults={
            "name": telegram_user.first_name,
            "username": telegram_user.username
        }
    )


# ==========================
# COMMANDS
# ==========================

def get_main_menu():

    keyboard = [

        ["📊 Resumo", "💰 Saldo"],

        ["💳 Crédito", "📅 Parcelas"],

        ["📋 Gastos", "❓ Ajuda"]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )


async def start(update, context):

    telegram_user = update.effective_user

    await create_user(
        telegram_user
    )

    await menu(
        update,
        context
    )

async def menu(update, context):

    text = """
💰 Finance Bot

Envie despesas normalmente:

Mercado 50 cred
Uber 25 pix
Recebi salário 5000

Ou utilize os botões abaixo 👇
"""

    await update.message.reply_text(
        text,
        reply_markup=get_main_menu()
    )


async def ajuda(update,context):

    text="""
Exemplos:

Mercado 50 pix

Gasolina 150 cred

Tênis 300 parc 10x

Recebi salário 5000

Freelance 1200
"""

    await update.message.reply_text(
        text
    )


# ==========================
# CONSULTAS
# ==========================

@sync_to_async
def get_last_transactions(
    telegram_id
):

    user=User.objects.get(
        telegram_id=telegram_id
    )

    return list(

        Transaction.objects.filter(
            user=user
        ).order_by(
            "-created_at"
        )[:5]

    )


async def gastos(update,context):

    transactions=await get_last_transactions(
        update.effective_user.id
    )

    if not transactions:

        await update.message.reply_text(
            "Sem registros."
        )

        return


    text="📋 Últimos gastos:\n\n"

    for t in transactions:

        text += (
            f"{t.description} "
            f"- R${t.value}\n"
        )

    await update.message.reply_text(
        text
    )


async def resumo(update,context):

    await update.message.reply_text(
"""
📊 Resumo do mês

Receitas:
R$0

Despesas:
R$0

Saldo:
R$0
"""
    )


async def saldo(update,context):

    await update.message.reply_text(
        "💰 Saldo: R$0"
    )


async def parcelas(update,context):

    await update.message.reply_text(
        "📅 Parcelas abertas: nenhuma"
    )


async def credito(update,context):

    await update.message.reply_text(
        "💳 Crédito: R$0"
    )


# ==========================
# MENSAGENS LIVRES
# ==========================

async def process_message(
    update,
    context
):


    text=update.message.text

    if text == "📊 Resumo":
        return await resumo(update, context)

    if text == "💰 Saldo":
        return await saldo(update, context)

    if text == "💳 Crédito":
        return await credito(update, context)

    if text == "📅 Parcelas":
        return await parcelas(update, context)

    if text == "📋 Gastos":
        return await gastos(update, context)

    if text == "❓ Ajuda":
        return await ajuda(update, context)

    ai=AIService()

    data=ai.classify_transaction(
        text
    )

    await FinanceService().save_transaction(
        telegram_id=update.effective_user.id,
        data=data
    )

    await update.message.reply_text(
f"""
✅ Registro salvo

Descrição:
{data['description']}

Valor:
R$ {data['value']}

Categoria:
{data['category']}

Pagamento:
{data['payment']}
"""
    )


# ==========================
# MAIN
# ==========================

def main():

    token=os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    app=ApplicationBuilder().token(
        token
    ).build()


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "menu",
            menu
        )
    )

    app.add_handler(
        CommandHandler(
            "ajuda",
            ajuda
        )
    )

    app.add_handler(
        CommandHandler(
            "resumo",
            resumo
        )
    )

    app.add_handler(
        CommandHandler(
            "saldo",
            saldo
        )
    )

    app.add_handler(
        CommandHandler(
            "parcelas",
            parcelas
        )
    )

    app.add_handler(
        CommandHandler(
            "credito",
            credito
        )
    )

    app.add_handler(
        CommandHandler(
            "gastos",
            gastos
        )
    )

    app.add_handler(

        MessageHandler(
            filters.TEXT &
            ~filters.COMMAND,
            process_message
        )

    )

    print(
        "Bot iniciado"
    )

    app.run_polling()


if __name__=="__main__":
    main()