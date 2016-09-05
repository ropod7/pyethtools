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

def _checkForHex(data):
    assert isinstance(data, unicode) or isinstance(data, str), "Unknown data format"
    if data.isdigit():
        return False
    try:
        longn = isinstance(int(data, 0), long)
        return longn if longn else isinstance(int(data, 0), int)
    except ValueError:
        return False

def intToPaddedHex(data):
    """Returns padded hex of int."""
    assert isinstance(data, int), "Given data not an int type"
    hexdata = hex(data)[2:]
    return _push(hexdata)

def floatToPaddedHex(data):
    """Returns padded hex of float."""
    assert isinstance(data, float), "Given data not a float type"
    left, right = toHex(data).split('.')
    hexed = left[2:], right
    return _push(hexed, floated=True)

def strToPaddedHex(data):
    """Returns padded hex of string."""
    assert isinstance(data, str) or isinstance(data, unicode), "Given data not a str or unicode type"
    hexed = toHex(data)
    chlen = len(hexed[2:])
    if chlen > 64:
        remain = chlen % 64
        if remain:
            tail = 64 - remain
            counter = chlen + tail
        else:
            counter = chlen
    else:
        tail = 64 - chlen
    return hexed + "0" * tail

def hexToPaddedHex(data):
    """Returns padded hex number."""
    assert _checkForHex(data), "Given data not hex, try 'strToPaddedHex'"
    if len(data) is 66:
        return data
    elif len(data) < 66:
        splitted = data.split('x')
        return _push(splitted[1])

def toHex(data):
    """Converts any value into HEX.
    Parameters:
    1. String|Number|Object|Array|BigNumber - The value to parse to HEX.
    If its a BigNumber it will make it the HEX value of a number."""
    def _mapper(symbol):
        return hex(ord(symbol))[2:]
    if isinstance(data, str):
        if _checkForHex(data):
            return data
        encoded = ["0x"]
        hexlist = list(map(_mapper, data))
        return ''.join(encoded + hexlist)
    elif isinstance(data, int):
        return hex(data)
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
    if isinstance(data, int):
        return intToPaddedHex(data)
    elif isinstance(data, float):
        return floatToPaddedHex(data)
    elif isinstance(data, str) or isinstance(data, unicode):
        isHex = _checkForHex(data)
        return hexToPaddedHex(data) if isHex else strToPaddedHex(data)
    elif isinstance(data, list):
        raise ValueError("Unsupported list data format")
    else:
        print data
        raise ValueError("Unsupported data format")

def getMethodID(signature):
    """Returns 4 bytes of sha3 function signature as function ID to give in 'getData'"""
    assert _checkForHex(signature), "Given signature not in hex format"
    return signature[:10]

def getData(params, data=None):
    """Returns fully encoded data with additional parameters that given on
    contract creation OR function calling.
    NB: On giving a list of parameters user will check the additional
    sequence of list to give them as in contract constructor or function
    call to encode equal sequence, because 'getData' is not a compiler:
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
        if isinstance(param, list):
            param.insert(0, len(param))
            return [1, param]
        elif isinstance(param, str) or isinstance(param, unicode):
            isHex = _checkForHex(param)
            if isHex or param.isdigit():
                arg = param
            else:
                arg = [1, [len(param), param]]
            return arg
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
    result = data + "".join(map(_mapper, hexarr))
    return result
