# Configuration System overview (infrastructure)

O Sistema de configuração é uma parte crucial para o funcionamento do projeto, sem ele, não poderíamos trocar e nem manter facilmente informações importantes que contribuem para o funcionamento/execução do código.

- A ideia gira quase toda em torno do modelo de configurações, o `ApplicationSettings`, uma dataclass imutável que contém todas as configurações (incluindo detalhes da infraestrutura) que envolvem a aplicação e seu funcionamento.

- O projeto segue como um dos princípios o SRP (Single Responsibility Principle) ou Princípio de Responsabilidade Única, sendo assim, esse sistema se divide em 4 categorias com suas respectivas funções:
    - Factory -> Coordena toda a execução para construir o modelo de configuração
    - Loaders -> Apenas carregam os dados de configuração
    - Parsers -> Convertem dados recebidos em objetos
    - Mappers -> Mapeiam/Constroem o modelo de configuração

- Além disso, a Factory não depende diretamente de nenhuma dependência, ela espera que sejam injetadas suas dependências, facilitando testes e mocks.
    - Obs.: É importante notar que a Factory espera uma implementação/interface de um Config loader, sendo um fator importante para garantir testabilidade e mockagem.

- Essa implementação como já dito antes garante uma ótima testabilidade seguindo princípios modernos de engenharia de software.