#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leitor de .glb (glTF 2.0 binário) e esqueleto posável — só numpy e Pillow.

Lê malhas (posições, normais, UVs, juntas e pesos, cor base e textura), a hierarquia de nós e a
pele (skin) de um modelo Mixamo, e sabe **deformar** a malha com a mesma convenção do formato
"roll6-animation" (skill `criar-animacao`): giros em graus sobre X, depois Y, depois Z, no
referencial do personagem (+X esquerda dele, +Y cima, +Z frente), sobre a pose de descanso do osso.

Uso como biblioteca (importado por renderizar.py e gerar.py, da mesma pasta):

    modelo = glb.carregar("orc.glb")
    malha = modelo.deformar({"Spine": [10, 0, 0]}, hips_lift=0.0)
"""
import io
import json
import math
import re
import struct
from pathlib import Path

import numpy as np
from PIL import Image

_COMPONENTES = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16,
                5125: np.uint32, 5126: np.float32}
_NUM = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}
_PREFIXO = re.compile(r"^mixamorig\d*[:_]?")

#: Direção para onde o Roll6 leva o braço ("pendurado relaxado"): tabela D0 do código dele.
#: O osso do braço gira da direção em que aponta no descanso até aqui — só quando a animação
#: tem trilha para ele, e só ele (o antebraço e a mão vão junto, pela hierarquia).
BRACO_ALVO = {"Left": (0.3, -1.0, 0.05), "Right": (-0.3, -1.0, 0.05)}


def nome_osso(nome):
    """'mixamorig:LeftArm' → 'LeftArm'."""
    return _PREFIXO.sub("", nome or "")


def rot_x(g):
    c, s = math.cos(math.radians(g)), math.sin(math.radians(g))
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)


def rot_y(g):
    c, s = math.cos(math.radians(g)), math.sin(math.radians(g))
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)


def rot_z(g):
    c, s = math.cos(math.radians(g)), math.sin(math.radians(g))
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)


def rot_graus(x, y, z):
    """Euler "XYZ" do three.js, como o Roll6 monta o giro: R = Rx·Ry·Rz (o Z age primeiro sobre o
    osso, o X por último), no referencial fixo do personagem."""
    return rot_x(x) @ rot_y(y) @ rot_z(z)


def rot_entre(a, b):
    """Rotação (3x3) que leva o vetor a para o vetor b."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = float(a @ b)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else rot_z(180)
    k = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + k + k @ k * (1 / (1 + c))


def _quat_mat(q):
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]], float)


class Primitiva:
    """Um pedaço da malha: vértices, triângulos e como colori-los."""

    def __init__(self):
        self.pos = self.nor = self.uv = self.juntas = self.pesos = self.tris = None
        self.cor = np.array([0.7, 0.7, 0.7])
        self.textura = None   # ndarray (h, w, 3) uint8
        self.no = None        # índice do nó da malha
        self.pele = None      # índice da pele, se houver


