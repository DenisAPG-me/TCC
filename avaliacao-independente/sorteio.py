# Como rodar, a partir de /mnt/c (WSL):
# /mnt/c/Python314/python.exe '<HOME>\Documents\TCC 2 2026\avaliacao-independente\sorteio.py'
# Usa openpyxl. Escreve somente ao lado deste arquivo; substitui os materiais gerados,
# inclusive as planilhas em branco. Não rode novamente sobre avaliações preenchidas.
"""Sorteio cego às decisões, com random.Random(20261110).
Ordem: embaralhar modelos; sortear resposta por modelo entre US ainda não usadas,
priorizando autores ainda não usados. Ordenação estável por autor e US.
Depois sortear 4 índices por resposta e 1 caso do oráculo por US.
Somente após congelar TODOS os sorteios são abertos julgamentos e notas.
Amostra estratificada com diversidade, não amostragem aleatória simples das 180.
"""
import csv
import io
import json
import random
import re
import shutil
import tokenize
import zipfile
from datetime import datetime
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Protection, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

SAIDA=Path(__file__).resolve().parent
BASE=SAIDA.parent/'pesquisa'/'experimento'
PROIBIDOS=re.compile(r'(?<![a-z])(?:haiku|opus|luna|astra|flash(?:lite)?|gemini|claude|gpt|chatgpt|grok|codex|anthropic|openai|google|origem|duplicado)(?![a-z])',re.I)
CLASSES=['Corresponde','Novo válido','Alucinado','Não verificável']
DECISOES=['Válido','Ajustar','Inválido','Não verificável']
DIMENSOES=['legibilidade','estrutura','assercoes','espera','manutenibilidade']
ANCORAS=[
('C1 — Legibilidade','Nomes opacos; leitura muito difícil.','Nomes e testes compreensíveis; clareza e idioma razoavelmente consistentes.','Nomes precisos, testes concisos e leitura clara, com idioma consistente.'),
('C2 — Estrutura','Sem organização; duplicação generalizada.','Fixtures/helpers e organização suficientes, com alguma repetição.','Fixtures, helpers ou objetos de página e parametrização adequados; pouca duplicação.'),
('C3 — Asserções significativas','Sem verificações úteis ou apenas assert True.','Verifica resultados principais de negócio, com lacunas.','Verifica precisamente resultados de negócio (textos, status, corpo) e condições relevantes.'),
('C4 — Espera/flakiness','Esperas frágeis e forte dependência entre testes.','Sincronização e isolamento aceitáveis, com fragilidades pontuais.','Auto-wait/expect quando aplicável, sem sleep fixo; dados únicos, isolamento e timeouts razoáveis.'),
('C5 — Manutenibilidade','Seletores/configurações frágeis; ordem e dados dificultam manutenção.','Seletores e configurações razoáveis; alguma independência e limpeza.','Seletores robustos quando aplicáveis, constantes, independência de ordem e limpeza de dados.')]
LEIAME="MATERIAL DE VERIFICAÇÃO INDEPENDENTE — USO DO ALUNO\n\nEntregar separadamente a cada avaliador SOMENTE seu avaliador_A.xlsx OU\navaliador_B.xlsx, junto com os cinco arquivos scripts_R1.txt a scripts_R5.txt.\nInstruções, critérios e casos estão no xlsx; scripts numerados, nos arquivos TXT.\nOs avaliadores trabalham\nsozinhos, sem IA, sem executar código e sem discutir decisões entre si.\nTempo previsto: 35–45 minutos. Devolver somente o xlsx preenchido.\n\nNÃO entregar: chave.csv, gabarito_automatico.csv, sorteio.py, analisar.py,\neste LEIAME, resultados de análise nem os diretórios/dados originais.\nAs duas planilhas são cópias idênticas com o nome em branco.\nG01–G20 e O01–O05 são avaliados. Outros O identificam material de apoio.\nA chave registra também índice original (base zero) e ID original, permitindo\nlocalizar no script os nomes de teste originais sem reescrever o código.\n\nREPRODUÇÃO (somente aluno; Python Windows com openpyxl):\nNo WSL, mude para /mnt/c e execute:\n/mnt/c/Python314/python.exe '<HOME>\\Documents\\TCC 2 2026\\avaliacao-independente\\sorteio.py'\nSe chave.csv existir, reutiliza a amostra registrada, sem novo sorteio.\nATENÇÃO: regenera e sobrescreve as planilhas EM BRANCO. Preserve as entregues.\nSomente as 180 linhas do scores_v3.csv entram no sorteio. Semente 20261110.\nModelos embaralhados; uma resposta por modelo, US não repetidas e prioridade\na autores inéditos. Há quatro autores: diversidade máxima de quatro em cinco\nrespostas. Não foram usadas notas ou decisões para selecionar os itens.\n\nANÁLISE (após ambas as entregas, no Windows, dentro desta pasta):\nC:\\Python314\\python.exe analisar.py avaliador_A.xlsx avaliador_B.xlsx gabarito_automatico.csv\nGera analise/concordancia.csv, divergencias.csv, ausencias.csv, excluidos.csv e lacunas_oraculo.csv.\nDuplicados ficaram fora da verificação humana por serem raros (8 casos em 7 das 180 respostas no julgamento automático).\nItens sorteados marcados como duplicados no automático são excluídos apenas\ndas comparações de classe humano × automático e listados em excluidos.csv\ncomo \"duplicado no automático, não avaliado pelos humanos\"; A × B é mantida.\nDiferença média assinada = esquerda menos direita; também é informada a\nmédia absoluta. Kappa de qualidade usa pesos lineares na escala fixa 0–5,\npor dimensão e no conjunto (este último é descritivo, sem independência).\nPercentuais usam somente pares preenchidos; ausências são contabilizadas.\nNão verificável é uma classe explícita, não uma célula ausente.\nKappa fica vazio se indefinido (sem pares ou variação marginal esperada).\nA média humano × automático é a média aritmética de A e B, e fica vazia\nse qualquer indicador necessário for indefinido. Não duplica o tamanho amostral.\nRegistre motivos das divergências após as duas entregas na coluna reservada.\nAs observações originais ficam preservadas; não se inventam motivos.\n\nEXECUÇÃO NESTA SESSÃO:\nA chamada solicitada ao Python Windows foi tentada a partir de /mnt/c, mas\no WSL retornou UtilBindVsockAnyPort: socket failed 1.\nA geração e os testes usaram Python local com o openpyxl da instalação\nWindows em modo somente leitura, sem extensões opcionais de outra plataforma.\nOs comandos Windows acima ficam disponíveis para reprodução no ambiente normal.\n\nLIMITAÇÃO DO GABARITO DO ORÁCULO:\nOs dados fornecidos não incluem decisões automáticas de validade dos itens\ndo oráculo. A presença no oráculo e sua cobertura por casos gerados NÃO são\numa decisão automática de Válido. Portanto, os cinco valores automáticos\nficam vazios, com ausência explicitada. A × B é calculável; A/B × automático\nno oráculo não é calculável sem uma fonte adicional dessas decisões.\nNos casos gerados, mapa_casos é a fonte: valido com correspondência vira\nCorresponde; valido sem correspondência vira Novo válido. Outras classes\nsão traduzidas literalmente quando compatíveis; nunca inferidas dos totais.\n\nÂncoras 0/3/5 operacionalizam a seção C da rubrica, que fornece dimensões e\nníveis gerais, mas não descreve cada célula da tabela. Conteúdos de testes e\ncódigo são preservados no idioma de origem para não alterar o objeto avaliado.\nAs descrições compactas do oráculo não são expandidas com passos inventados.\n\nAmostra pequena: o percentual é o indicador principal e kappa é complementar\ne instável. Maior concordância entre humanos que com o automático pode apontar\nviés, mas não prova sua causa. Não generalizar para as 180 respostas nem alterar\nas notas do experimento. Declarar no TCC que a amostra não exclui possível viés\ndo avaliador automático (família Claude) a favor dos modelos Claude.\n\nNOVO LAYOUT:\nInício, Oráculo, R1, R2, R3, R4, R5. Respostas em amarelo; proteção sem\nsenha contra edição acidental. Os scripts estão nos cinco arquivos TXT em UTF-8,\ncom linhas numeradas; as abas R indicam o arquivo correspondente.\nA correspondência aceita um ID da própria US ou Nenhum; se houver mais\nequivalentes, registre os IDs adicionais na observação. As medidas de\nconcordância dos casos continuam sendo sobre a classe, não sobre os IDs.\nA pergunta opcional fica logo abaixo do oráculo nas abas R, somente na primeira\naba de cada US. Responda em uma linha a condição e o resultado esperado.\nRespostas preenchidas são exportadas em analise/lacunas_oraculo.csv (avaliador\nA/B, US, texto); vazias são omitidas. Uso qualitativo, sem cálculo estatístico.\n"

