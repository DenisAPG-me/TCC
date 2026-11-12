# Como rodar (no Windows): C:\Python314\python.exe analisar.py avaliador_A.xlsx avaliador_B.xlsx gabarito_automatico.csv
"""Análise pareada; nenhuma ausência é convertida em classe ou nota."""
import argparse
import csv
import math
import re
from pathlib import Path
from collections import Counter
from openpyxl import load_workbook

CLASSES = ['Corresponde', 'Novo válido', 'Alucinado', 'Não verificável']
ORACULO = ['Válido', 'Ajustar', 'Inválido', 'Não verificável']

def kappa(a, b, ponderado=False):
    if not a:
        return None
    n = len(a)
    ca, cb = Counter(a), Counter(b)
    if ponderado:
        observado = sum(abs(x-y)/5 for x,y in zip(a,b))/n
        esperado = sum(ca[x]*cb[y]*abs(x-y)/5 for x in ca for y in cb)/(n*n)
        return None if esperado == 0 else 1-observado/esperado
    po = sum(x == y for x,y in zip(a,b))/n
    pe = sum(ca[x]*cb[x] for x in ca)/(n*n)
    return None if math.isclose(pe, 1) else (po-pe)/(1-pe)

def ler_planilha(caminho, lacunas=None, avaliador=None):
    w = load_workbook(caminho, data_only=False)
    dados = {}
    def guardar(chave, valor, obs, correspondencia=''):
        if chave in dados:
            raise ValueError(f'ID duplicado em {caminho}: {chave}')
        tipo, _, _ = chave
        if valor == '': valor = None
        if valor is not None:
            if tipo == 'Qualidade':
                if isinstance(valor, bool) or not isinstance(valor, (int,float)) or valor not in range(6):
                    raise ValueError(f'Nota inválida em {caminho}: {chave}: {valor}')
                valor = int(valor)
            elif valor not in (CLASSES if tipo == 'Casos' else ORACULO):
                raise ValueError(f'Classe inválida em {caminho}: {chave}: {valor}')
        dados[chave] = (valor, obs or '', correspondencia or '')
    if w.sheetnames != ['Início','Oráculo','R1','R2','R3','R4','R5']:
        raise ValueError('Layout inesperado: use as planilhas atuais com Início, Oráculo e R1–R5.')
    for r in w['Oráculo'].iter_rows(values_only=True):
        if isinstance(r[0],str) and r[0] in {f'O{i:02d}' for i in range(1,6)}:
            guardar(('Oráculo',r[0],''),r[5],r[6])
    us_lidas=set()
    for i in range(1,6):
        rid=f'R{i}';ws=w[rid]
        us=ws['A1'].value.split(' • ')[1].strip()
        if us not in us_lidas and lacunas is not None:
            for row in ws.iter_rows():
                if isinstance(row[0].value,str) and row[0].value.startswith('Faltou algum caso importante para esta User Story?'):
                    texto=ws.cell(row[0].row+1,2).value
                    if texto is not None and str(texto).strip():
                        lacunas.append({'avaliador':avaliador,'US':us,'texto':str(texto)})
                    break
        us_lidas.add(us)
        # Apenas o bloco de avaliação, encerrado pela seção de qualidade.
        em_casos=False
        for r in ws.iter_rows(values_only=True):
            if r[0]=='ID' and r[2]=='Classe':
                em_casos=True
                continue
            if isinstance(r[0],str) and r[0].startswith('Qualidade •'):
                em_casos=False
            if em_casos and isinstance(r[0],str) and re.fullmatch(r'G\d+',r[0]):
                guardar(('Casos',r[0],''),r[2],r[4],'' if r[3]=='Nenhum' else r[3])
            if r[0] in {f'C{j}' for j in range(1,6)}:
                guardar(('Qualidade',rid,r[0]),r[2],r[4])
    w.close()
    return dados

