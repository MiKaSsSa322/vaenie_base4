#!/usr/bin/env python3
"""Offline sanity checks for Frontier: Military Installations data assets."""
import gzip, json, pathlib, struct, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / 'src/main/resources'

def read_nbt(path):
    data = memoryview(gzip.decompress(path.read_bytes()))
    pos = 0
    def take(n):
        nonlocal pos
        out = data[pos:pos+n]; pos += n
        if len(out) != n: raise ValueError('unexpected end of NBT')
        return out
    def u16(): return struct.unpack('>H', take(2))[0]
    def name(): return bytes(take(u16())).decode('utf-8')
    def payload(tag):
        if tag == 1: return struct.unpack('>b', take(1))[0]
        if tag == 2: return struct.unpack('>h', take(2))[0]
        if tag == 3: return struct.unpack('>i', take(4))[0]
        if tag == 4: return struct.unpack('>q', take(8))[0]
        if tag == 5: return struct.unpack('>f', take(4))[0]
        if tag == 6: return struct.unpack('>d', take(8))[0]
        if tag == 7:
            n=struct.unpack('>i',take(4))[0]; return bytes(take(n))
        if tag == 8: return name()
        if tag == 9:
            t=struct.unpack('>B',take(1))[0]; n=struct.unpack('>i',take(4))[0]
            return [payload(t) for _ in range(n)]
        if tag == 10:
            result={}
            while True:
                t=struct.unpack('>B',take(1))[0]
                if t == 0: return result
                key = name()
                result[key] = payload(t)
        if tag == 11:
            n=struct.unpack('>i',take(4))[0]; return list(struct.unpack('>'+'i'*n,take(4*n)))
        if tag == 12:
            n=struct.unpack('>i',take(4))[0]; return list(struct.unpack('>'+'q'*n,take(8*n)))
        raise ValueError(f'unknown NBT tag {tag}')
    if struct.unpack('>B',take(1))[0] != 10: raise ValueError('root is not compound')
    name() # root name
    root=payload(10)
    if pos != len(data): raise ValueError('trailing NBT bytes')
    return root

def fail(msg):
    print('FAIL:', msg); sys.exit(1)

names = ['field_dugout','observation_post','small_camp','reinforced_bunker','fortified_camp','large_base']
for name in names:
    nbt_path=RES/f'data/frontierinstallations/structures/{name}.nbt'
    if not nbt_path.exists(): fail(f'missing structure template {name}')
    nbt=read_nbt(nbt_path)
    size=nbt.get('size'); palette=nbt.get('palette'); blocks=nbt.get('blocks')
    if not (isinstance(size,list) and len(size)==3 and all(isinstance(x,int) and x>0 for x in size)):
        fail(f'{name}: invalid size {size}')
    if not palette or not blocks: fail(f'{name}: empty palette or blocks')
    seen=set()
    for entry in blocks:
        pos=entry.get('pos'); state=entry.get('state')
        if not isinstance(pos,list) or len(pos)!=3: fail(f'{name}: invalid block position')
        if not all(0 <= pos[i] < size[i] for i in range(3)): fail(f'{name}: block out of bounds {pos}')
        if not isinstance(state,int) or not 0 <= state < len(palette): fail(f'{name}: invalid palette index')
        key=tuple(pos)
        if key in seen: fail(f'{name}: duplicate block position {key}')
        seen.add(key)
    for folder in ('structure','structure_set','template_pool'):
        p=RES/f'data/frontierinstallations/worldgen/{folder}/{name}.json'
        if not p.exists(): fail(f'missing worldgen {folder} for {name}')
        json.loads(p.read_text(encoding='utf-8'))
    st=json.loads((RES/f'data/frontierinstallations/worldgen/structure/{name}.json').read_text())
    pool=json.loads((RES/f'data/frontierinstallations/worldgen/template_pool/{name}.json').read_text())
    if st.get('start_pool') != f'frontierinstallations:{name}': fail(f'{name}: start_pool mismatch')
    loc=pool['elements'][0]['element'].get('location')
    if loc != f'frontierinstallations:{name}': fail(f'{name}: template location mismatch')
    print(f'OK {name}: {len(blocks)} blocks, size {size}, palette {len(palette)}')
print('PASS: all 6 NBT templates and 18 worldgen JSON files are structurally consistent.')
