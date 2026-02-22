from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import scraper
import schemas
import csv
import io

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/validar-login", response_model=schemas.RespostaLogin)
@limiter.limit("5/minute")
async def validar_login(request: Request, body: schemas.RequisicaoLogin):
    try:
        resultado = await scraper.validar_login(body.usuario, body.senha)
        return resultado
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}

@app.post("/boletim")
@limiter.limit("5/minute")
async def obter_boletim(request: Request, body: schemas.RequisicaoLogin):
    try:
        resultado = await scraper.obter_boletim(body.usuario, body.senha)
        if not resultado["sucesso"]:
             return JSONResponse(status_code=400, content=resultado)
        
        output = io.StringIO()
        escritor = csv.writer(output)
        escritor.writerow(["Área de Conhecimento", "Disciplina", "N1", "N2", "N3", "N4", "MFD"])
        
        for n in resultado["notas"]:
            escritor.writerow([
                n["area_conhecimento"],
                n["disciplina"],
                n["n1"], 
                n["n2"], 
                n["n3"], 
                n["n4"],
                n["mfd"]
            ])
            
        return Response(content=output.getvalue(), media_type="text/csv")
    except Exception as e:
        return JSONResponse(status_code=500, content={"sucesso": False, "mensagem": str(e)})

@app.post("/perfil", response_model=schemas.RespostaPerfil)
@limiter.limit("5/minute")
async def obter_perfil(request: Request, body: schemas.RequisicaoLogin):
    try:
        resultado = await scraper.obter_perfil(body.usuario, body.senha)
        return resultado
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}

@app.post("/criterios-avaliacao", response_model=schemas.RespostaCriterios)
@limiter.limit("5/minute")
async def obter_criterios(request: Request, body: schemas.RequisicaoAvancada):
    try:
        resultado = await scraper.obter_criterios(body.usuario, body.senha, body.disciplina)
        return resultado
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}

@app.post("/plano-de-aulas")
@limiter.limit("5/minute")
async def obter_plano_de_aulas(request: Request, body: schemas.RequisicaoAvancada):
    try:
        resultado = await scraper.obter_plano_de_aulas(body.usuario, body.senha, body.disciplina)
        if not resultado["sucesso"]:
             return JSONResponse(status_code=400, content=resultado)
        
        output = io.StringIO()
        escritor = csv.writer(output)
        escritor.writerow(["Disciplina", "Data", "Conteúdo", "Metodologia", "Mensagem"])
        
        for item in resultado["dados"]:
            disciplina = item["disciplina"]
            msg = item.get("mensagem", "")
            cronograma = item.get("cronograma", [])
            
            if cronograma:
                for aula in cronograma:
                    escritor.writerow([
                        disciplina,
                        aula["data"],
                        aula["conteudo"],
                        aula["metodologia"],
                        msg
                    ])
            else:
                escritor.writerow([disciplina, "", "", "", msg])
            
        return Response(content=output.getvalue(), media_type="text/csv")
    except Exception as e:
        return JSONResponse(status_code=500, content={"sucesso": False, "mensagem": str(e)})

@app.post("/disciplinas", response_model=schemas.RespostaDisciplinas)
@limiter.limit("5/minute")
async def listar_disciplinas(request: Request, body: schemas.RequisicaoLogin):
    try:
        resultado = await scraper.obter_disciplinas(body.usuario, body.senha)
        if not resultado.get("sucesso"):
             return JSONResponse(status_code=400, content=resultado)
        return resultado
    except Exception as e:
        return JSONResponse(status_code=500, content={"sucesso": False, "mensagem": str(e)})

@app.get("/health")
@limiter.limit("100/minute")
async def verificacao_saude(request: Request):
    return {"status": "ativo"}
