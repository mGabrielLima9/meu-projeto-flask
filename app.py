import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Caminho relativo para o arquivo JSON, com base na localização do arquivo app.py
json_path = os.path.join(os.path.dirname(__file__), 'retencao.json')
with open(json_path, encoding='utf-8') as f:
    cnae_data = json.load(f)

# Resto do seu código aqui...

# Função para obter os dados do CNAE
def get_cnae_info(cnae_code):
    # Normalizar o código CNAE removendo espaços e tornando insensível a maiúsculas
    cnae_code = cnae_code.strip().lower()
    for item in cnae_data:
        # Também normalizamos o código CNAE no JSON para garantir a correspondência
        if item['CNAE'].strip().lower() == cnae_code:
            return {
                "servico": item.get('SERVIÇO', "N/A"),
                "aliquota": item.get('ALIQ.', "N/A") * 100 if item.get('ALIQ.') is not None else "N/A",
                "natureza": item.get('NATUREZA', "N/A"),
                "item_lc116": item.get('ITEM LC 116', "N/A")
            }
    return None

# Rota principal
@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    cnae_info = None
    
    if request.method == 'POST':
        cnae_code = request.form['cnae']
        cnpj = request.form['cnpj']
        
        # Remover os símbolos de moeda e converter o valor da nota para um número
        valor_nota = float(request.form['valor_nota'].replace("R$", "").replace(".", "").replace(",", "."))

        # Obter informações do CNAE
        cnae_info = get_cnae_info(cnae_code)
        
        if cnae_info and isinstance(cnae_info['aliquota'], (int, float)):
            # Calcular retenção usando a alíquota em decimal
            aliquota_decimal = cnae_info['aliquota'] / 100  # Converter porcentagem para decimal
            valor_retencao = valor_nota * aliquota_decimal
            resultado = f"{valor_retencao:.2f}".replace('.', ',')

        else:
            resultado = "Código CNAE não encontrado."

    return render_template('index.html', resultado=resultado, cnae_info=cnae_info, valor_nota=request.form['valor_nota'])

# Rota para obter dados de CNAE em JSON para a interface de pesquisa
@app.route('/get_cnae_data', methods=['GET'])
def get_cnae_data():
    return jsonify([{"CNAE": item['CNAE'], "SERVIÇO": item['SERVIÇO']} for item in cnae_data])

# Rota para obter os detalhes do CNAE selecionado
@app.route('/get_cnae_details', methods=['GET'])
def get_cnae_details():
    cnae_code = request.args.get('cnae')
    cnae_info = get_cnae_info(cnae_code)
    if cnae_info:
        return jsonify(cnae_info)
    return jsonify({"error": "CNAE não encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

