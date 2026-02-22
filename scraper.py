from playwright.async_api import async_playwright
import re

async def validar_login(usuario, senha):
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        contexto = await navegador.new_context()
        pagina = await contexto.new_page()

        try:
            await pagina.goto("https://suap.ifsp.edu.br/accounts/login/")
            await pagina.fill("#id_username", usuario)
            await pagina.fill("#id_password", senha)
            await pagina.click('input[type="submit"]')

            await pagina.wait_for_load_state('networkidle')

            if pagina.url == "https://suap.ifsp.edu.br/" or "dashboard" in pagina.url or "inicio" in pagina.url:
                conteudo = await pagina.content()
                if "Sair" in conteudo or "Meus Dados" in conteudo:
                     await navegador.close()
                     return {"sucesso": True, "mensagem": "Login realizado com sucesso"}

            mensagem_erro = await pagina.locator(".errornote").text_content() if await pagina.locator(".errornote").count() > 0 else "Falha no login ou credenciais inválidas"
            
            await navegador.close()
            return {"sucesso": False, "mensagem": mensagem_erro.strip()}

        except Exception as e:
            await navegador.close()
            return {"sucesso": False, "mensagem": str(e)}

async def obter_boletim(usuario, senha):
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        contexto = await navegador.new_context()
        pagina = await contexto.new_page()

        try:
            await pagina.goto("https://suap.ifsp.edu.br/accounts/login/")
            await pagina.fill("#id_username", usuario)
            await pagina.fill("#id_password", senha)
            await pagina.click('input[type="submit"]')
            await pagina.wait_for_load_state('networkidle')

            if "dashboard" not in pagina.url and "inicio" not in pagina.url and pagina.url != "https://suap.ifsp.edu.br/":
                 await navegador.close()
                 return {"sucesso": False, "mensagem": "Falha no login"}

            await pagina.goto(f"https://suap.ifsp.edu.br/edu/aluno/{usuario}/?tab=boletim")
            
            seletor_tabela = "table:has-text('Disciplina')"
            await pagina.wait_for_selector(seletor_tabela, timeout=10000)
            linhas = await pagina.locator(f"{seletor_tabela} tbody tr").all()
            notas = []

            for linha in linhas:
                colunas = await linha.locator("td").all()
                if len(colunas) < 10:
                    continue
                
                texto_primeira_col = (await colunas[0].inner_text()).strip()
                if not texto_primeira_col.isdigit():
                    continue

                async def obter_texto_seguro(indice):
                    if indice < len(colunas):
                        texto = await colunas[indice].inner_text()
                        t = texto.strip()
                        return "null" if t == "-" or t == "" else t
                    return "null"

                area_conhecimento = (await colunas[1].inner_text()).strip().replace("\n", " ")
                
                nome_disciplina_bruto = (await colunas[2].inner_text()).strip()
                
                nome_disciplina_limpo = re.sub(r'\s+\d+(?=:|$)', '', nome_disciplina_bruto)
                
                dados_nota = {
                    "disciplina": nome_disciplina_limpo,
                    "area_conhecimento": area_conhecimento,
                    "n1": await obter_texto_seguro(9),
                    "n2": await obter_texto_seguro(11),
                    "n3": await obter_texto_seguro(13),
                    "n4": await obter_texto_seguro(15),
                    "mfd": await obter_texto_seguro(20)
                }
                notas.append(dados_nota)

            await navegador.close()
            return {"sucesso": True, "notas": notas}

        except Exception as e:
            await navegador.close()
            return {"sucesso": False, "mensagem": str(e)}