def ler_automatico(caminho):
    dados = {}
    with open(caminho, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            key = (r['tipo'],r['id'],r['dimensao'])
            if key in dados: raise ValueError(f'ID automático duplicado: {key}')
            v = r['valor'] or None
            if v is not None and r['tipo']=='Qualidade': v = int(v)
            if v is not None and ((r['tipo']=='Qualidade' and v not in range(6)) or
                (r['tipo']=='Casos' and v not in CLASSES + ['Duplicado']) or
                (r['tipo']=='Oráculo' and v not in ORACULO)):
                raise ValueError(f'Valor automático inválido: {key}')
            dados[key] = (v,r['justificativa'],r['correspondencia'])
    return dados

def escrever_csv(caminho, linhas, campos):
    with open(caminho,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=campos);w.writeheader();w.writerows(linhas)

def analisar(a, b, automatico, saida):
    lacunas=[]
    fontes={'A':ler_planilha(a,lacunas,'A'),'B':ler_planilha(b,lacunas,'B'),'Automático':ler_automatico(automatico)}
    esperado = set(fontes['Automático'])
    for nome in ['A','B']:
        if set(fontes[nome]) != esperado:
            raise ValueError(f'IDs de {nome} diferem do gabarito; confira a versão da amostra.')
    resultados=[]; divergencias=[]; ausencias=[]; excluidos=[]
    def excluir(esq, dir, k):
        return 'Automático' in (esq, dir) and k[0]=='Casos' and fontes['Automático'][k][0]=='Duplicado'

    grupos=[('Casos',''),('Oráculo','')]+[('Qualidade',f'C{i}') for i in range(1,6)]+[('Qualidade','Todas')]
    for esq,dir in [('A','B'),('A','Automático'),('B','Automático')]:
        for tipo,dim in grupos:
            keys=sorted(k for k in esperado if k[0]==tipo and (dim=='Todas' or k[2]==dim))
            pares=[(fontes[esq][k][0],fontes[dir][k][0]) for k in keys if not excluir(esq,dir,k) and fontes[esq][k][0] is not None and fontes[dir][k][0] is not None]
            aa=[p[0] for p in pares]; bb=[p[1] for p in pares];n=len(pares)
            q=tipo=='Qualidade'
            resultados.append(dict(comparacao=f'{esq} × {dir}',tipo=tipo,dimensao=dim,n_previsto=len(keys),n_pares=n,n_excluidos=len(keys)-n,
                concordancia_pct=100*sum(x==y for x,y in pares)/n if n else None,
                kappa=kappa(aa,bb,q),ponderacao='linear (0–5)' if q else 'não ponderado',
                diferenca_media=sum(x-y for x,y in pares)/n if q and n else None,
                diferenca_absoluta_media=sum(abs(x-y) for x,y in pares)/n if q and n else None,
                diferenca_ate_1_pct=100*sum(abs(x-y)<=1 for x,y in pares)/n if q and n else None,
                observacao='Kappa indefinido se não houver pares ou variação esperada; célula vazia = indisponível.'))
        for k in sorted(esperado):
            x,ox,cx=fontes[esq][k];y,oy,cy=fontes[dir][k]
            if excluir(esq,dir,k):
                excluidos.append(dict(comparacao=f'{esq} × {dir}',tipo=k[0],id=k[1],dimensao=k[2],
                    valor_esquerda=x,valor_direita=y,motivo='duplicado no automático, não avaliado pelos humanos'))
                continue
            if x is None or y is None:
                ausencias.append(dict(comparacao=f'{esq} × {dir}',tipo=k[0],id=k[1],dimensao=k[2],ausente_em='; '.join(n for n,v in [(esq,x),(dir,y)] if v is None)))
            elif x!=y:
                divergencias.append(dict(comparacao=f'{esq} × {dir}',tipo=k[0],id=k[1],dimensao=k[2],valor_esquerda=x,valor_direita=y,
                    diferenca=x-y if k[0]=='Qualidade' else '',observacao_esquerda=ox,observacao_direita=oy,
                    correspondencia_esquerda=cx,correspondencia_direita=cy,motivo_apos_entrega=''))
    for tipo,dim in grupos:
        rs=[r for r in resultados if r['tipo']==tipo and r['dimensao']==dim and r['comparacao'] in ['A × Automático','B × Automático']]
        media=dict(rs[0]);media['comparacao']='Média A/B × Automático'
        for campo in ['n_previsto','n_pares','n_excluidos','concordancia_pct','kappa','diferenca_media','diferenca_absoluta_media','diferenca_ate_1_pct']:
            vs=[r[campo] for r in rs];media[campo]=sum(vs)/2 if all(v is not None for v in vs) else None
        media['observacao']='Média aritmética dos dois indicadores; indisponível se qualquer um for indefinido. Contagens são médias, não observações independentes.'
        resultados.append(media)
    saida=Path(saida);saida.mkdir(parents=True,exist_ok=True)
    escrever_csv(saida/'lacunas_oraculo.csv',lacunas,['avaliador','US','texto'])
    escrever_csv(saida/'concordancia.csv',resultados,list(resultados[0]))
    escrever_csv(saida/'divergencias.csv',divergencias,['comparacao','tipo','id','dimensao','valor_esquerda','valor_direita','diferenca','observacao_esquerda','observacao_direita','correspondencia_esquerda','correspondencia_direita','motivo_apos_entrega'])
    escrever_csv(saida/'excluidos.csv',excluidos,['comparacao','tipo','id','dimensao','valor_esquerda','valor_direita','motivo'])
    escrever_csv(saida/'ausencias.csv',ausencias,['comparacao','tipo','id','dimensao','ausente_em'])
    for r in resultados:
        pct=r['concordancia_pct']; kap=r['kappa']
        print(f"{r['comparacao']} | {r['tipo']} {r['dimensao']} | pares={r['n_pares']} | concordância={pct if pct is not None else 'indisponível'}% | kappa={round(kap,4) if kap is not None else 'indefinido'}")
        if r['tipo']=='Qualidade': print(f"  diferença média (esquerda − direita): {r['diferenca_media']}; absoluta: {r['diferenca_absoluta_media']}; até 1 ponto (%): {r['diferenca_ate_1_pct']}")
    print(f'{len(excluidos)} pares excluídos por duplicado no automático; {len(divergencias)} divergências; {len(ausencias)} pares incompletos. Motivos devem ser registrados após as duas entregas. Amostra pequena: priorize percentuais; não generalize para as 180 respostas.')
    return resultados,divergencias,ausencias

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('avaliador_a',type=Path);p.add_argument('avaliador_b',type=Path);p.add_argument('gabarito',type=Path)
    p.add_argument('--saida',type=Path,default=Path(__file__).resolve().parent/'analise')
    args=p.parse_args()
    raiz=Path(__file__).resolve().parent
    if not args.saida.resolve().is_relative_to(raiz): p.error('A saída deve ficar dentro da pasta deste programa.')
    analisar(args.avaliador_a,args.avaliador_b,args.gabarito,args.saida)