def ler(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def csv_salvar(nome,linhas,campos):
    with (SAIDA/nome).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=campos);w.writeheader();w.writerows(linhas)
def texto(caso):
    nomes={'titulo':'Título','tipo':'Tipo','criterio':'Critério','criterios':'Critérios','passos':'Passos','esperado':'Resultado esperado','descricao':'Descrição (condição e resultado)','origem':'Origem'}
    def val(k,v):
        if k=='criterios': return (', '.join(f'CA{n}' for n in v)) if v else 'nenhum'
        return json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v
    return '\n'.join(f"{nomes.get(k,k)}: {val(k,v)}" for k,v in caso.items() if k not in ('id','origem'))
def validar_cegamento(texto_entrada):
    achou=PROIBIDOS.search(texto_entrada)
    if achou: raise ValueError(f'Identificação proibida no material: {achou.group()}')
def script_cego(conteudo):
    # Remove apenas comentários identificadores; preserva todo o restante e as linhas.
    linhas=conteudo.splitlines(keepends=True)
    for tok in tokenize.generate_tokens(io.StringIO(conteudo).readline):
        if tok.type==tokenize.COMMENT and PROIBIDOS.search(tok.string):
            n,c=tok.start; fim=tok.end[1]
            linhas[n-1]=linhas[n-1][:c]+linhas[n-1][fim:]
    final=''.join(linhas)
    validar_cegamento(final) # Falha fechada para identificadores fora de comentários.
    return final

