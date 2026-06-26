from groq import Groq
import os
import json
import re


class AIService:

    PAYMENT_MAP = {

        "cc":"credito",
        "cred":"credito",
        "credito":"credito",
        "crédito":"credito",

        "cd":"debito",
        "deb":"debito",
        "debito":"debito",
        "débito":"debito",

        "pix":"pix",

        "din":"dinheiro",
        "cash":"dinheiro",

        "transf":"transferencia"
    }

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv(
                "GROQ_API_KEY"
            )
        )


    def preprocess(self,text):

        text = text.lower()

        words = text.split()

        normalized=[]

        payment=""

        installments=1


        for word in words:

            if word in self.PAYMENT_MAP:

                payment=self.PAYMENT_MAP[word]

                normalized.append(
                    payment
                )

                continue


            installment_match=re.match(
                r"(\d+)x",
                word
            )

            if installment_match:

                installments=int(
                    installment_match.group(1)
                )

                normalized.append(
                    f"parcelado {installments}x"
                )

                continue


            if word in [
                "parc",
                "parcela",
                "parcelado",
                "2x",
                "3x",
                "5x",
                "4x",
                "6x",
                "7x",
                "8x",
                "9x",
                "10x",
                "12x",
            ]:

                normalized.append(
                    "parcelado"
                )

                continue


            normalized.append(word)


        normalized_text=" ".join(
            normalized
        )

        return {
            "text":normalized_text,
            "payment":payment,
            "installments":installments
        }



    def classify_transaction(
        self,
        text
    ):

        preprocessed=self.preprocess(
            text
        )

        prompt=f"""
Você é um extrator financeiro.

Retorne SOMENTE JSON válido.

Formato:

{{
"description":"",
"value":0,
"category":"",
"type":"expense"
}}

Mensagem:

{preprocessed['text']}
"""

        response=self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ]
        )

        content = response.choices[0].message.content

        # remove markdown que o LLM pode inventar
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        print("\n===== GROQ =====")
        print(content)
        print("================")

        try:

            match=re.search(
                r"\{.*\}",
                content,
                re.DOTALL
            )

            data=json.loads(
                match.group()
            )

            data["payment"]=(
                preprocessed["payment"]
            )

            data["installments"]=(
                preprocessed["installments"]
            )

            return data

        except Exception as e:

            print(
                f"Erro: {e}"
            )

            return {

                "description":text,
                "value":0,
                "category":"Outros",
                "payment":"pix",
                "type":"expense",
                "installments":1
            }