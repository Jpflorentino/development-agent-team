# Development Agent Team — guia em português de Portugal

A versão 1.0.0 disponibiliza dez papéis de engenharia, definições canónicas, adaptadores para Claude Code, Codex, GitHub Copilot e ChatGPT, instalação com deteção de conflitos e memória persistente por projeto. Requer Python 3.11 ou superior e utiliza apenas a biblioteca standard.

O Team Leader coordena o trabalho e é o interlocutor do utilizador. Seleciona apenas os especialistas necessários: Software Architect, UI/UX Designer, Frontend Developer, Backend Developer, Database Engineer, QA/Test Engineer, Security Engineer, DevOps Engineer e Code Review Engineer. Os agentes respondem, por defeito, no idioma do utilizador.

## Para que serve

A framework organiza assistentes de programação numa equipa virtual de engenharia de software. Pode utilizá-la para transformar uma ideia num projeto novo, desenvolver funcionalidades numa aplicação existente, corrigir erros, coordenar revisões e testes ou preparar entregas autorizadas. A memória do projeto conserva decisões aprovadas e contexto relevante para continuar noutra sessão.

Recebe definições dos agentes, adaptadores para as plataformas, ferramentas de instalação e gestão de contexto. A execução decorre na plataforma de IA escolhida, com as ferramentas e permissões efetivamente disponíveis; não exige um servidor permanente da framework.

## Como funciona

1. Descreve normalmente o que queres criar ou alterar. As instruções instaladas ativam o Team Leader; não é necessário nomear o papel nem pedir português ou ausência de JSON.
2. Discute o produto, a arquitetura e as tecnologias com o Team Leader, que consulta o Software Architect quando essas escolhas estão por decidir. Recebe opções, motivos e alternativas, e aprova ou pede alterações.
3. Depois da aprovação da arquitetura, recebe uma tabela de tarefas por agente, entregáveis, dependências e critérios de validação. Aprova a execução desse plano antes da implementação. Aprovar apenas a arquitetura não autoriza escrever a aplicação.
4. Quando fizer sentido, discute deployment e custos com o Team Leader e o DevOps, numa fase própria. A escolha de fornecedor ou orçamento não autoriza automaticamente a contratação ou publicação.
5. O Team Leader coordena o trabalho aprovado, verifica os resultados e conserva decisões duradouras com a referência da aprovação. Reutiliza autorizações já dadas para o mesmo âmbito, sem repetir confirmações desnecessárias.

Continua a conversar com o Team Leader, que coordena a participação dos especialistas. O instalador prepara os ficheiros; os agentes trabalham dentro da plataforma. A instalação, por si só, não demonstra execução nativa: consulte a [matriz de compatibilidade](../compatibility.md) para as diferenças e limitações.

O Team Leader responde em linguagem natural, no seu idioma, com a recomendação ou resultado, a explicação relevante e as perguntas ou próximos passos. Os relatórios JSON dos especialistas são comunicação interna; o Team Leader sintetiza as conclusões validadas. Só apresenta um formato estruturado ao utilizador quando este o pede explicitamente.

As instruções geradas para a conversa principal omitem os esquemas de campos JSON internos. Esses contratos continuam nos perfis delegados e nas referências canónicas, para os relatórios dos especialistas.

O plano identifica a tarefa atribuída a cada especialista relevante, o estado real da participação, a recomendação, os motivos e as evidências disponíveis. Os papéis desnecessários são identificados com uma justificação breve; não se convocam os dez agentes só para preencher um relatório. Uma delegação nativa, uma passagem sequencial por um papel e uma proposta do líder são situações distintas. Ter o perfil instalado não prova que recebeu uma tarefa.

## Instalação

Execute a partir da cópia local da framework:

```sh
python3 scripts/dat.py validate
python3 scripts/dat.py install --platform codex --scope project --target /caminho/do/projeto --dry-run
python3 scripts/dat.py install --platform codex --scope project --target /caminho/do/projeto
python3 scripts/dat.py memory init --target /caminho/do/projeto
python3 scripts/dat.py doctor --target /caminho/do/projeto
```

Substitua `codex` por `claude-code`, `github-copilot` ou `chatgpt`. No Windows pode utilizar `py -3.11` e um caminho como `C:\trabalho\projeto`. A instalação global usa `--scope global` e a pasta pessoal como `--target`; não é suportada para ChatGPT. A instalação ChatGPT exporta ficheiros locais para aplicação manual nas instruções e anexos de um Project.

Os identificadores nativos têm o prefixo `dat-`, por exemplo `dat-team-leader`. Abra o projeto na plataforma escolhida e confirme o carregamento dos perfis. Instalar ficheiros não demonstra invocação nem delegação. Consulte os [passos por plataforma](../installation.md) e a [matriz de compatibilidade](../compatibility.md).

## Utilização

Depois da instalação, abra a pasta de destino na plataforma e inicie uma nova conversa. Pode começar numa pasta sem código e sem stack definida; a instalação prepara a equipa, não cria a aplicação.

### Começar um projeto do zero

Explique a ideia em linguagem natural. Não precisa de escolher tecnologias, organizar o repositório ou escrever uma especificação completa antes de começar. Se faltarem dados essenciais, o Team Leader faz algumas perguntas de cada vez; se já tiver fornecido um briefing completo e decisões aprovadas, usa essa informação sem repetir a entrevista.

