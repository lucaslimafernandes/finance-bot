from asgiref.sync import sync_to_async
from accounts.models import User
from finances.models import Transaction


class FinanceService:

    async def save_transaction(self, telegram_id, data):

        user = await sync_to_async(User.objects.get)(
            telegram_id=telegram_id
        )

        await sync_to_async(Transaction.objects.create)(
            user=user,
            description=data["description"],
            value=data["value"],
            category=data["category"],
            payment_type=data.get("payment", "pix"),
            transaction_type=data["type"]
        )