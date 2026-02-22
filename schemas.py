from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class RequisicaoLogin(BaseModel):
    usuario: str = Field(..., pattern=r'^BP\d{1,8}[A-Z]?$')
    senha: str

    @field_validator('usuario', mode='before')
    @classmethod
    def formatar_usuario(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

class RespostaLogin(BaseModel):
    sucesso: bool
    mensagem: str | None = None

class DadosPerfil(BaseModel):
    nome_completo: str
    periodo_referencia: str
    ira: str
    url_perfil: Optional[str] = None

class RespostaPerfil(BaseModel):
    sucesso: bool
    perfil: Optional[DadosPerfil] = None
    mensagem: Optional[str] = None

class DadosNota(BaseModel):
    disciplina: str
    area_conhecimento: str
    n1: str
    n2: str
    n3: str
    n4: str
    mfd: str

class RespostaBoletim(BaseModel):
    sucesso: bool
    notas: Optional[List[DadosNota]] = None
    mensagem: Optional[str] = None

class RequisicaoAvancada(BaseModel):
    usuario: str = Field(..., pattern=r'^BP\d{1,8}[A-Z]?$')
    senha: str
    disciplina: str = "todas"

    @field_validator('usuario', mode='before')
    @classmethod
    def formatar_usuario(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

class ItemCriterio(BaseModel):
    disciplina: str
    criterios: Optional[str]
    mensagem: Optional[str]

class RespostaCriterios(BaseModel):
    sucesso: bool
    dados: Optional[List[ItemCriterio]] = None
    mensagem: Optional[str] = None

class ItemAula(BaseModel):
    data: str
    conteudo: str
    metodologia: str

class ItemPlanoAula(BaseModel):
    disciplina: str
    cronograma: Optional[List[ItemAula]]
    mensagem: Optional[str]

class RespostaPlanoAula(BaseModel):
    sucesso: bool
    dados: Optional[List[ItemPlanoAula]] = None
    mensagem: Optional[str] = None

class RespostaDisciplinas(BaseModel):
    sucesso: bool
    disciplinas: Optional[List[str]] = None
    mensagem: Optional[str] = None
