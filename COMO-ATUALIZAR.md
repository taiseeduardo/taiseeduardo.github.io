# Atualização do site

Para adicionar fotos, coloque os novos originais na pasta do álbum correspondente e execute:

    python3 otimizar-site-dropbox.py

O atualizador guarda os originais na pasta local do Dropbox registrada na configuração, cria cópias menores em fotos-*/_web e atualiza as listas. Aguarde a sincronização do Dropbox. Depois faça Commit e Push pelo GitHub Desktop.

Mantenha o arquivo local .estado-otimizacao-fotos.json. Ele registra os originais e as cópias já processadas. A limpeza não remove nem substitui esse arquivo.

Para editar os links dos originais, use download-originais.json. As permissões de visualização/download são configuradas no Dropbox. O link de recebimento de fotos continua separado.

## Organização

- index.html: conteúdo da página inicial.
- inicio.css / inicio.js: aparência, slides e contagem da página inicial.
- fotos.html / fotos-convidados.html / fotos-enviadas.html: os três álbuns.
- galerias.css: aparência compartilhada dos álbuns.
- galerias-paginadas.js: 50 fotos por página e visualizador com setas.
- idioma.js / galerias-idiomas.js: português e inglês.
- player-musicas.js / player-musicas.css / musicas.json: música e controle entre abas.
- download-originais.js / download-originais.json: botões para o Dropbox.
- otimizar-site-dropbox.py: único atualizador das fotos.

Os códigos ativos de paginação, idiomas, música e download foram mantidos. Os instaladores antigos, três scripts antigos de galeria, backups antigos e fontes sem referência foram retirados para um backup fora do repositório. As duas fontes utilizadas e textos de licença foram mantidos. Nenhuma foto ou música é removida por esta limpeza. As listas JSON existentes também são preservadas.

## Aplicar / desfazer a limpeza

Coloque limpar-site.py junto do index.html e execute:

    python3 limpar-site.py

Antes de mudar os arquivos, o programa cria um backup somente do código afetado em uma pasta ao lado do site. Ele não duplica as fotos nem as músicas. Se os arquivos diferirem da versão auditada, o programa interrompe ou preserva os itens alterados, em vez de sobrescrevê-los sem conferir.

Para desfazer:

    python3 limpar-site.py --desfazer

O programa confere se os arquivos foram modificados depois da limpeza. Se houver alterações posteriores, ele para para não sobrescrever seu trabalho. A limpeza não executa git, Commit ou Push. Desfazer arquivos locais depois de publicar exige outro Commit e Push para restaurar também o site.

## Limites desta revisão

A conferência foi feita nos arquivos enviados em Archive.zip. As fotos de fotos-*/_web e o estado local do otimizador não foram enviados; esses itens serão preservados na instalação. A conversão sips precisa rodar no Mac; o fluxo do atualizador foi verificado com conversão simulada, sem acesso ao seu Dropbox ou às permissões da conta. A limpeza reorganiza o código; a economia de espaço vem principalmente da otimização das fotos já feita.
