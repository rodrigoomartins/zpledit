import streamlit as st
import requests
import shutil
import datetime
import os
from PIL import Image, ImageFont, ImageDraw

st.set_page_config(page_title="ZPL Edit Manual",page_icon="🖨",layout="wide", initial_sidebar_state="auto")

st.page_link("zpl.py",label="ZPL Edit")


with st.sidebar:
   
    st.subheader("Configurações da etiqueta")
    layout_etiquetas = st.selectbox(
        'Layout predefinidos',
        ('Personalizado','73x20', '45x20', '100x25'),
        key="layout_etiquetas",
    )
    tamanhos_predefinidos = {
        "Personalizado": (1,1),
        "73x20": (73,20),
        "45x20": (45,20),
        "100x25": (100,25),
    }
    
    #largura, altura = tamanhos_predefinidos[layout_etiquetas]

    if layout_etiquetas == "Personalizado":
        largura = st.number_input("Largura da etiqueta:",1,1000,73,key="largura")
        altura = st.number_input("Altura da etiqueta:",1,1000,20,key="altura")
    if layout_etiquetas != "Personalizado":
        largura, altura = tamanhos_predefinidos[layout_etiquetas]
    

    st.divider()
    dpi = st.select_slider(
        'DPI:',
        options=[6,8,12,24],
        value=8,
    )

dpi_y = altura*dpi
dpi_x = largura*dpi
percent_y = 100/(dpi_y)
percent_x = 100/(dpi_x)
posicao_x_texto = "Posição X"
posicao_y_texto = "Posição Y"


def converter_imagem_zpl(imagem):
    url = "http://api.labelary.com/v1/graphics"
    files = {"file": (imagem.name, imagem.read(), imagem.type)}
    headers = {"Accept": "application/zpl"}
    response = requests.post(url, files=files, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Erro ao converter imagem: {response.status.code}")
        return None

st.title("ZPL Edit - Manual")

col1, col2 = st.columns([1,1])
with col1:
    zpl_code = st.text_area("Insira o código ZPL:", value="""^XA

^RFW,H^FD{epc}^FS

^FO257.0,54^GB20,3,3^FS
^FO257.0,54^GB3,40,3^FS
^FO257.0,94^GB40,3,3^FS
^FO297.0,79.5^GB3,17,3^FS
^FO262.0,79^A0N,14,17^FDRFID^FS
^FO282.0,50^GC25,25,B^FS
^FO280.0,52^GC25,25,W^FS
^FO285.0,57^GC15,15,B^FS
^FO283.0,59^GC15,15,W^FS
^FO287.0,64^GC6,5,B^FS

^FO17.5,13,^A0N,18^FD{descricao}^FS
^FO17.5,34^A0N,15,15^FD{cor}^FS
^FO362.1,29^A0N,12,12^FDREFERENCIA:^FS
^FO362.1,45^A0N,30,30^FD{referencia}^FS
^FO17.5,51^GB115.0,50.0,2^FS
^FO22.5,69^A0N,18,18^FDTAM:^FS
^FO72.5,61^A0N,38.0,33.0^FD{tamanho}^FS
^BY2^FO367.9,77^BEN,45,Y,N^FD{barcode}^FS
^FO17.5,112^AC,8,10^FD{epc}^FS
^FO17.5,136^A0N,18,18^FDTROCAR ATE 30 DIAS C/ ETIQUETA^FS

^XZ""",
    height=600, key="insert_zpl_code")
    
    col3, col4 = st.columns(2)
    with col3:
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        file_name = f"zpl_code_{timestamp}.zpl"
        st.download_button(
            label="Download ZPL",
            data=zpl_code,
            file_name=file_name,
            mime="text/plain"
        )


url = f'http://api.labelary.com/v1/printers/{dpi}dpmm/labels/{largura / 25.4}x{altura / 25.4}/0/'
files = {'file' : zpl_code}
with st.spinner('Gerando Preview...'):
    response = requests.post(url, files = files, stream = True)

file_name_label = f"label_manual.png"
imagem_branca = Image.new("RGB", (int(25.4*largura),int(25.4*altura)),(255,255,255))
fonte = ImageFont.truetype("fonts/PTMono-Regular.ttf", 100)
texto = f"<Imagem não gerada>\n\n<Revise o código ZPL>"
marca_dagua = Image.new("RGBA", imagem_branca.size, (0, 0, 0, 0))
desenhador = ImageDraw.Draw(marca_dagua)
desenhador.text((largura*(largura*0.01), altura*(altura*0.1)), texto, font=fonte, fill=(128, 128, 128), align="left")
imagem_branca.paste(marca_dagua, (0, 0), mask=marca_dagua)

if response.status_code == 200:
    response.raw.decode_content = True
    with open(file_name_label, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    with col2:
        st.text("Preview")
        st.caption(f"{largura} x {altura} (mm)")
        st.image(file_name_label)
        with open(file_name_label, "rb") as file:
            st.download_button(
                label="Download",
                data=file,
                file_name=file_name_label,
                mime="image/png",
                type='primary'
            )
        st.markdown(f"<h3 style='text-align: center; background: yellow; color: black'>⚠ Revise o código com atenção ⚠</h3><br><br>", unsafe_allow_html=True)
        st.warning("Nossos desenvolvedores ainda não conseguem avisar se você esquecer uma , ou um ^ em um comando!")
        st.link_button("Consultar documentação","https://www.zebra.com/content/dam/zebra_new_ia/en-us/manuals/printers/common/programming/zpl-zbi2-pm-en-pg.pdf")
else:
    st.error(response.text)
    with col2:
        st.text("Preview")
        st.caption(f"{largura} x {altura} (mm)")
        st.empty()
        st.image(imagem_branca)