def lista(ws,col,inicio,fim,valores):
    dv=DataValidation(type='list',formula1='"'+','.join(valores)+'"',allow_blank=True)
    dv.errorTitle='Valor não permitido';dv.error='Escolha um valor da lista.';dv.showErrorMessage=True;dv.errorStyle='stop'
    ws.add_data_validation(dv);dv.add(f'{col}{inicio}:{col}{fim}')

def montar_planilha(w, escolhidas, stories, oraculo, gm, om):
    """Layout público: só conteúdo dos requisitos/casos e respostas humanas."""
    def aba(nome, widths):
        ws=w.create_sheet(nome)
        for i,width in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=width
        ws.freeze_panes=None;ws.sheet_view.zoomScale=85
        ws.sheet_view.showGridLines=False
        ws.protection.sheet=True
        ws.protection.selectLockedCells=False
        ws.protection.selectUnlockedCells=False
        return ws
    borda=Border(**{lado: Side(style='thin', color='B8C7D1') for lado in ('left','right','top','bottom')})
    def linha(ws, valores, cab=False, altura=None):
        n=ws.max_row+1 if ws['A1'].value is not None else 1
        for i,v in enumerate(valores,1):
            c=ws.cell(n,i,v)
            if isinstance(v,str): c.data_type='s'
            c.border=borda
            c.font=Font(name='Calibri',size=11,bold=cab,color='243746')
            c.alignment=Alignment(vertical='top',wrap_text=True)
            if cab: c.fill=PatternFill('solid',fgColor='DCEAF3')
        if altura is None:
            import textwrap
            altura=max(1,max(sum(max(1,len(textwrap.wrap(t,width=max(8,int(ws.column_dimensions[get_column_letter(i)].width)-3)))) for t in str(v or '').split('\n')) for i,v in enumerate(valores,1)))*15+10
        ws.row_dimensions[n].height=min(120,max(26,altura))
        return n
    def branco(ws):
        ws.cell(ws.max_row+1,1,'')
        ws.row_dimensions[ws.max_row].height=12
    def faixa(ws, texto, cab=False, altura=None):
        import math
        largura=sum(d.width for d in ws.column_dimensions.values())-4
        if cab and ws['A1'].value is not None: branco(ws)
        altura=15*sum(max(1,math.ceil(len(t)/largura)) for t in texto.split('\n'))+10
        n=linha(ws,[texto],False,altura)
        ws.merge_cells(start_row=n,start_column=1,end_row=n,end_column=len(ws.column_dimensions))
        ws.cell(n,1).font=Font(name='Calibri',size=11,bold=cab,color='243746')
        return n
    def resposta(ws,n,cols):
        ws.row_dimensions[n].height=45
        for col in cols:
            c=ws.cell(n,col);c.fill=PatternFill('solid',fgColor='FFF2CC');c.protection=Protection(locked=False)
            c.alignment=Alignment(vertical='top',wrap_text=True)
    ini=aba('Início',[24,65,48,48]);ini.freeze_panes=None
    faixa(ini,'Avaliação independente • 35–45 minutos',True)
    for rotulo in ('Nome','Início (data/hora)','Fim (data/hora)'):
        n=linha(ini,[rotulo,None]);resposta(ini,n,[2])
    branco(ini)
    instrucoes=[
        'Você recebe esta planilha e cinco arquivos: scripts_R1.txt, scripts_R2.txt, scripts_R3.txt, scripts_R4.txt e scripts_R5.txt.',
        '1. Início (3 min): preencha nome e início. Trabalhe sozinho, sem IA e sem consultar o outro avaliador. Use somente navegador, esta planilha e um leitor de texto para os cinco arquivos scripts_R*.txt; não execute scripts, comandos, console ou clientes de API.',
        '2. Oráculo (5 min): confira O01–O05 no site quando possível, escolha a decisão e explique. O oráculo é referência a verificar, não prova do comportamento atual.',
        'Oráculo — Válido: condição e resultado corretos e verificáveis. Ajustar: aproveitável com correção de passos, dados ou resultado; descreva-a. Inválido: contradiz o alvo/requisito ou não corresponde a funcionalidade existente. Não verificável: falta acesso, evidência ou condições; explique.',
        '3. R1 → R5 (cerca de 5–6 min por aba): leia US, critérios e oráculo. Logo abaixo do oráculo, responda opcionalmente em uma linha se faltou um caso importante (somente na primeira aba de cada US; até 1 min por US). Em seguida, classifique os quatro casos amarelos. Depois leia o arquivo scripts_R correspondente à aba (por exemplo, scripts_R1.txt para R1) e atribua as cinco notas.',
        'Casos — Corresponde: mesma condição de entrada e resultado esperado de pelo menos um caso do oráculo. Novo válido: correto e verificável no alvo, sem equivalente no oráculo. Alucinado: inventa ou contradiz campos, mensagens, endpoints, status ou fluxos do alvo/US.',
        'Casos — Não verificável: não é possível concluir com os recursos/evidências disponíveis.',
        'Prioridade: sem evidência, Não verificável; com contradição comprovada, Alucinado; senão, Corresponde ou Novo válido. Para Corresponde, selecione um ID O; outros equivalentes podem ir na observação. Nas demais classes, selecione Nenhum.',
        '4. Qualidade (12–17 min no total, incluídos nas abas R): notas inteiras 0–5; 1, 2 e 4 são intermediários. Justifique fragilidades com números de linha. Avalie o código apresentado sem corrigir ou executar. Em APIs, C4/C5 não exigem seletores ou esperas de interface.',
        '5. Conclusão (3 min): confira respostas amarelas (a pergunta sobre casos faltantes é opcional), preencha o fim e salve. Devolva somente esta planilha, sem discutir decisões antes das duas entregas. Registre indisponibilidade, mudanças e impedimentos; sem confirmação suficiente, use Não verificável sem presumir erro.',
        'As descrições do oráculo foram preservadas: quando faltarem passos, consulte a US e registre a insuficiência. Em APIs, use os critérios e o material; não execute requisições por código. G01–G20 e O01–O05 são avaliados; demais IDs são apoio.'
    ]
    for t in instrucoes: faixa(ini,t,altura=44)
    faixa(ini,'Âncoras de qualidade • 0 = ausente/péssimo • 3 = aceitável • 5 = exemplar',True)
    linha(ini,['Dimensão','0','3','5'],True)
    for a in ANCORAS: linha(ini,a)
    ora=aba('Oráculo',[9,28,44,49,27,23,36])
    faixa(ora,'Oráculo • 5 minutos • confira cada caso',True)
    linha(ora,['ID','US — título e contexto','Caso: condição/passos e resultado esperado','Critérios de aceitação — texto completo','Site','Decisão','Observação / correção / impedimento'],True)
    ora.freeze_panes='A3'
    ora.print_title_rows='1:2'
    for r in escolhidas:
        u=stories[r['us']];c=oraculo[r['us']]['casos'][r['oi']]
        # Quando não há vínculo explícito, fornecer todos os critérios como
        # contexto sem indicar a procedência do caso nem inventar associação.
        refs=c.get('criterios') or range(1,len(u['criterios'])+1)
        criterios='\n'.join(f'CA{i}: {u["criterios"][i-1]}' for i in refs)
        faixa(ora,om[(r['us'],r['oi'])]+' — '+u['titulo']+'\n'+u['texto']+'\n'+texto(c)+'\n'+criterios)
        n=linha(ora,[om[(r['us'],r['oi'])],u['titulo'],'Caso descrito acima','Critérios descritos acima',u['url_base'],None,None])
        ora.cell(n,5).hyperlink=u['url_base'];ora.cell(n,5).font=Font(color='0563C1',underline='single')
        resposta(ora,n,[6,7]);lista(ora,'F',n,n,DECISOES)
    us_perguntadas=set()
    for r in escolhidas:
        rid=r['rid'];us=r['us'];u=stories[us]
        ws=aba(rid,[9,78,25,25,52])
        faixa(ws,f'{rid} • {us} • {u["titulo"]} • cerca de 5–6 minutos',True)
        faixa(ws,u['texto'],altura=42)
        n=faixa(ws,'Abrir site: '+u['url_base']);ws.cell(n,1).hyperlink=u['url_base'];ws.cell(n,1).font=Font(color='0563C1',underline='single')
        faixa(ws,'Critérios de aceitação',True)
        for i,c in enumerate(u['criterios'],1): faixa(ws,f'CA{i}: {c}',altura=44)
        faixa(ws,'Oráculo desta US • referência para correspondência',True)
        n=linha(ws,['ID','Caso: condição e resultado esperado',None,None,None],True)
        ws.merge_cells(start_row=n,start_column=2,end_row=n,end_column=5)
        for idx,c in enumerate(oraculo[us]['casos']):
            import math
            descricao=c.get('descricao') or texto(c)
            largura=sum(ws.column_dimensions[k].width for k in 'BCDE')-4
            altura=15*sum(max(1,math.ceil(len(t)/largura)) for t in descricao.split('\n'))+10
            n=linha(ws,[om[(us,idx)],descricao,None,None,None],altura=altura)
            ws.merge_cells(start_row=n,start_column=2,end_row=n,end_column=5)
        if us not in us_perguntadas:
            branco(ws)
            faixa(ws,'Faltou algum caso importante para esta User Story? (opcional; se sim, descreva em uma linha a condição e o resultado esperado)',altura=30)
            n=linha(ws,['Resposta opcional',None,None,None,None]);resposta(ws,n,[2])
            us_perguntadas.add(us)
        faixa(ws,'Avalie os quatro casos • classe, correspondência e observação em amarelo',True)
        linha(ws,['ID','Caso gerado completo','Classe','Caso do oráculo','Observação (outros equivalentes: cite O)'],True)
        ids=[om[(us,i)] for i in range(len(oraculo[us]['casos']))]
        for idx in r['indices']:
            faixa(ws,gm[(rid,idx)]+' — '+texto(r['casos'][idx]))
            n=linha(ws,[gm[(rid,idx)],'Registre a avaliação do caso acima.',None,None,None])
            resposta(ws,n,[3,4,5]);lista(ws,'C',n,n,CLASSES);lista(ws,'D',n,n,ids+['Nenhum'])
        faixa(ws,'Qualidade • avaliação do script',True)
        faixa(ws,f'Leia o script no arquivo scripts_{rid}.txt (enviado junto com esta planilha) e registre as notas; cite os números de linha nas observações.')
        linha(ws,['Dimensão','Descrição e âncoras','Nota 0–5','Referência','Observação / linhas'],True)
        for i,a in enumerate(ANCORAS,1):
            faixa(ws,a[0]+'\n0 — '+a[1]+'\n3 — '+a[2]+'\n5 — '+a[3])
            n=linha(ws,[f'C{i}',a[0],None,'Âncoras acima',None])
            resposta(ws,n,[3,5]);lista(ws,'C',n,n,[str(v) for v in range(6)])
        ws.print_options.horizontalCentered=True
    for ws in w:
        for region in ws.merged_cells.ranges:
            anchor=ws.cell(region.min_row,region.min_col)
            for row in ws.iter_rows(min_row=region.min_row,max_row=region.max_row,min_col=region.min_col,max_col=region.max_col):
                for c in row:
                    c.border=borda
                    if anchor.fill.fgColor.rgb=='00DCEAF3': c.fill=PatternFill('solid',fgColor='DCEAF3')
        ws.print_area=f'A1:{get_column_letter(len(ws.column_dimensions))}{ws.max_row}'
        for dv in ws.data_validations.dataValidation:
            for region in dv.ranges.ranges:
                for row in ws.iter_rows(min_row=region.min_row,max_row=region.max_row,min_col=region.min_col,max_col=region.max_col):
                    for c in row: c.alignment=Alignment(horizontal='center',vertical='top',wrap_text=True)
        for row in ws:
            for c in row:
                if isinstance(c.value,str): validar_cegamento(c.value)
        ws.sheet_properties.pageSetUpPr.fitToPage=True
        ws.page_setup.orientation='landscape';ws.page_setup.paperSize=ws.PAPERSIZE_A3
        ws.page_setup.fitToWidth=1;ws.page_setup.fitToHeight=0


