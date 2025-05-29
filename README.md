
# 📦 Gerador de KML com base em Polígono e Raio

Este script processa um arquivo `objeto.txt` com dados geoespaciais no formato GeoJSON, gera polígonos circulares baseados em taxas de entrega e salva a interseção desses polígonos com uma área delimitada em um arquivo `.kml`.

## 📂 Estrutura recomendada

```
projeto/
├── script/
│   ├── script.py
│   ├── objeto.txt
├── saida/
│   └── italin-saipos.kml
└── README.md
```

- O script (`script.py`) pode ser colocado em qualquer pasta, mas atualmente ele espera que o `objeto.txt` esteja na **mesma pasta** onde ele está.
- A saída `italin-saipos.kml` será criada automaticamente dentro da pasta `saida/`. Se a pasta não existir, o script a criará automaticamente.

## 📦 Dependências

Antes de executar o script, instale as bibliotecas necessárias com o comando:

```bash
pip install shapely geopandas fiona pyproj simplekml 
```

- shapely: para operações geométricas como criação de polígonos e interseções.

- geopandas: para manipulação de dados geoespaciais no formato GeoJSON.

- fiona: backend usado pelo geopandas para leitura de arquivos geoespaciais.

- pyproj: para transformações de sistemas de coordenadas.

- simplekml: para geração de arquivos .kml.

## 🚀 Como executar

1. Coloque o `objeto.txt` na **mesma pasta** do script.
2. Execute com:

```bash
python script.py
```

3. O arquivo `italin-saipos.kml` será gerado dentro da pasta `saida/`.

## ⚠️ Importante sobre as coordenadas

Na linha do código:

```python
origin_point = (coords[0], coords[1])  # <-------- Se der erro precisa inverter esse 0 e 1 (as vezes a Saipos envia invertido no object)
```

**Atenção!**  
- Algumas vezes, os dados da Saipos vêm com latitude e longitude invertidos.
- Se ao rodar o script der erro na geração dos raios, **tente inverter** para:

```python
origin_point = (coords[1], coords[0])
```