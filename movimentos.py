import datetime
import re

import pandas as pd
import streamlit as st


def formatar_n(linha):
    if linha["rubrica"] == "0018FO":
        try:
            return int(linha["n"])
        except ValueError:
            return pd.NA
    else:
        return ""


def format_val(val):
    if val is None or pd.isna(val):
        return ""

    # Os dados de tempo podem entrar como um de vários formatos diferentes. Então lidamos com:
    # pd.Timedelta
    if isinstance(val, pd.Timedelta):
        componentes = val.components
        horas = 24 * componentes[0] + componentes[1]
        minutos = componentes[2]

        return f"{horas},{minutos:02}"

    # datetime.time
    elif isinstance(val, datetime.time):
        horas = val.hour
        minutos = val.minute

        return f"{horas},{minutos:02}"

    # str
    elif isinstance(val, str):
        tempo = re.fullmatch(r"^(\d{2,3}):(\d{2})(:\d{2})?", val)
        if tempo:
            return f"{tempo.group(1)},{tempo.group(2)}"
        else:
            return pd.NA

    elif isinstance(val, float):
        return f"{val:.2f}".replace(".", ",")

    else:
        return f"{val}"


nome_do_arquivo_de_saida = "movimentos.txt"

arquivo = st.file_uploader("Selecione o arquivo.")

if arquivo is not None:
    df_in = pd.read_excel(arquivo, sheet_name="Plan1")

    df = df_in.melt(
        id_vars=["funcionario", "n"],
        var_name="rubrica",
        value_name="valor",
    ).sort_values("funcionario")

    df = df[["funcionario", "rubrica", "valor", "n"]]

    df["n"] = df.apply(formatar_n, axis=1)

    for n in range(5, 9):
        df[f"{n}"] = df.apply(lambda x: pd.NA)

    df = df.dropna(subset=["valor"])

    df["valor"] = df["valor"].apply(format_val)

    df = df.reset_index(drop=True)

    df.to_csv(nome_do_arquivo_de_saida, index=False, header=False, sep=";")

    df

    with open(nome_do_arquivo_de_saida, "r") as file:
        st.download_button(
            label="Baixe o arquivo.",
            data=file,
            file_name=nome_do_arquivo_de_saida,
        )