def gerar():
    if (SAIDA/'chave.csv').exists():
        # Reutiliza a amostra congelada, sem executar qualquer sorteio.
        with (SAIDA/'chave.csv').open(encoding='utf-8-sig',newline='') as f:
            registros=list(csv.DictReader(f))
        oraculo=ler(BASE/'oraculo-casos.json');stories={u['id']:u for u in ler(BASE/'user-stories.json')}
        escolhidas=[]
        for item in registros:
            if item['tipo']!='Resposta': continue
            rid=item['id']
            r={k:item[k] for k in ('autor_prompt','modelo','us')}
            r['rid']=rid
            r['pasta']=BASE/f"resultados_prompt-{r['autor_prompt']}"/r['modelo']/r['us']
            r['casos']=ler(r['pasta']/'casos_teste.json')
            r['indices']=[int(c['indice_original']) for c in sorted(registros,key=lambda c:c['id']) if c['resposta']==rid and c['tipo']=='Casos' and c['sorteado']=='sim']
            r['oi']=next(int(c['indice_original']) for c in registros if c['resposta']==rid and c['tipo']=='Oráculo' and c['sorteado']=='sim')
            assert len(r['indices'])==4
            escolhidas.append(r)
        assert [r['rid'] for r in escolhidas]==['R1','R2','R3','R4','R5']
    else:
        rng=random.Random(20261110)
        with (BASE/'revisao-orientador/scores_v3.csv').open(encoding='utf-8-sig',newline='') as f:
            # Descartar todas as colunas de resultados antes de qualquer sorteio.
            candidatos=[{k:r[k] for k in ('autor_prompt','modelo','us')} for r in csv.DictReader(f)]
        assert len(candidatos)==180 and len({tuple(r.values()) for r in candidatos})==180
        modelos=['haiku','opus','luna','astra','flashlite'];rng.shuffle(modelos)
        escolhidas=[]
        for modelo in modelos:
            pool=[r for r in candidatos if r['modelo']==modelo and r['us'] not in [s['us'] for s in escolhidas]]
            novos=[r for r in pool if r['autor_prompt'] not in [s['autor_prompt'] for s in escolhidas]]
            escolhidas.append(rng.choice(sorted(novos or pool,key=lambda r:(r['autor_prompt'],r['us']))).copy())
        assert len({r['us'] for r in escolhidas})==5
        assert len({r['autor_prompt'] for r in escolhidas})==4
        oraculo=ler(BASE/'oraculo-casos.json');stories={u['id']:u for u in ler(BASE/'user-stories.json')}
        for i,r in enumerate(escolhidas,1):
            r['rid']=f'R{i}';r['pasta']=BASE/f"resultados_prompt-{r['autor_prompt']}"/r['modelo']/r['us']
            r['casos']=ler(r['pasta']/'casos_teste.json')
            r['indices']=rng.sample(range(len(r['casos'])),4)
        for r in escolhidas: r['oi']=rng.randrange(len(oraculo[r['us']]['casos']))
    # AMOSTRA CONGELADA: a partir daqui é permitido consultar os julgamentos.
    gm={};om={};chave=[];gab=[]
    for r in escolhidas:
        for idx in r['indices']: gm[(r['rid'],idx)]=f'G{len(gm)+1:02d}'
    for r in escolhidas: om[(r['us'],r['oi'])]=f'O{len(om)+1:02d}'
    for r in escolhidas:
        for idx in range(len(r['casos'])):
            if (r['rid'],idx) not in gm: gm[(r['rid'],idx)]=f'G{len(gm)+1:02d}'
        for idx in range(len(oraculo[r['us']]['casos'])):
            if (r['us'],idx) not in om: om[(r['us'],idx)]=f'O{len(om)+1:02d}'
    orig_para_o={c['id']:om[(r['us'],i)] for r in escolhidas for i,c in enumerate(oraculo[r['us']]['casos'])}
    w=Workbook();w.remove(w.active)
    for r in escolhidas:
        rid=r['rid'];us=r['us'];u=stories[us];url=u['url_base']
        chave.append(dict(tipo='Resposta',id=rid,resposta=rid,autor_prompt=r['autor_prompt'],modelo=r['modelo'],us=us,indice_original='',id_original='',sorteado='sim'))
        for idx,c in enumerate(oraculo[us]['casos']):
            oid=om[(us,idx)]
            chave.append(dict(tipo='Oráculo',id=oid,resposta=rid,autor_prompt='',modelo='',us=us,indice_original=idx,id_original=c['id'],sorteado='sim' if idx==r['oi'] else 'não'))
        for idx,c in enumerate(r['casos']):
            gid=gm[(rid,idx)]
            chave.append(dict(tipo='Casos',id=gid,resposta=rid,autor_prompt='',modelo='',us=us,indice_original=idx,id_original=c.get('id',str(idx)),sorteado='sim' if idx in r['indices'] else 'não'))
        oid=om[(us,r['oi'])]
        gab.append(dict(tipo='Oráculo',id=oid,resposta=rid,dimensao='',valor='',correspondencia='',justificativa='Ausente: fonte não contém julgamento automático de validade do oráculo.',fonte='oraculo-casos.json (sem decisão)'))
        julgamento=ler(r['pasta']/'julgamento.json');qualidade=ler(r['pasta']/'qualidade.json')
        for idx in r['indices']:
            gid=gm[(rid,idx)]
            m=julgamento['mapa_casos'][str(idx)];classe=m['classe'];cor=m.get('oraculo',[])
            traducao={'valido':'Corresponde' if cor else 'Novo válido','alucinado':'Alucinado','duplicado':'Duplicado','nao_verificavel':'Não verificável'}
            if classe not in traducao: raise ValueError(f'Classe sem tradução: {classe}')
            gab.append(dict(tipo='Casos',id=gid,resposta=rid,dimensao='',valor=traducao[classe],correspondencia=';'.join(orig_para_o[c] for c in cor),justificativa=m.get('nota',''),fonte=str(r['pasta']/'julgamento.json')))
        for i,dim in enumerate(DIMENSOES,1):
            gab.append(dict(tipo='Qualidade',id=rid,resposta=rid,dimensao=f'C{i}',valor=qualidade[dim],correspondencia='',justificativa=qualidade.get('justificativas',{}).get(dim,''),fonte=str(r['pasta']/'qualidade.json')))
    montar_planilha(w, escolhidas, stories, oraculo, gm, om)
    w.save(SAIDA/'avaliador_A.xlsx')
    # openpyxl preenche datas e propriedades de aplicativo ao salvar: remover
    # todo o conteúdo de propriedades no pacote final, inclusive timestamps.
    caminho=SAIDA/'avaliador_A.xlsx'
    with zipfile.ZipFile(caminho) as z:
        partes={n:z.read(n) for n in z.namelist()}
    partes['docProps/core.xml']=b'<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"/>'
    partes['docProps/app.xml']=b'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"/>'
    with zipfile.ZipFile(caminho,'w',zipfile.ZIP_DEFLATED) as z:
        for n,d in partes.items(): z.writestr(n,d)
    shutil.copyfile(caminho,SAIDA/'avaliador_B.xlsx')
    for nome in ['avaliador_A.xlsx','avaliador_B.xlsx']:
        with zipfile.ZipFile(SAIDA/nome) as z:
            for parte in z.namelist():
                if parte.endswith(('.xml','.rels')): validar_cegamento(z.read(parte).decode('utf-8'))
        wb=load_workbook(SAIDA/nome)
        assert wb.sheetnames==['Início','Oráculo','R1','R2','R3','R4','R5']
        assert all(ws.sheet_state=='visible' and ws.protection.sheet and not ws.protection.password for ws in wb)
        assert all(c.data_type!='f' for ws in wb for row in ws for c in row)
        wb.close()
    for r in escolhidas:
        conteudo=script_cego((r['pasta']/'script.py').read_text(encoding='utf-8-sig'))
        numerado=''.join(f'{i:4d} | {code}\n' for i,code in enumerate(conteudo.splitlines(),1))
        validar_cegamento(numerado)
        (SAIDA/f"scripts_{r['rid']}.txt").write_text(numerado,encoding='utf-8')
    csv_salvar('chave.csv',chave,['tipo','id','resposta','autor_prompt','modelo','us','indice_original','id_original','sorteado'])
    csv_salvar('gabarito_automatico.csv',gab,['tipo','id','resposta','dimensao','valor','correspondencia','justificativa','fonte'])
    (SAIDA/'LEIAME.txt').write_text(LEIAME,encoding='utf-8')
    print('Gerados e verificados: duas planilhas idênticas; 20 casos, 5 itens do oráculo e 25 notas; cegamento XML completo aprovado.')
    for r in escolhidas: print(r['rid'],r['us'])

if __name__ == "__main__":
    gerar()