async def obter_perfil(usuario, senha):
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        contexto = await navegador.new_context()
        pagina = await contexto.new_page()

        try:
            await pagina.goto("https://suap.ifsp.edu.br/accounts/login/")
            await pagina.fill("#id_username", usuario)
            await pagina.fill("#id_password", senha)
            await pagina.click('input[type="submit"]')
            await pagina.wait_for_load_state('networkidle')

            if "dashboard" not in pagina.url and "inicio" not in pagina.url and pagina.url != "https://suap.ifsp.edu.br/":
                 await navegador.close()
                 return {"sucesso": False, "mensagem": "Falha no login"}

            url_pagina_perfil = f"https://suap.ifsp.edu.br/edu/aluno/{usuario}/"
            await pagina.goto(url_pagina_perfil)
            
            nome = await pagina.get_by_text("Nome", exact=True).locator("xpath=following-sibling::td").first.inner_text()
            periodo = await pagina.get_by_text("Período Referência", exact=True).locator("xpath=following-sibling::td").first.inner_text()
            ira = await pagina.get_by_text("I.R.A.", exact=True).locator("xpath=following-sibling::td").first.inner_text()
            
            elemento_img = pagina.locator(".photo-circle.big img")
            if await elemento_img.count() > 0:
                url_imagem_perfil = await elemento_img.get_attribute("src")
                if url_imagem_perfil and not url_imagem_perfil.startswith("http"):
                    url_imagem_perfil = "https://suap.ifsp.edu.br" + url_imagem_perfil
            else:
                url_imagem_perfil = None

            dados_perfil = {
                "nome_completo": nome.strip(),
                "periodo_referencia": periodo.strip(),
                "ira": ira.strip(),
                "url_perfil": url_imagem_perfil
            }

            await navegador.close()
            return {"sucesso": True, "perfil": dados_perfil}

        except Exception as e:
            await navegador.close()
            return {"sucesso": False, "mensagem": str(e)}

async def obter_links_diarios(pagina):

    links = {}
    seletor_tabela = "table:has-text('Disciplina')"
    try:
        await pagina.wait_for_selector(seletor_tabela, timeout=5000)
    except:
        return links 

    linhas = await pagina.locator(f"{seletor_tabela} tbody tr").all()
    
    for linha in linhas:
        colunas = await linha.locator("td").all()
        if len(colunas) < 3:
            continue
            
        try:
            elemento_link = colunas[0].locator("a")
            if await elemento_link.count() == 0:
                continue
                
            href = await elemento_link.get_attribute("href")
            disciplina_bruta = (await colunas[2].inner_text()).strip()
            
            if href:
                url_completa = "https://suap.ifsp.edu.br" + href if not href.startswith("http") else href
                links[disciplina_bruta] = url_completa
        except:
            continue
            
    return links

async def raspar_dados_plano_aula(pagina, url_diario):
    try:
        await pagina.goto(url_diario)
        
        btn_plano = pagina.locator("a:has-text('Visualizar Plano de Aulas')")
        
        if await btn_plano.count() == 0:
            return {
                "status": "indisponivel",
                "mensagem": "Ainda não foi disponibilizado o plano de aulas para este componente curricular"
            }
        
        await btn_plano.click()
        
        try:
            await pagina.wait_for_selector("div.tinner", timeout=5000)
        except:
            return {"status": "erro", "mensagem": "Falha ao carregar o modal do plano de aulas"}

        dados = {"status": "disponivel", "criterios": "", "cronograma": []}
        
        div_conteudo = pagina.locator("div.tinner")
        
        if await div_conteudo.count() > 0:
            texto_completo = await div_conteudo.inner_text()
            
            if "Instrumentos e Critérios de Avaliação da Aprendizagem" in texto_completo:
                partes = texto_completo.split("Instrumentos e Critérios de Avaliação da Aprendizagem")
                if len(partes) > 1:
                    parte_criterios = partes[1].split("Desenvolvimento das Aulas")[0]
                    dados["criterios"] = parte_criterios.strip()
        
        linhas_cronograma = await pagina.locator("div.tinner table tbody tr").all()
        
        for linha in linhas_cronograma:
            colunas = await linha.locator("td").all()
            if len(colunas) >= 3:
                dados_linha = {
                    "data": (await colunas[1].inner_text()).strip(),
                    "conteudo": (await colunas[2].inner_text()).strip(),
                    "metodologia": (await colunas[3].inner_text()).strip() if len(colunas) > 3 else ""
                }
                dados["cronograma"].append(dados_linha)
                
        return dados
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

