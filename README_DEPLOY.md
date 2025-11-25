
# 🚀 Deploy do Dashboard no Streamlit Cloud — Instruções Rápidas

## 1) Estrutura necessária
Certifique-se de que seu repositório contenha:


/
├── spotify_dashboard_app.py
├── requirements.txt
├── data/
│   └── spotify_semana2_tratado.csv
└── README.md


## 2) Como publicar no Streamlit Cloud

1. Acesse https://share.streamlit.io  
2. Clique em *New App*  
3. Escolha:
   - Repositório GitHub
   - Branch: main
   - Arquivo principal: spotify_dashboard_app.py
4. Clique em *Deploy*

## 3) Como testar localmente


pip install -r requirements.txt
streamlit run spotify_dashboard_app.py


## 4) Observações
- O dataset deve estar acessível dentro da pasta /data.
- Todos os gráficos usam Plotly e são totalmente interativos.
- A aplicação segue o storytelling completo (EDA + interpretação + insights IA).
