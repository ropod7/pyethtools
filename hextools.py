# -*- coding: utf8 -*-
import sys
from binascii import unhexlify
import json

def _push(data, floated=False):
    def _zeroes(part, padn):
        return "0" * (padn - len(part))
    padn = 64
    left = data
    right = ""
    if floated:
        padn = 32
        left, right = data
        right += _zeroes(right, padn)
    return '0x%s' % _zeroes(left, padn) + left + right

def _breakline(line, s=2, clean=True):
    if clean:
        z = u"0" * s
        return [line[i-s:i] for i in range(s, len(line)+1*s, s) if line[i-s:i] != z]
    else:
        return [line[i-s:i] for i in range(s, len(line)+1*s, s)]

def _assertNotString(data):
    _exc = "Unsupported data format %s" % type(data)
    if sys.version[0] is "2":
        assert isinstance(data, str) or isinstance(data, unicode), _exc
    else:
        assert isinstance(data, str) or isinstance(data, bytes), _exc

def _isstring(data):
    if sys.version[0] is "2":
        return isinstance(data, unicode) or isinstance(data, str)
    else:
        return isinstance(data, str) or isinstance(data, bytes)

def _checkForHex(data):
    if not _isstring(data):
        return False
    if data.isdigit() or data[:2] != '0x':
        return False
    try:
        try:
            longn = isinstance(int(data, 0), long)
        except NameError:
            longn = False
        return longn if longn else isinstance(int(data, 0), int)
    except ValueError:
        return False

def intToPaddedHex(data):
    """Returns padded hex of int."""
    assert isinstance(data, int) or isinstance(data, long), "Given data not an int type"
    hexdata = toHex(data)[2:]
    return _push(hexdata)

def floatToPaddedHex(data):
    """Returns padded hex of float."""
    assert isinstance(data, float), "Given data not a float type"
    left, right = toHex(data).split('.')
    hexed = left[2:], right
    return _push(hexed, floated=True)

def strToPaddedHex(data):
    """Returns padded hex of string."""
    _assertNotString(data)
    if sys.version[0] is "2":
        try:
            hexed = toHex(data.decode("utf8").encode("utf8"))
        except UnicodeEncodeError:
            hexed = toHex(unicode(data).encode("utf8"))
    else:
        hexed = toHex(data.encode("utf8"))
        hexed = toHex(data) if isinstance(hexed, bytes) else hexed
    chlen = len(hexed[2:])
    if chlen > 64:
        remain = chlen % 64
        if remain:
            tail = 64 - remain
            counter = chlen + tail
        else:
            tail = 0
            counter = chlen
    else:
        tail = 64 - chlen
    return hexed + "0" * tail

def hexToPaddedHex(data):
    """Returns padded hex number."""
    _assertNotString(data)
    assert _checkForHex(data), "Given data not hex, try 'strToPaddedHex'"
    if len(data) is 66:
        return data
    elif len(data) < 66:
        splitted = data.split('x')
        return _push(splitted[1])
    else:
        raise ValueError("Given datais too large.")

def toHex(data):
    """Converts any value into HEX.
    Parameters:
    1. String|Number|Object|Array|BigNumber - The value to parse to HEX.
    If its a BigNumber it will make it the HEX value of a number."""
    def _mapper(symbol):
        try:
            symbol = ord(symbol)
        except TypeError: pass
        hexed = hex(symbol)[2:]
        return hexed if symbol > 15 else '0' + hexed
    isstring = _isstring(data)
    if isstring:
        if _checkForHex(data):
            return data
        encoded = ["0x"]
        hexlist = list(map(_mapper, data))
        return ''.join(encoded + hexlist)
    elif isinstance(data, int):
        return hex(data)
    elif sys.version[0] is "2" and isinstance(data, long):
        return hex(data)[:-1]
    elif isinstance(data, float):
        integer = hex(int(data))
        fraction = format(data%int(data))
        fraction32 = hex(int(256*float(fraction)))[2:]
        return '.'.join([integer, fraction32])
    else:
        data = json.dumps(data)
        return toHex(data)