async def obter_criterios(usuario, senha, disciplina="todas"):
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        contexto = await navegador.new_context()
        pagina = await contexto.new_page()

        try:
            await pagina.goto("https://suap.ifsp.edu.br/accounts/login/")
            await pagina.fill("#id_username", usuario)
            await pagina.fill("#id_password", senha)
            await pagina.click('input[type="submit"]')
            await pagina.wait_for_load_state('networkidle')
            
            if "dashboard" not in pagina.url and "inicio" not in pagina.url and pagina.url != "https://suap.ifsp.edu.br/":
                 await navegador.close()
                 return {"sucesso": False, "mensagem": "Falha no login"}

            await pagina.goto(f"https://suap.ifsp.edu.br/edu/aluno/{usuario}/?tab=boletim")
            
            links = await obter_links_diarios(pagina)
            
            resultados = []
            alvos = links.keys() if disciplina in ["todas", "all"] else [disciplina]
            
            if disciplina not in ["todas", "all"] and disciplina not in links:
                 encontrado = False
                 for k in links.keys():
                     if disciplina.lower() in k.lower():
                         alvos = [k]
                         encontrado = True
                         break
                 if not encontrado:
                     await navegador.close()
                     return {"sucesso": False, "mensagem": f"Disciplina '{disciplina}' não encontrada"}

            for materia in alvos:
                url = links[materia]
                dados_plano = await raspar_dados_plano_aula(pagina, url)
                
                resultado = {
                    "disciplina": materia,
                    "criterios": dados_plano.get("criterios"),
                    "mensagem": dados_plano.get("mensagem")
                }
                resultados.append(resultado)

            await navegador.close()
            return {"sucesso": True, "dados": resultados}

        except Exception as e:
            await navegador.close()
            return {"sucesso": False, "mensagem": str(e)}

async def obter_plano_de_aulas(usuario, senha, disciplina="todas"):
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        contexto = await navegador.new_context()
        pagina = await contexto.new_page()

        try:
            await pagina.goto("https://suap.ifsp.edu.br/accounts/login/")
            await pagina.fill("#id_username", usuario)
            await pagina.fill("#id_password", senha)
            await pagina.click('input[type="submit"]')
            await pagina.wait_for_load_state('networkidle')
            
            if "dashboard" not in pagina.url and "inicio" not in pagina.url and pagina.url != "https://suap.ifsp.edu.br/":
                 await navegador.close()
                 return {"sucesso": False, "mensagem": "Falha no login"}

            await pagina.goto(f"https://suap.ifsp.edu.br/edu/aluno/{usuario}/?tab=boletim")
            
            links = await obter_links_diarios(pagina)
            
            resultados = []
            alvos = links.keys() if disciplina in ["todas", "all"] else [disciplina]
            
            if disciplina not in ["todas", "all"] and disciplina not in links:
                 encontrado = False
                 for k in links.keys():
                     if disciplina.lower() in k.lower():
                         alvos = [k]
                         encontrado = True
                         break
                 if not encontrado:
                     await navegador.close()
                     return {"sucesso": False, "mensagem": f"Disciplina '{disciplina}' não encontrada"}

            for materia in alvos:
                url = links[materia]
                dados_plano = await raspar_dados_plano_aula(pagina, url)
                
                resultado = {
                    "disciplina": materia,
                    "cronograma": dados_plano.get("cronograma", []),
                    "mensagem": dados_plano.get("mensagem")
                }
                resultados.append(resultado)

            await navegador.close()
            return {"sucesso": True, "dados": resultados}

        except Exception as e:
            await navegador.close()
            return {"sucesso": False, "mensagem": str(e)}

async def obter_disciplinas(usuario, senha):
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        contexto = await navegador.new_context()
        pagina = await contexto.new_page()

        try:
            await pagina.goto("https://suap.ifsp.edu.br/accounts/login/")
            await pagina.fill("#id_username", usuario)
            await pagina.fill("#id_password", senha)
            await pagina.click('input[type="submit"]')
            await pagina.wait_for_load_state('networkidle')
            
            if "dashboard" not in pagina.url and "inicio" not in pagina.url and pagina.url != "https://suap.ifsp.edu.br/":
                 await navegador.close()
                 return {"sucesso": False, "mensagem": "Falha no login"}

            await pagina.goto(f"https://suap.ifsp.edu.br/edu/aluno/{usuario}/?tab=boletim")
            
            links = await obter_links_diarios(pagina)
            
            await navegador.close()
            return {"sucesso": True, "disciplinas": list(links.keys())}
        except Exception as e:
            await navegador.close()
            return {"sucesso": False, "mensagem": str(e)}
