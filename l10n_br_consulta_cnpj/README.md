# Consulta CNPJ

Esse módulo realizada a consulta de CNPJ na base do SEFAZ para cadastros que possuem Inscrição Estadual

## Recursos

- Preenche os campo de endereço
- Preenche os campos Inscrição Estadual e Razão Social
- Preenche o campo CNAE Principal (Aba Fiscal)

## Instalação

Este módulo usa a depêndencia [PyTrustNFe](https://github.com/it-brasil/PyTrustNFe/tree/itbrasil) por enquanto.

```sh
pip3 install git+https://github.com/it-brasil/PyTrustNFe.git@itbrasil#egg=pytrustnfe3
```

## TODO
[ ] Integração com API Pública unificada - [CNPJS.ws](https://www.cnpj.ws)
[ ] Criação de um pacote Python

## Restrições

- Nesse momento, o módulo só realizada consultas em algumas bases do SEFAZ (Cadastros com Inscrição Estadual)

## License

AGPL-3
