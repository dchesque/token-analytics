# 🎨 Agente: Interface CLI

## 📋 Objetivo
Criar interface de linha de comando moderna, intuitiva e visualmente atrativa para o Crypto Analyzer.

## 🎯 Responsabilidades

### **1. Interface de Linha de Comando**

#### **Modos de Operação**
```python
# Modo direto - análise única
python src/main.py bitcoin

# Modo comparativo - múltiplos tokens
python src/main.py --compare bitcoin ethereum cardano

# Modo batch - lista de arquivo
python src/main.py --batch tokens.txt

# Modo interativo
python src/main.py
```

#### **Argumentos Suportados**
```python
import argparse

parser = argparse.ArgumentParser(description='Crypto Analyzer - Análise de tokens crypto')
parser.add_argument('tokens', nargs='*', help='Tokens para analisar')
parser.add_argument('--compare', action='store_true', help='Modo comparativo')
parser.add_argument('--batch', type=str, help='Arquivo com lista de tokens')
parser.add_argument('--detailed', action='store_true', help='Análise detalhada')
parser.add_argument('--save-report', action='store_true', help='Salvar relatório')
parser.add_argument('--format', choices=['table', 'panel', 'json'], default='panel')
```

### **2. Interface Visual Rica**

#### **Componentes Rich**
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.align import Align
from rich.text import Text

console = Console()
```

#### **Exibição de Classificações**
```python
def display_token_analysis(result):
    # Cores por classificação
    classification_colors = {
        'MAJOR': 'bright_yellow',
        'LARGE CAP': 'bright_blue',
        'MID CAP': 'blue',
        'SMALL CAP': 'cyan',
        'MICRO CAP': 'magenta',
        'NANO CAP': 'red',
        'MEME COIN': 'yellow',
        'STABLECOIN': 'green',
        'LAYER 2': 'bright_cyan',
        'DEFI': 'bright_magenta'
    }
    
    classification = result['classification_info']
    color = classification_colors.get(classification['classification'], 'white')
    
    # Panel principal com classificação
    panel_content = f"""
{classification['emoji']} [bold {color}]{classification['classification']}[/bold {color}]
📝 {classification['description']}
⚖️ Risco: {classification['risk_level']}
📊 Score: {result['score']}/10
🏆 Rank: #{result.get('market_cap_rank', 'N/A')}

💰 Market Cap: ${result['market_cap']/1e9:.1f}B
📈 Preço: ${result['price']:,.2f}
"""
    
    if classification['classification'] == 'MAJOR':
        if major_metrics := classification.get('major_metrics'):
            panel_content += f"\n🔑 MÉTRICAS PRINCIPAIS:\n"
            for metric in major_metrics['key_metrics']:
                panel_content += f"• {metric}\n"
    
    return Panel(
        panel_content,
        title=f"📊 {result['token_name']} ({result['token']})",
        border_style=color
    )
```

#### **Tabela Comparativa**
```python
def display_comparison_table(results):
    table = Table(title="📊 Comparação de Tokens")
    
    # Colunas
    table.add_column("Token", style="cyan", no_wrap=True)
    table.add_column("Classificação", style="magenta")
    table.add_column("Score", justify="right", style="green")
    table.add_column("Market Cap", justify="right", style="blue")
    table.add_column("Rank", justify="right", style="yellow")
    table.add_column("Risco", style="red")
    
    # Ordenar por score
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
    
    for result in sorted_results:
        classification = result['classification_info']
        
        table.add_row(
            f"{classification['emoji']} {result['token']}",
            classification['classification'],
            f"{result['score']}/10",
            f"${result['market_cap']/1e9:.1f}B",
            f"#{result.get('market_cap_rank', 'N/A')}",
            classification['risk_level']
        )
    
    return table
```

### **3. Indicadores de Progresso**

#### **Loading Animado**
```python
def analyze_with_progress(token_query):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task(f"🔍 Analisando {token_query.upper()}...", total=None)
        
        # Executar análise
        analyzer = CryptoAnalyzer()
        result = analyzer.analyze(token_query)
        
        progress.update(task, description=f"✅ {token_query.upper()} analisado!")
        
    return result
```

#### **Progresso de Batch**
```python
def analyze_batch(tokens):
    results = []
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        main_task = progress.add_task(f"🔄 Analisando {len(tokens)} tokens...", total=len(tokens))
        
        for i, token in enumerate(tokens):
            progress.update(main_task, description=f"🔍 Analisando {token.upper()} ({i+1}/{len(tokens)})")
            
            try:
                result = analyzer.analyze(token)
                if result:
                    results.append(result)
                progress.advance(main_task)
                
                # Delay entre análises
                if i < len(tokens) - 1:
                    time.sleep(3)
                    
            except Exception as e:
                console.print(f"❌ Erro ao analisar {token}: {e}")
    
    return results
