# Development Agent Team — guia em português de Portugal

A versão 1.0.0 disponibiliza dez papéis de engenharia, definições canónicas, adaptadores para Claude Code, Codex, GitHub Copilot e ChatGPT, instalação com deteção de conflitos e memória persistente por projeto. Requer Python 3.11 ou superior e utiliza apenas a biblioteca standard.

O Team Leader coordena o trabalho e é o interlocutor do utilizador. Seleciona apenas os especialistas necessários: Software Architect, UI/UX Designer, Frontend Developer, Backend Developer, Database Engineer, QA/Test Engineer, Security Engineer, DevOps Engineer e Code Review Engineer. Os agentes respondem, por defeito, no idioma do utilizador.

## Para que serve

A framework organiza assistentes de programação numa equipa virtual de engenharia de software. Pode utilizá-la para transformar uma ideia num projeto novo, desenvolver funcionalidades numa aplicação existente, corrigir erros, coordenar revisões e testes ou preparar entregas autorizadas. A memória do projeto conserva decisões aprovadas e contexto relevante para continuar noutra sessão.

Recebe definições dos agentes, adaptadores para as plataformas, ferramentas de instalação e gestão de contexto. A execução decorre na plataforma de IA escolhida, com as ferramentas e permissões efetivamente disponíveis; não exige um servidor permanente da framework.

## Como funciona

1. Descreve ao Team Leader o objetivo, seja uma ideia inicial ou uma tarefa num projeto existente.
2. O Team Leader consulta a informação disponível, esclarece apenas as dúvidas relevantes e coordena as decisões necessárias.
3. Os especialistas adequados implementam ou analisam o trabalho; o Team Leader integra os resultados e verifica as evidências, revisões e testes proporcionais.
4. O Team Leader atualiza o contexto duradouro e apresenta o resultado real, incluindo o que ficou por resolver.

Continua a conversar com o Team Leader, que coordena a participação dos especialistas. O instalador prepara os ficheiros; os agentes trabalham dentro da plataforma. A instalação, por si só, não demonstra execução nativa: consulte a [matriz de compatibilidade](../compatibility.md) para as diferenças e limitações.

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

> Assume o papel de Team Leader da Development Agent Team no modo NEW_PROJECT. Quero criar **[descreve a ideia, o problema e os utilizadores, na medida em que já os conheces]**. Ainda não existe código da aplicação. Ajuda-me a definir os fluxos essenciais, o âmbito do MVP e as restrições. Faz apenas as perguntas importantes que ainda não tenham resposta, em pequenos grupos, antes de recomendar a stack e a arquitetura. Confirma as escolhas relevantes que eu ainda não tenha aprovado antes de criar a estrutura da aplicação ou instalar as suas dependências. Quando essas decisões estiverem resolvidas, coordena a implementação, a revisão e os testes com os especialistas necessários. Não faças commit, push nem pull request sem autorização.

Se a ideia ainda for muito inicial, basta:

> Assume o papel de Team Leader da Development Agent Team. Quero começar um projeto do zero, mas só tenho esta ideia: **[a tua ideia]**. Ajuda-me a clarificá-la e faz as perguntas essenciais antes de propor como a implementar.

A existência de `.codex/`, `.ai-team/`, `AGENTS.md` ou metadados Git não significa que já exista uma aplicação. A ausência de código ou de contexto preenchido é normal neste modo. O Team Leader esclarece o produto, consulta o Software Architect quando útil e só depois encaminha a implementação necessária. Não convoca automaticamente os dez agentes nem cria ficheiros de planeamento no projeto.

### Trabalhar num projeto existente

Descreva a funcionalidade, o erro ou a revisão pretendida, por exemplo:

> Assume o papel de Team Leader da Development Agent Team. Lê as instruções do repositório e o contexto em `.ai-team/context.md`, analisa o código relevante e corrige o erro de validação reportado. Preserva a stack existente. Seleciona apenas os especialistas necessários, verifica as ferramentas reais de delegação e apresenta os testes executados e as limitações. Não faças commit, push nem pull request sem autorização.

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