def encodeData(data):
    """Encodes any data to Ethereum blockchain format with paddings.
    Parameters:
    1. String|Number|Bool|BigNumber|Hexnumber|Address|Float - The value to encode.
    """
    isstring = _isstring(data)
    if isinstance(data, int):
        return intToPaddedHex(data)
    elif isinstance(data, float):
        return floatToPaddedHex(data)
    elif isstring:
        isHex = _checkForHex(data)
        return hexToPaddedHex(data) if isHex else strToPaddedHex(data)
    elif isinstance(data, list):
        raise ValueError("Unsupported list data format")
    else:
        raise ValueError("Unsupported data format")

def getMethodID(signature):
    """Returns 4 bytes of sha3 function signature as function ID to give in 'getData'"""
    assert _checkForHex(signature), "Given signature not in hex format"
    return signature[:10]

def getData(params, data=None):
    """Returns fully encoded data with additional parameters that given on
    contract creation OR function calling.
    NB: On giving a list of parameters make shore that the additional
    # sequence of list is equals to a contract constructor or function
    # call arguments for the required encoding, because 'getData' is not
    # a compiler.
    Parameters:
    1. Array - array of parameters.
        - Strings - dynamic argument.
        - Numbers.
        - Single level of Arrays of any type.
        - Booleans.
        - Addresses - contract or private account.
        - Floats.
    2. Data - contract code OR method ID, see 'getMethodID'"""
    def _paramsMapper(param):
        isstring = _isstring(param)
        if isinstance(param, list):
            param.insert(0, len(param))
            return [1, param]
        elif isstring:
            isHex = _checkForHex(param)
            if isHex or param.isdigit():
                return param
            else:
                try:
                    return [1, [len(param.encode("utf8")), param]]
                except UnicodeDecodeError:
                    return [1, [len(param), param]]
        elif isinstance(param, int) or isinstance(param, float):
            return param
    def _mapper(item):
        return encodeData(item)[2:]
    assert data is not None, "None type of data"
    assert _checkForHex(data), "Given data must be in hex format"
    assert isinstance(params, list) or len(params) is 0, "Given data must be in list format with len > 0"
    params = list(map(_paramsMapper, params))
    pos = len(params)
    hexarr = []
    i = 0
    for item in params:
        if isinstance(item, list):
            hexarr.insert(i, pos*32)
            pos += len(item[1])
            hexarr.extend(item[1])
        else:
            hexarr.insert(i, item)
        i+=1
    result = data + "".join(list(map(_mapper, hexarr)))
    return result

