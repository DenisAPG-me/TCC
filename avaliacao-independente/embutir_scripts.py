# Pós-processamento (rodar depois do sorteio.py): coloca o script de cada resposta em um
# único quadro de texto ao lado dos casos nas abas R1–R5 e junta as instruções da aba
# Início (linhas 5 a 16) em um bloco. Requer Excel (COM). Uso: python embutir_scripts.py
import os, shutil, win32com.client as w

PASTA = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(PASTA, "avaliador_A.xlsx"); B = os.path.join(PASTA, "avaliador_B.xlsx")
AVISO = "Você recebe somente esta planilha. Em cada aba R, o script completo está no quadro cinza à direita dos casos (role para a direita)."

xl = w.DispatchEx("Excel.Application"); xl.Visible = False; xl.DisplayAlerts = False
try:
    wb = xl.Workbooks.Open(A)
    ws = wb.Worksheets("Início"); ws.Unprotect()
    linhas = [str(ws.Cells(r, 1).Value) for r in range(5, 17) if ws.Cells(r, 1).Value]
    linhas = [AVISO if l.startswith("Você recebe") else l for l in linhas]
    texto = "\n\n".join(linhas)
    rg = ws.Range("A5:D16"); rg.UnMerge(); rg.ClearContents(); rg.Merge()
    rg.Value = texto
    rg.WrapText = True; rg.VerticalAlignment = -4160; rg.HorizontalAlignment = -4131
    rg.Interior.Color = 0xFFFFFF; rg.Font.Bold = False
    n = sum(1 + len(l) // 160 for l in linhas) + len(linhas)
    for r in range(5, 17): ws.Rows(r).RowHeight = (15.5 * n + 10) / 12
    ws.Protect("", True, True)

    for k in range(1, 6):
        ws = wb.Worksheets(f"R{k}"); ws.Unprotect()
        for s in list(ws.Shapes):
            if s.Name.startswith("Script_"): s.Delete()
        topo = ws.UsedRange.Find("Avalie os quatro casos", LookAt=2).Top
        esq = ws.Columns(6).Left + 12
        cod = open(os.path.join(PASTA, f"scripts_R{k}.txt"), encoding="utf-8").read().rstrip("\n")
        tb = ws.Shapes.AddTextbox(1, esq, topo, 560, 200)
        tb.Name = f"Script_R{k}"
        tf = tb.TextFrame2
        tf.WordWrap = False; tf.AutoSize = 1
        tf.MarginLeft = tf.MarginRight = tf.MarginTop = tf.MarginBottom = 6
        cab = f"SCRIPT R{k} (somente leitura; cite os números de linha)"
        tf.TextRange.Text = cab + "\r\r" + cod.replace("\n", "\r")
        tf.TextRange.Font.Name = "Consolas"; tf.TextRange.Font.Size = 9
        tb.TextFrame.Characters(1, len(cab)).Font.Bold = True
        tb.Fill.ForeColor.RGB = 0xF7F7F7; tb.Line.ForeColor.RGB = 0xBFBFBF
        tb.Placement = 2; tb.Locked = True
        c = ws.UsedRange.Find("Leia o script no arquivo", LookAt=2)
        if c is not None:
            c.Value = "Leia o script no quadro cinza à direita dos casos (role para a direita) e registre as notas; cite os números de linha nas observações."
        ws.Protect("", True, True)
    wb.Worksheets("Início").Activate()
    wb.Save(); wb.Close(False)
finally:
    xl.Quit()
shutil.copyfile(A, B)
print("ok")