> Quero criar um site para uma empresa de fisioterapia ao domicílio. Quero apresentar a equipa e permitir escolher uma profissional e pedir uma sessão. Ainda não escolhi tecnologias. Ajuda-me a definir a melhor abordagem.

Este pedido deve iniciar a discussão de arquitetura, com consulta ao arquiteto. Depois da tua aprovação, o líder prepara as tarefas dos agentes e pede autorização para as executar. O deployment e os custos podem ser discutidos posteriormente. Não tens de repetir estas regras na prompt.

A existência de `.codex/`, `.ai-team/`, `AGENTS.md` ou metadados Git não significa que já exista uma aplicação. A ausência de código ou de contexto preenchido é normal neste modo. O Team Leader esclarece o produto, consulta o Software Architect quando útil e só depois encaminha a implementação necessária. Não convoca automaticamente os dez agentes nem cria ficheiros de planeamento no projeto.

### Explicar um projeto já iniciado

> Suspende a implementação e analisa o projeto atual apenas em leitura. Explica a stack, a arquitetura e as integrações a partir dos ficheiros existentes. Para cada especialista, identifica a tarefa atribuída, o estado da participação, a recomendação e as evidências quando existirem registos. Distingue o que observaste no código das decisões e aprovações históricas documentadas; assinala como não verificado o histórico indisponível. Identifica novas consultas como retrospetivas. Apresenta os próximos passos para minha aprovação antes de continuar a implementar.

### Trabalhar num projeto existente

Descreva a funcionalidade, o erro ou a revisão pretendida, por exemplo:

> Corrige o erro de validação quando o cliente **[descreve o problema e como o reproduzir]**. O resultado esperado é **[descreve o comportamento]**.

Quando existem subagentes nativos, o Team Leader pode delegar tarefas delimitadas. Sem esse mecanismo, executa passagens sequenciais pelos papéis e identifica essa limitação. Uma passagem de revisão na mesma conversa não constitui revisão independente. Riscos HIGH e CRITICAL exigem uma revisão separada para satisfazer o respetivo gate.

Paralelismo requer tarefas independentes, contratos definidos, isolamento e responsabilidade exclusiva pelos ficheiros. O módulo Python `dat/policy.py` valida contratos e políticas determinísticas; não executa modelos, não lança agentes e não concede permissões.

## Manutenção e contexto

```sh
python3 scripts/dat.py update --platform codex --scope project --target /caminho/do/projeto --dry-run
python3 scripts/dat.py update --platform codex --scope project --target /caminho/do/projeto
python3 scripts/dat.py memory show --target /caminho/do/projeto
python3 scripts/dat.py memory add --target /caminho/do/projeto --section DECISIONS --text 'Manter o contrato público existente.' --status APPROVED
python3 scripts/dat.py memory compact --target /caminho/do/projeto
python3 scripts/dat.py memory stale --target /caminho/do/projeto --days 30
python3 scripts/dat.py uninstall --platform codex --scope project --target /caminho/do/projeto
```

O contexto técnico partilhável reside em `.ai-team/context.md`; o contexto operacional privado reside em `.ai-team/context.local.md`. Nenhum pode conter secrets, credenciais ou dados pessoais desnecessários. A partilha é uma opção explícita, através de `--share-context`; `--share-agents` permite partilhar os perfis. Um commit continua a exigir autorização. A desinstalação preserva a memória.

O Team Leader consolida as atualizações. `memory show` apresenta um hash; `memory add --expected-hash HASH` rejeita uma escrita baseada numa versão antiga. A compactação conserva decisões; a deteção por idade assinala informação a rever, sem a declarar automaticamente incorreta. Numa nova sessão, confirme a memória contra o código e os testes atuais.

São permitidas alterações relevantes e testes não destrutivos dentro da tarefa autorizada. Commits, push, pull requests, mudanças arquiteturais significativas, operações destrutivas, produção e recursos pagos relevantes exigem autorização. As permissões reais da plataforma prevalecem. A framework não cria ficheiros de planeamento nos projetos consumidores.

## Validação e contribuição

```sh
python3 scripts/dat.py validate
python3 -m unittest discover -s tests -v
```

Os testes estruturais, de instalação e de contratos não substituem testes nativos nas plataformas. A [compatibilidade](../compatibility.md) identifica o que falta verificar; os [dez exemplos](../../examples/README.md) mostram a coordenação em situações concretas. A documentação pública principal é inglesa. Consulte [contribuições](../contributing.md) e a [licença MIT](../../LICENSE).

A [validação da versão 1.0.0](../validation.md) regista 69 testes locais aprovados
e nove jobs de CI aprovados em Linux, macOS e Windows com Python 3.11–3.13.
No Windows, um dos 69 testes fica explicitamente ignorado por depender de
privilégios para criar symlinks. O Codex executou uma delegação real com definição
canónica fornecida ao subagente; a seleção de perfis TOML pelo nome não ficou
validada. O Claude carregou os dez perfis, mas a invocação ficou bloqueada por
falta de autenticação. Copilot e a importação manual para ChatGPT não foram
executados. Estas limitações fazem parte da entrega.
