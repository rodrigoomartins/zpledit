import streamlit as st
import requests
import shutil

altura = 19 #milimetros
largura = 73 #milimetros
dpi_y = altura*8
dpi_x = largura*8
percent_y = 100/(dpi_y)
percent_x = 100/(dpi_x)
posicao_x_texto = "Posição X"
posicao_y_texto = "Posição Y"

def ajustar_valor_x(valor_x):
    return round(valor_x*(1/percent_x),1)
def ajustar_valor_y(valor_y):
    return round(valor_y*(1/percent_y))

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

col1, col2, col3, col40 = st.columns(4)
with col1:
    descricao = st.text_input("Descrição:",value="DESCRICAO DESCRICAO DESCRICAO DESCRICAO", placeholder="Digite a descrição...", max_chars=50)
    col4, col5, col6 = st.columns(3)
    with col4:
        tamanho_descricao = st.slider("Tamanho",0,200,18)
    with col5:
        posicao_descricao_x = st.slider(posicao_x_texto,0,100,round(15*percent_x), key="posicao_descricao_x")
        posicao_descricao_x = ajustar_valor_x(posicao_descricao_x)
    with col6:
        posicao_descricao_y = st.slider(posicao_y_texto,0,100,round(10*percent_y), key="posicao_descricao_y")
        posicao_descricao_y = ajustar_valor_y(posicao_descricao_y)
    st.divider()
    cor = st.text_input("Cor:",value="COR COR COR COR", placeholder="Digite a cor...", max_chars=30)
    col7, col8, col9 = st.columns(3)
    with col7:
        tamanho_cor = st.slider("Tamanho",0, 100, 15, key="tamanho_cor")
    with col8:
        posicao_cor_x = st.slider(posicao_x_texto,0,100,round(15*percent_x), key="posicao_cor_x")
        posicao_cor_x = ajustar_valor_x(posicao_cor_x)
    with col9:
        posicao_cor_y = st.slider(posicao_y_texto,0,100,round(31*percent_y), key="posicao_cor_y")
        posicao_cor_y = ajustar_valor_y(posicao_cor_y)
    
with col2:
    tamanho = st.text_input("Tamanho da peça:",value="XGG", placeholder="Digite o tamanho...",max_chars=3)
    col16, col17 = st.columns(2)
    with col16:
        posicao_tamanho_x = st.slider(posicao_x_texto,0,100,34, key="posicao_tamanho_x")
        posicao_tamanho_x = ajustar_valor_x(posicao_tamanho_x)
    with col17:
        posicao_tamanho_y = st.slider(posicao_y_texto,0,100,26, key="posicao_tamanho_y")
        posicao_tamanho_y = ajustar_valor_y(posicao_tamanho_y)
    st.divider()
    referencia = st.text_input("Referência:",value="999999999", placeholder="Digite a referência...", max_chars=9)
    col10, col11, col12 = st.columns(3)
    with col10:
        tamanho_referencia = st.slider("Tamanho",0,100,40, key = "tamanho_referencia")
    with col11:
        posicao_referencia_x = st.slider(posicao_x_texto,0,100,round(15*percent_x), key="posicao_referencia_x")
        posicao_referencia_x = ajustar_valor_x(posicao_referencia_x)
    with col12:
        posicao_referencia_y = st.slider(posicao_y_texto,0,100,round(55*percent_y), key="posicao_referencia_y")
        posicao_referencia_y = ajustar_valor_y(posicao_referencia_y)
    
with col3:
    barcode = st.text_input("Código de barras:",value="0123456789012", placeholder="Digite o código de barras...",max_chars=13)
    col18, col19 = st.columns(2)
    with col18:
        posicao_barcode_x = st.slider(posicao_x_texto,0,100,round(330*percent_x),key="posicao_barcode_x")
        posicao_barcode_x = ajustar_valor_x(posicao_barcode_x)
    with col19:
        posicao_barcode_y = st.slider(posicao_y_texto,0,100,round(40*percent_y),key="posicao_barcode_y")
        posicao_barcode_y = ajustar_valor_y(posicao_barcode_y)
    st.divider()
    msg_inferior = st.text_input("Mensagem (inferior):",value="EM CASO DE TROCA, MANTENHA A ETIQUETA NA PECA", placeholder="Digite uma mensagem...",max_chars=50)
    col30, col31, col32 = st.columns(3)
    with col30:
        tamanho_msg_inferior = st.slider("Tamanho",0,100,15, key = "tamanho_msg_inferior")
    with col31:
        posicao_msg_inferior_x = st.slider(posicao_x_texto,0,100,round(15*percent_x), key="posicao_msg_inferior_x")
        posicao_msg_inferior_x = ajustar_valor_x(posicao_msg_inferior_x)
    with col32:
        posicao_msg_inferior_y = st.slider(posicao_y_texto,0,100,round(128*percent_y), key="posicao_msg_inferior_y")
        posicao_msg_inferior_y = ajustar_valor_y(posicao_msg_inferior_y)


