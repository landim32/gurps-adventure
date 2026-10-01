#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente do roll6 — a mesa virtual onde a campanha também é jogada.

O roll6 é um ESPELHO do repositório: o que a mesa muda aqui (PV, Fadiga, estado,
posição no mapa) é empurrado para lá. Os scripts das outras skills importam este
módulo; o modelo usa a linha de comando para o que não é automático.

    python .claude/skills/roll6/scripts/roll6.py estado
    python .claude/skills/roll6/scripts/roll6.py chamar list_campaigns '{"mine": true}'
    python .claude/skills/roll6/scripts/roll6.py subir-imagem personagens/x/foto.png --lado 1024
    python .claude/skills/roll6/scripts/roll6.py subir-documento personagens/x/ficha.jpg
    python .claude/skills/roll6/scripts/roll6.py alinhar --indice cenarios/com-grid/estrada.json --modelo 2
    python .claude/skills/roll6/scripts/roll6.py mapa --indice cenarios/com-grid/estrada.json
    python .claude/skills/roll6/scripts/roll6.py saude --pj "Jah Kagadu"

Conexão: ROLL6_URL e ROLL6_API_KEY no ambiente, ou o servidor MCP "roll6" configurado
no ~/.claude.json (a mesma chave que o Claude Code usa). A chave nunca é impressa.
ROLL6_DESLIGADO=1 desliga a sincronização (os scripts seguem gravando só no repositório).