class Modelo:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        dados = self.caminho.read_bytes()
        if dados[:4] != b"glTF":
            raise ValueError("não é um .glb (glTF binário)")
        pos, self.j, self.bin = 12, None, b""
        while pos < len(dados):
            tam, tipo = struct.unpack("<II", dados[pos:pos + 8])
            corpo = dados[pos + 8:pos + 8 + tam]
            if tipo == 0x4E4F534A:
                self.j = json.loads(corpo)
            elif tipo == 0x004E4942:
                self.bin = corpo
            pos += 8 + tam
        self._nos()
        self._primitivas()

    # ---------- leitura ----------
    def _acessor(self, i):
        a = self.j["accessors"][i]
        bv = self.j["bufferViews"][a["bufferView"]]
        dt = np.dtype(_COMPONENTES[a["componentType"]])
        n = _NUM[a["type"]]
        ini = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        passo = bv.get("byteStride") or n * dt.itemsize
        if passo == n * dt.itemsize:
            arr = np.frombuffer(self.bin, dt, a["count"] * n, ini).reshape(a["count"], n)
        else:
            bruto = np.frombuffer(self.bin, np.uint8, passo * a["count"], ini).reshape(a["count"], passo)
            arr = bruto[:, :n * dt.itemsize].copy().view(dt).reshape(a["count"], n)
        if a.get("normalized"):
            arr = arr / float(np.iinfo(dt).max)
        return arr

    def _nos(self):
        nos = self.j["nodes"]
        self.pai = [-1] * len(nos)
        for i, n in enumerate(nos):
            for c in n.get("children", []):
                self.pai[c] = i
        self.nomes = [nome_osso(n.get("name", "")) for n in nos]
        self.local = []
        for n in nos:
            if "matrix" in n:
                m = np.array(n["matrix"], float).reshape(4, 4).T
            else:
                m = np.eye(4)
                t = np.array(n.get("translation", [0, 0, 0]), float)
                r = _quat_mat(n.get("rotation", [0, 0, 0, 1]))
                s = np.array(n.get("scale", [1, 1, 1]), float)
                m[:3, :3] = r @ np.diag(s)
                m[:3, 3] = t
            self.local.append(m)
        # ordem pai antes de filho
        ordem, visto = [], set()

        def visita(i):
            if i in visto:
                return
            if self.pai[i] >= 0:
                visita(self.pai[i])
            visto.add(i)
            ordem.append(i)
        for i in range(len(nos)):
            visita(i)
        self.ordem = ordem
        self.mundo = [None] * len(nos)
        for i in ordem:
            p = self.pai[i]
            self.mundo[i] = self.local[i] if p < 0 else self.mundo[p] @ self.local[i]
        self.por_nome = {}
        for i, nm in enumerate(self.nomes):
            self.por_nome.setdefault(nm, i)

    def _primitivas(self):
        j = self.j
        imgs = []
        for im in j.get("images", []):
            if "bufferView" in im:
                bv = j["bufferViews"][im["bufferView"]]
                bruto = self.bin[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]
                imgs.append(bruto)
            else:
                imgs.append(None)
        cache = {}

        def textura(ti):
            if ti not in cache:
                try:
                    fonte = j["textures"][ti]["source"]
                    cache[ti] = np.array(Image.open(io.BytesIO(imgs[fonte])).convert("RGB"))
                except Exception:
                    cache[ti] = None
            return cache[ti]

        self.peles = []
        for s in j.get("skins", []):
            ibm = self._acessor(s["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1) \
                if "inverseBindMatrices" in s else np.tile(np.eye(4), (len(s["joints"]), 1, 1))
            self.peles.append({"juntas": s["joints"], "ibm": ibm.astype(float)})

        self.prims = []
        for ni, n in enumerate(j["nodes"]):
            if "mesh" not in n:
                continue
            for p in j["meshes"][n["mesh"]]["primitives"]:
                if p.get("mode", 4) != 4:
                    continue
                a = p["attributes"]
                pr = Primitiva()
                pr.no, pr.pele = ni, n.get("skin")
                pr.pos = self._acessor(a["POSITION"]).astype(float)
                pr.nor = self._acessor(a["NORMAL"]).astype(float) if "NORMAL" in a else None
                pr.uv = self._acessor(a["TEXCOORD_0"]).astype(float) if "TEXCOORD_0" in a else None
                if "JOINTS_0" in a:
                    pr.juntas = self._acessor(a["JOINTS_0"]).astype(int)
                    pr.pesos = self._acessor(a["WEIGHTS_0"]).astype(float)
                if "indices" in p:
                    pr.tris = self._acessor(p["indices"]).astype(int).reshape(-1, 3)
                else:
                    pr.tris = np.arange(len(pr.pos)).reshape(-1, 3)
                if "material" in p:
                    pbr = j["materials"][p["material"]].get("pbrMetallicRoughness", {})
                    f = pbr.get("baseColorFactor", [1, 1, 1, 1])
                    pr.cor = np.array(f[:3], float)
                    if "baseColorTexture" in pbr:
                        pr.textura = textura(pbr["baseColorTexture"]["index"])
                self.prims.append(pr)

    # ---------- esqueleto ----------
    def osso(self, nome):
        return self.por_nome.get(nome)

    def ossos_mixamo(self):
        return [n for n in self.nomes if n]

    def altura_descanso(self):
        ys = np.concatenate([self._pos_descanso(p)[:, 1] for p in self.prims])
        return float(ys.max() - ys.min())

    def _pos_descanso(self, pr):
        return self._vertices(pr, self.mundo)[0]

    def esquerda_e_mais_x(self):
        """True se o osso 'LeftArm' está em +X (convenção do Roll6). Falso = modelo espelhado."""
        e, d = self.osso("LeftArm"), self.osso("RightArm")
        if e is None or d is None:
            return True
        return self.mundo[e][0, 3] > self.mundo[d][0, 3]

    def _relaxar(self):
        """{índice do osso do braço: rotação 3x3} que leva o braço do descanso até o relaxado.

        Igual ao `G0` do Roll6: do osso até o primeiro osso filho, rumo à direção de BRACO_ALVO."""
        d = {}
        for lado, alvo in BRACO_ALVO.items():
            a = self.osso(lado + "Arm")
            if a is None:
                continue
            filhos = [i for i in range(len(self.pai)) if self.pai[i] == a and self.nomes[i]]
            if not filhos:
                continue
            dir_ = self.mundo[filhos[0]][:3, 3] - self.mundo[a][:3, 3]
            d[a] = rot_entre(dir_, np.array(alvo, float))
        return d

    def matrizes(self, graus, hips_lift=0.0, hips_de="height", relaxar=True):
        """Matrizes de mundo (4x4) de todos os nós na pose pedida — a conta do Roll6.

        Cada osso com trilha leva um giro D (Euler XYZ, em graus, no referencial do personagem);
        o do braço leva também o "relaxado" (D = E·g). O giro acumula pela hierarquia
        (Q[filho] = Q[pai]·D[filho]) e age sobre a pose de descanso do osso: mundo = Q·descanso.
        """
        base = self._relaxar() if relaxar else {}
        n = len(self.local)
        q = [np.eye(3)] * n
        t = [None] * n
        out = [None] * n
        for i in self.ordem:
            p = self.pai[i]
            nome = self.nomes[i]
            d = np.eye(3)
            if nome in graus:
                d = rot_graus(*graus[nome])
                if i in base:
                    d = d @ base[i]
            qp = np.eye(3) if p < 0 else q[p]
            q[i] = qp @ d
            m = self.mundo[i]
            if p < 0:
                t[i] = m[:3, 3].copy()
            else:
                t[i] = t[p] + qp @ (m[:3, 3] - self.mundo[p][:3, 3])
            if nome == "Hips" and hips_lift:
                if hips_de == "hips":
                    ys = np.concatenate([self._pos_descanso(pr)[:, 1] for pr in self.prims])
                    ref = m[1, 3] - ys.min()
                else:
                    ref = self.altura_descanso()
                t[i] = t[i] + np.array([0, hips_lift * ref, 0])
            r = np.eye(4)
            r[:3, :3] = q[i] @ m[:3, :3]
            r[:3, 3] = t[i]
            out[i] = r
        return out

    def _vertices(self, pr, mundo):
        v = np.c_[pr.pos, np.ones(len(pr.pos))]
        nor = pr.nor
        if pr.pele is not None and pr.juntas is not None:
            pele = self.peles[pr.pele]
            jm = np.stack([mundo[nj] @ pele["ibm"][k] for k, nj in enumerate(pele["juntas"])])
            acc = np.zeros((len(v), 3))
            acn = np.zeros((len(v), 3))
            for k in range(4):
                w = pr.pesos[:, k:k + 1]
                if not np.any(w):
                    continue
                m = jm[pr.juntas[:, k]]
                acc += w * np.einsum("nij,nj->ni", m, v)[:, :3]
                if nor is not None:
                    acn += w * np.einsum("nij,nj->ni", m[:, :3, :3], nor)
            return acc, (acn if nor is not None else None)
        m = mundo[pr.no]
        return (v @ m.T)[:, :3], (nor @ m[:3, :3].T if nor is not None else None)

    def deformar(self, graus=None, hips_lift=0.0, hips_de="height", relaxar=True):
        """Devolve [(Primitiva, vertices(N,3), normais|None)] na pose pedida."""
        mundo = self.matrizes(graus or {}, hips_lift, hips_de, relaxar) if (graus or hips_lift or relaxar) \
            else self.mundo
        return [(pr,) + self._vertices(pr, mundo) for pr in self.prims], mundo


def carregar(caminho):
    return Modelo(caminho)
