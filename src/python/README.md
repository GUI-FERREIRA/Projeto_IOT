# Parte feita em python da aplicação

## Interface web
Deve acessar o gerenciador 
e mostrar as tomadas disponiveis 
se estão acesas ou apagadas 

Um botao para ativar ou desativar

A funcionalidade de adicionar uma nova lampada


## Gerenciador
Deve ser responsavel por gerenciar quais tomadas deverao ser ligadas
´´´ python
 changePlug(id,state)
 
 getPlugs()--> dict 
 
 getAvailablePlugs()--> iterable [int]
 registerPlug(name:str,plug:int)
´´´

## Comunicação
deve fornecer os metodos

´´´ python
 send(msg:str)--> Bool
 receiveListener(listener:func(str))
´´´

onde o metodo send envia uma mensagem do tipo string

o metodo receiveListener adiciona uma escuta para quando receber uma mensagem chamar uma funcao