def decodeArgData(data, types=()):
    """Returns list of fully decoded Data received from active
    contract on blockchain.
    To decode data make shore that the given list of types have the same
    sequence as contract returns, otherwise function returns exception.
    To decode automatically simple results see 'decodeData'.
    Parameters:
    1. Hexnumber - result that contract returns
    2. Equal sequence of Solidity types placed to the Python tuple.
        - Python int is Solidity uint8/uint256 types
        - Python str/unicode is Solidity bytes (not all) or string types
        - Python str of digits [str.isdigit()] is a Solidity bytes10 type
        - Python hex format is any hash types of Solidity (address|tx hash etc.)
        - Python float is a Soliditys fixed128x128 (returns in hex format)."""
    _assertNotString(data)
    assert data is not None or _checkForHex(data), _exc
    assert isinstance(types, tuple), "Types must be a sequence of tuple"
    assert types, "Zero length of types"
    assert dict not in types, "Unsupported type of dict"
    assert tuple not in types, "Unsupported type of tuple"
    assert not (len(data)-2) % 64, "Unknown length of Hexnumber"
    if data == u"0x": return [hex(0)]
    def _typeMapper(line):
        if line[0] is list:
            return line[1:]
        tp, data = line
        if sys.version[0] is "2":
            isstring = tp is str or tp is unicode
        else:
            isstring = tp is str
        if isstring:
            return toUnicode(data)
        elif tp is int or sys.version[0] is "2" and tp is long:
            return tp(data, 0) if data != "0x" else 0
        elif tp is float:
            left, right = data[:32], data[32:34]
            data = ".".join([''.join(_breakline(left)), right])
            return "0x" + ''.join(_breakline(data, s=1))
        elif tp is hex:
            return data
        else:
            raise TypeError("%s Unsopported type format" % tp)
    data = data[2:]
    lines = _breakline(data, s=64, clean=False)
    lentypes = len(types) if types else len(lines)
    decoded = []
    j = 0
    for i in range(lentypes):
        hexline = "0x" + lines[j]
        if sys.version[0] is "2":
            isstring = types[i] is str or types[i] is unicode
        else:
            isstring = types[i] is str
        if not types:
            decoded.append("".join(_breakline(hexline)))
        elif types[i] is list:
            raise TypeError("list must be a list of types, not a type of list")
        elif types[i] is int:
            decoded.append([types[i], hexline])
        elif types[i] is float:
            decoded.append([types[i], hexline[2:]])
        elif isstring and hexline[2:4] == u"00":
            strpos = int(hexline, 0) // 32 + 1
            strlen = int("0x" + lines[strpos-1], 0) * 2
            strpos = strpos * 64
            listobj = [types[i], "0x" + data[strpos:strpos+strlen]]
            decoded.append(listobj)
        elif type(types[i]) is list:
            assert types[i], "Empty list"
            pos = j * 64 + len(types[i]) * 64
            hexstr = "0x" + data[j*64:pos]
            array = decodeArgData(hexstr, types=tuple(types[i]))
            array.insert(0, list)
            decoded.append(array)
            j += len(types[i]) - 1
        else:
            decoded.append([types[i], "".join(_breakline(hexline))])
        j += 1
    return list(map(_typeMapper, decoded)) if types else decoded

def decodeWord(word):
    _assertNotString(word)
    assert word is not None or _checkForHex(word), _exc
    testline = "".join(_breakline(word))
    if len(testline) < 38:
        return int(word, 0)
    else:
        return testline

def toUnicode(word):
    _assertNotString(word)
    assert word is not None or not _checkForHex(word), _exc
    return unhexlify(word[2:])

def decodeData(data):
    """Returns list of fully decoded Data received from active
    contract on blockchain.
    To decode more complex results see 'decodeArgData'.
    Parameters:
    1. Hexnumber - result that contract returns"""
    _assertNotString(data)
    assert data is not None or _checkForHex(data), _exc
    assert not (len(data)-2) % 64, "Unknown length of bytes"
    if data == u"0x": return [hex(0)]
    def _decode(line):
        if isinstance(line, tuple):
            try:
                return toUnicode(line[0]).decode("utf8")
            except UnicodeDecodeError:
                return line[0]
        else:
            return decodeWord(line)
    data = data[2:]
    counter = len(data) + 64
    lines = _breakline(data, s=64, clean=False)
    decoded = []
    strline = ""
    empty = u"00"
    linepos = []
    lenlines = len(lines)
    for i in range(lenlines-1, -1, -1):
        l = lines[i]
        hexline = "0x" + l
        zerohead, zerotail = l.startswith(empty), l.endswith(empty)
        # check for last line of string
        if zerotail and not zerohead and not strline:
            l = "".join(_breakline(l))
            strline = l + strline
        # check for bytes10 string
        elif zerotail and not zerohead and strline:
            decoded.append(("0x" + strline,))
            strline = ""
            l = "".join(_breakline(l))
            strline = l + strline
        # if multiply lines in string
        elif not zerotail and not zerohead:
            strline = l + strline
        # check for line that contains length of string
        elif zerohead and int(hexline, 0) == len(strline)//2 and strline:
            decoded.append(("0x" + strline,))
            strline = ""
            linepos.insert(0, float(i))
        # if not string or bytes10 types just append
        elif int(hexline, 0)/32.0 not in linepos:
            if strline:
                decoded.append(("0x" + strline,))
                strline = ""
            decoded.extend(["0x" + l])
        # if line contains start byte of string
        else:
            if linepos:
                linepos.pop()
    return list(map(_decode, reversed(decoded)))
