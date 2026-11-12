# User stories do experimento

As User Stories foram escritas pelo Claude e verificadas nos sistemas reais em 30/10/2026. O texto abaixo corresponde ao que foi enviado aos agentes.

US01 – Buscar e ordenar produtos (sistema: Toolshop; tipo: interface; complexidade: simples; URL base: https://practicesoftwaretesting.com/)

Como cliente da loja de ferramentas, quero buscar produtos por palavra-chave e ordenar os resultados, para encontrar rapidamente o item que desejo comprar.

Critérios de aceitação: (1) Dado que estou na página inicial da loja, quando busco por "hammer", então a listagem exibe somente produtos cujo nome contém "hammer" e a página indica que a busca foi por "hammer". (2) Dado que estou na página inicial, quando busco por um termo inexistente (ex.: "zzzzxx"), então vejo a mensagem "There are no products found." e nenhum produto é listado. (3) Dado que estou na página inicial com produtos listados, quando ordeno por preço do menor para o maior, então os preços da página aparecem em ordem crescente. (4) Dado que estou na página inicial com produtos listados, quando ordeno por nome de Z a A, então os nomes da página aparecem em ordem alfabética decrescente.

US02 – Gerenciar itens no carrinho (sistema: Toolshop; tipo: interface; complexidade: média; URL base: https://practicesoftwaretesting.com/)

Como cliente da loja de ferramentas, quero adicionar produtos ao carrinho e alterar as quantidades, para revisar o valor total antes de comprar.

Critérios de aceitação: (1) Dado que abri a página de um produto disponível (ex.: "Claw Hammer"), quando defino a quantidade 3 e adiciono ao carrinho, então vejo a confirmação "Product added to shopping cart." e o indicador do carrinho mostra 3. (2) Dado que o carrinho contém 3 unidades de um produto, quando abro o carrinho, então o total da linha é igual ao preço unitário multiplicado por 3 e o total do carrinho é igual ao total da linha. (3) Dado que o carrinho contém 3 unidades de um produto, quando altero a quantidade no carrinho para 1, então o total do carrinho passa a ser igual ao preço unitário. (4) Dado que abri a página do produto "Thor Hammer", quando tento adicionar 3 unidades ao carrinho, então vejo a mensagem "You can only have one Thor Hammer in the cart.".

US03 – Login e checkout com cartão (sistema: Toolshop; tipo: interface; complexidade: complexa; URL base: https://practicesoftwaretesting.com/)

Como cliente cadastrado da loja de ferramentas, quero entrar na minha conta e finalizar uma compra com cartão de crédito, para receber meus produtos. Conta de demonstração: customer@practicesoftwaretesting.com / welcome01.

Critérios de aceitação: (1) Dado que estou na tela de login, quando envio o formulário vazio, então vejo as mensagens "Email is required" e "Password is required". (2) Dado que estou na tela de login, quando informo o e-mail da conta de demonstração com senha incorreta, então vejo "Invalid email or password" e permaneço sem sessão. (3) Dado que tenho um produto no carrinho e não estou autenticado, quando avanço para o checkout, então sou levado a informar e-mail e senha. (4) Dado que me autentiquei com a conta de demonstração, então vejo a página "My account" com o nome do usuário no menu. (5) Dado que estou autenticado com um produto no carrinho e no passo de endereço, quando deixo campos obrigatórios do endereço vazios, então não consigo avançar para o pagamento; ao preenchê-los (país, CEP, número, rua, cidade, estado) consigo avançar. (6) Dado que estou no passo de pagamento, quando escolho cartão de crédito, informo dados fictícios válidos e confirmo, então vejo "Payment was successful" e, ao confirmar o pedido, "Thanks for your order! Your invoice number is INV-...".

US04 – Validar formulário de contato (sistema: B&B; tipo: interface; complexidade: simples; URL base: https://automationintesting.online/)

Como visitante da pousada, quero enviar uma mensagem pelo formulário de contato, para tirar dúvidas antes de reservar.

Critérios de aceitação: (1) Dado que estou na página inicial, quando envio o formulário de contato vazio, então vejo mensagens indicando que nome, e-mail, telefone, assunto e mensagem não podem ficar em branco. (2) Dado que preenchi um telefone com menos de 11 caracteres, quando envio, então vejo "Phone must be between 11 and 21 characters.". (3) Dado que preenchi assunto com menos de 5 caracteres e mensagem com menos de 20 caracteres, quando envio, então vejo "Subject must be between 5 and 100 characters." e "Message must be between 20 and 2000 characters.". (4) Dado que preenchi um e-mail malformado (ex.: "bad"), quando envio, então vejo "must be a well-formed email address". (5) Dado que preenchi todos os campos com dados válidos, quando envio, então vejo "Thanks for getting in touch <nome>!" e o assunto informado na confirmação.

US05 – Login e logout do administrador (sistema: B&B; tipo: interface; complexidade: média; URL base: https://automationintesting.online/)

Como administrador da pousada, quero entrar e sair do painel administrativo, para gerenciar quartos e mensagens com segurança. Conta de demonstração: admin / password (painel em /admin).

Critérios de aceitação: (1) Dado que estou na tela de login do painel, quando envio usuário e senha vazios, então vejo "Invalid credentials" e continuo na tela de login. (2) Dado que estou na tela de login do painel, quando informo usuário "admin" e senha incorreta, então vejo "Invalid credentials". (3) Dado que informo usuário "admin" e senha "password", quando faço login, então sou levado à lista de quartos, que inclui o quarto 101 do tipo Single, e o menu mostra Rooms, Report, Branding e Messages. (4) Dado que estou autenticado, quando clico em Logout, então retorno à página inicial pública da pousada. (5) Dado que fiz logout, quando acesso diretamente a lista de quartos do painel, então vejo novamente a tela de login.

US06 – Mensagem do visitante chega à caixa do admin (sistema: B&B; tipo: interface; complexidade: complexa; URL base: https://automationintesting.online/)

Como dono da pousada, quero ver no painel administrativo as mensagens enviadas pelos visitantes, para responder aos interessados. Conta de demonstração: admin / password (painel em /admin).

Critérios de aceitação: (1) Dado que estou autenticado no painel, quando anoto o número exibido ao lado de Messages, então consigo compará-lo depois do próximo envio de um visitante. (2) Dado que um visitante preenche o formulário de contato da página inicial com nome, assunto e dados válidos, quando envia, então vê a confirmação "Thanks for getting in touch <nome>!". (3) Dado que o visitante enviou uma mensagem, quando o administrador faz login, então o contador ao lado de Messages é uma unidade maior que o anotado antes. (4) Dado que o administrador abre a caixa de mensagens, então a mensagem recém-enviada aparece na lista com o nome do remetente e o assunto informados. (5) Dado que o administrador saiu do painel (logout), quando tenta abrir a caixa de mensagens diretamente, então é solicitado a fazer login.

US07 – Criar e consultar reserva (sistema: API; tipo: API; complexidade: simples; URL base: https://restful-booker.herokuapp.com)

Como consumidor da API de reservas, quero criar uma reserva e consultá-la, para confirmar que os dados foram gravados corretamente.

Critérios de aceitação: (1) Dado um corpo JSON válido (nome, sobrenome, preço total, depósito pago, datas de check-in e check-out, necessidades adicionais), quando crio uma reserva, então recebo status 200 com um identificador numérico e os mesmos dados enviados. (2) Dado que criei uma reserva, quando consulto pelo identificador retornado, então recebo status 200 e todos os campos iguais aos enviados. (3) Dado um identificador inexistente (ex.: 99999999), quando consulto a reserva, então recebo status 404. (4) Dado que criei uma reserva com nome e sobrenome únicos, quando listo reservas filtrando por esse nome e sobrenome, então a lista contém o identificador criado.

US08 – Autenticar e atualizar reserva (sistema: API; tipo: API; complexidade: média; URL base: https://restful-booker.herokuapp.com)

Como administrador consumindo a API de reservas, quero me autenticar e atualizar reservas existentes, para corrigir dados de clientes. Credenciais de demonstração: admin / password123.

Critérios de aceitação: (1) Dado as credenciais admin / password123, quando solicito autenticação, então recebo status 200 e um token não vazio. (2) Dado credenciais inválidas, quando solicito autenticação, então a resposta não contém token e informa o motivo "Bad credentials". (3) Dado uma reserva existente e um token válido, quando envio uma atualização completa com novo nome e novo preço, então recebo status 200 e os novos valores. (4) Dado uma reserva existente e um token válido, quando envio uma atualização parcial apenas do sobrenome, então recebo status 200, o sobrenome muda e os demais campos permanecem. (5) Dado uma reserva existente, quando tento atualizar sem token, então recebo status 403. (6) Dado uma reserva existente e um token válido, quando envio uma atualização completa com campos obrigatórios ausentes, então recebo status 400.

US09 – Ciclo de vida e exclusão de reserva (sistema: API; tipo: API; complexidade: complexa; URL base: https://restful-booker.herokuapp.com)

Como administrador consumindo a API de reservas, quero excluir reservas com autorização e ter garantias de segurança e consistência, para manter a base correta. Credenciais de demonstração: admin / password123.

Critérios de aceitação: (1) Dado uma reserva criada, quando tento excluí-la sem token, então recebo status 403 e a reserva continua consultável com status 200. (2) Dado uma reserva criada, quando tento excluí-la com um token inválido, então recebo status 403 e a reserva continua existindo. (3) Dado uma reserva criada e um token válido obtido por autenticação, quando a excluo, então recebo status 201. (4) Dado que excluí uma reserva, quando a consulto pelo mesmo identificador, então recebo status 404. (5) Dado que excluí uma reserva, quando tento excluí-la novamente com token válido, então recebo um status de erro 4xx e nenhuma outra reserva é afetada. (6) Dado que excluí uma reserva, quando listo reservas filtrando pelo nome único dela, então a lista retornada está vazia.