Nada aqui derruba o script que chamou: toda falha vira uma linha "roll6: ..." na saída.
"""
import argparse
import base64
import io
import importlib.util
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# O console do Windows é cp1252 e engasga com seta e travessão — e um print que falha
# DEPOIS de uma chamada que já gravou (process_turn) faz parecer que ela não aconteceu.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Normalização de nome vem da folha `contexto`, como em todo o resto do repo. Carregada
# aqui — e nao no topo com as demais — porque este arquivo e importado por sys.path por
# `campanha`, `atualizar-mapa` e `processar-turno`.
try:
    _espec = importlib.util.spec_from_file_location(
        "contexto", Path(__file__).resolve().parents[2] / "contexto" / "scripts" / "contexto.py")
    _ctx = importlib.util.module_from_spec(_espec)
    _espec.loader.exec_module(_ctx)
except Exception as erro:                                      # nunca derruba quem chamou
    print(f"roll6: sem a folha contexto para slug(): {erro}")

    class _CtxFallback:
        @staticmethod
        def slug(texto):
            return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-",
                                             (texto or "").lower())).strip("-")

    _ctx = _CtxFallback

MAPEAMENTO = Path("campanha/roll6.json")
R6 = 40                      # raio do hexágono no roll6 (centro ao canto, px) — HexGrid.HEX_SIZE
LOOK = {"N": 0, "NE": 1, "SE": 2, "S": 3, "SW": 4, "NW": 5}
STATUS_MAX = 260


class Roll6Erro(Exception):
    pass


def slug(texto):
    """Mesma normalização da folha `contexto` — `processar-turno` chama isto 8 vezes,
    então o nome fica e a implementação passa a ser uma só."""
    return _ctx.slug(texto)


def desligado():
    return os.environ.get("ROLL6_DESLIGADO", "").strip() not in ("", "0")


def aviso(msg):
    print(f"roll6: {msg}")


# --- conexão ------------------------------------------------------------------

def _config():
    url, chave = os.environ.get("ROLL6_URL"), os.environ.get("ROLL6_API_KEY")
    if url and chave:
        return url, {"X-Api-Key": chave}
    f = Path.home() / ".claude.json"
    if not f.is_file():
        raise Roll6Erro("sem ROLL6_URL/ROLL6_API_KEY e sem ~/.claude.json")

    def achar(o):
        if isinstance(o, dict):
            s = o.get("roll6")
            if isinstance(s, dict) and s.get("url"):
                return s
            for v in o.values():
                r = achar(v)
                if r:
                    return r
        return None

    srv = achar(json.loads(f.read_text(encoding="utf-8")))
    if not srv:
        raise Roll6Erro("servidor MCP 'roll6' não está configurado no ~/.claude.json")
    return srv["url"], dict(srv.get("headers") or {})


class Cliente:
    """Fala MCP por HTTP (streamable): initialize uma vez, depois tools/call."""

    def __init__(self):
        self.url, self.cab = _config()
        self.sessao = None
        self._n = 0
        self._rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                 "clientInfo": {"name": "gurps-adventure", "version": "1"}})
        self._rpc("notifications/initialized", {}, notificacao=True)

    def _rpc(self, metodo, params, notificacao=False):
        corpo = {"jsonrpc": "2.0", "method": metodo, "params": params}
        if not notificacao:
            self._n += 1
            corpo["id"] = self._n
        cab = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream",
               "User-Agent": "gurps-adventure/1.0", **self.cab}
        if self.sessao:
            cab["Mcp-Session-Id"] = self.sessao
        req = urllib.request.Request(self.url, json.dumps(corpo).encode(), cab)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                self.sessao = r.headers.get("Mcp-Session-Id") or self.sessao
                txt = r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raise Roll6Erro(f"HTTP {e.code} em {metodo}")
        except urllib.error.URLError as e:
            raise Roll6Erro(f"sem conexão ({e.reason})")
        if notificacao:
            return None
        for linha in txt.splitlines():          # resposta em SSE: a última linha data:
            if linha.startswith("data:"):
                txt = linha[5:]
        return json.loads(txt) if txt.strip() else None

    def chamar(self, ferramenta, argumentos=None):
        r = self._rpc("tools/call", {"name": ferramenta, "arguments": argumentos or {}})
        if "error" in r:
            raise Roll6Erro(f"{ferramenta}: {r['error'].get('message')}")
        res = r["result"]
        txt = res["content"][0]["text"] if res.get("content") else ""
        if res.get("isError") or txt.startswith('{"status":'):
            raise Roll6Erro(f"{ferramenta}: {txt[:300]}")
        try:
            return json.loads(txt)
        except ValueError:
            return txt


_cliente = None


def cliente():
    global _cliente
    if _cliente is None:
        _cliente = Cliente()
    return _cliente


def lista(r):
    """Umas ferramentas devolvem a lista crua, as paginadas devolvem {"items": [...]}."""
    return r["items"] if isinstance(r, dict) and "items" in r else (r or [])


# --- o mapeamento repositório → roll6 -----------------------------------------

def mapeamento(raiz):
    f = Path(raiz) / MAPEAMENTO
    if not f.is_file():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def nome_no_roll6(mapa, nome):
    """O nome local pode ter apelido no roll6 ("Sir William" → "Lorde William de Wallace")."""
    ap = {slug(k): v for k, v in (mapa.get("apelidos") or {}).items()}
    return ap.get(slug(nome), nome)


def rotulo_para_xy(rotulo, desloc=(0, 0)):
    """"P7" → (15, 6): letras são a coluna (A=0 … Z=25, AA=26), número é a linha (1 = 0)."""
    m = re.fullmatch(r"([A-Za-z]+)(\d+)", rotulo.strip())
    if not m:
        raise ValueError(rotulo)
    col = 0
    for ch in m.group(1).upper():
        col = col * 26 + (ord(ch) - 64)
    return col - 1 + desloc[0], int(m.group(2)) - 1 + desloc[1]


def xy_para_rotulo(x, y, desloc=(0, 0)):
    """(15, 6) → "P7" — o inverso de rotulo_para_xy."""
    col, letras = x - desloc[0] + 1, ""
    while col > 0:
        col, resto = divmod(col - 1, 26)
        letras = chr(65 + resto) + letras
    return f"{letras}{y - desloc[1] + 1}"


LOOK_NOME = {v: k for k, v in LOOK.items()}


# --- imagens e documentos -----------------------------------------------------

def subir_imagem(caminho, lado=1024, formato=None):
    """Reduz (lado maior) e sobe. PNG com transparência continua PNG; o resto vira JPG."""
    from PIL import Image
    im = Image.open(caminho)
    im.thumbnail((lado, lado))
    png = formato == "png" or (formato is None and im.mode in ("RGBA", "LA", "P"))
    buf = io.BytesIO()
    if png:
        im.save(buf, "PNG", optimize=True)
    else:
        im.convert("RGB").save(buf, "JPEG", quality=88)
    nome = Path(caminho).stem + (".png" if png else ".jpg")
    return cliente().chamar("upload_image", {
        "fileName": nome, "contentBase64": base64.b64encode(buf.getvalue()).decode()})["fileName"]


def subir_documento(caminhos):
    """Uma imagem sobe como está; duas ou mais viram um PDF (ficha + grimório)."""
    from PIL import Image
    caminhos = [Path(c) for c in caminhos]
    if len(caminhos) == 1 and caminhos[0].suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".pdf"):
        dado, nome = caminhos[0].read_bytes(), caminhos[0].name
    else:
        pags = [Image.open(c).convert("RGB") for c in caminhos]
        buf = io.BytesIO()
        pags[0].save(buf, "PDF", save_all=True, append_images=pags[1:], resolution=300, quality=85)
        dado, nome = buf.getvalue(), caminhos[0].stem + ".pdf"
    return cliente().chamar("upload_document", {
        "fileName": nome, "contentBase64": base64.b64encode(dado).decode()})["fileName"]


# --- grade: alinhar o modelo de mapa ao grid local ----------------------------

def alinhamento(indice):
    """Parâmetros do modelo do roll6 para que coluna/linha lá = coluna/linha do grid local.

    Grid local (add-grid-hex): topo chato, hexágono de altura metro_px, A1 centrado em
    `origem`. roll6: raio fixo de 40 px, hex (0,0) centrado em (40, 20·√3), imagem
    desenhada em (−imageLeft, −imageTop). Escala = raio roll6 / raio local.
    """
    d = json.loads(Path(indice).read_text(encoding="utf-8"))
    raio_local = d["metro_px"] / math.sqrt(3)
    s = R6 / raio_local
    ox, oy = (d.get("origem") or [0, 0])[:2]
    return {"imageWidth": round(d["largura_px"] * s), "imageHeight": round(d["altura_px"] * s),
            "imageLeft": round(s * ox - R6), "imageTop": round(s * oy - R6 * math.sqrt(3) / 2),
            "gridWidth": d["colunas"], "gridHeight": d["linhas"]}


# --- sincronizações -----------------------------------------------------------

def _pecas(mapa_id):
    return lista(cliente().chamar("list_map_tokens", {"mapId": mapa_id}))


def _gravar_peca(p, **mudar):
    """Posição e frente sem registrar movimento no turno (update_map_token). Nas peças de
    personagem e de NPC só x/y/look contam: o resto a tela lê da participação/ocorrência."""
    v = {**p, **mudar}
    cliente().chamar("update_map_token", {
        "mapTokenId": p["mapTokenId"], "name": v["name"], "tokenType": v["tokenType"],
        "sheet": v.get("sheet"), "life": v.get("life") or 0, "energy": v.get("energy") or 0,
        "status": v.get("status"), "move": v.get("move") or 0,
        "x": v["x"], "y": v["y"], "look": v.get("look")})


def sincronizar_mapa(raiz, indice, ocupacao):
    """Empurra a ocupação local (hex, frente) para o mapa do roll6 ligado a este índice."""
    if desligado():
        return
    try:
        m = mapeamento(raiz)
        rel = Path(indice).resolve().relative_to(Path(raiz).resolve()).as_posix() \
            if Path(indice).is_absolute() else Path(indice).as_posix()
        ligado = (m or {}).get("mapas", {}).get(rel)
        if not ligado:
            return aviso(f"{rel} não está ligado a um mapa (campanha/roll6.json → mapas); nada sincronizado.")
        mapa_id, desloc = ligado["mapId"], tuple(ligado.get("deslocamento") or (0, 0))
        pecas = {slug(p["name"]): p for p in _pecas(mapa_id)}
        participacoes = {slug(c["characterName"]): c for c in lista(cliente().chamar(
            "list_campaign_characters", {"campaignId": m["campaignId"]})) if c["status"] == 3}
        npcs_camp = {slug(n["name"]): n for n in lista(cliente().chamar(
            "list_campaign_npcs", {"campaignId": m["campaignId"]}))}
        vistos, feitos = set(), []
        for rot, o in ocupacao.items():
            nome = nome_no_roll6(m, o.get("quem", ""))
            x, y = rotulo_para_xy(rot, desloc)
            look = LOOK.get(o.get("frente"))
            p = pecas.get(slug(nome))
            if p:
                vistos.add(slug(nome))
                if (p["x"], p["y"]) != (x, y) or (look is not None and p.get("look") != look):
                    _gravar_peca(p, x=x, y=y, look=look if look is not None else p.get("look"))
                    feitos.append(f"{nome} → ({x},{y})")
            elif o.get("tipo") == "pj" and slug(nome) in participacoes:
                nova = cliente().chamar("place_character_on_map", {
                    "mapId": mapa_id, "campaignCharacterId": participacoes[slug(nome)]["campaignCharacterId"],
                    "x": x, "y": y})
                if look is not None:
                    _gravar_peca(nova, look=look)
                feitos.append(f"{nome} posto em ({x},{y})")
            elif o.get("tipo") == "npc" and slug(nome) in npcs_camp:
                cliente().chamar("place_npc_on_map", {"mapId": mapa_id, "npcId": npcs_camp[slug(nome)]["npcId"],
                                                      "x": x, "y": y, "look": look})
                feitos.append(f"{nome} posto em ({x},{y})")
            else:
                feitos.append(f"{o.get('quem')} sem peça no roll6 (cavalo, objeto ou nome sem cadastro) — ignorado")
        fora = [p["name"] for s, p in pecas.items() if s not in vistos and p["tokenType"] in (1, 2)]
        aviso(f"mapa {mapa_id}: " + ("; ".join(feitos) if feitos else "nada mudou"))
        if fora:
            aviso("saíram do mapa local e continuam no roll6 (não apago peça sozinho): " + ", ".join(fora))
    except Exception as e:                      # nunca derruba quem chamou
        aviso(f"mapa não sincronizado — {e}")


def _achar_participacao(m, nome):
    for c in lista(cliente().chamar("list_campaign_characters", {"campaignId": m["campaignId"]})):
        if slug(c["characterName"]) == slug(nome) and c["status"] == 3:
            return c
    return None


def _achar_ocorrencias(m, nome):
    """Ocorrências de NPC com este nome em todos os mapas ativos da campanha."""
    achadas = []
    for mp in lista(cliente().chamar("list_campaign_maps", {"campaignId": m["campaignId"]})):
        for o in lista(cliente().chamar("list_map_npcs", {"mapId": mp["mapId"]})):
            if slug(o["name"]) == slug(nome):
                achadas.append((mp["mapId"], o))
    return achadas


def sincronizar_saude(raiz, secao, nome, pv, fadiga, estados, mexeu_estado):
    """PJ → update_participation (PV, Fadiga e, se o estado mudou, o status).
    NPC → update_map_npc de cada ocorrência (PV = total do NPC + o acumulado).

    pv/fadiga: para PJ, o valor atual; para NPC, o acumulado (negativo) do saude.md.
    """
    if desligado():
        return
    try:
        m = mapeamento(raiz)
        if not m:
            return aviso("sem campanha/roll6.json; saúde não sincronizada.")
        alvo = nome_no_roll6(m, nome)
        status = ("; ".join(estados) or None) if mexeu_estado else "__manter__"
        if status not in (None, "__manter__") and len(status) > STATUS_MAX:
            status = status[:STATUS_MAX - 1] + "…"
        if secao == "pj":
            c = _achar_participacao(m, alvo)
            if not c:
                return aviso(f"{alvo} não tem participação aprovada na campanha {m['campaignId']}.")
            atual = cliente().chamar("get_participation", {"campaignCharacterId": c["campaignCharacterId"]})
            cliente().chamar("update_participation", {
                "campaignCharacterId": c["campaignCharacterId"],
                "currentLife": pv if pv is not None else atual["currentLife"],
                "currentEnergy": fadiga if fadiga is not None else atual["currentEnergy"],
                "characterStatus": atual.get("characterStatus") if status == "__manter__" else status,
                "sheet": atual.get("sheet")})
            return aviso(f"{alvo}: PV {pv}, energia {fadiga}" + ("" if status == "__manter__" else f", status «{status or ''}»"))
        ocorr = _achar_ocorrencias(m, alvo)
        if not ocorr:
            return aviso(f"{alvo} não está em nenhum mapa da campanha; nada sincronizado.")
        for mapa_id, o in ocorr:
            vida = o["totalLife"] + (pv or 0)          # o saude.md de NPC guarda o acumulado
            st = o.get("status") if status == "__manter__" else status
            cliente().chamar("update_map_npc", {"mapNpcId": o["mapNpcId"], "name": o["name"],
                                                "currentLife": vida, "currentEnergy": o["currentEnergy"],
                                                "status": st})
            aviso(f"{alvo} (mapa {mapa_id}): PV {vida}/{o['totalLife']}"
                  + ("" if status == "__manter__" else f", status «{st or ''}»"))
    except Exception as e:
        aviso(f"saúde não sincronizada — {e}")


# --- linha de comando ---------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Cliente do roll6 (espelho da mesa).")
    ap.add_argument("--raiz", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("estado", help="Testa a conexão e mostra o mapeamento")
    s = sub.add_parser("chamar", help="Chama qualquer ferramenta: chamar <nome> '<json>'")
    s.add_argument("ferramenta")
    s.add_argument("argumentos", nargs="?", default="{}")
    s = sub.add_parser("subir-imagem", help="Reduz e sobe; imprime o fileName")
    s.add_argument("arquivo")
    s.add_argument("--lado", type=int, default=1024)
    s.add_argument("--formato", choices=("png", "jpg"))
    s = sub.add_parser("subir-documento", help="Sobe ficha (imagem/PDF); 2+ arquivos viram um PDF")
    s.add_argument("arquivos", nargs="+")
    s = sub.add_parser("alinhar", help="Ajusta o modelo de mapa ao grid local (coluna/linha iguais)")
    s.add_argument("--indice", required=True)
    s.add_argument("--modelo", type=int, required=True)
    s.add_argument("--linhas-extras", type=int, default=0,
                   help="Linhas de grid além da arte (corridas que saem pela borda)")
    s = sub.add_parser("mapa", help="Empurra a ocupação do índice local para o roll6")
    s.add_argument("--indice", required=True)
    s = sub.add_parser("saude", help="Empurra a saúde de um PJ/NPC do saude.md para o roll6")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--pj")
    g.add_argument("--npc")
    s.add_argument("--com-estado", action="store_true",
                   help="Reescreve também o status com os estados ativos do saude.md")
    a = ap.parse_args()
    raiz = Path(a.raiz).resolve()

    try:
        if a.cmd == "estado":
            eu = cliente().chamar("get_my_profile")
            print(f"Conectado como {eu.get('name')} (userId {eu.get('userId')}).")
            print(json.dumps(mapeamento(raiz), ensure_ascii=False, indent=2)
                  if mapeamento(raiz) else f"Sem {MAPEAMENTO}.")
        elif a.cmd == "chamar":
            print(json.dumps(cliente().chamar(a.ferramenta, json.loads(a.argumentos)),
                             ensure_ascii=False, indent=2))
        elif a.cmd == "subir-imagem":
            print(subir_imagem(a.arquivo, a.lado, a.formato))
        elif a.cmd == "subir-documento":
            print(subir_documento(a.arquivos))
        elif a.cmd == "alinhar":
            mod = cliente().chamar("get_map_model", {"mapModelId": a.modelo})
            al = alinhamento(a.indice)
            al["gridHeight"] += a.linhas_extras
            novo = cliente().chamar("update_map_model", {
                "mapModelId": a.modelo, "name": mod["name"], "description": mod.get("description"),
                "image": mod.get("image"), **al})
            print(json.dumps({k: novo[k] for k in al}, indent=2))
        elif a.cmd == "mapa":
            d = json.loads(Path(a.indice).read_text(encoding="utf-8"))
            sincronizar_mapa(raiz, a.indice, d.get("ocupacao") or {})
        elif a.cmd == "saude":
            sys.path.insert(0, str(raiz / ".claude/skills/campanha/scripts"))
            import campanha as cp
            p = cp.exige_campanha(raiz)
            quem = a.pj or a.npc
            titulo = "Personagens" if a.pj else "NPCs"
            ls = next((ls for sec, n, ls in cp.ler_saude(p / cp.SAUDE)
                       if sec == titulo and slug(n) == slug(quem)), None)
            if ls is None:
                raise SystemExit(f"{quem} não está no saude.md.")
            pv_max, fad_max = cp.maximos_da_ficha(raiz, quem) if a.pj else (None, None)
            pv = sum(v for _, t, v, _ in ls if t == "PV" and v is not None)
            fad = sum(v for _, t, v, _ in ls if t == "FAD" and v is not None)
            _, _, estados = cp.resumo_saude(ls, pv_max, fad_max)
            if a.pj:
                sincronizar_saude(raiz, "pj", quem, pv_max + pv, fad_max + fad, estados, a.com_estado)
            else:
                sincronizar_saude(raiz, "npc", quem, pv, None, estados, a.com_estado)
    except Roll6Erro as e:
        raise SystemExit(f"roll6: {e}")


if __name__ == "__main__":
    main()
