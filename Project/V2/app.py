from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Configuração do banco de dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:M2157@localhost/grid'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class AgregadoAssuntoRegiao(db.Model):
    __tablename__ = 'AGREGADO_ASSUNTO_REGIAO'
    assunto = db.Column('ASSUNTO', db.String)
    regiao = db.Column('REGIÃO', db.String)
    total = db.Column('TOTAL', db.Integer)
    id = db.Column('id', db.Integer, primary_key=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_regiao = request.args.get('regiao')  # Captura a região selecionada
    selected_assunto = request.args.get('assunto')  # Captura o assunto selecionado

    # Consultar dados da tabela
    base_data = AgregadoAssuntoRegiao.query.all()
    df = pd.DataFrame([(d.assunto, d.regiao, d.total) for d in base_data], columns=['Assunto', 'Região', 'Total'])

    # Obter todos os assuntos e regiões para o formulário
    assuntos = df['Assunto'].unique()
    regioes = df['Região'].unique()

    # Filtrar os dados com base na seleção
    if selected_assunto:
        df_grouped = df[df['Assunto'] == selected_assunto]
        if selected_regiao:
            df_grouped = df_grouped[df_grouped['Região'] == selected_regiao]
        fig_regiao = px.bar(df_grouped, x='Região', y='Total', title=f"Distribuição de {selected_assunto} por Região")
    else:
        if selected_regiao:
            df_grouped = df[df['Região'] == selected_regiao]
            fig_regiao = px.bar(df_grouped, x='Assunto', y='Total', title=f"Distribuição de Assuntos em {selected_regiao}")
        else:
            df_grouped = df.groupby('Região', as_index=False).sum()
            fig_regiao = px.bar(df_grouped, x='Região', y='Total', title="Quantidade de Registro por região")

            # Adicionando os valores ao final das barras
            fig_regiao.update_traces(marker_color='blue', marker_line_width=0, text=df_grouped['Total'], textposition='outside')

            # Definindo a ordem das categorias conforme solicitado
            fig_regiao.update_layout(
                xaxis={'categoryorder':'array', 
                       'categoryarray': ['VISA', 'VE', 'VA', 'REGIÃO 5', 'REGIÃO 4', 'REGIÃO 3', 'REGIÃO 2', 'REGIÃO 1', 'CCZ', 'ATENÇÃO ESPECIALIZADA']}
            )

    fig_regiao.update_layout(xaxis_title=None,
                             yaxis_title=None,
                             showlegend=False)

    graph_html_regiao = pio.to_html(fig_regiao, full_html=False)

    return render_template('index.html', graph_html_regiao=graph_html_regiao, regiao=selected_regiao, assunto=selected_assunto, assuntos=assuntos, regioes=regioes)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