```

### **4. Modo Interativo**

#### **Menu Principal**
```python
def interactive_mode():
    console.print(Panel(
        "[bold cyan]🚀 Crypto Analyzer[/bold cyan]\n"
        "Sistema de análise de tokens crypto",
        title="Bem-vindo",
        border_style="cyan"
    ))
    
    while True:
        console.print("\n[bold]Opções:[/bold]")
        console.print("1. 🔍 Analisar token")
        console.print("2. ⚖️ Comparar tokens")
        console.print("3. 📊 Análise em lote")
        console.print("4. ❓ Ajuda")
        console.print("5. 🚪 Sair")
        
        choice = console.input("\n[bold cyan]Escolha uma opção (1-5): [/bold cyan]")
        
        if choice == "1":
            single_token_mode()
        elif choice == "2":
            comparison_mode()
        elif choice == "3":
            batch_mode()
        elif choice == "4":
            show_help()
        elif choice == "5":
            console.print("[green]👋 Até logo![/green]")
            break
        else:
            console.print("[red]❌ Opção inválida![/red]")
```

### **5. Sistema de Relatórios**

#### **Relatório JSON**
```python
def save_json_report(result, filename):
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "analysis": result,
        "metadata": {
            "analyzer_version": "2024.1",
            "apis_used": ["CoinGecko", "Fear & Greed Index"],
            "disclaimer": "Não constitui consultoria financeira"
        }
    }
    
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/{filename}", 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
```

#### **Relatório Markdown**
```python
def save_markdown_report(result, filename):
    template = f"""
# 📊 Análise: {result['token_name']} ({result['token']})

## 🎯 Classificação
- **Tipo**: {result['classification_info']['classification']} {result['classification_info']['emoji']}
- **Descrição**: {result['classification_info']['description']}
- **Nível de Risco**: {result['classification_info']['risk_level']}
- **Score**: {result['score']}/10

## 💰 Métricas Financeiras
- **Preço**: ${result['price']:,.2f}
- **Market Cap**: ${result['market_cap']/1e9:.1f}B
- **Volume 24h**: ${result['volume']/1e6:.1f}M
- **Ranking**: #{result.get('market_cap_rank', 'N/A')}

## 📈 Performance
- **24h**: {result.get('price_change_24h', 0):+.1f}%
- **7d**: {result.get('price_change_7d', 0):+.1f}%
- **30d**: {result.get('price_change_30d', 0):+.1f}%

## 💪 Pontos Fortes
{chr(10).join([f"- {strength}" for strength in result.get('strengths', [])])}

## ⚠️ Pontos de Atenção
{chr(10).join([f"- {weakness}" for weakness in result.get('weaknesses', [])])}

## 🌡️ Contexto de Mercado
- **Fear & Greed Index**: {result['market_context']['fear_greed_index']}/100
- **Sentimento**: {result['market_context']['market_sentiment']}

---
*Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*
*⚠️ Não constitui consultoria financeira. Faça sua própria pesquisa.*
"""
    
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/{filename}", 'w', encoding='utf-8') as f:
        f.write(template)
```

## 🔧 Implementação Principal

### **Arquivo main.py**
```python
#!/usr/bin/env python3
"""
Crypto Analyzer - Interface CLI
Sistema de análise de tokens crypto com terminologia correta
"""

import sys
import os
import argparse
import json
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.align import Align

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent))

from analyzer import CryptoAnalyzer

console = Console()

def main():
    parser = argparse.ArgumentParser(description='Crypto Analyzer - Análise de tokens crypto')
    parser.add_argument('tokens', nargs='*', help='Tokens para analisar')
    parser.add_argument('--compare', action='store_true', help='Modo comparativo')
    parser.add_argument('--batch', type=str, help='Arquivo com lista de tokens')
    parser.add_argument('--detailed', action='store_true', help='Análise detalhada')
    parser.add_argument('--save-report', action='store_true', help='Salvar relatório')
    
    args = parser.parse_args()
    
    # Exibir header
    display_header()
    
    if args.batch:
        batch_analysis(args.batch, args.save_report)
    elif args.compare and args.tokens:
        comparison_analysis(args.tokens, args.save_report)
    elif args.tokens:
        for token in args.tokens:
            single_analysis(token, args.detailed, args.save_report)
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
```

## ⚠️ Considerações Importantes

### **UX/UI Guidelines**
- Interface intuitiva e auto-explicativa
- Cores consistentes para cada tipo de classificação
- Feedback visual claro para todas as ações
- Tratamento gracioso de erros

### **Performance**
- Loading indicators para operações demoradas
- Progress bars para análises em batch
- Cache de resultados quando apropriado
- Otimização de renderização

### **Acessibilidade**
- Suporte a diferentes tamanhos de terminal
- Texto alternativo para elementos visuais
- Contraste adequado para legibilidade
- Compatibilidade com screen readers

### **Responsabilidade**
- Disclaimers claros em todas as telas
- Avisos sobre riscos de investimento
- Informações sobre limitações do sistema
- Links para recursos educacionais

---

**🎯 Objetivo Final:** Interface CLI moderna e intuitiva que torna a análise crypto acessível e visualmente atrativa