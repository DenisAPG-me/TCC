# Oráculo de casos de teste

O oráculo reúne 114 casos (55 positivos, 37 negativos e 22 de borda), dos quais 77 derivam diretamente dos critérios de aceitação e 37 são complementares. A coluna Critérios indica os critérios de aceitação da User Story a que cada caso se refere.

Quadro 6 – Oráculo de casos de teste (114 casos)

| Id | Tipo | Descrição | Critérios |
|---|---|---|---|
| US01-C01 | positivo | Buscar 'hammer' lista apenas produtos com hammer no nome e indica o termo buscado | 1 |
| US01-C02 | positivo | Buscar em minúsculas e maiúsculas (HAMMER) retorna o mesmo resultado | 1 |
| US01-C03 | negativo | Buscar termo inexistente mostra 'There are no products found.' | 2 |
| US01-C04 | borda | Buscar string vazia retorna a listagem padrão |  |
| US01-C05 | borda | Buscar com espaços/caracteres especiais não quebra a página |  |
| US01-C06 | positivo | Ordenar por preço crescente mantém preços em ordem não decrescente | 3 |
| US01-C07 | positivo | Ordenar por preço decrescente mantém preços em ordem não crescente |  |
| US01-C08 | positivo | Ordenar por nome A-Z |  |
| US01-C09 | positivo | Ordenar por nome Z-A mantém ordem decrescente | 4 |
| US01-C10 | positivo | Combinar busca com ordenação | 1, 3 |
| US01-C11 | positivo | Limpar a busca (botão X) restaura a listagem |  |
| US01-C12 | positivo | Paginação: avançar para a página 2 mostra outros produtos |  |
| US01-C13 | positivo | Filtrar por categoria Hammer |  |
| US02-C01 | positivo | Adicionar produto disponível com quantidade 1 exibe toast e badge 1 | 1 |
| US02-C02 | positivo | Adicionar com quantidade 3 exibe toast e badge 3 | 1 |
| US02-C03 | positivo | Total da linha = preço unitário x quantidade | 2 |
| US02-C04 | positivo | Total do carrinho = total da linha com um item | 2 |
| US02-C05 | positivo | Alterar quantidade no carrinho para 1 atualiza o total | 3 |
| US02-C06 | positivo | Adicionar dois produtos diferentes soma os totais |  |
| US02-C07 | positivo | Remover item do carrinho esvazia o total |  |
| US02-C08 | negativo | Thor Hammer: limite de 1 por carrinho exibe mensagem | 4 |
| US02-C09 | borda | Quantidade mínima 1 no botão decrementar não vai a 0 |  |
| US02-C10 | borda | Quantidade máxima 99 / valor acima do máximo no campo do carrinho |  |
| US02-C11 | borda | Quantidade 0 ou negativa no carrinho |  |
| US02-C12 | negativo | Produto fora de estoque não pode ser adicionado (se existir) |  |
| US02-C13 | positivo | Carrinho persiste ao navegar para outra página |  |
| US03-C01 | negativo | Login com formulário vazio mostra as duas mensagens de obrigatório | 1 |
| US03-C02 | negativo | Login com senha errada mostra 'Invalid email or password' | 2 |
| US03-C03 | negativo | Login com e-mail malformado mostra 'Email format is invalid' |  |
| US03-C04 | negativo | Login com e-mail não cadastrado | 2 |
| US03-C05 | positivo | Login válido leva a /account com título My account e nome no menu | 4 |
| US03-C06 | positivo | Checkout sem login pede credenciais | 3 |
| US03-C07 | positivo | Logout após login |  |
| US03-C08 | negativo | Endereço com campos obrigatórios vazios mantém botão desabilitado | 5 |
| US03-C09 | positivo | Endereço completo habilita avanço ao pagamento | 5 |
| US03-C10 | negativo | Finalizar sem escolher método de pagamento (botão desabilitado) |  |
| US03-C11 | positivo | Pagamento com cartão de crédito válido exibe 'Payment was successful' | 6 |
| US03-C12 | positivo | Confirmar pedido exibe número de fatura INV- | 6 |
| US03-C13 | negativo | Cartão com número/validade/CVV inválidos |  |
| US03-C14 | positivo | Pagamento por Cash on Delivery / Bank Transfer conclui |  |
| US03-C15 | borda | Checkout fluxo completo ponta a ponta (carrinho->login->endereço->pagamento->confirmação) | 3, 4, 5, 6 |
| US04-C01 | negativo | Formulário vazio mostra mensagens de campo em branco para os 5 campos | 1 |
| US04-C02 | negativo | Telefone com 10 caracteres rejeitado | 2 |
| US04-C03 | borda | Telefone com exatamente 11 caracteres aceito | 2 |
| US04-C04 | borda | Telefone com 21 e 22 caracteres |  |
| US04-C05 | negativo | Assunto com 4 caracteres rejeitado | 3 |
| US04-C06 | borda | Assunto com 5 caracteres aceito | 3 |
| US04-C07 | borda | Assunto com 101 caracteres rejeitado |  |
| US04-C08 | negativo | Mensagem com 19 caracteres rejeitada | 3 |
| US04-C09 | borda | Mensagem com 20 caracteres aceita | 3 |
| US04-C10 | borda | Mensagem com 2001 caracteres rejeitada |  |
| US04-C11 | negativo | E-mail malformado rejeitado | 4 |
| US04-C12 | positivo | Envio válido exibe agradecimento com o nome e o assunto | 5 |
| US04-C13 | borda | Caracteres especiais/acentos nos campos |  |
| US04-C14 | positivo | Após erro e correção dos campos o envio é aceito | 1, 5 |
| US05-C01 | negativo | Login com campos vazios mostra Invalid credentials | 1 |
| US05-C02 | negativo | Login com senha errada mostra Invalid credentials | 2 |
| US05-C03 | negativo | Login com usuário inexistente | 2 |
| US05-C04 | positivo | Login admin/password leva à lista de quartos | 3 |
| US05-C05 | positivo | Lista de quartos contém 101 Single | 3 |
| US05-C06 | positivo | Menu exibe Rooms, Report, Branding e Messages | 3 |
| US05-C07 | positivo | Logout retorna à home pública | 4 |
| US05-C08 | negativo | Acesso direto a /admin/rooms sem sessão exibe login | 5 |
| US05-C09 | borda | Back do navegador após logout não restaura sessão | 5 |
| US05-C10 | borda | Usuário válido com maiúsculas diferentes (Admin) |  |
| US05-C11 | borda | Espaços antes/depois nas credenciais |  |
| US06-C01 | positivo | Ler contador de Messages antes do envio | 1 |
| US06-C02 | positivo | Visitante envia mensagem válida e vê confirmação com o nome | 2 |
| US06-C03 | positivo | Contador de Messages aumenta em 1 após envio | 3 |
| US06-C04 | positivo | Mensagem aparece na lista com nome e assunto | 4 |
| US06-C05 | negativo | Envio inválido do visitante não incrementa o contador |  |
| US06-C06 | negativo | Sem login, caixa de mensagens exige autenticação | 5 |
| US06-C07 | positivo | Mensagem persiste após logout e novo login | 4 |
| US06-C08 | borda | Duas mensagens seguidas incrementam o contador em 2 | 3 |
| US06-C09 | borda | Nome com caracteres especiais aparece corretamente na lista | 4 |
| US07-C01 | positivo | POST com corpo válido retorna 200, bookingid numérico e dados ecoados | 1 |
| US07-C02 | positivo | GET do id criado retorna os mesmos dados | 2 |
| US07-C03 | positivo | Campos tipados corretamente (totalprice número, depositpaid booleano, datas YYYY-MM-DD) | 1, 2 |
| US07-C04 | positivo | POST sem additionalneeds (opcional) é aceito |  |
| US07-C05 | positivo | Filtro por firstname/lastname retorna o id criado | 4 |
| US07-C06 | positivo | Filtro por datas checkin/checkout retorna 200 e lista |  |
| US07-C07 | positivo | GET /booking sem filtros retorna lista de ids |  |
| US07-C08 | negativo | GET de id inexistente retorna 404 | 3 |
| US07-C09 | negativo | GET com id não numérico retorna 404 | 3 |
| US07-C10 | negativo | POST com campos obrigatórios ausentes não retorna 200 (observado 500) |  |
| US07-C11 | negativo | POST com JSON malformado retorna 400 |  |
| US07-C12 | borda | totalprice 0 e depositpaid false |  |
| US07-C13 | borda | Filtro sem resultados retorna lista vazia 200 |  |
| US07-C14 | positivo | Dois POSTs idênticos geram ids distintos |  |
| US08-C01 | positivo | POST /auth com admin/password123 retorna 200 e token não vazio | 1 |
| US08-C02 | negativo | POST /auth com senha errada retorna reason Bad credentials sem token | 2 |
| US08-C03 | negativo | POST /auth com corpo vazio retorna Bad credentials | 2 |
| US08-C04 | positivo | PUT completo com token (cookie) retorna 200 e novos valores | 3 |
| US08-C05 | positivo | PUT com Authorization Basic também é aceito | 3 |
| US08-C06 | positivo | PATCH parcial altera apenas o sobrenome e preserva o resto | 4 |
| US08-C07 | negativo | PUT sem token retorna 403 | 5 |
| US08-C08 | negativo | PUT com token inválido retorna 403 | 5 |
| US08-C09 | negativo | PATCH sem token retorna 403 | 5 |
| US08-C10 | negativo | PUT com corpo incompleto retorna 400 | 6 |
| US08-C11 | negativo | PUT em id inexistente retorna erro (observado 405) |  |
| US08-C12 | positivo | GET após PUT reflete a atualização | 3 |
| US08-C13 | borda | PUT mudando datas para checkout anterior ao checkin (sem validação) |  |
| US09-C01 | negativo | DELETE sem token retorna 403 | 1 |
| US09-C02 | negativo | Reserva continua existente (GET 200) após DELETE sem token | 1 |
| US09-C03 | negativo | DELETE com token inválido retorna 403 | 2 |
| US09-C04 | positivo | DELETE com token válido retorna 201 | 3 |
| US09-C05 | positivo | DELETE com autenticação Basic retorna 201 | 3 |
| US09-C06 | positivo | GET após exclusão retorna 404 | 4 |
| US09-C07 | negativo | DELETE repetido retorna erro 4xx (observado 405) | 5 |
| US09-C08 | negativo | DELETE de id inexistente retorna erro 4xx | 5 |
| US09-C09 | positivo | Listagem filtrada pelo nome da reserva excluída está vazia | 6 |
| US09-C10 | positivo | Outras reservas permanecem após exclusão de uma | 5 |
| US09-C11 | positivo | Fluxo completo: auth, criar, excluir, confirmar 404 | 3, 4 |
| US09-C12 | borda | DELETE com token de sessão anterior reutilizado |  |

Fonte: Elaborado pelo autor.
