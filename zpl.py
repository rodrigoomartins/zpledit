import streamlit as st
import requests
import shutil

st.set_page_config(page_title="ZPL Edit", page_icon="🖨", layout="wide", initial_sidebar_state="auto")
st.page_link("pages/zpl_manual.py", label="ZPL Edit - Manual")

# Fontes padrão e opções de orientação
fontes_disponiveis = [
    "0 (Escalável)", "A", "B", "C", "D", "E (OCR-B)", "F", "G", "H (OCR-A)",
    "P", "Q", "R", "S", "T", "U", "V"
]
orientacoes = {"Normal (N)": "N", "90° (R)": "R", "180° (I)": "I", "270° (B)": "B"}
def converter_imagem_zpl(imagem):
    url = "http://api.labelary.com/v1/graphics"
    files = {"file": (imagem.name, imagem.read(), imagem.type)}
    headers = {"Accept": "application/zpl"}
    response = requests.post(url, files=files, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Erro ao converter imagem: {response.status_code}")
        return None

def remover_parametros_zpl(codigo_zpl):
    pos_inicio = codigo_zpl.find("^GFA")
    pos_fim = codigo_zpl.rfind("^XZ")
    return codigo_zpl[pos_inicio:pos_fim].strip()

with st.sidebar:
    st.subheader("Configurações da etiqueta")
    layout_etiquetas = st.selectbox('Layout predefinidos', ('Personalizado', '73x20', '45x20', '100x25'))
    tamanhos_predefinidos = {
        "Personalizado": (1, 1),
        "73x20": (73, 20),
        "45x20": (45, 20),
        "100x25": (100, 25),
    }
    largura, altura = tamanhos_predefinidos[layout_etiquetas]
    if layout_etiquetas == "Personalizado":
        largura = st.number_input("Largura da etiqueta (mm):", 1, 500, 73)
        altura = st.number_input("Altura da etiqueta (mm):", 1, 500, 20)
    dpi = st.select_slider('DPI:', options=[6, 8, 12, 24], value=8)
    layout_nome = st.text_input("Nome do layout ZPL:", placeholder="Ex: LAYOUT1")

dpi_y = altura * dpi
dpi_x = largura * dpi
percent_y = 100 / dpi_y
percent_x = 100 / dpi_x

def ajustar_valor_x(valor_x): return round(valor_x * (1 / percent_x), 1)
def ajustar_valor_y(valor_y): return round(valor_y * (1 / percent_y))

st.title("ZPL Edit")
st.text("Campos personalizados (^FN)")

num_campos = st.number_input("Quantos campos deseja adicionar?", min_value=1, max_value=20, value=1, step=1)

campos_preview = ""
campos_export = ""
proximo_fn = 1
epc_fn = None
fn_legenda = []  # <<<<< NOVO: armazena (FN, etiqueta/valor)
fn_map = {}
col_geral1, col_geral2 = st.columns([3,2])
with col_geral1:
    # Campos dinâmicos
    for i in range(1, num_campos + 1):
        with st.expander(f"Campo {i}"):
            nome = st.text_input(f"Nome do campo {i}", key=f"nome_{i}")
            col_1, col_2, col_3, col_4, col_5, col_6 = st.columns(6)
            with col_1:
                fonte = st.selectbox("Fonte", fontes_disponiveis, key=f"fonte_{i}")
            with col_2:
                orientacao = st.selectbox("Orientação", orientacoes.keys(), key=f"orientacao_{i}")
            with col_3:
                largura_fonte = st.number_input("Largura (dots)", 1, 200, 30, key=f"largura_{i}")
            with col_4:
                altura_fonte = st.number_input("Altura (dots)", 1, 200, 30, key=f"altura_{i}")
            with col_5:
                pos_x = st.slider("Posição X (%)", 0, 100, 10, key=f"x_{i}")
                pos_x = ajustar_valor_x(pos_x)
            with col_6:
                pos_y = st.slider("Posição Y (%)", 0, 100, 10, key=f"y_{i}")
                pos_y = ajustar_valor_y(pos_y)
            cod_fonte = fonte.split()[0] + orientacoes[orientacao]
            campos_preview += f"^FO{pos_x},{pos_y}^A{cod_fonte},{altura_fonte},{largura_fonte}^FD{nome}^FS\n"
            campos_export += f"^FO{pos_x},{pos_y}^A{cod_fonte},{altura_fonte},{largura_fonte}^FN{proximo_fn}^FS\n"
            # <<<<< NOVO: legenda para campos personalizados (usa o nome digitado)
            fn_legenda.append((proximo_fn, nome if nome else f"Campo {i}"))
            proximo_fn += 1
    st.divider()
    st.caption("Campos predefinidios")
    # Campo TAMANHO
    with st.expander("Tamanho da peça"):
        input_tamanho = st.text_input("Valor (ex: G, GG, P...)", placeholder="Digite o tamanho...", max_chars=4)
        col_tamanho1, col_tamanho2, col_tamanho3, col_tamanho4 = st.columns(4)
        with col_tamanho1:
            fonte_valor = st.selectbox("Fonte para valor", fontes_disponiveis, key="fonte_valor")
            fonte_tag = st.selectbox("Fonte para 'TAM:'", fontes_disponiveis, key="fonte_tag")
        with col_tamanho2:
            orientacao_valor = st.selectbox("Orientação do valor", orientacoes.keys(), key="orientacao_valor")
            orientacao_tag = st.selectbox("Orientação TAM:", orientacoes.keys(), key="orientacao_tag")
        with col_tamanho3:
            altura_valor = st.number_input("Altura valor", 1, 1000, 38, key="tam_valor")
            altura_tag = st.number_input("Altura TAM:", 1, 1000, 18, key="tam_tag")
        with col_tamanho4:
            largura_valor = st.number_input("Largura valor", 1, 1000, 38, key="larg_valor")
            largura_tag = st.number_input("Largura TAM:", 1, 1000, 18, key="larg_tag")
        
        col1, col2 = st.columns(2)
        with col1:
            pos_x_tam = st.slider("Posição X", 0, 100, 34, key="posicao_tamanho_x")
            pos_x_tam = ajustar_valor_x(pos_x_tam)
        with col2:
            pos_y_tam = st.slider("Posição Y", 0, 100, 26, key="posicao_tamanho_y")
            pos_y_tam = ajustar_valor_y(pos_y_tam)

    if input_tamanho:
        cod_valor = fonte_valor.split()[0] + orientacoes[orientacao_valor]
        cod_tag = fonte_tag.split()[0] + orientacoes[orientacao_tag]
        campos_preview += f"""
^FO{pos_x_tam},{pos_y_tam}^GB115,50,2^FS
^FO{pos_x_tam+55},{pos_y_tam+10}^A{cod_valor},{altura_valor},{largura_valor}^FD{input_tamanho}^FS
^FO{pos_x_tam+5},{pos_y_tam+18}^A{cod_tag},{altura_tag},{largura_tag}^FDTAM:^FS
"""
        campos_export += f"""
^FO{pos_x_tam},{pos_y_tam}^GB115,50,2^FS
^FO{pos_x_tam+55},{pos_y_tam+10}^A{cod_valor},{altura_valor},{largura_valor}^FN{proximo_fn}^FS
^FO{pos_x_tam+5},{pos_y_tam+18}^A{cod_tag},{altura_tag},{largura_tag}^FDTAM:^FS
"""
        # <<<<< NOVO: legenda para Tamanho (usa o valor digitado)
        fn_legenda.append((proximo_fn, f"Tamanho: {input_tamanho}"))
        proximo_fn += 1

    # Campo Código de Barras
    with st.expander("Código de Barras"):
        tipo_barcode = st.selectbox('Tipo de código de barras', ('EAN-13', 'Code 128 (sem dígito verificador)'))
        input_barcode = st.text_input("Código:", placeholder="Digite o código...", max_chars=50, key="input_barcode")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            altura_barcode = st.slider("Altura", 1, 500, 50, key="altura_barcode")
        with col2:
            largura_barcode = st.slider("Largura", 1, 10, key="largura_barcode")
        with col3:
            pos_x_barcode = st.slider("Posição X", 0, 100, 70, key="posicao_barcode_x")
            pos_x_barcode = ajustar_valor_x(pos_x_barcode)
        with col4:
            pos_y_barcode = st.slider("Posição Y", 0, 100, 40, key="posicao_barcode_y")
            pos_y_barcode = ajustar_valor_y(pos_y_barcode)

    if input_barcode:
        tipo_zpl = "^BEN" if tipo_barcode == 'EAN-13' else "^BCN"
        campos_preview += f"^BY{largura_barcode}^FO{pos_x_barcode},{pos_y_barcode}{tipo_zpl},{altura_barcode},Y,N^FD{input_barcode}^FS\n"
        campos_export += f"^BY{largura_barcode}^FO{pos_x_barcode},{pos_y_barcode}{tipo_zpl},{altura_barcode},Y,N^FN{proximo_fn}^FS\n"
        # <<<<< NOVO: legenda para Código de Barras (usa o código digitado)
        fn_legenda.append((proximo_fn, f"Código de Barras: {input_barcode}"))
        proximo_fn += 1

    # EPC
    with st.expander("EPC"):
        input_epc = st.text_input("EPC:", placeholder="Digite o EPC...", max_chars=24, key="input_epc")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fonte_epc = st.selectbox("Fonte EPC", fontes_disponiveis, key="fonte_epc")
        with col2:
            orientacao_epc = st.selectbox("Orientação EPC", orientacoes.keys(), key="orientacao_epc")
        with col3:
            altura_epc = st.number_input("Altura", 1, 1000, 30, key="altura_epc")
        with col4:
            largura_epc = st.number_input("Largura", 1, 1000, 30, key="largura_epc")
        col1, col2 = st.columns(2)
        with col1:
            pos_x_epc = st.slider("Posição X", 0, 100, 15, key="posicao_epc_x")
            pos_x_epc = ajustar_valor_x(pos_x_epc)
        with col2:
            pos_y_epc = st.slider("Posição Y", 0, 100, 80, key="posicao_epc_y")
            pos_y_epc = ajustar_valor_y(pos_y_epc)

    if input_epc:
        cod_fonte_epc = fonte_epc.split()[0] + orientacoes[orientacao_epc]
        # Preview mostra o EPC digitado (visual)
        campos_preview += f"^FO{pos_x_epc},{pos_y_epc}^A{cod_fonte_epc},{altura_epc},{largura_epc}^FD{input_epc}^FS\n"

        # Export usa ^FN (sem ^FD aqui!)
        campos_export += f"^FO{pos_x_epc},{pos_y_epc}^A{cod_fonte_epc},{altura_epc},{largura_epc}^FN{proximo_fn}^FS\n"

        # guarda o FN do EPC para inserir o ^RFW uma única vez no início do ZPL final
        epc_fn = proximo_fn
        # <<<<< NOVO: legenda para EPC (usa o EPC digitado)
        fn_legenda.append((proximo_fn, f"EPC: {input_epc}"))
        proximo_fn += 1

    # Logo RFID com escala proporcional
    with st.expander("Logo RFID"):
        habilitar_logo_rfid = st.toggle("Habilitar logo", value=False, key="habilitar_logo_rfid")
        col1, col2, col3 = st.columns(3)

        if not habilitar_logo_rfid:
            with col1:
                st.slider("Posição X (%)", 0, 100, 50, disabled=True, key="posicao_logo_rfid_x")
            with col2:
                st.slider("Posição Y (%)", 0, 100, 50, disabled=True, key="posicao_logo_rfid_y")
            with col3:
                st.slider("Escala", 1, 10, 1, disabled=True, key="escala_logo_rfid")
        else:
            with col1:
                pos_x_logo = st.slider("Posição X (%)", 0, 100, 50, key="posicao_logo_rfid_x")
                pos_x_logo = ajustar_valor_x(pos_x_logo)
            with col2:
                pos_y_logo = st.slider("Posição Y (%)", 0, 100, 50, key="posicao_logo_rfid_y")
                pos_y_logo = ajustar_valor_y(pos_y_logo)
            with col3:
                escala_logo = st.slider("Escala", 1, 10, 1, key="escala_logo_rfid")

            esc = escala_logo
            logo_rfid = f"""^FO{pos_x_logo},{pos_y_logo}^GB{20*esc},{3*esc},{3*esc}^FS
^FO{pos_x_logo},{pos_y_logo}^GB{3*esc},{40*esc},{3*esc}^FS
^FO{pos_x_logo},{pos_y_logo + 40*esc}^GB{40*esc},{3*esc},{3*esc}^FS
^FO{pos_x_logo + 40*esc},{pos_y_logo + 26*esc}^GB{3*esc},{17*esc},{3*esc}^FS
^FO{pos_x_logo + 5*esc},{pos_y_logo + 25*esc}^A0N,{14*esc},{17*esc}^FDRFID^FS
^FO{pos_x_logo + 25*esc},{pos_y_logo - 4*esc}^GC{25*esc},{25*esc},B^FS
^FO{pos_x_logo + 23*esc},{pos_y_logo - 2*esc}^GC{25*esc},{25*esc},W^FS
^FO{pos_x_logo + 28*esc},{pos_y_logo + 3*esc}^GC{15*esc},{15*esc},B^FS
^FO{pos_x_logo + 26*esc},{pos_y_logo + 5*esc}^GC{15*esc},{15*esc},W^FS
^FO{pos_x_logo + 30*esc},{pos_y_logo + 10*esc}^GC{6*esc},{5*esc},B^FS
"""
            campos_preview += logo_rfid
            campos_export += logo_rfid
    # IMAGEM
    with st.expander("Inserir imagem"):
        imagem_file = st.file_uploader("Selecione uma imagem (formato PNG):", type=['png'])
        codigo_zpl_imagem = ""
        if imagem_file is not None:
            zpl_convertido = converter_imagem_zpl(imagem_file)
            if zpl_convertido:
                codigo_zpl_imagem = remover_parametros_zpl(zpl_convertido)
                st.success("Imagem convertida com sucesso!", icon="✅")
                col_img1, col_img2 = st.columns(2)
                with col_img1:
                    pos_x_img = st.slider("Posição X (%)", 0, 100, 10, key="posicao_imagem_x")
                    pos_x_img = ajustar_valor_x(pos_x_img)
                with col_img2:
                    pos_y_img = st.slider("Posição Y (%)", 0, 100, 10, key="posicao_imagem_y")
                    pos_y_img = ajustar_valor_y(pos_y_img)

                codigo_zpl_imagem = f"^FO{pos_x_img},{pos_y_img}^XGIMAGEM.GRF,1,1^FS\n{codigo_zpl_imagem}"
            else:
                codigo_zpl_imagem = ""

with col_geral2:
    # Monta os ZPLs
    zpl_preview = f"^XA\n^LH0,0\n"
    if codigo_zpl_imagem:
        zpl_preview += f"{codigo_zpl_imagem}\n"
    zpl_preview += f"{campos_preview}^XZ"


    # Reorganiza o ^RFW se EPC estiver presente
    zpl_export = f"^XA\n^LH0,0\n^DFE:{layout_nome}.ZPL^FS\n"

    # Insere o ^RFW com o ^FN do EPC (apenas 1x)
    if epc_fn is not None:
        zpl_export += f"^RFW,H^FN{epc_fn}^FS\n"
    if codigo_zpl_imagem:
        zpl_export += f"{codigo_zpl_imagem}\n"
    zpl_export += f"{campos_export}^JZN\n^XZ"


    # Preview com Labelary
    url = f'http://api.labelary.com/v1/printers/{dpi}dpmm/labels/{largura / 25.4}x{altura / 25.4}/0/'
    response = requests.post(url, files={'file': zpl_preview}, stream=True)

    if response.status_code == 200:
        response.raw.decode_content = True
        with open("label.png", "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        st.image("label.png", caption=f"Preview: {largura}x{altura} mm @ {dpi}dpmm")
    else:
        st.error("Erro ao gerar a visualização da etiqueta")

    # <<<<< NOVO: legenda de FNs abaixo do preview
    if fn_legenda:
        legenda_txt = "\n".join([f"FN{n}: {label}" for n, label in fn_legenda])
        st.text_area("Legenda de FNs (^FN)", value=legenda_txt, height=120)

    with st.expander("ZPL Preview (visual)"):
        st.code(zpl_preview, language="zpl")

    with st.expander("ZPL Exportação (real com ^FN)"):
        st.code(zpl_export, language="zpl")
        st.download_button("Download ZPL", zpl_export, file_name=f"{layout_nome}.zpl", mime="text/plain")