with col40:
    epc = st.text_input("EPC:", placeholder="Digite o EPC...",value="FFFFFFFFFFFFFFFFFFFFFFFF", max_chars=24)
    col13, col14, col15 = st.columns(3)
    with col13:
        tamanho_epc = st.slider("Tamanho",0,100,18, key = "tamanho_epc")
    with col14:
        posicao_epc_x = st.slider(posicao_x_texto,0,100,round(15*percent_x), key="posicao_epc_x")
        posicao_epc_x = ajustar_valor_x(posicao_epc_x)
    with col15:
        posicao_epc_y = st.slider(posicao_y_texto,0,100,round(105*percent_y), key="posicao_epc_y")
        posicao_epc_y = ajustar_valor_y(posicao_epc_y)
    st.divider()

    habilitar_qrcode = st.toggle("QRCode")
    if not habilitar_qrcode:
        qrcode_zpl = "^XZ"
    if habilitar_qrcode:
        opcao_1 = st.radio("",("EPC","Barcode"))
        if opcao_1 == "EPC":
            conteudo_qrcode = epc
        elif opcao_1 == "Barcode":
            conteudo_qrcode = barcode
        col43, col44, col45 = st.columns(3)
        with col43:
            tamanho_qrcode = st.slider("Tamanho",0,10,3,key="tamanho_qrcode")
        with col44:
            posicao_qrcode_x = st.slider(posicao_x_texto,0,100,round(500*percent_x),key="posicao_qrcode_x")
            posicao_qrcode_x = ajustar_valor_x(posicao_qrcode_x)
        with col45:
            posicao_qrcode_y = st.slider(posicao_y_texto,0,100,round(10*percent_y),key="posicao_qrcode_y")
            posicao_qrcode_y = ajustar_valor_y(posicao_qrcode_y)
        qrcode_zpl = (f"""^FO{posicao_qrcode_x},{posicao_qrcode_y}^BQN,2,{tamanho_qrcode},Q,7^FDQR,{conteudo_qrcode}^FS
    ^XZ""")




zpl  = f"""
    ^XA
    ^FO{posicao_descricao_x},{posicao_descricao_y}^A0N,{tamanho_descricao},{tamanho_descricao}^FD{descricao}^FS
    ^FO{posicao_cor_x},{posicao_cor_y}^A0N,{tamanho_cor},{tamanho_cor}^FD{cor}^FS
    ^FO{posicao_referencia_x},{posicao_referencia_y}^A0N,{tamanho_referencia},{tamanho_referencia}^FD{referencia}^FS
    ^FO{posicao_epc_x},{posicao_epc_y}^A0N,{tamanho_epc},{tamanho_epc}^FD{epc}^FS
    ^FO{posicao_msg_inferior_x},{posicao_msg_inferior_y}^A0N,{tamanho_msg_inferior},{tamanho_msg_inferior}^FD{msg_inferior}^FS
    ^FO{posicao_tamanho_x},{posicao_tamanho_y}^GB120,50,2^FS
    ^FO{posicao_tamanho_x+55},{posicao_tamanho_y+6}^ASN^FD{tamanho}^FS
    ^FO{posicao_tamanho_x+5},{posicao_tamanho_y+18}^AN,18,18^FDTAM^FS
    ^FO{posicao_barcode_x},{posicao_barcode_y}^BCN,60,Y,N,N,A^FD{barcode}^FS
    {qrcode_zpl}
    """

# adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
url = f'http://api.labelary.com/v1/printers/8dpmm/labels/{largura / 25.4}x{altura / 25.4}/0/'
files = {'file' : zpl}
#headers = {'Accept' : 'image/png'} # omit this line to get PNG images back
response = requests.post(url, files = files, stream = True)

if response.status_code == 200:
    response.raw.decode_content = True
    with open('label.png', 'wb') as out_file: # change file name for PNG images
        shutil.copyfileobj(response.raw, out_file)
else:
    print('Error: ' + response.text)

st.divider()
col41, col42 = st.columns(2)
with col41:
    st.subheader("ZPL")
    st.code(zpl)
with col42:
    st.subheader("Tag")
    st.image('label.png')
    with open("label.png", "rb") as file:
        st.download_button(
            label="Download",
            data=file,
            file_name="label.png",
            mime="image/png"
        )