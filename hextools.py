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
    assert isinstance(data, int), "Given data not an int type"
    hexdata = hex(data)[2:]
    return _push(hexdata)

def floatToPaddedHex(data):
    assert isinstance(data, float), "Given data not a float type"
    integer = hex(int(data))[2:]
    fraction = format(data%int(data))
    fraction32 = hex(int(256*float(fraction)))[2:]
    hexed = [integer, fraction32]
    return _push(hexed, floated=True)

def strToPaddedHex(data):
    assert isinstance(data, str) or isinstance(data, unicode), "Given data not a str or unicode type"
    hexed = strToHex(data)
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
    assert _checkForHex(data), "Given data not hex, try 'strToPaddedHex'"
    if len(data) is 66:
        return data
    elif len(data) < 66:
        splitted = data.split('x')
        return _push(splitted[1])

def strToHex(data):
    """Converts any value into HEX.
    Parameters:
    1. String|Number|Object|Array|BigNumber - The value to parse to HEX.
    If its a BigNumber it will make it the HEX value of a number."""
    def _mapper(symbol):
        return hex(ord(symbol))[2:]
    strinp = isinstance(data, str)
    data = json.dumps(data)
    data = data[1:-1] if strinp else data
    encoded = ["0x"]
    hexlist = list(map(_mapper, data))
    return ''.join(encoded + hexlist)

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

def getMethodID(self, signature):
    assert _checkForHex(signature), "Given signature not in hex format"
    return signature[:10]

def getData(params, data=None):
    """Returns fully encoded additional parameters that given on contract creation OR
    function calling.
    Parameters:
    1. Array - array of parameters.
        - Strings - dynamic argument.
        - Numbers.
        - Single level of Arrays of any type.
        - Booleans.
        - Addresses - contract or private account.
        - Floats."""
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
    data32 = list(map(_paramsMapper, params))
    pos = len(data32)
    hexarr = []
    i = 0
    for item in data32:
        if isinstance(item, list):
            hexarr.insert(i, pos*32)
            pos += len(item[1])
            hexarr.extend(item[1])
        else:
            hexarr.insert(i, item)
        i+=1
    result = data + "".join(map(_mapper, hexarr))
    return result

if __name__ == "__main__":
    from request import Request
    req = Request('http://localhost', 8545)
    string = u"The Solidity optimizer operates on assembly, so it can be and also is used by other languages. It splits the sequence of instructions into basic blocks at JUMPs and JUMPDESTs. Inside these blocks, the instructions are analysed and every modification to the stack, to memory or storage is recorded as an expression which consists of an instruction and a list of arguments which are essentially pointers to other expressions"
    #print encodeData(3.978)
    data = getData([u'0x123', ['0x456', '0x789'], "1234567890", 765.122, string], data="0x26e365b0")
    #print data
    remain = len(data)%64
    counter = len(data) + 64-remain if remain else len(data)+64
    data = data[10:]
    for line in [data[i-64:i] for i in range(64,counter,64)]:
        print line
    #print [string[i-64:i] for i in range(64,2880,64)]
