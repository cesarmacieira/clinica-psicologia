import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from textwrap import wrap
from PIL import Image
from reportlab.lib.units import cm
from num2words import num2words
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate

# Função para converter data em extenso
def data_extenso(data):
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    dia = data.day
    mes = meses[data.month - 1]
    ano = data.year
    return f"{dia} de {mes} de {ano}"

# Função para formatar CPF no padrão XXX.XXX.XXX-XX
def formatar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))  # Remove qualquer caractere não numérico
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

# Função para gerar o PDF
def generate_pdf(nome, cpf, valor, data_extensa):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Inserir logo centralizada no topo
    logo = Image.open("Logo clínica.png")
    logo = ImageReader(logo)
    pdf.drawImage(logo, width / 2 - 3.5*cm, height - 4*cm, width=7*cm, height=2*cm, mask='auto')  # Aumentar o espaço entre a logo e o título

    # Título "RECIBO" centralizado, em negrito e tamanho 14
    pdf.setFont("Times-Roman", 16)
    pdf.drawCentredString(width / 2, height - 6*cm, "RECIBO")  # Espaço ajustado entre o título e o parágrafo

    # Inserir marca d'água centralizada no fundo com ajuste para a direita
    marca_dagua = Image.open("Marca dagua 2.png")
    marca_dagua = ImageReader(marca_dagua)
    pdf.saveState()
    pdf.setFillAlpha(0.21)  # Opacidade reduzida para marca d'água
    pdf.drawImage(marca_dagua, width / 2 - 6.3*cm, height / 2 - 5.5*cm, width=13*cm, height=11.5*cm, mask='auto')  # Mover um pouco para a direita
    pdf.restoreState()

    # Formatar o CPF no padrão brasileiro
    cpf_formatado = formatar_cpf(cpf)

    # Formatar o valor no padrão brasileiro
    valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Converter valores
    valor_extenso = num2words(valor, lang='pt_BR', to='currency')
    data_num = data_input.strftime('%d-%m-%Y')
    data_extensa = data_extenso(data_input)

    # Texto do parágrafo, justificado
    pdf.setFont("Times-Roman", 14)
    texto = (f"Recebemos de {nome}, inscrita(o) sob o CPF {cpf_formatado}, a importância de R${valor_formatado} "
             f"({valor_extenso}) referente ao atendimento psicológico realizado no dia {data_num}.")

    # Definir estilo de parágrafo justificado
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleN.alignment = 4  # Código para texto justificado
    styleN.fontSize = 14  # Aumentar o tamanho da fonte
    styleN.leading = 20  # Ajustar o espaçamento entre linhas

    # Criar objeto Paragraph e aplicar a justificação
    paragrafo = Paragraph(texto, styleN)
    
    # Definir a posição do parágrafo no PDF
    width, height = A4
    paragrafo.wrapOn(pdf, width - 6*cm, height)  # Definir largura para justificação
    paragrafo.drawOn(pdf, 3*cm, height - 10*cm)  # Definir posição do texto
    
    # Quebrar o texto para respeitar as margens
    y_position = height - 8.5*cm  # Aumentar o espaço entre o título e o parágrafo

    # Aumentar o espaço entre o parágrafo e "Belo Horizonte"
    y_position -= 5*cm
    # Centralizar data e cidade por extenso
    pdf.drawCentredString(width / 2 + 5, y_position - 5, f"Belo Horizonte, Minas Gerais, {data_extensa}.")

    # Descer o carimbo e linha de assinatura mais abaixo
    assinatura = Image.open("Ass + carimbo.png")
    assinatura = ImageReader(assinatura)
    # Descer o carimbo e aumentar a altura
    pdf.drawImage(assinatura, width / 2 - 4*cm, y_position - 10.7*cm, width=9*cm, height=5*cm, mask='auto')  # Aumentar a altura do carimbo

    # Linha de assinatura mais abaixo
    pdf.line(width / 2 - 4.5*cm, y_position - 10.2*cm, width / 2 + 4.5*cm, y_position - 10.2*cm)  # Linha de assinatura mais abaixo
    pdf.setFont("Times-Roman", 14)
    pdf.drawCentredString(width / 2, y_position - 10.8*cm, "Janine Sonale Lima Viana")
    pdf.drawCentredString(width / 2, y_position - 11.7*cm, "CPF: 054.037.526-84")

    # Inserir rodapé com telefones primeiro e endereço abaixo
    pdf.setFont("Times-Roman", 12)
    pdf.setFillColor(colors.grey)
    rodape_texto_1 = "(31) 9 7555-0104 / (31) 9 8026-8083"
    rodape_texto_2 = "Avenida Barbacena, 600 - 6º andar, sala 615, Santo Agostinho, Belo Horizonte - MG"
    pdf.drawRightString(width - 2.5*cm, 2.5*cm, rodape_texto_1)
    pdf.drawRightString(width - 2.5*cm, 2*cm, rodape_texto_2)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer

# Função para baixar o PDF
def download_pdf(buffer, file_name):
    st.download_button(
        label="Baixar Recibo em PDF",
        data=buffer,
        file_name=file_name,
        mime="application/pdf"
    )

# Interface do Streamlit
st.title('Gerador de Recibo de Atendimento Psicológico')

# Inputs para o recibo
nome = st.text_input('Nome do paciente:')
cpf = st.text_input('CPF do paciente:')
valor = st.number_input('Valor da sessão:', min_value=0.0, step=10.0)
data_input = st.date_input('Data:', format="DD/MM/YYYY")
data_num = data_input.strftime('%d-%m-%Y')

# Se todos os dados estiverem preenchidos, gerar o PDF
if st.button("Gerar Recibo"):
    if nome and cpf and valor and data_input:
        data_extensa = data_extenso(data_input)
        buffer = generate_pdf(nome, cpf, valor, data_extensa)
        download_pdf(buffer, f"recibo_{nome}.pdf")
    else:
        st.warning("Por favor, preencha todos os campos para gerar o recibo.")
