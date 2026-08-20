# Desktop scripts

Repositorio para organizar scripts locais executados no computador de trabalho.

## Uso

Execute o script principal pelo Python:

```powershell
py .\run.py
```

O `run.py` apenas executa as tarefas em ordem. Caminhos e configuracoes ficam dentro do script de cada tarefa.

As mensagens usam cores no terminal para diferenciar tarefas, avisos, informacoes e sucessos. Defina `NO_COLOR=1` se quiser desativar as cores.

Atalhos globais de cor ficam em `scripts\console.py`: `TASK`, `INFO`, `SUCCESS`, `WARNING`, `ERROR` e os aliases curtos `OK`, `WARN`, `ERR`.

O script de papel de parede escolhe automaticamente uma imagem aleatoria do diretorio `photography` do repositorio `mozartsempiano/wallpapers` e salva uma copia local em `.cache\wallpapers`.

O script de organizacao de downloads usa pastas derivadas do usuario atual: `Path.home() / 'Downloads'` como origem, `Path.home() / 'Pictures'` para imagens e uma subpasta `Fontes` dentro da pasta de downloads para fontes.

## Ordem atual

1. Organiza a pasta de downloads.
2. Altera o papel de parede do Windows.
3. Inicia `Path.home() / 'Downloads' / 'ASF' / 'Core' / 'ArchiSteamFarm.exe`.
4. Inicia `Path.home() / 'Downloads' / 'ASF' / 'ASFclaim' / 'start.bat`.

Antes de abrir ASF ou ASFclaim, o script verifica se eles ja estao em execucao e ignora a etapa para evitar duplicidade.

ASF e ASFclaim abrem em terminais separados. Esses terminais fecham quando os processos terminam. Enquanto eles estiverem abertos, o `run.py` continua aguardando; use `Ctrl+C` no terminal do `run.py` para encerrar as tarefas abertas por ele.

Se ASF ou ASFclaim ja estiverem abertos, o terminal da tarefa pode fechar rapidamente e o `run.py` mostrara que a etapa foi ignorada para evitar duplicidade.

## Scripts individuais

```powershell
py -m scripts.organize_downloads
py -m scripts.set_wallpaper
py -m scripts.start_asf
py -m scripts.start_asfclaim
```
